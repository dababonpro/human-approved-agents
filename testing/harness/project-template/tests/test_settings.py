import unittest

from orderdesk import settings


class SettingsTests(unittest.TestCase):
    def test_sqlite_path(self):
        self.assertEqual(settings.sqlite_path("sqlite:////srv/x.sqlite?password=p"), "/srv/x.sqlite")

    def test_env_keys_present(self):
        cfg = settings.load()
        for key in ("DATABASE_URL", "TEST_DATABASE_URL", "HELPDESK_URL"):
            self.assertIn(key, cfg)


if __name__ == "__main__":
    unittest.main()
