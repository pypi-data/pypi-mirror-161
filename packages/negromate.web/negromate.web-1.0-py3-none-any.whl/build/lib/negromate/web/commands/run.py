from functools import partial
from http.server import test, SimpleHTTPRequestHandler
from pathlib import Path


name = 'run'
help_text = 'Start web server to test the website'
initial_config = {
    'port': '8000',
    'bind': '',
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))
    parser.add_argument(
        '-p', '--port', default=config[name]['port'], type=int,
        help='Specify alternate port, defaults to {}'.format(config[name]['port']))
    parser.add_argument(
        '--bind', '-b', default=config[name]['bind'], metavar='ADDRESS',
        help='Specify alternate bind address, defaults to {}'.format(
            config[name]['bind'] or 'all interfaces',
        ))


def run(args, **kwargs):
    Handler = partial(
        SimpleHTTPRequestHandler,
        directory=str(args.song_folder.expanduser()),
    )

    test(HandlerClass=Handler, port=args.port, bind=args.bind or None)
