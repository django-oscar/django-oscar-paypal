from oscar.apps.shipping.repository import Repository as BaseRepository

from . import methods as shipping_methods


class Repository(BaseRepository):
    methods = (
        shipping_methods.SecondClassRecorded(),
    )
