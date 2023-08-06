import unittest
from os import getenv
from time import sleep

from dotenv import load_dotenv

load_dotenv()

from featureguards.feature_flags import feature_flags


class TestClient(unittest.TestCase):

    def test_start_stop(self):
        try:
            fg = feature_flags(api_key=getenv('FEATUREGUARDS_API_KEY', ''),
                               addr=getenv('FEATUREGUARDS_ADDR',
                                           'api.featureguards.com'))
            self.assertGreater(fg.client_version, 0)
            # Sleep a bit to ensure that we're listening.
            sleep(0.5)
            self.assertTrue(fg.listener.is_alive())
        finally:
            if fg:
                fg.stop()

    def test_is_on(self):
        try:
            fg = feature_flags(api_key=getenv('FEATUREGUARDS_API_KEY', ''),
                               addr=getenv('FEATUREGUARDS_ADDR',
                                           'api.featureguards.com'))
            self.assertGreater(fg.client_version, 0)
            self.assertTrue(fg.is_on('FOO'))
        finally:
            if fg:
                fg.stop()


if __name__ == '__main__':
    unittest.main()
