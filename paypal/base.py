import urlparse

from django.db import models


class ResponseModel(models.Model):

    # Debug information
    raw_request = models.TextField(max_length=512)
    raw_response = models.TextField(max_length=512)

    response_time = models.FloatField(help_text="Response time in milliseconds")

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-date_created',)
        app_label = 'paypal'

    def request(self):
        request_params = urlparse.parse_qs(self.raw_request)
        return self._as_table(request_params)
    request.allow_tags = True

    def response(self):
        return self._as_table(self.context)
    response.allow_tags = True

    def _as_table(self, params):
        rows = []
        for k, v in sorted(params.items()):
            rows.append('<tr><th>%s</th><td>%s</td></tr>' % (k, v[0]))
        return '<table>%s</table>' % ''.join(rows)

    @property
    def context(self):
        return urlparse.parse_qs(self.raw_response)

    def value(self, key):
        ctx = self.context
        return ctx[key][0] if key in ctx else None
