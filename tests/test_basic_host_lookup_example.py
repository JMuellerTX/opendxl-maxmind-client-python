import os
import sys
import unittest

if sys.version_info[0] > 2:
    import builtins # pylint: disable=import-error, unused-import
else:
    import __builtin__ # pylint: disable=import-error
    builtins = __builtin__ # pylint: disable=invalid-name

# pylint: disable=wrong-import-position
from mock import patch
import dxlmaxmindservice


class StringMatches(str):
    def __eq__(self, other):
        return self in other


class BasicHostLookupExample(unittest.TestCase):
    MAX_WAIT = 90
    SERVICE_CONFIG_FILE = "sample/dxlmaxmindservice.config"

    def _license_key_configured(self):
        if not os.path.isfile(self.SERVICE_CONFIG_FILE):
            return False
        with open(self.SERVICE_CONFIG_FILE) as f:
            for line in f:
                if line.strip().startswith("licenseKey="):
                    return line.strip() != "licenseKey="
        return False

    def test_basic_host_lookup_example(self): # pylint: disable=no-self-use
        if not self._license_key_configured():
            self.skipTest("MaxMind license key not configured in " +
                          self.SERVICE_CONFIG_FILE)
        sample_file = "sample/basic/basic_host_lookup_example.py"
        sample_globals = {"__file__": sample_file}
        with dxlmaxmindservice.MaxMindGeolocationService("sample") as app:
            app.run()
            with open(sample_file) as f, \
                    patch.object(builtins, 'print') as mock_print:
                exec(f.read(), sample_globals) # pylint: disable=exec-used
        mock_print.assert_called_with(StringMatches("Response:"))
        mock_print.assert_called_with(StringMatches("registered_country"))
