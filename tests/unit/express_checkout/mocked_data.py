# Returned by `PaymentProcessor.create_order` with request.prefer('return=minimal')
CREATE_ORDER_RESULT_DATA_MINIMAL = {
    'id': '4MW805572N795704B',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://www.sandbox.paypal.com/checkoutnow?token=4MW805572N795704B',
            'method': 'GET',
            'rel': 'approve'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'PATCH',
            'rel': 'update'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B/capture',
            'method': 'POST',
            'rel': 'capture'
        }
    ],
    'status': 'CREATED'
}

# Returned by `PaymentProcessor.create_order` with request.prefer('return=representation').
# Is not used in tests for the moment - shown just as an example.
CREATE_ORDER_RESULT_DATA_REPRESENTATION = {
    'create_time': '2020-03-05T11:15:33Z',
    'id': '4MW805572N795704B',
    'intent': 'CAPTURE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://www.sandbox.paypal.com/checkoutnow?token=4MW805572N795704B',
            'method': 'GET',
            'rel': 'approve'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'PATCH',
            'rel': 'update'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B/capture',
            'method': 'POST',
            'rel': 'capture'
        }
    ],
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '9.99'
            },
            'items': [
                {
                    'category': 'PHYSICAL_GOODS',
                    'description': '" The Shellcoder\'s Handbook '
                                   'shows you how to: Non-Find out '
                                   'where security holes come from '
                                   'and how to close them so they '
                                   'neve...',
                    'name': "The shellcoder's handbook",
                    'quantity': '1',
                    'sku': '9780764544682',
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            }
        }
    ],
    'status': 'CREATED'
}

# Returned by `PaymentProcessor.get_order`
GET_ORDER_RESULT_DATA = {
    'create_time': '2019-12-27T16:39:20Z',
    'id': '4MW805572N795704B',
    'intent': 'CAPTURE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B/capture',
            'method': 'POST',
            'rel': 'capture'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '10.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '19.99'
            },
            'items': [
                {
                    'category': 'PHYSICAL_GOODS',
                    'description': (
                        "The Shellcoder's Handbook shows you how to: Non-Find out where security holes come from "
                        "and how to close them so they neve..."
                    ),
                    'name': "The shellcoder's handbook",
                    'quantity': '1',
                    'sku': '9780764544682',
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            }
        }
    ],
    'status': 'APPROVED'
}

# Returned by `PaymentProcessor.capture_order` with request.prefer('return=minimal')
CAPTURE_ORDER_RESULT_DATA_MINIMAL = {
    'id': '4MW805572N795704B',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'payments': {
                'captures': [
                    {
                        'amount': {
                            'currency_code': 'GBP',
                            'value': '19.99'
                        },
                        'create_time': '2019-12-30T18:31:01Z',
                        'final_capture': True,
                        'id': '2D6171889X1782919',
                        'links': [
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/2D6171889X1782919',
                                'method': 'GET',
                                'rel': 'self'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/2D6171889X1782919/refund',
                                'method': 'POST',
                                'rel': 'refund'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
                                'method': 'GET',
                                'rel': 'up'
                            }
                        ],
                        'seller_protection': {
                            'dispute_categories': [
                                'ITEM_NOT_RECEIVED',
                                'UNAUTHORIZED_TRANSACTION'
                            ],
                            'status': 'ELIGIBLE'
                        },
                        'status': 'PENDING',
                        'status_details': {
                            'reason': 'RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION'
                        },
                        'update_time': '2019-12-30T18:31:01Z'
                    }
                ]
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            }
        }
    ],
    'status': 'COMPLETED'
}

# Returned by `PaymentProcessor.get_order`
GET_ORDER_RESULT_NO_SHIPPING_DATA = {
    'create_time': '2019-12-27T16:39:20Z',
    'id': '4MW805572N795704B',
    'intent': 'CAPTURE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B/capture',
            'method': 'POST',
            'rel': 'capture'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '10.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '19.99'
            },
            'items': [
                {
                    'category': 'PHYSICAL_GOODS',
                    'description': (
                        "The Shellcoder's Handbook shows you how to: Non-Find out where security holes come from "
                        "and how to close them so they neve..."
                    ),
                    'name': "The shellcoder's handbook",
                    'quantity': '1',
                    'sku': '9780764544682',
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'reference_id': 'default'
        }
    ],
    'status': 'APPROVED'
}

