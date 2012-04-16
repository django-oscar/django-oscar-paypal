from django.contrib import admin
from paypal.express import models


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['method', 'amount', 'currency', 'correlation_id', 'ack', 'token',
                    'date_created']


admin.site.register(models.Transaction, TransactionAdmin)
