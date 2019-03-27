from django.contrib import admin

from paypal import models


class ExpressTransactionAdmin(admin.ModelAdmin):
    list_display = ['method', 'amount', 'currency', 'correlation_id', 'ack',
                    'token', 'error_code', 'error_message', 'date_created']
    readonly_fields = [
        'method',
        'version',
        'amount',
        'currency',
        'ack',
        'correlation_id',
        'token',
        'error_code',
        'error_message',
        'raw_request',
        'raw_response',
        'response_time',
        'date_created',
        'request',
        'response']


admin.site.register(models.ExpressTransaction, ExpressTransactionAdmin)
