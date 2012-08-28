from django.contrib import admin

from paypal.payflow import models


class TxnAdmin(admin.ModelAdmin):
    list_display = ['pnref', 'comment1', 'amount', 'get_trxtype_display',
                    'get_tender_display', 'result', 'respmsg', 'date_created']

    readonly_fields = [
        'trxtype',
        'tender',
        'amount',
        'pnref',
        'ppref',
        'cvv2match',
        'comment1',
        'avsaddr',
        'avszip',
        'result',
        'respmsg',
        'authcode',
        'request',
        'response',
        'raw_request',
        'raw_response',
        'response_time',
        'date_created',
    ]


admin.site.register(models.PayflowTransaction, TxnAdmin)
