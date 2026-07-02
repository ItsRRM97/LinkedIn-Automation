"""Unit tests for feed post classification."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "lib"))

from feed_post_classify import (  # noqa: E402
    COMMENT_STYLE_CAREER,
    COMMENT_STYLE_OPINION,
    classify_post,
    detect_post_kind,
)


def _cfg() -> dict:
    with (REPO / "linkedin-feed-engage" / "config.json").open() as f:
        return json.load(f)


def _item(**overrides):
    base = {
        "text": "Most teams build one AI agent and call it a transformation. Product managers need better discovery habits.",
        "author_headline": "Product Manager at Acme",
        "is_company": False,
        "is_group": False,
        "share_urn": "urn:li:ugcPost:123",
        "post_age_hours": 3.0,
        "reactions": 12,
        "comments_count": 4,
    }
    base.update(overrides)
    return base


class TestFeedPostClassify(unittest.TestCase):
    def test_pm_opinion_not_job_posting(self):
        ok, reason, style = classify_post(_item(), _cfg())
        self.assertTrue(ok)
        self.assertEqual(reason, "opinion")
        self.assertEqual(style, COMMENT_STYLE_OPINION)

    def test_career_update_ack(self):
        ok, reason, style = classify_post(
            _item(
                text="Excited to share that I am stepping into a new role as Principal Product Manager at ExampleCo!",
            ),
            _cfg(),
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "career_update")
        self.assertEqual(style, COMMENT_STYLE_CAREER)

    def test_job_posting_pm_role(self):
        ok, reason, style = classify_post(
            _item(text="We're hiring a product manager to own discovery and roadmap for our B2B SaaS platform. Apply via link."),
            _cfg(),
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "job_posting")
        self.assertEqual(style, COMMENT_STYLE_CAREER)

    def test_anniversary_at_company(self):
        self.assertEqual(
            detect_post_kind("One year ago, I joined Google as a PM. Grateful for the team."),
            "career_update",
        )

    def test_low_engagement_skipped_when_counts_present(self):
        cfg = {**_cfg(), "prefer_engaged_posts": True, "min_reactions_or_comments": 5}
        ok, reason, _ = classify_post(_item(reactions=1, comments_count=0), cfg)
        self.assertFalse(ok)
        self.assertEqual(reason, "low_engagement")

    def test_low_engagement_not_skipped_when_counts_missing(self):
        cfg = {**_cfg(), "prefer_engaged_posts": True, "min_reactions_or_comments": 5}
        ok, reason, _ = classify_post(_item(reactions=None, comments_count=None), cfg)
        self.assertTrue(ok)
        self.assertEqual(reason, "opinion")


if __name__ == "__main__":
    unittest.main()
