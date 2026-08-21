import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).parents[2] / "plugins" / "filter" / "claw_schedule.py"
SPEC = importlib.util.spec_from_file_location("claw_schedule", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ClawScheduleTests(unittest.TestCase):
    def test_same_day_schedule(self):
        result = MODULE.claw_morning_schedule(
            "08:30", 30, ["mon", "tue", "wed", "thu", "fri"], "America/New_York"
        )
        self.assertEqual(result["cron"], "0 8 * * 1,2,3,4,5")
        self.assertEqual(result["local_time"], "08:00")

    def test_previous_day_schedule(self):
        result = MODULE.claw_morning_schedule(
            "00:15", 30, ["mon", "tue", "wed", "thu", "fri"], "UTC"
        )
        self.assertEqual(result["cron"], "45 23 * * 0,1,2,3,4")

    def test_invalid_timezone(self):
        with self.assertRaises(MODULE.AnsibleFilterError):
            MODULE.claw_morning_schedule("08:30", 30, ["mon"], "Mars/Olympus")

    def test_empty_workweek(self):
        with self.assertRaises(MODULE.AnsibleFilterError):
            MODULE.claw_morning_schedule("08:30", 30, [], "UTC")


if __name__ == "__main__":
    unittest.main()
