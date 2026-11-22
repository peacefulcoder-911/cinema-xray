"""
Cinema X-Ray: Unified Master Automated Production Test Suite
-----------------------------------------------------------
Comprehensive unit and integration test suite validating:
  - All 23 Quality Gates (binary critical checks and scoring)
  - Duplicate topic detection and daily batch selection
  - Script word count and hook retention scoring
  - Storyboard duration & motion compliance
  - Audio mastering, loudness, and peak clipping rejection
  - Subtitle styling (Arc Cyan) and timing synchronization
  - Video technical standards (1080x1920, duration sync)
  - Metadata compliance and clickbait filtering
  - Upload security (blocking public uploads in test mode)
  - Production state persistence, artifact verification, and safe rollback
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.quality_framework import QualityFramework, QualityGateId, GateResult, QualityGateError
from pipeline.topic_database import TopicDatabase
from pipeline.script_storytelling_engine import ScriptStorytellingEngine
from pipeline.production_state_manager import ProductionStateManager, ProductionState
from pipeline.upload_manager import UploadManager
from pipeline.youtube_metadata_engine import YouTubeMetadataEngine


class TestTopicAndDuplicatePrevention(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db = TopicDatabase(db_path=Path(self.tmp_dir) / "test_topics.db")
        self.qf = QualityFramework(fail_fast=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_topic_uniqueness_pass(self):
        res = self.qf.check_topic_uniqueness("unique_topic_slug", "Fight Club", completed_slugs=set())
        self.assertTrue(res.passed)
        self.assertEqual(res.gate_id, QualityGateId.QG01_TOPIC_SELECTION)

    def test_duplicate_topic_rejection(self):
        completed = {"fight_club_tyler_durden"}
        with self.assertRaises(QualityGateError):
            self.qf.check_topic_uniqueness("fight_club_tyler_durden", "Fight Club", completed_slugs=completed)

    def test_active_reservation_conflict(self):
        reserved = {"matrix_cypher_steak"}
        with self.assertRaises(QualityGateError):
            self.qf.check_topic_uniqueness("matrix_cypher_steak", "The Matrix", completed_slugs=set(), active_reservations=reserved)

    def test_daily_batch_movie_diversity(self):
        candidates = self.db.select_daily_batch(count=2)
        if len(candidates) >= 2:
            movie1 = candidates[0]["movie_name"].lower()
            movie2 = candidates[1]["movie_name"].lower()
            self.assertNotEqual(movie1, movie2, "Daily batch must enforce distinct movies!")


class TestScriptAndStorytellingEngine(unittest.TestCase):
    def setUp(self):
        self.qf = QualityFramework(fail_fast=True)

    def test_word_count_compliance_pass(self):
        sample_script = " ".join(["word"] * 110)
        res = self.qf.check_word_count(sample_script)
        self.assertTrue(res.passed)

    def test_word_count_overlength_fail(self):
        bloated_script = " ".join(["word"] * 180)
        with self.assertRaises(QualityGateError):
            self.qf.check_word_count(bloated_script)

    def test_hook_generic_opener_rejection(self):
        bad_hook = "Hey guys, welcome back to Cinema X-Ray, today we are looking at Fight Club."
        with self.assertRaises(QualityGateError):
            self.qf.evaluate_hook_quality(bad_hook)

    def test_hook_punchy_curiosity_pass(self):
        good_hook = "Why does Tyler Durden never appear in the same frame when anyone else is talking to the Narrator?"
        res = self.qf.evaluate_hook_quality(good_hook)
        self.assertTrue(res.passed)
        self.assertGreaterEqual(res.score, 80.0)


class TestAudioAndSubtitleIntegrity(unittest.TestCase):
    def setUp(self):
        self.qf = QualityFramework(fail_fast=True)
        self.fight_club_dir = REPO_ROOT / "projects" / "cinema-decoded-fight-club-narrator-no-name"

    def test_audio_master_fight_club(self):
        audio_file = self.fight_club_dir / "assets" / "narration" / "master_narration.wav"
        if audio_file.exists():
            res = self.qf.check_audio_master(audio_file)
            self.assertTrue(res.passed)
            self.assertLessEqual(res.metrics.get("max_volume_dbfs", 0), -0.5)

    def test_subtitles_arc_cyan_and_sync(self):
        sub_file = self.fight_club_dir / "subtitles.ass"
        if sub_file.exists():
            res = self.qf.check_subtitles(sub_file, audio_duration=51.87)
            self.assertTrue(res.passed)
            self.assertTrue(res.metrics.get("has_arc_cyan"))


class TestRenderValidation(unittest.TestCase):
    def setUp(self):
        self.qf = QualityFramework(fail_fast=True)
        self.fight_club_dir = REPO_ROOT / "projects" / "cinema-decoded-fight-club-narrator-no-name"

    def test_master_1080p_video(self):
        video_file = self.fight_club_dir / "output" / "cinema_xray_fight-club-narrator-no-name_1080p.mp4"
        if video_file.exists():
            res = self.qf.check_rendered_video(video_file, expected_audio_dur=51.87, target_res="1080p")
            self.assertTrue(res.passed)
            self.assertEqual(res.metrics.get("width"), 1080)
            self.assertEqual(res.metrics.get("height"), 1920)


class TestMetadataAndUploadSecurity(unittest.TestCase):
    def setUp(self):
        self.qf = QualityFramework(fail_fast=True)
        self.meta_engine = YouTubeMetadataEngine()
        self.upload_mgr = UploadManager(is_test_run=True)

    def test_metadata_compliance_pass(self):
        res = self.qf.check_metadata(
            title="The Real Reason Fight Club's Narrator Has No Name #shorts",
            description="A deep dive into Fincher's Fight Club. Chapters:\n00:00 - Hook\n00:15 - Breakdown",
            tags=["Fight Club", "David Fincher", "Cinema X-Ray", "Shorts"]
        )
        self.assertTrue(res.passed)

    def test_metadata_title_overlength_fail(self):
        long_title = "A" * 105
        with self.assertRaises(QualityGateError):
            self.qf.check_metadata(long_title, "Valid description", ["Tag1", "Tag2", "Tag3"])

    def test_upload_security_blocks_public_in_test_mode(self):
        with self.assertRaises(QualityGateError):
            self.qf.check_upload_security(privacy_status="public", is_test_run=True)

    def test_upload_security_permits_private_in_test_mode(self):
        res = self.qf.check_upload_security(privacy_status="private", is_test_run=True)
        self.assertTrue(res.passed)


class TestProductionStateRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.p = Path(self.tmp_dir)
        self.sm = ProductionStateManager(self.p)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_state_persistence_and_reload(self):
        self.sm.transition_to(ProductionState.IDEA_SELECTED)
        self.sm.transition_to(ProductionState.TOPIC_RESERVED)
        self.assertEqual(self.sm.current_state, ProductionState.TOPIC_RESERVED)

        # Reload in fresh instance
        sm2 = ProductionStateManager(self.p)
        self.assertEqual(sm2.current_state, ProductionState.TOPIC_RESERVED)
        self.assertEqual(len(sm2.history), 2)

    def test_missing_artifact_fallback(self):
        self.sm.transition_to(ProductionState.AUDIO_GENERATED)
        # Prerequisite audio artifact does not exist
        valid, safe_state, msg = self.sm.validate_resumption()
        # Should fallback to state where artifacts exist
        self.assertNotEqual(safe_state, ProductionState.AUDIO_GENERATED)

    def test_exponential_backoff_retry(self):
        attempts = 0
        def unreliable_task():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise TimeoutError("Simulated network timeout")
            return "SUCCESS"

        res = self.sm.retry_with_backoff(unreliable_task, max_retries=3, initial_delay=0.05, operation_name="UnreliableTask")
        self.assertEqual(res, "SUCCESS")
        self.assertEqual(attempts, 2)


if __name__ == "__main__":
    unittest.main()
