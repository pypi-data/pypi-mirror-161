import subprocess
from pathlib import Path

name = 'rsync'
help_text = 'Sincronize the static web with the server'
initial_config = {
    'host': 'negromate.rocks',
    'user': 'root',
    'port': '22',
    'destination': "/var/www/html",
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))
    parser.add_argument(
        '-H', '--host', default=config[name]['host'],
        help="Target server, defaults to {}.".format(config[name]['host']))
    parser.add_argument(
        '-u', '--user', default=config[name]['user'],
        help="User in the server, defaults to {}.".format(config[name]['user']))
    parser.add_argument(
        '-p', '--port', default=config[name]['port'], type=int,
        help="Port of the ssh server, defaults to {}.".format(config[name]['port']))
    parser.add_argument(
        '-d', '--destination', default=config[name]['destination'],
        help="Folder of the server, defaults to {}".format(config[name]['destination']))


def run(args, **kwargs):
    contents = str(args.song_folder.expanduser()) + '/'
    destination = "{user}@{host}:{folder}".format(
        user=args.user,
        host=args.host,
        folder=args.destination,
    )
    command = [
        "rsync",
        "-av",
        '--rsh=ssh -p {}'.format(args.port),
        contents,
        destination,
    ]
    print(" ".join(command))
    subprocess.check_call(command)
