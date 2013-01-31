from django.contrib.sites.models import Site


def absolute_url(request, path):
    """
    Return an absolute URL that can be given to PayPal as a return or cancel
    URL
    """
    scheme = 'https' if request.is_secure() else 'http'
    if 'HTTP_HOST' in request.META:
        domain = request.META['HTTP_HOST']
    else:
        domain = Site.objects.get_current().domain
    return '%s://%s%s' % (scheme, domain, path)
