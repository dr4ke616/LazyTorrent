
from the_pirate_bay.tpb import ThePirateBay
from downloader import Downloader


def torrent_callback(torrents):
    for t in torrents:
        t.print_torrent()


def test_pb():
    pb = ThePirateBay('http://thepiratebay.se')
    # request = pb.recent()
    # request = pb.search('The Walking Dead')
    request = pb.top()
    request.load_torrents(torrent_callback)


def file_created(filename):
    print 'File Created', filename


def test_downlaod():

    file_to_download = {
        'remote_file': '8472688/Warm.Bodies.2013.720p.WEB-DL.X264-WEBiOS_[PublicHD].torrent',
        'location': 'Warm.Bodies.torrent'
    }
    files = (file_to_download, )

    downloader = Downloader('torrents.thepiratebay.se')
    downloader.get(files, on_file_created=file_created)
