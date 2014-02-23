from the_pirate_bay.tpb import ThePirateBay
from downloader import Downloader


def torrent_callback(torrents):
    for t in torrents:
        t.print_torrent()


def test_pb():
    pb = ThePirateBay('http://thepiratebay.se')
    # request = pb.recent()
    request = pb.search('The Walking Dead')
    # request = pb.top()
    request.load_torrents(torrent_callback)


def file_created(filename):
    print 'File Created', filename


def test_downlaod():

# http://torrents.thepiratebay.se/9627612/The.Walking.Dead.S04E10.HDTV.x264-EXCELLENCE.[VTV].mp4.torrent

    file_to_download = {
        'remote_file': '9627612/The.Walking.Dead.S04E10.HDTV.x264-EXCELLENCE.[VTV].mp4.torrent',
        'location': '/home/adam/Downloads/auto_torrent/The.Walking.Dead.S04E10.HDTV.x264-EXCELLENCE.[VTV].mp4.torrent'
    }
    files = (file_to_download, )

    downloader = Downloader('torrents.thepiratebay.se')
    downloader.get(files, on_file_created=file_created)
