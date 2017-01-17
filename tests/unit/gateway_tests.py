from __future__ import unicode_literals
from django.test import TestCase
import mock

from paypal.gateway import post
from paypal.payflow.models import PayflowTransaction

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

    def test_response_context_doesnt_fail_with_string(self):
        """
        Test to avoid regression: in the context property there used to be an attempt
        to .decode('ASCII') the object's raw_response (probably to fix a case where that
        field ended up being a bytestr), that caused an error as that type didn't have
        the decode method.
        That part of code is now checking the type to decide wheter to decode or not,
        so we test that it doesn't raise an exception both if the object is a str or
        bytestrings.
        """
        string_response_transaction = PayflowTransaction.objects.create(
                                          raw_request='test',
                                          raw_response='test_key=test_value',
                                          response_time=0.1,
                                          comment1='asd',
                                          trxtype='test',
                                          respmsg='test'
                                      )
        bytestring_response_transaction = PayflowTransaction.objects.create(
                                              raw_request='test',
                                              raw_response=b'test_key=test_value',
                                              response_time=0.1,
                                              comment1='asd',
                                              trxtype='test',
                                              respmsg='test'
                                          )
        # Just calling the context property will raise an error if there is a regression
        assert string_response_transaction.context == {'test_key': ['test_value']}
        assert bytestring_response_transaction.context == {'test_key': ['test_value']}
