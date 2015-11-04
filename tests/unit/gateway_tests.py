from __future__ import unicode_literals
from django.test import TestCase
import mock

from paypal.gateway import post

# Fixtures
ERROR_RESPONSE = 'RESULT=126&PNREF=V25A2BB645A7&RESPMSG=Under review by Fraud Service&AUTHCODE=525PNI&PREFPSMSG=Review: More than one rule was triggered for Review&POSTFPSMSG=Review'


class TestErrorResponse(TestCase):

    def setUp(self):
        with mock.patch('requests.post') as mock_post:
            response = mock.Mock()
            response.status_code = 200
            response.content = ERROR_RESPONSE
            mock_post.return_value = response
            self.pairs = post('http://example.com', {})

    def test_return_value_includes_response_time(self):
        self.assertTrue('_response_time' in self.pairs)

    def test_return_value_keys(self):
        expected = {
            'RESULT': '126',
            'PNREF': 'V25A2BB645A7',
            'RESPMSG': 'Under review by Fraud Service',
            'AUTHCODE': '525PNI',
            'POSTFPSMSG': 'Review'
        }
        for key, value in expected.items():
            self.assertEqual(value, self.pairs[key])

    def test_audit_information_is_included(self):
        expected = ['_raw_request',
                    '_raw_response',
                    '_response_time']
        for key in expected:
            self.assertTrue(key in self.pairs)
