import subprocess
import unittest


class DeployScriptTests(unittest.TestCase):
    def test_unknown_command_prints_usage_and_exits_2(self):
        result = subprocess.run(["sh", "scripts/deploy"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: scripts/deploy check", result.stderr)


if __name__ == "__main__":
    unittest.main()
