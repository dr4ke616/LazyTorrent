
from torrent_list import List


class Paginated(List):
    """
    Abstract class on top of ``List`` for parsing a torrent list with
    pagination capabilities.
    """
    def __init__(self, *args, **kwargs):
        super(Paginated, self).__init__(*args, **kwargs)
        self._multipage = False

    def load_torrents(self, callback):
        if self._multipage:
            # TODO: This needs to be implemented.
            # Logic is: Keep pooling for torrents
            # until empty result returned
            # (i.e. no more torrents)
            # On each return of a list of torrents
            # call self.next() to go to next page of torrents
            raise NotImplementedError('Multipage not implemented yet')
        else:
            super(Paginated, self).load_torrents(callback)

    def multipage(self):
        """
        Enable multipage iteration.
        """
        self._multipage = True
        return self

    def page(self, number=None):
        """
        If page is given, modify the URL correspondingly, return the current
        page otherwise.
        """
        if number is None:
            return int(self.url.page)
        self.url.page = str(number)

    def next(self):
        """
        Jump to the next page.
        """
        self.page(self.page() + 1)
        return self

    def previous(self):
        """
        Jump to the previous page.
        """
        self.page(self.page() - 1)
        return self
