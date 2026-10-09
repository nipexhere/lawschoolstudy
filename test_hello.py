import unittest
from unittest.mock import patch

from hello import calculate_average, calculate_grade, get_scores


class StudentScoreManagerTests(unittest.TestCase):
    def test_calculate_average(self):
        self.assertEqual(calculate_average([85, 72, 90]), 82.33333333333333)

    def test_calculate_average_requires_scores(self):
        with self.assertRaises(ValueError):
            calculate_average([])

    def test_calculate_grade_boundaries(self):
        self.assertEqual(calculate_grade(95), "A")
        self.assertEqual(calculate_grade(85), "B")
        self.assertEqual(calculate_grade(75), "C")
        self.assertEqual(calculate_grade(65), "D")
        self.assertEqual(calculate_grade(55), "F")

    @patch("builtins.input", side_effect=["abc", "105", "80", "90", "done"])
    def test_get_scores_rejects_invalid_values(self, mocked_input):
        self.assertEqual(get_scores(), [80.0, 90.0])
        self.assertEqual(mocked_input.call_count, 5)


if __name__ == "__main__":
    unittest.main()