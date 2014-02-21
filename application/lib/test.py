
from the_pirate_bay.tpb import ThePirateBay


def torrent_callback(torrents):
    for t in torrents:
        t.print_torrent()


def test_pb():
    pb = ThePirateBay('http://thepiratebay.se')
    # request = pb.recent()
    # request = pb.search('The Walking Dead')
    request = pb.top()
    request.load_torrents(torrent_callback)


def main():
    test_pb()


if __name__ == '__main__':
    main()