# Returned by `PaymentProcessor.capture_order` with request.prefer('return=minimal')
CAPTURE_ORDER_RESULT_NO_SHIPPING_DATA_MINIMAL = {
    'id': '4MW805572N795704B',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'payments': {
                'captures': [
                    {
                        'amount': {
                            'currency_code': 'GBP',
                            'value': '19.99'
                        },
                        'create_time': '2019-12-30T18:31:01Z',
                        'final_capture': True,
                        'id': '2D6171889X1782919',
                        'links': [
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/2D6171889X1782919',
                                'method': 'GET',
                                'rel': 'self'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/2D6171889X1782919/refund',
                                'method': 'POST',
                                'rel': 'refund'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
                                'method': 'GET',
                                'rel': 'up'
                            }
                        ],
                        'seller_protection': {
                            'dispute_categories': [
                                'ITEM_NOT_RECEIVED',
                                'UNAUTHORIZED_TRANSACTION'
                            ],
                            'status': 'ELIGIBLE'
                        },
                        'status': 'PENDING',
                        'status_details': {
                            'reason': 'RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION'
                        },
                        'update_time': '2019-12-30T18:31:01Z'
                    }
                ]
            },
            'reference_id': 'default'
        }
    ],
    'status': 'COMPLETED'
}

# Returned by `PaymentProcessor.capture_order` with request.prefer('return=representation').
# Is not used in tests for the moment - shown just as an example.
CAPTURE_ORDER_RESULT_DATA_REPRESENTATION = {
    'create_time': '2020-10-04T09:15:37Z',
    'id': '2SK113799B370635B',
    'intent': 'CAPTURE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/2SK113799B370635B',
            'method': 'GET',
            'rel': 'self'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'handling': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'insurance': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '0.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'shipping_discount': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '0.99'
            },
            'description': 'Google Hacking',
            'items': [
                {
                    'description': '*Author Johnny Long, the '
                                   'authority on Google hacking, '
                                   'will be speaking about "Google '
                                   'Hacking" at the Black Hat 2004 '
                                   'Briefing.',
                    'name': 'Google Hacking',
                    'quantity': '1',
                    'sku': '9781931836364',
                    'tax': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '0.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'payments': {
                'captures': [
                    {
                        'amount': {
                            'currency_code': 'GBP',
                            'value': '0.99'
                        },
                        'create_time': '2020-10-04T09:16:06Z',
                        'final_capture': True,
                        'id': '45315376249711632',
                        'links': [
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/45315376249711632',
                                'method': 'GET',
                                'rel': 'self'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/captures/45315376249711632/refund',
                                'method': 'POST',
                                'rel': 'refund'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/2SK113799B370635B',
                                'method': 'GET',
                                'rel': 'up'
                            }
                        ],
                        'seller_protection': {
                            'dispute_categories': [
                                'ITEM_NOT_RECEIVED',
                                'UNAUTHORIZED_TRANSACTION'
                            ],
                            'status': 'ELIGIBLE'
                        },
                        'status': 'PENDING',
                        'status_details': {
                            'reason': 'RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION'
                        },
                        'update_time': '2020-10-04T09:16:06Z'
                    }
                ]
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'},
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            },
            'soft_descriptor': 'PAYPAL *TESTFACILIT'
        }
    ],
    'status': 'COMPLETED',
    'update_time': '2020-10-04T09:16:06Z'
}

# Returned by `PaymentProcessor.refund_order` with request.prefer('return=minimal').
REFUND_ORDER_DATA_MINIMAL = {
    'id': '0SM71185A67927728',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/refunds/0SM71185A67927728',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/45315376249711632',
            'method': 'GET',
            'rel': 'up'
        }
    ],
    'status': 'COMPLETED'
}

