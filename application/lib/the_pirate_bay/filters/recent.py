
from ..paginated import Paginated
from ..utils import URL


class Recent(Paginated):
    """
    Paginated most recent torrents.
    """
    base_path = '/recent'

    def __init__(self, base_url, page='0'):
        super(Recent, self).__init__()

        self.url = URL(
            base=base_url,
            path=self.base_path,
            segments=['page'],
            defaults=[str(page)]
        )

    def load_torrents(self, callback):
        super(Recent, self).load_torrents(callback)
