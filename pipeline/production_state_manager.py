"""
Cinema X-Ray: Production State Manager, Checkpointing & Recovery Engine
-----------------------------------------------------------------------
Implements resilient state tracking and recovery across all 24 production phases:
  - Atomic JSON checkpointing to production_state.json.
  - Granular stage logging with timestamps, retry attempts, and artifact receipts.
  - Resumption verification (checks that reported artifacts exist and are non-empty before skipping).
  - Exponential backoff retry handler for transient errors.
  - Safe rollback and temporary file isolation.
"""

import os
import time
import json
import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


class ProductionState(str, Enum):
    # 24 Canonical Production States
    INIT = "INIT"
    IDEA_SELECTED = "IDEA_SELECTED"
    TOPIC_RESERVED = "TOPIC_RESERVED"
    RESEARCH_STARTED = "RESEARCH_STARTED"
    RESEARCH_DOSSIER_COMPLETE = "RESEARCH_DOSSIER_COMPLETE"
    RESEARCH_VERIFIED = "RESEARCH_VERIFIED"
    SCRIPT_STARTED = "SCRIPT_STARTED"
    SCRIPT_DRAFTED = "SCRIPT_DRAFTED"
    SCRIPT_EVALUATED = "SCRIPT_EVALUATED"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"
    SCENE_PLAN_STARTED = "SCENE_PLAN_STARTED"
    SCENE_PLAN_COMPLETE = "SCENE_PLAN_COMPLETE"
    SCENE_PLAN_VERIFIED = "SCENE_PLAN_VERIFIED"
    ASSETS_SOURCED = "ASSETS_SOURCED"
    ASSETS_VERIFIED = "ASSETS_VERIFIED"
    AUDIO_GENERATED = "AUDIO_GENERATED"
    AUDIO_VERIFIED = "AUDIO_VERIFIED"
    SUBTITLES_GENERATED = "SUBTITLES_GENERATED"
    SUBTITLES_VERIFIED = "SUBTITLES_VERIFIED"
    COMPOSITION_READY = "COMPOSITION_READY"
    VIDEO_RENDERED = "VIDEO_RENDERED"
    VIDEO_QC_PASSED = "VIDEO_QC_PASSED"
    METADATA_GENERATED = "METADATA_GENERATED"
    VIDEO_UPLOADED = "VIDEO_UPLOADED"
    COMPLETED = "COMPLETED"

    # Terminal / Recovery States
    FAILED = "FAILED"
    ABORTED = "ABORTED"
    ROLLED_BACK = "ROLLED_BACK"


# Expected artifact rules for validating checkpoints before resuming
STATE_ARTIFACT_REQUIREMENTS: Dict[ProductionState, List[str]] = {
    ProductionState.TOPIC_RESERVED: [],
    ProductionState.RESEARCH_DOSSIER_COMPLETE: ["research/research_dossier.json"],
    ProductionState.RESEARCH_VERIFIED: ["research/research_dossier.json"],
    ProductionState.SCRIPT_APPROVED: ["script/approved_script.txt"],
    ProductionState.SCENE_PLAN_COMPLETE: ["scene_plan.json"],
    ProductionState.SCENE_PLAN_VERIFIED: ["scene_plan.json"],
    ProductionState.ASSETS_VERIFIED: ["scene_plan.json"],
    ProductionState.AUDIO_GENERATED: ["assets/narration/master_narration.wav"],
    ProductionState.AUDIO_VERIFIED: ["assets/narration/master_narration.wav"],
    ProductionState.SUBTITLES_GENERATED: ["subtitles.ass"],
    ProductionState.SUBTITLES_VERIFIED: ["subtitles.ass"],
    ProductionState.VIDEO_RENDERED: ["output/cinema_xray_*_1080p.mp4"],
    ProductionState.VIDEO_QC_PASSED: ["output/qc_report.json"],
    ProductionState.METADATA_GENERATED: ["metadata.json", "METADATA.md"],
    ProductionState.VIDEO_UPLOADED: ["upload_record.json"],
    ProductionState.COMPLETED: ["output/qc_report.json", "metadata.json", "upload_record.json"]
}


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    timestamp: str
    artifacts: List[str] = field(default_factory=list)
    duration_sec: float = 0.0
    notes: str = ""


