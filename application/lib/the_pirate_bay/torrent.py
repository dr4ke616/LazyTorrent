import dateutil.parser
import datetime
import time
import sys

from lxml import html

if sys.version_info >= (3, 0):
    from urllib.request import urlopen
    unicode = str
else:
    from urllib2 import urlopen


class Torrent(object):
    """
    Holder of a single TPB torrent.
    """

    title = None
    url = None
    category = None
    sub_category = None
    magnet_link = None
    torrent_link = None
    size = None
    user = None
    seeders = None
    leechers = None

    def __init__(self, *args, **kwargs):

        for key, value in kwargs.iteritems():
            if key == 'created':
                # Tupple - (Uploaded date, current time)
                self._created = (value, time.time())
            else:
                if hasattr(self, key):
                    setattr(self, key, value)

        self.id = self.url.path_segments()[1]
        self._info = None
        self._files = {}

    @property
    def info(self):
        if self._info is None:
            request = urlopen(str(self.url))
            document = html.parse(request)
            root = document.getroot()
            info = root.cssselect('#details > .nfo > pre')[0].text_content()
            self._info = info
        return self._info

    @property
    def files(self):
        if not self._files:
            path = '/ajax_details_filelist.php?id={id}'.format(id=self.id)
            url = self.url.path(path)
            print '-->>>', url
            request = urlopen(str(url))
            document = html.parse(request)
            root = document.getroot()
            rows = root.findall('.//tr')
            for row in rows:
                name, size = [unicode(v.text_content())
                              for v in row.findall('.//td')]
                self._files[name] = size.replace('\xa0', ' ')
        return self._files

    @property
    def created(self):
        """
        Attempt to parse the human readable torrent creation datetime.
        """
        timestamp, current = self._created
        if timestamp.endswith('ago'):
            quantity, kind, ago = timestamp.split()
            quantity = int(quantity)
            if 'sec' in kind:
                current -= quantity
            elif 'min' in kind:
                current -= quantity * 60
            elif 'hour' in kind:
                current -= quantity * 60 * 60
            return datetime.datetime.fromtimestamp(current)

        current = datetime.datetime.fromtimestamp(current)

        timestamp = timestamp.replace(
            'Y-day', str(current.date() - datetime.timedelta(days=1)))

        timestamp = timestamp.replace(
            'Today', current.date().isoformat())

        try:
            return dateutil.parser.parse(timestamp)
        except:
            return current

    @property
    def torrent_link_chunks(self):
        link = self.torrent_link
        link = link.split('/')
        return {
            'url-scheme': link[0] + '//',
            'host': link[2],
            'id': link[3],
            'url-title': link[4]
        }

    def print_torrent(self):
        """
        Print the details of a torrent
        """
        print('Title: %s' % self.title)
        print('URL: %s' % self.url)
        print('Category: %s' % self.category)
        print('Sub-Category: %s' % self.sub_category)
        print('Magnet Link: %s' % self.magnet_link)
        print('Torrent Link: %s' % self.torrent_link)
        print('Uploaded: %s' % self.created)
        print('Size: %s' % self.size)
        print('User: %s' % self.user)
        print('Seeders: %d' % self.seeders)
        print('Leechers: %d' % self.leechers)

    def __repr__(self):
        return '{0} by {1}'.format(self.title, self.user)
