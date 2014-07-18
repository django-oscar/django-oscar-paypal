try:
    from oscar.apps.payment.exceptions import PaymentError
except ImportError:
    class PaymentError(Exception):
        pass


class PayPalError(PaymentError):
    pass


class PayPalError(PaymentError):
    pass
