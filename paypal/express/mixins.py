
class GatewayViewMixin(object):
    ''' mixin for views that call gateway functions '''
    def get_gateway_kwargs(self):
        '''
        override this method to pass custom / additional params to
        the Paypal API.
        '''
        return {}