# Returned by `PaymentProcessor.refund_order` with request.prefer('return=representation').
# Is not used in tests for the moment - shown just as an example.
REFUND_ORDER_DATA_REPRESENTATION = {
    'amount': {
        'currency_code': 'GBP', 'value': '0.99'
    },
    'create_time': '2020-10-04T02:51:57-07:00',
    'id': '0SM71185A67927728',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/refunds/0SM71185A67927728',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/45315376249711632',
            'method': 'GET',
            'rel': 'up'
        }
    ],
    'seller_payable_breakdown': {
        'gross_amount': {
            'currency_code': 'GBP',
            'value': '0.99'
        },
        'net_amount': {
            'currency_code': 'GBP',
            'value': '0.99'
        },
        'paypal_fee': {
            'currency_code': 'GBP',
            'value': '0.00'
        },
        'total_refunded_amount': {
            'currency_code': 'GBP',
            'value': '0.99'
        }
    },
    'status': 'COMPLETED',
    'update_time': '2020-10-04T02:51:57-07:00'
}


# Returned by `PaymentProcessor.get_order` for authorized order.
GET_ORDER_AUTHORIZE_RESULT_DATA = {
    'create_time': '2020-03-04T19:57:30Z',
    'id': '4MW805572N795704B',
    'intent': 'AUTHORIZE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B/authorize',
            'method': 'POST',
            'rel': 'authorize'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'GB'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '9.99'
            },
            'items': [
                {
                    'category': 'PHYSICAL_GOODS',
                    'description': '" The Shellcoder\'s Handbook '
                                   'shows you how to: Non-Find out '
                                   'where security holes come from '
                                   'and how to close them so they '
                                   'neve...',
                    'name': "The shellcoder's handbook",
                    'quantity': '1',
                    'sku': '9780764544682',
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            }
        }
    ],
    'status': 'APPROVED'
}

# Returned by `PaymentProcessor.authorize_order` with request.prefer('return=minimal').
AUTHORIZE_ORDER_RESULT_DATA_MINIMAL = {
    'id': '4MW805572N795704B',
    'status': 'COMPLETED',
    'purchase_units': [
        {
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            },
            'payments': {
                'authorizations': [
                    {'amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                        'create_time': '2020-03-04T19:57:47Z',
                        'expiration_time': '2020-04-02T19:57:47Z',
                        'id': '3PW0120338716941H',
                        'links': [
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H',
                                'method': 'GET',
                                'rel': 'self'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/capture',
                                'method': 'POST',
                                'rel': 'capture'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/void',
                                'method': 'POST',
                                'rel': 'void'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/reauthorize',
                                'method': 'POST',
                                'rel': 'reauthorize'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
                                'method': 'GET',
                                'rel': 'up'
                            },
                        ],
                        'seller_protection': {
                            'dispute_categories': [
                                'ITEM_NOT_RECEIVED',
                                'UNAUTHORIZED_TRANSACTION'
                            ],
                            'status': 'ELIGIBLE'
                        },
                        'status': 'CREATED',
                        'update_time': '2020-03-04T19:57:47Z'
                    }
                ]
            }
        }
    ],
    'payer': {
        'address': {
            'country_code': 'US'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        }
    ]
}

