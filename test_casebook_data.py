import unittest

from casebook_data import (
    casebook_from_json,
    casebook_to_json,
    create_case_brief,
    filter_case_briefs,
)


def sample_brief(**overrides):
    values = {
        "case_name": "Example v. Student",
        "course": "Torts",
        "topic": "Negligence",
        "facts": "A driver failed to stop at a marked crossing.",
        "issue": "Did the driver owe a duty of care?",
        "rule": "Use the standard from the assigned opinion and course materials.",
        "holding": "The court found a duty on these facts.",
        "reasoning": "The risk was foreseeable under the court's analysis.",
        "citation": "",
        "year": "",
        "procedure": "",
        "exam_note": "Separate duty from breach.",
    }
    values.update(overrides)
    return create_case_brief(**values)


class CasebookDataTests(unittest.TestCase):
    def test_create_case_brief_trims_fields_and_requires_core_sections(self):
        brief = sample_brief(case_name="  Example v. Student  ")
        self.assertEqual(brief["case_name"], "Example v. Student")
        self.assertEqual(brief["course"], "Torts")
        self.assertTrue(brief["brief_id"])
        self.assertTrue(brief["added_on"])

    def test_create_case_brief_rejects_missing_core_sections(self):
        with self.assertRaisesRegex(ValueError, "facts"):
            sample_brief(facts=" ")

    def test_casebook_json_round_trip(self):
        briefs = [sample_brief(case_name="People v. Rivera", exam_note="Use the professor's rule.")]
        self.assertEqual(casebook_from_json(casebook_to_json(briefs)), briefs)

    def test_casebook_json_rejects_unsupported_version(self):
        with self.assertRaisesRegex(ValueError, "unsupported format"):
            casebook_from_json(b'{"format_version": 2, "briefs": []}')

    def test_filter_case_briefs_matches_course_topic_and_full_text(self):
        briefs = [
            sample_brief(),
            sample_brief(case_name="Contract Case", course="Contracts", topic="Offer"),
        ]
        matches = filter_case_briefs(briefs, query="foreseeable", course="Torts")
        self.assertEqual([brief["case_name"] for brief in matches], ["Example v. Student"])
        self.assertEqual(filter_case_briefs(briefs, topic="Offer")[0]["course"], "Contracts")


if __name__ == "__main__":
    unittest.main()