# Transaction types (TRXTYPE)...
SALE, CREDIT, AUTHORIZATION, DELAYED_CAPTURE, VOID, DUPLICATE_TRANSACTION = (
    'S', 'C', 'A', 'D', 'V', 'N')

# ...for humans
trxtype_map = {
    SALE: 'Sale',
    AUTHORIZATION: 'Authorize',
    CREDIT: 'Credit',
    DELAYED_CAPTURE: 'Delayed capture',
    VOID: 'Void',
    DUPLICATE_TRANSACTION: 'Duplicate transaction',
}

# Payment methods (TENDER)
BANKCARD, PAYPAL = 'C', 'P'
tender_map = {
    BANKCARD: 'Bankcard',
    PAYPAL: 'PayPal'
}
