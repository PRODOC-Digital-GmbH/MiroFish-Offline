"""
Unit tests for MIR-17: BenchmarkCollector + evaluate_content
"""

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.services.benchmark_collector import (
    BenchmarkCollector,
    evaluate_content,
    _calc_quality_score,
    _eval_platform,
)


# ========== Helpers ==========

def _create_test_db(db_path: str, posts: list[dict], comments: list[dict] | None = None):
    """Create a SQLite DB matching the OASIS simulation schema with test data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE user (
            user_id INTEGER PRIMARY KEY,
            agent_id INTEGER,
            user_name TEXT,
            name TEXT,
            bio TEXT,
            created_at DATETIME,
            num_followings INTEGER DEFAULT 0,
            num_followers INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE post (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_post_id INTEGER,
            content TEXT DEFAULT '',
            quote_content TEXT,
            created_at DATETIME,
            num_likes INTEGER DEFAULT 0,
            num_dislikes INTEGER DEFAULT 0,
            num_shares INTEGER DEFAULT 0,
            num_reports INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES user(user_id),
            FOREIGN KEY(original_post_id) REFERENCES post(post_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE comment (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            num_likes INTEGER DEFAULT 0,
            num_dislikes INTEGER DEFAULT 0,
            FOREIGN KEY(post_id) REFERENCES post(post_id),
            FOREIGN KEY(user_id) REFERENCES user(user_id)
        )
    """)

    # Insert a default user
    cursor.execute("INSERT INTO user (user_id, agent_id, user_name, name) VALUES (1, 1, 'test_agent', 'Test')")

    for p in posts:
        cursor.execute(
            "INSERT INTO post (user_id, original_post_id, content, num_likes, num_dislikes, num_shares) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (1, p.get("original_post_id"), p.get("content", ""),
             p.get("num_likes", 0), p.get("num_dislikes", 0), p.get("num_shares", 0))
        )

    for c in (comments or []):
        cursor.execute(
            "INSERT INTO comment (post_id, user_id, content) VALUES (?, ?, ?)",
            (c.get("post_id", 1), 1, c.get("content", ""))
        )

    conn.commit()
    conn.close()


# ========== BenchmarkCollector Tests ==========

