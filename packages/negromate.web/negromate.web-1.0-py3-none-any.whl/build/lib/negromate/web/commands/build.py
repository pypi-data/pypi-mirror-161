from pathlib import Path
from ..builder import Builder


name = 'build'
help_text = 'Generate static website'
initial_config = {
    'template_folder': '~/negro_mate/web/templates',
    'static_folder': '~/negro_mate/web/static',
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))
    parser.add_argument(
        '-l', '--lyrics_file', type=Path,
        default=config['global']['lyrics_file'],
        help="File with the lyrics of the songs, defaults to {}".format(
            config['global']['lyrics_file']))
    parser.add_argument(
        '-t', '--template_folder', type=Path,
        default=config['build']['template_folder'],
        help="Folder with jinja2 templates, defaults to {}".format(
            config['build']['template_folder']))
    parser.add_argument(
        '-S', '--static_folder', type=Path,
        default=config['build']['static_folder'],
        help="Folder with static content, defaults to {}".format(
            config['build']['static_folder']))


def run(args, **kwargs):
    builder = Builder(
        root_folder=args.song_folder.expanduser(),
        libreto=args.lyrics_file.expanduser(),
        template_folder=args.template_folder.expanduser(),
        static_folder=args.static_folder.expanduser(),
    )
    builder.build()
