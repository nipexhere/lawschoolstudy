import unittest

from streamlit.testing.v1 import AppTest


class FocusLedgerAppTests(unittest.TestCase):
    def test_dashboard_renders_without_sessions(self):
        app = AppTest.from_file("app.py", default_timeout=15).run()

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "0")
        self.assertEqual([tab.label for tab in app.tabs], ["Case library", "New brief", "Active recall", "Study log"])

    def test_saving_a_case_adds_it_to_the_casebook(self):
        app = AppTest.from_file("app.py", default_timeout=15).run()
        app.session_state["new_case_name"] = "Example v. Student"
        app.session_state["new_course"] = "Torts"
        app.session_state["new_facts"] = "A driver failed to stop at a crossing."
        app.session_state["new_issue"] = "Was there a duty?"
        app.session_state["new_rule"] = "The assigned opinion states the rule."
        app.session_state["new_holding"] = "The court found a duty."
        app.session_state["new_reasoning"] = "The risk was foreseeable."
        app.run()
        app.button(key="FormSubmitter:new_case_brief-Save case brief").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1")
        self.assertEqual(app.session_state["case_briefs"][0]["course"], "Torts")

    def test_logging_a_session_updates_weekly_metrics(self):
        app = AppTest.from_file("app.py", default_timeout=15).run()
        app.text_input(key="study_subject").set_value("Torts").run()
        app.button(key="FormSubmitter:session_form-Add study session").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value, "0.8 h")
        self.assertEqual(app.session_state["sessions"][0]["subject"], "Torts")

    def test_study_log_requires_a_course(self):
        app = AppTest.from_file("app.py", default_timeout=15).run()
        app.button(key="FormSubmitter:session_form-Add study session").click().run()

        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["sessions"], [])

    def test_case_brief_requires_core_sections(self):
        app = AppTest.from_file("app.py", default_timeout=15).run()
        app.button(key="FormSubmitter:new_case_brief-Save case brief").click().run()

        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["case_briefs"], [])

    def test_active_recall_reveals_reference_notes(self):
        app = AppTest.from_file("app.py", default_timeout=15)
        app.session_state["case_briefs"] = [{
            "brief_id": "brief-1",
            "added_on": "2026-10-09",
            "case_name": "Example v. Student",
            "citation": "",
            "course": "Torts",
            "topic": "Negligence",
            "year": "",
            "facts": "A driver failed to stop at a crossing.",
            "procedure": "",
            "issue": "Was there a duty?",
            "rule": "The rule from class notes.",
            "holding": "The court found a duty.",
            "reasoning": "The risk was foreseeable.",
            "exam_note": "Separate duty from breach.",
        }]
        app.run()
        app.button(key="reveal_brief-1").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["revealed_brief_id"], "brief-1")
        self.assertTrue(any("Rule from your notes" in node.value for node in app.markdown))


if __name__ == "__main__":
    unittest.main()