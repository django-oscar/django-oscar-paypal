from django.test import TestCase
from decimal import Decimal as D
from mock import patch, Mock

from paypal.adaptive import gateway

# Fixtures
PAY_SUCCESS_RESPONSE = 'responseEnvelope.timestamp=2013-01-31T02%3A37%3A26.080-08%3A00&responseEnvelope.ack=Success&responseEnvelope.correlationId=d59ed693b9244&responseEnvelope.build=4923149&payKey=AP-9WC20815W6814813H&paymentExecStatus=CREATED'
PAY_FAILURE_RESPONSE = 'responseEnvelope.timestamp=2013-01-31T02%3A25%3A33.140-08%3A00&responseEnvelope.ack=Failure&responseEnvelope.correlationId=f8840ca36f442&responseEnvelope.build=4923149&error(0).errorId=580028&error(0).domain=PLATFORM&error(0).subdomain=Application&error(0).severity=Error&error(0).category=Application&error(0).message=The+URL+%2Fcheckout%2Fadaptive-payments%2Fcancel%2F+is+malformed&error(0).parameter(0)=%2Fcheckout%2Fadaptive-payments%2Fcancel%2F'
PAYMENT_DETAILS_SUCCESS_RESPONSE = 'responseEnvelope.timestamp=2013-01-31T04%3A31%3A42.664-08%3A00&responseEnvelope.ack=Success&responseEnvelope.correlationId=32fbda1927e43&responseEnvelope.build=4923149&cancelUrl=http%3A%2F%2Fe%3A8008%2Fcheckout%2Fadaptive-payments%2Fcancel%2F&currencyCode=GBP&memo=Hello+this+is+a+memo&paymentInfoList.paymentInfo(0).transactionId=6FY27192VP721873F&paymentInfoList.paymentInfo(0).transactionStatus=COMPLETED&paymentInfoList.paymentInfo(0).receiver.amount=12.00&paymentInfoList.paymentInfo(0).receiver.email=david._1332854868_per%40gmail.com&paymentInfoList.paymentInfo(0).receiver.primary=true&paymentInfoList.paymentInfo(0).receiver.paymentType=SERVICE&paymentInfoList.paymentInfo(0).refundedAmount=0.00&paymentInfoList.paymentInfo(0).pendingRefund=false&paymentInfoList.paymentInfo(0).senderTransactionId=9H519180408085510&paymentInfoList.paymentInfo(0).senderTransactionStatus=COMPLETED&paymentInfoList.paymentInfo(1).transactionId=9CF6707788801361C&paymentInfoList.paymentInfo(1).transactionStatus=PENDING&paymentInfoList.paymentInfo(1).receiver.amount=12.00&paymentInfoList.paymentInfo(1).receiver.email=david._1359545821_pre%40gmail.com&paymentInfoList.paymentInfo(1).receiver.primary=false&paymentInfoList.paymentInfo(1).receiver.paymentType=SERVICE&paymentInfoList.paymentInfo(1).refundedAmount=0.00&paymentInfoList.paymentInfo(1).pendingRefund=false&paymentInfoList.paymentInfo(1).senderTransactionId=6VB581506G499114T&paymentInfoList.paymentInfo(1).senderTransactionStatus=PENDING&paymentInfoList.paymentInfo(1).pendingReason=MULTI_CURRENCY&returnUrl=http%3A%2F%2Fe%3A8008%2Fcheckout%2Fadaptive-payments%2Fsuccess%2F&senderEmail=david._1359628789_per%40gmail.com&status=COMPLETED&payKey=AP-9WC20815W6814813H&actionType=PAY&feesPayer=EACHRECEIVER&reverseAllParallelPaymentsOnError=false&sender.email=david._1359628789_per%40gmail.com&sender.useCredentials=false'


class TestPayOperation(TestCase):

    def test_successful_create(self):
        receivers = (
            gateway.Receiver(email='person1@gmail.com',
                             amount=D('28.00'), is_primary=True),
            gateway.Receiver(email='person2@gmail.com',
                             amount=D('14.00'), is_primary=False),
            gateway.Receiver(email='person3@gmail.com',
                             amount=D('14.00'), is_primary=False),
        )
        return_url = 'http://example.com/success/'
        cancel_url = 'http://example.com/cancel/'

        with patch('requests.post') as post:
            post.return_value = Mock()
            post.return_value.status_code = 200
            post.return_value.content = PAY_SUCCESS_RESPONSE
            txn = gateway.pay(
                receivers=receivers,
                currency='GBP',
                return_url=return_url,
                cancel_url=cancel_url,
                ip_address='127.0.0.1')

        self.assertTrue(txn.is_successful)
        self.assertEqual('AP-9WC20815W6814813H', txn.pay_key)
        self.assertEqual('d59ed693b9244', txn.correlation_id)
        self.assertTrue('AP-9WC20815W6814813H' in txn.redirect_url)
        self.assertEqual(D('28.00'), txn.amount)

    def test_unsuccessful_create(self):
        receivers = (
            gateway.Receiver(email='person1@gmail.com',
                             amount=D('12.00'), is_primary=True),
            gateway.Receiver(email='person2@gmail.com',
                             amount=D('14.00'), is_primary=False),
        )
        return_url = 'http://example.com/success/'
        cancel_url = 'http://example.com/cancel/'

        with patch('requests.post') as post:
            post.return_value = Mock()
            post.return_value.status_code = 200
            post.return_value.content = PAY_FAILURE_RESPONSE
            txn = gateway.pay(
                receivers=receivers,
                currency='GBP',
                return_url=return_url,
                cancel_url=cancel_url,
                ip_address='127.0.0.1')

        self.assertFalse(txn.is_successful)
        self.assertEqual('f8840ca36f442', txn.correlation_id)


class TestPaymentDetailsOperation(TestCase):

    def test_successful_fetch(self):
        with patch('requests.post') as post:
            post.return_value = Mock()
            post.return_value.status_code = 200
            post.return_value.content = PAYMENT_DETAILS_SUCCESS_RESPONSE
            txn = gateway.payment_details('AP-9WC20815W6814813H')

        self.assertTrue(txn.is_successful)
        self.assertEqual('AP-9WC20815W6814813H', txn.pay_key)
