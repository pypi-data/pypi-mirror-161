from pathlib import Path
import getpass
import subprocess
import urllib.request

from negromate.songs import logger


name = 'ipfs'
help_text = 'Upload the web to IPFS'
initial_config = {
    'api': 'http://ipfs.negromate.rocks',
    'pinfile': '~/.negromate/ipfs.hash',
    'realm': 'IPFS Gitea Negromate',
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))
    parser.add_argument(
        '-a', '--api', default=config[name]['api'],
        help="IPFS API server, defaults to {}.".format(config[name]['api']))
    parser.add_argument(
        '-r', '--realm', default=config[name]['realm'],
        help="IPFS API basic authentication realm, defaults to {}.".format(config[name]['realm']))
    parser.add_argument(
        '-p', '--pinfile', default=config[name]['pinfile'], type=Path,
        help="file to store the current ipfs hash, defaults to {}".format(
            config[name]['pinfile']))


def run(args, **kwargs):
    # Setup HTTP Basic authentication
    user = input('Username: ')
    password = getpass.getpass('Password:')
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm=args.realm,
        uri=args.api,
        user=user,
        passwd=password)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    # add to local
    command = [
        "ipfs",
        "add",
        "--recursive",
        "--quieter",
        args.song_folder.expanduser(),
    ]
    new_hash = subprocess.check_output(command).decode('utf-8').strip()
    logger.info('New hash: {}'.format(new_hash))

    # pin in server
    data = urllib.parse.urlencode({
        'arg': new_hash,
        'progress': 'false',
    })
    url = '{}/api/v0/pin/add?{}'.format(args.api, data)
    logger.debug("server pin request: {}".format(url))
    request = urllib.request.Request(url, method='POST')
    urllib.request.urlopen(request)
    logger.info('Hash pinned on server.')

    # update ipns on server
    data = urllib.parse.urlencode({
        'arg': new_hash,
        'resolve': 'true',
    })
    url = "{}/api/v0/name/publish?{}".format(args.api, data)
    logger.debug("server ipns request: {}".format(url))
    request = urllib.request.Request(url, method='POST')
    urllib.request.urlopen(request)
    logger.info('IPNS name updated.')

    # read previous hash and update value
    pinfile = args.pinfile.expanduser()
    if pinfile.exists():
        with pinfile.open() as f:
            previous_hash = f.read()
        logger.info('Previous hash: {}'.format(previous_hash))
    else:
        if not pinfile.parent.exists():
            pinfile.parent.mkdir()
        previous_hash = None

    if previous_hash is not None and previous_hash != new_hash:
        # remove previous pin on local
        command = [
            'ipfs',
            'pin',
            'rm',
            previous_hash,
        ]
        result = subprocess.run(command)
        if result.returncode != 0:
            logger.info('Previous {} hash not removed: {}'.format(previous_hash, result.stdout))
        else:
            logger.info('Previous hash unpinned on local')

        # remove previous pin on server
        data = urllib.parse.urlencode({
            'arg': previous_hash,
        })
        url = "{}/api/v0/pin/rm?{}".format(args.api, data)
        logger.debug("server unpin request: {}".format(url))
        request = urllib.request.Request(url, method='POST')
        urllib.request.urlopen(request)
        logger.info('Previous hash unpinned on server')

    with pinfile.open('w') as f:
        f.write(new_hash)
