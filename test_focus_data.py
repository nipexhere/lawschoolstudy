import unittest
from datetime import date

from focus_data import create_session, sessions_from_csv, sessions_to_csv, weekly_summary


class FocusDataTests(unittest.TestCase):
    def test_create_session_normalizes_text(self):
        session = create_session(date(2026, 10, 9), "  Python  ", 45, "  Chapter 3  ")
        self.assertEqual(session, {
            "date": "2026-10-09",
            "subject": "Python",
            "focus_minutes": 45,
            "notes": "Chapter 3",
        })

    def test_create_session_rejects_empty_subject(self):
        with self.assertRaises(ValueError):
            create_session(date(2026, 10, 9), "  ", 45)

    def test_create_session_rejects_out_of_range_focus_time(self):
        for minutes in (0, 601):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                create_session(date(2026, 10, 9), "Python", minutes)

    def test_weekly_summary_includes_only_current_week(self):
        sessions = [
            create_session(date(2026, 10, 5), "Python", 45),
            create_session(date(2026, 10, 9), "Writing", 30),
            create_session(date(2026, 10, 4), "Old week", 90),
        ]

        result = weekly_summary(sessions, date(2026, 10, 9), 120)

        self.assertEqual(result["total_minutes"], 75)
        self.assertEqual(result["session_count"], 2)
        self.assertEqual(result["subject_count"], 2)
        self.assertEqual(result["active_days"], 2)
        self.assertEqual(result["goal_progress"], 0.625)
        self.assertEqual(result["daily_minutes"][date(2026, 10, 9)], 30)

    def test_weekly_summary_caps_goal_progress(self):
        sessions = [create_session(date(2026, 10, 9), "Python", 120)]
        result = weekly_summary(sessions, date(2026, 10, 9), 60)
        self.assertEqual(result["goal_progress"], 1.0)

    def test_csv_round_trip(self):
        sessions = [create_session(date(2026, 10, 9), "Python, data", 45, "Read, review")]
        self.assertEqual(sessions_from_csv(sessions_to_csv(sessions)), sessions)

    def test_csv_rejects_missing_columns(self):
        with self.assertRaisesRegex(ValueError, "must include"):
            sessions_from_csv(b"subject,minutes\nPython,45\n")

    def test_csv_rejects_invalid_rows(self):
        content = b"date,subject,focus_minutes,notes\n2026-10-09,Python,900,Too long\n"
        with self.assertRaisesRegex(ValueError, "row 2"):
            sessions_from_csv(content)


if __name__ == "__main__":
    unittest.main()