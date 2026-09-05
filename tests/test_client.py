import json
import unittest

from mock import MagicMock
from dxlclient.message import ErrorResponse, Request, Response

from dxlmaxmindclient.client import MaxMindGeolocationClient


class MaxMindGeolocationClientTest(unittest.TestCase):
    """
    Tests for the client wrapper that do not need a broker or a MaxMind
    license key (the DXL client is mocked).
    """

    def _create_client(self, response):
        dxl_client = MagicMock()
        dxl_client.sync_request.return_value = response
        return dxl_client, MaxMindGeolocationClient(dxl_client)

    def test_lookup_host(self):
        request = Request("/dummy")
        response = Response(request)
        response.payload = json.dumps({"country": {"iso_code": "US"}}).encode("utf-8")
        dxl_client, client = self._create_client(response)

        result = client.lookup_host("www.google.com")

        self.assertEqual({"country": {"iso_code": "US"}}, result)
        sent_request = dxl_client.sync_request.call_args[0][0]
        self.assertEqual(MaxMindGeolocationClient.HOST_LOOKUP_TOPIC,
                         sent_request.destination_topic)
        self.assertEqual({"host": "www.google.com"},
                         json.loads(sent_request.payload.decode("utf-8")))
        self.assertEqual(client.response_timeout,
                         dxl_client.sync_request.call_args[1]["timeout"])

    def test_lookup_host_error_response(self):
        response = ErrorResponse(Request("/dummy"), error_code=1,
                                 error_message="unable to lookup host")
        _, client = self._create_client(response)
        with self.assertRaises(Exception) as context:
            client.lookup_host("www.google.com")
        self.assertIn("unable to lookup host", str(context.exception))
