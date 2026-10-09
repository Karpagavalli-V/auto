import unittest

import autotyper


class AutotyperSpeedTest(unittest.TestCase):
    def test_default_type_interval_is_editor_friendly(self):
        self.assertEqual(autotyper.DEFAULT_TYPE_INTERVAL, 0.05)

    def test_pyautogui_pause_does_not_override_type_interval(self):
        self.assertEqual(autotyper.pyautogui.PAUSE, 0)


if __name__ == "__main__":
    unittest.main()
