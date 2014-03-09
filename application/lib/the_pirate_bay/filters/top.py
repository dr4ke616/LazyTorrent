
from ..paginated import Paginated
from ..utils import URL


class Top(Paginated):
    """
    Top torrents featuring category management.
    """
    base_path = '/top'

    def __init__(self, base_url, use_tor, category='0'):
        super(Top, self).__init__(use_tor=use_tor)

        self.url = URL(
            base=base_url,
            path=self.base_path,
            segments=['category'],
            defaults=[str(category)]
        )

    def load_torrents(self, callback):
        super(Top, self).load_torrents(callback)

    def category(self, category=None):
        """
        If category is given, modify the URL correspondingly, return the
        current category otherwise.
        """
        if category is None:
            return int(self.url.category)
        self.url.category = str(category)
