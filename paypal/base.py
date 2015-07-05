from __future__ import unicode_literals
from django.utils import six
from django.utils.six.moves.urllib.parse import parse_qsl
from django.utils.translation import ugettext_lazy as _

from django.db import models


class ResponseModel(models.Model):

    # Debug information
    raw_request = models.TextField(max_length=512)
    raw_response = models.TextField(max_length=512)

    response_time = models.FloatField(help_text=_("Response time in milliseconds"))

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-date_created',)
        app_label = 'paypal'

    def request(self):
        request_params = self.context
        return self._as_dl(request_params)
    request.allow_tags = True

    def response(self):
        return self._as_dl(self.context)
    response.allow_tags = True

    def _as_table(self, params):
        rows = []
        for k, v in sorted(params.items()):
            rows.append('<tbody><tr><th>%s</th><td>%s</td></tr></tbody>' % (k, v[0]))
        return '<table>%s</table>' % ''.join(rows)

    def _as_dl(self, params):
        rows = []
        for k, v in sorted(params.items()):
            rows.append('<dt>%s</dt><dd>%s</dd>' % (k, v[0]))
        return '<dl>%s</dl>' % ''.join(rows)

    @property
    def context(self):
        ctx = {}
        if six.PY2 and isinstance(self.raw_response, six.text_type):
            self.raw_response = self.raw_response.encode('utf8')
        for key, val in parse_qsl(self.raw_response):
            if isinstance(key, six.binary_type):
                key = key.decode('utf8')
            if isinstance(val, six.binary_type):
                val = val.decode('utf8')
            ctx[key] = [val]
        return ctx

    def value(self, key, default=None):
        ctx = self.context
        return ctx[key][0] if key in ctx else default