# Returned by `PaymentProcessor.authorize_order` with request.prefer('return=representation').
# Is not used in tests for the moment - shown just as an example.
AUTHORIZE_ORDER_RESULT_DATA_REPRESENTATION = {
    'create_time': '2020-03-04T19:57:30Z',
    'id': '4MW805572N795704B',
    'intent': 'AUTHORIZE',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
            'method': 'GET',
            'rel': 'self'
        }
    ],
    'payer': {
        'address': {
            'country_code': 'US'
        },
        'email_address': 'sherlock.holmes@example.com',
        'name': {
            'given_name': 'Sherlock',
            'surname': 'Holmes'
        },
        'payer_id': '0000000000001'
    },
    'purchase_units': [
        {
            'amount': {
                'breakdown': {
                    'handling': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'insurance': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'item_total': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                    'shipping': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'shipping_discount': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    }
                },
                'currency_code': 'GBP',
                'value': '9.99'
            },
            'description': "The shellcoder's handbook",
            'items': [
                {
                    'description': '" The Shellcoder\'s Handbook '
                                   'shows you how to: Non-Find out '
                                   'where security holes come from '
                                   'and how to close them so they '
                                   'neve...',
                    'name': "The shellcoder's handbook",
                    'quantity': '1',
                    'sku': '9780764544682',
                    'tax': {
                        'currency_code': 'GBP',
                        'value': '0.00'
                    },
                    'unit_amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    }
                }
            ],
            'payee': {
                'email_address': 'seller@example.com',
                'merchant_id': '1234567890111'
            },
            'payments': {
                'authorizations': [
                    {'amount': {
                        'currency_code': 'GBP',
                        'value': '9.99'
                    },
                        'create_time': '2020-03-04T19:57:47Z',
                        'expiration_time': '2020-04-02T19:57:47Z',
                        'id': '3PW0120338716941H',
                        'links': [
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H',
                                'method': 'GET',
                                'rel': 'self'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/capture',
                                'method': 'POST',
                                'rel': 'capture'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/void',
                                'method': 'POST',
                                'rel': 'void'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/3PW0120338716941H/reauthorize',
                                'method': 'POST',
                                'rel': 'reauthorize'
                            },
                            {
                                'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/4MW805572N795704B',
                                'method': 'GET',
                                'rel': 'up'
                            },
                        ],
                        'seller_protection': {
                            'dispute_categories': [
                                'ITEM_NOT_RECEIVED',
                                'UNAUTHORIZED_TRANSACTION'
                            ],
                            'status': 'ELIGIBLE'
                        },
                        'status': 'CREATED',
                        'update_time': '2020-03-04T19:57:47Z'
                    }
                ]
            },
            'reference_id': 'default',
            'shipping': {
                'address': {
                    'address_line_1': '221B Baker Street',
                    'admin_area_2': 'London',
                    'country_code': 'GB',
                    'postal_code': 'WC2N 5DU'
                },
                'name': {
                    'full_name': 'Sherlock Holmes'
                }
            },
            'soft_descriptor': 'PAYPAL *TESTFACILIT'
        }
    ],
    'status': 'COMPLETED',
    'update_time': '2020-03-04T19:57:47Z'
}


# Returned by `PaymentProcessor.capture_order` for authorized order with request.prefer('return=minimal')
CAPTURE_AUTHORIZATION_RESULT_DATA_MINIMAL = {
    'id': '62Y22172G0146141U',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/62Y22172G0146141U',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/62Y22172G0146141U/refund',
            'method': 'POST',
            'rel': 'refund'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/4LV54391KE128404B',
            'method': 'GET',
            'rel': 'up'
        }
    ],
    'status': 'PENDING'
}

# Returned by `PaymentProcessor.capture_order` for authorized order with request.prefer('return=representation')
# Is not used in tests for the moment - shown just as an example.
CAPTURE_AUTHORIZATION_RESULT_DATA_REPRESENTATION = {
    'amount': {
        'currency_code': 'GBP',
        'value': '9.99'
    },
    'create_time': '2020-03-04T21:14:12Z',
    'final_capture': True,
    'id': '18U17537MY9788827',
    'links': [
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/18U17537MY9788827',
            'method': 'GET',
            'rel': 'self'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/captures/18U17537MY9788827/refund',
            'method': 'POST',
            'rel': 'refund'
        },
        {
            'href': 'https://api.sandbox.paypal.com/v2/payments/authorizations/2AP88001H0435332B',
            'method': 'GET',
            'rel': 'up'
        }
    ],
    'seller_protection': {
        'dispute_categories': [
            'ITEM_NOT_RECEIVED',
            'UNAUTHORIZED_TRANSACTION'
        ],
        'status': 'ELIGIBLE'
    },
    'seller_receivable_breakdown': {
        'exchange_rate': {},
        'gross_amount': {
            'currency_code': 'USD',
            'value': '13.20'
        },
        'net_amount': {
            'currency_code': 'GBP',
            'value': '9.50'
        },
        'paypal_fee': {
            'currency_code': 'GBP',
            'value': '0.49'
        }
    },
    'status': 'PENDING',
    'update_time': '2020-03-04T21:14:12Z'
}
