from unittest import TestCase

from mock import MagicMock, patch


class ScoopConfigEnvTests(TestCase):

    @patch("flask_appsfoundry.config.os.getenv")
    def test_env_method(self, mock_getenv):
        pass
        #mock_getenv.assert


