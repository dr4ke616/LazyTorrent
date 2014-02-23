
# from .application.lib.paginated import Paginated
# from .application.lib.utils import URL
from ..paginated import Paginated
from ..utils import URL


class Search(Paginated):
    """
    Paginated search featuring query, category and order management.
    """
    base_path = '/search'

    def __init__(self, base_url, query, page='0', order='7', category='0'):
        super(Search, self).__init__()

        self.url = URL(
            base=base_url,
            path=self.base_path,
            segments=['query', 'page', 'order', 'category'],
            defaults=[query, str(page), str(order), str(category)])

    def load_torrents(self, callback, **kwargs):
        super(Search, self).load_torrents(callback, **kwargs)

    def query(self, query=None):
        """
        If query is given, modify the URL correspondingly, return the current
        query otherwise.
        """
        if query is None:
            return self.url.query
        self.url.query = query

    def order(self, order=None):
        """
        If order is given, modify the URL correspondingly, return the current
        order otherwise.
        """
        if order is None:
            return int(self.url.order)
        self.url.order = str(order)

    def category(self, category=None):
        """
        If category is given, modify the URL correspondingly, return the
        current category otherwise.
        """
        if category is None:
            return int(self.url.category)
        self.url.category = str(category)
