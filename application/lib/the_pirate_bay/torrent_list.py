import re
from lxml import html

from twisted.python import log

from torrent import Torrent
from ..web_client import WebClient


class List(object):
    """
    Abstract class for parsing a torrent list at some url and generate torrent
    objects to iterate over. Includes a resource path parser.
    """

    _meta = re.compile('Uploaded (.*), Size (.*), ULed by (.*)')
    base_path = ''

    def load_torrents(self, callback):
        """
        Creates an instance of PirateBayClient twisted client.
        sends of request and exeutes callback functions on
        response
        :param callback: This is a callback function that gets passed
            from the caller. The function passes a list of returned torrent
            objects. The list is empty if no torrents exist
        """

        client = WebClient(self.url.base.host())

        def _process_error(failure):
            log.err(str(failure))
            log.err(failure.getTraceback())

        def _process_torrents(response):
            document = html.fromstring(response)
            torrents = [
                self._build_torrent(row)
                for row in self._get_torrent_rows(document)]

            callback(torrents)

        result = client.request_page(self.url.full_path())
        result.addCallback(_process_torrents)
        result.addErrback(_process_error)

    def _get_torrent_rows(self, page):
        """
        Returns all 'tr' tag rows as a list of tuples. Each tuple is for
        a single torrent.
        """

        # The table with all torrent listing
        table = page.find('.//table')

        # No table means no results
        # Else, get all rows but header and footer
        if table is None:
            return []
        else:
            return table.findall('.//tr')[1:-1]

    def _build_torrent(self, row):
        """
        Builds and returns a Torrent object for the given parsed row.
        """

        ## Scrape, strip and build!!!
        # Split the row into it's columns
        cols = row.findall('.//td')

        # This column contains the categories
        [category, sub_category] = [c.text for c in cols[0].findall('.//a')]

        ## This column with all important info
        # Get 4 a tags from this columns
        links = cols[1].findall('.//a')
        title = unicode(links[0].text)
        url = self.url.build().path(links[0].get('href'))
        # the magnet download link
        magnet_link = links[1].get('href')

        try:
            # The torrent download link
            torrent_link = links[2].get('href')
            if not torrent_link.endswith('.torrent'):
                torrent_link = None
        except IndexError:
            torrent_link = None

        ## Torrent not available, manually create the link
        if torrent_link is None:
            link = str(url).split('http://')[1]
            link = link.replace('/torrent', '')
            torrent_link = 'http://torrents.{0}.torrent'.format(link)

        # Don't need user
        meta_col = cols[1].find('.//font').text_content()
        match = self._meta.match(meta_col)
        created = match.groups()[0].replace(u'\xa0', ' ')
        size = match.groups()[1].replace(u'\xa0', ' ')
        # Uploaded by user
        user = match.groups()[2]

        # Last 2 columns for seeders and leechers
        seeders = int(cols[2].text)
        leechers = int(cols[3].text)

        kwargs = {
            'title': title,
            'url': url,
            'category': category,
            'sub_category': sub_category,
            'magnet_link': magnet_link,
            'torrent_link': torrent_link,
            'created': created,
            'size': size,
            'user': user,
            'seeders': seeders,
            'leechers': leechers
        }

        return Torrent(**kwargs)
