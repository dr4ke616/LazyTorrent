
from filters.recent import Recent
from filters.search import Search
from filters.top import Top


class ThePirateBay(object):
    """
    TPB API with searching, most recent torrents and top torrents support.
    Passes on base_url to the instantiated Search, Recent and Top classes.
    """

    def __init__(self, base_url, use_tor):
        self.base_url = base_url
        self.use_tor = use_tor

    def recent(self, page=0):
        """
        Lists most recent Torrents added to TPB.
        """
        return Recent(self.base_url, self.use_tor, page)

    def search(self, query, page=0, order=7, category=0, multipage=False):
        """
        Searches TPB for query and returns a list of paginated Torrents capable
        of changing query, categories and orders.
        """
        search = Search(
            self.base_url, self.use_tor, query, page, order, category
        )
        if multipage:
            search.multipage()
        return search

    def top(self, category=0):
        """
        Lists top Torrents on TPB optionally filtering by category.
        """
        return Top(self.base_url, self.use_tor, category)