class TestBenchmarkCollector:

    def test_start_end_phase(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        bc.start_phase("entity_reading")
        bc.end_phase("entity_reading")

        assert "entity_reading_start" in bc._timestamps
        assert "entity_reading_end" in bc._timestamps
        # Both should be valid ISO timestamps
        datetime.fromisoformat(bc._timestamps["entity_reading_start"])
        datetime.fromisoformat(bc._timestamps["entity_reading_end"])

    def test_set_metric(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        bc.set_metric("agents_count", 42)
        bc.set_metric("model_name", "qwen2.5:14b")

        assert bc._metrics["agents_count"] == 42
        assert bc._metrics["model_name"] == "qwen2.5:14b"

    def test_set_timestamp(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        ts = "2026-04-21T12:00:00"
        bc.set_timestamp("simulation", "start", ts)
        bc.set_timestamp("simulation", "end", "2026-04-21T13:00:00")

        assert bc._timestamps["simulation_start"] == ts
        assert bc._timestamps["simulation_end"] == "2026-04-21T13:00:00"

    def test_calc_durations(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        bc.set_timestamp("entity_reading", "start", "2026-04-21T10:00:00")
        bc.set_timestamp("entity_reading", "end", "2026-04-21T10:00:30")
        bc.set_timestamp("profile_generation", "start", "2026-04-21T10:00:30")
        bc.set_timestamp("profile_generation", "end", "2026-04-21T10:05:30")

        durations = bc.get_durations()
        assert durations["entity_reading"] == 30.0
        assert durations["profile_generation"] == 300.0
        assert durations["total_pipeline"] == 330.0

    def test_calc_durations_incomplete_phase(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        bc.set_timestamp("entity_reading", "start", "2026-04-21T10:00:00")
        # No end timestamp
        bc.set_timestamp("profile_generation", "start", "2026-04-21T10:00:30")
        bc.set_timestamp("profile_generation", "end", "2026-04-21T10:05:30")

        durations = bc.get_durations()
        assert "entity_reading" not in durations
        assert durations["profile_generation"] == 300.0

    def test_save_and_reload(self, tmp_path):
        bc = BenchmarkCollector(str(tmp_path))
        bc.start_phase("test_phase")
        bc.end_phase("test_phase")
        bc.set_metric("chunks_count", 29)
        bc.save()

        # Verify file exists
        timing_path = tmp_path / "timing.json"
        assert timing_path.exists()

        # Reload and verify data preserved
        bc2 = BenchmarkCollector(str(tmp_path))
        assert "test_phase_start" in bc2._timestamps
        assert "test_phase_end" in bc2._timestamps
        assert bc2._metrics["chunks_count"] == 29

    @patch("app.services.benchmark_collector.Config")
    def test_save_includes_model_config(self, mock_config, tmp_path):
        mock_config.LLM_MODEL_NAME = "qwen2.5:14b"
        mock_config.NER_MODEL_NAME = "phi4-mini-ner"
        mock_config.EMBEDDING_MODEL = "qwen3-embedding:0.6b-fp16"
        mock_config.OUTPUT_LANGUAGE = "English"

        bc = BenchmarkCollector(str(tmp_path))
        bc.save()

        with open(tmp_path / "timing.json") as f:
            data = json.load(f)

        assert data["model"] == "qwen2.5:14b"
        assert data["ner_model"] == "phi4-mini-ner"
        assert data["embedding_model"] == "qwen3-embedding:0.6b-fp16"
        assert data["output_language"] == "English"

    @patch("app.services.benchmark_collector.Config")
    def test_save_ner_fallback_to_llm(self, mock_config, tmp_path):
        mock_config.LLM_MODEL_NAME = "qwen2.5:14b"
        mock_config.NER_MODEL_NAME = ""  # empty = fallback
        mock_config.EMBEDDING_MODEL = "test"
        mock_config.OUTPUT_LANGUAGE = "English"

        bc = BenchmarkCollector(str(tmp_path))
        bc.save()

        with open(tmp_path / "timing.json") as f:
            data = json.load(f)
        assert data["ner_model"] == "qwen2.5:14b"

    def test_multi_stage_accumulation(self, tmp_path):
        """Verify that timing data accumulates across multiple save/reload cycles."""
        bc1 = BenchmarkCollector(str(tmp_path))
        bc1.set_timestamp("entity_reading", "start", "2026-04-21T10:00:00")
        bc1.set_timestamp("entity_reading", "end", "2026-04-21T10:00:30")
        bc1.set_metric("entities_count", 50)
        bc1.save()

        # Second stage (like simulation_runner)
        bc2 = BenchmarkCollector(str(tmp_path))
        bc2.set_timestamp("simulation", "start", "2026-04-21T10:05:00")
        bc2.set_timestamp("simulation", "end", "2026-04-21T11:05:00")
        bc2.set_metric("simulation_rounds", 40)
        bc2.save()

        with open(tmp_path / "timing.json") as f:
            data = json.load(f)

        # Both stages should be present
        assert "entity_reading_start" in data["timestamps"]
        assert "simulation_start" in data["timestamps"]
        assert data["metrics"]["entities_count"] == 50
        assert data["metrics"]["simulation_rounds"] == 40
        assert data["durations_seconds"]["entity_reading"] == 30.0
        assert data["durations_seconds"]["simulation"] == 3600.0


# ========== Content Evaluation Tests ==========

class TestEvalPlatform:

    def test_eval_missing_db(self, tmp_path):
        result = _eval_platform(str(tmp_path / "nonexistent.db"), "twitter")
        assert result is None

    def test_eval_empty_db(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        _create_test_db(db_path, posts=[])
        result = _eval_platform(db_path, "twitter")
        assert result == {"total_posts": 0}

    def test_eval_basic_posts(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "This is a great post about diabetes treatment options today"},
            {"content": "Another interesting post with #health and #science hashtags"},
            {"content": "Short post"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["total_posts"] == 3
        assert result["original_posts"] == 3
        assert result["reposts"] == 0
        assert result["avg_length_words"] > 0
        assert result["avg_length_chars"] > 0
        assert result["min_length_words"] == 2  # "Short post"
        assert result["posts_with_hashtags_pct"] > 0  # 1 out of 3

    def test_eval_reposts(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "Original post here"},
            {"content": "Original post here", "original_post_id": 1},  # repost
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["original_posts"] == 1
        assert result["reposts"] == 1

    def test_eval_emojis(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "Great news! 🎉🎊 We are celebrating!"},  # adjacent emojis must count individually
            {"content": "No emojis in this post at all"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["emoji_total"] == 2  # each emoji counted separately
        assert result["avg_emojis_per_post"] == 1.0

    def test_eval_hashtags(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "#diabetes #treatment #health three hashtags here"},
            {"content": "No hashtags here"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["posts_with_hashtags_pct"] == 50.0
        assert result["avg_hashtags_per_post"] == 1.5  # 3 hashtags / 2 posts

    def test_eval_exact_duplicates(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "This is a duplicate post"},
            {"content": "This is a duplicate post"},
            {"content": "This is a unique post"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["exact_duplicates"] == 1  # 1 extra copy

    def test_eval_near_duplicates(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        # Posts that share the same first 50 chars but differ after
        prefix = "A" * 50
        posts = [
            {"content": prefix + " and then something unique happens here in this post"},
            {"content": prefix + " but something different happens in this other post"},
            {"content": "Completely different post with different content entirely"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["near_duplicates"] == 1

    def test_eval_non_target_language(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "English post about diabetes treatment"},
            {"content": "这是一个中文帖子关于糖尿病治疗"},  # Chinese
            {"content": "นี่คือโพสต์ภาษาไทย"},  # Thai
            {"content": "Another English post here"},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["non_target_language_pct"] == 50.0  # 2 out of 4

    def test_eval_comments(self, tmp_path):
        db_path = str(tmp_path / "reddit_simulation.db")
        posts = [{"content": "A reddit post"}]
        comments = [
            {"post_id": 1, "content": "Great post!"},
            {"post_id": 1, "content": "I agree"},
        ]
        _create_test_db(db_path, posts, comments)
        result = _eval_platform(db_path, "reddit")

        assert result["total_comments"] == 2

    def test_eval_engagement(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "Popular post", "num_likes": 10, "num_shares": 5, "num_dislikes": 1},
            {"content": "Less popular", "num_likes": 2, "num_shares": 1, "num_dislikes": 0},
        ]
        _create_test_db(db_path, posts)
        result = _eval_platform(db_path, "twitter")

        assert result["avg_likes"] == 6.0
        assert result["avg_shares"] == 3.0
        assert result["avg_dislikes"] == 0.5


# ========== Quality Score Tests ==========

class TestQualityScore:

    def test_perfect_score(self):
        stats = {
            "total_posts": 100,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "non_target_language_pct": 0,
            "avg_length_words": 30,    # sweet spot 15-50
            "avg_emojis_per_post": 0.3, # sweet spot 0.1-0.5
            "avg_hashtags_per_post": 0.5, # sweet spot 0.2-1.0
        }
        score = _calc_quality_score(stats)
        assert score == 100.0

    def test_zero_posts(self):
        assert _calc_quality_score({"total_posts": 0}) == 0.0

    def test_penalty_duplicates(self):
        perfect = {
            "total_posts": 100,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "non_target_language_pct": 0,
            "avg_length_words": 30,
            "avg_emojis_per_post": 0.3,
            "avg_hashtags_per_post": 0.5,
        }
        with_dupes = {**perfect, "exact_duplicates": 10, "near_duplicates": 5}

        score_perfect = _calc_quality_score(perfect)
        score_dupes = _calc_quality_score(with_dupes)
        assert score_dupes < score_perfect

    def test_penalty_non_target_language(self):
        base = {
            "total_posts": 100,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "avg_length_words": 30,
            "avg_emojis_per_post": 0.3,
            "avg_hashtags_per_post": 0.5,
        }
        score_clean = _calc_quality_score({**base, "non_target_language_pct": 0})
        score_mixed = _calc_quality_score({**base, "non_target_language_pct": 50})
        assert score_mixed < score_clean

    def test_short_posts_penalty(self):
        base = {
            "total_posts": 100,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "non_target_language_pct": 0,
            "avg_emojis_per_post": 0.3,
            "avg_hashtags_per_post": 0.5,
        }
        score_good = _calc_quality_score({**base, "avg_length_words": 30})
        score_short = _calc_quality_score({**base, "avg_length_words": 3})
        assert score_short < score_good


# ========== Integration: evaluate_content ==========

class TestEvaluateContent:

    def test_evaluate_content_writes_file(self, tmp_path):
        db_path = str(tmp_path / "twitter_simulation.db")
        posts = [
            {"content": "A solid English post about health and wellness topics"},
            {"content": "Another English post with #hashtag content included"},
        ]
        _create_test_db(db_path, posts)

        result_path = evaluate_content(str(tmp_path))
        assert result_path is not None
        assert os.path.exists(result_path)

        with open(result_path) as f:
            data = json.load(f)
        assert "platforms" in data
        assert "twitter" in data["platforms"]
        assert "combined" in data
        assert "quality_score" in data["combined"]
        assert data["combined"]["total_posts"] == 2

    def test_evaluate_content_no_dbs(self, tmp_path):
        result = evaluate_content(str(tmp_path))
        assert result is None

    def test_evaluate_content_both_platforms(self, tmp_path):
        _create_test_db(str(tmp_path / "twitter_simulation.db"),
                        [{"content": "Twitter post one"}, {"content": "Twitter post two"}])
        _create_test_db(str(tmp_path / "reddit_simulation.db"),
                        [{"content": "Reddit post one"}])

        result_path = evaluate_content(str(tmp_path))
        with open(result_path) as f:
            data = json.load(f)

        assert "twitter" in data["platforms"]
        assert "reddit" in data["platforms"]
        assert data["combined"]["total_posts"] == 3