class ProductionStateManager:
    """Manages transactional state transitions, persistence, and checkpoint resumption."""

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.state_file = self.project_dir / "production_state.json"
        self.current_state = ProductionState.INIT
        self.history: List[StateTransitionRecord] = []
        self.metadata: Dict[str, Any] = {}
        self.errors: List[Dict[str, Any]] = []
        self._last_transition_time = time.time()

        if self.state_file.exists():
            self.load()

    def load(self) -> None:
        """Loads state checkpoint from disk."""
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.current_state = ProductionState(data.get("current_state", ProductionState.INIT))
            self.metadata = data.get("metadata", {})
            self.errors = data.get("errors", [])
            self.history = [StateTransitionRecord(**rec) for rec in data.get("history", [])]
        except Exception as e:
            print(f"⚠️ Error reading production state checkpoint from {self.state_file}: {e}")
            self.current_state = ProductionState.INIT

    def save(self) -> None:
        """Atomically saves state checkpoint to production_state.json."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "project_name": self.project_dir.name,
            "current_state": self.current_state.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
            "errors": self.errors,
            "history": [asdict(h) for h in self.history]
        }
        # Atomic write via temp file
        temp_file = self.project_dir / f"production_state.json.tmp.{os.getpid()}"
        temp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_file.replace(self.state_file)

    def transition_to(
        self,
        new_state: ProductionState,
        artifacts: Optional[List[str]] = None,
        notes: str = ""
    ) -> None:
        """Executes a state transition, records duration, and persists state."""
        now = time.time()
        dur = round(now - self._last_transition_time, 2)
        rec = StateTransitionRecord(
            from_state=self.current_state.value,
            to_state=new_state.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            artifacts=artifacts or [],
            duration_sec=dur,
            notes=notes
        )
        self.history.append(rec)
        old_state = self.current_state
        self.current_state = new_state
        self._last_transition_time = now
        self.save()
        print(f"🔄 State Transition: [{old_state.value}] ➔ [{new_state.value}] ({dur:.2f}s)")

    def validate_resumption(self) -> Tuple[bool, ProductionState, str]:
        """
        Inspects the recorded state and verifies that all prerequisite artifacts
        actually exist on disk before permitting resumption.
        Returns (is_valid, safe_resumption_state, reason).
        """
        if self.current_state in [ProductionState.INIT, ProductionState.FAILED, ProductionState.ABORTED]:
            return True, self.current_state, "Fresh start or terminal state."

        # Check all requirements up to current state
        states_enum_list = list(ProductionState)
        try:
            curr_idx = states_enum_list.index(self.current_state)
        except ValueError:
            return False, ProductionState.INIT, f"Unrecognized state {self.current_state}"

        # Step backwards to find the highest verified state whose artifacts exist
        for state in reversed(states_enum_list[:curr_idx + 1]):
            reqs = STATE_ARTIFACT_REQUIREMENTS.get(state, [])
            all_exist = True
            for pattern in reqs:
                if "*" in pattern:
                    matches = list(self.project_dir.glob(pattern))
                    if not matches or matches[0].stat().st_size == 0:
                        all_exist = False
                        break
                else:
                    target_p = self.project_dir / pattern
                    if not target_p.exists() or target_p.stat().st_size == 0:
                        all_exist = False
                        break

            if all_exist:
                if state != self.current_state:
                    print(f"⚠️ Resumption fallback: Artifacts missing for {self.current_state.value}. Safely rolling back to verified state: {state.value}")
                    self.transition_to(state, notes="Fallback due to missing downstream artifacts.")
                return True, state, f"Artifacts verified up to {state.value}."

        return False, ProductionState.INIT, "No prerequisite artifacts found on disk."

    def record_error(self, message: str, is_recoverable: bool = False, exc: Optional[Exception] = None) -> None:
        """Logs an error to the persistent history."""
        err = {
            "state": self.current_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": str(message),
            "is_recoverable": is_recoverable,
            "exception_type": type(exc).__name__ if exc else None
        }
        self.errors.append(err)
        if not is_recoverable:
            self.transition_to(ProductionState.FAILED, notes=f"Critical failure: {message}")
        else:
            self.save()

    def retry_with_backoff(
        self,
        fn: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        factor: float = 2.0,
        operation_name: str = "Operation"
    ) -> Any:
        """Executes a function with exponential backoff on transient exceptions."""
        delay = initial_delay
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_exc = e
                print(f"⚠️ {operation_name} failed (Attempt {attempt}/{max_retries}): {e}")
                self.record_error(f"{operation_name} attempt {attempt} failed: {e}", is_recoverable=(attempt < max_retries), exc=e)
                if attempt < max_retries:
                    print(f"⏳ Backoff waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
                    delay *= factor
                else:
                    break
        raise last_exc

    def cleanup_temporary_files(self) -> int:
        """Safely removes temporary .tmp, .wav fragments, or aborted renders."""
        removed = 0
        for tmp in self.project_dir.glob("**/*.tmp*"):
            try:
                if tmp.is_file():
                    tmp.unlink()
                    removed += 1
            except Exception:
                pass
        return removed
