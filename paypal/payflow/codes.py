# Make strings collectable with gettext tools, but don't trnslate them here:
_ = lambda x: x

# Transaction types (TRXTYPE)...
SALE, CREDIT, AUTHORIZATION, DELAYED_CAPTURE, VOID, DUPLICATE_TRANSACTION = (
    'S', 'C', 'A', 'D', 'V', 'N')

# ...for humans
trxtype_map = {
    SALE: _('Sale'),
    AUTHORIZATION: _('Authorize'),
    CREDIT: _('Credit'),
    DELAYED_CAPTURE: _('Delayed capture'),
    VOID: _('Void'),
    DUPLICATE_TRANSACTION: _('Duplicate transaction'),
}

# Payment methods (TENDER)
BANKCARD, PAYPAL = 'C', 'P'
tender_map = {
    BANKCARD: 'Bankcard',
    PAYPAL: 'PayPal'
}
