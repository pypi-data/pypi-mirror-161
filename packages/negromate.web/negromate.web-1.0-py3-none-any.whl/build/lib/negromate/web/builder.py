import os
from shutil import copy
import subprocess

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.utils import Markup
import srt

from negromate.songs.loader import load_songs


class SongPage:
    def __init__(self, song):
        self.song = song

    def get_context_data(self):
        parsed_srt = None
        if self.song.srt:
            with self.song.srt.open('r') as srtfile:
                try:
                    srt_str = srtfile.read().encode('utf-8').decode('utf-8-sig')
                    parsed_srt = list(srt.parse(srt_str))
                except Exception as e:
                    print("{}: srt parse error: {}".format(self.song.path.name, e))
        root_path = os.path.relpath(self.song.root, self.song.path)
        return {
            'song': self,
            'parsed_srt': parsed_srt,
            'root_path': root_path,
        }

    def render(self, builder, context):
        ctx = self.get_context_data()
        ctx.update(context)
        builder.render('song.html', self.song.path, ctx)

    def __getattr__(self, name):
        return getattr(self.song, name)


class Builder:
    def __init__(self, root_folder, libreto, template_folder, static_folder):
        self.root_folder = root_folder
        self.libreto = libreto
        self.static_folder = static_folder
        self.template_folder = template_folder

        self.env = Environment(
            loader=FileSystemLoader(template_folder),
            autoescape=select_autoescape(['html']),
        )
        self.env.filters['url'] = self.url
        self.env.filters['display_boolean'] = self.display_boolean
        self.current_path = self.root_folder

    def url(self, path):
        return os.path.relpath(path, self.current_path)

    def display_boolean(self, value):
        if value:
            return Markup('&check;')
        else:
            return Markup('&cross;')

    def render(self, template, target, context):
        html_file = target / 'index.html'
        page_template = self.env.get_template(template)
        root_path = os.path.relpath(self.root_folder, target)
        context['root_path'] = root_path

        with html_file.open('w') as page:
            page.write(page_template.render(context))

    def build(self):
        songs, pending_songs = load_songs(self.root_folder)
        songs = [SongPage(s) for s in songs]
        pending_songs = [SongPage(s) for s in pending_songs]

        global_context = {
            'songs': songs,
            'root_folder': self.root_folder,
        }

        for song in songs:
            self.current_path = song.path
            song.render(self, global_context)

        self.render('index.html', self.root_folder, global_context)

        home = self.root_folder / 'home'
        self.current_path = home
        if not home.exists():
            home.mkdir()
        self.render('home.html', home, global_context)

        playlist = self.root_folder / 'playlist'
        self.current_path = playlist
        if not playlist.exists():
            playlist.mkdir()

        self.render('playlist.html', playlist, global_context)

        todo = self.root_folder / 'todo'
        self.current_path = todo
        if not todo.exists():
            todo.mkdir()
        todo_context = {
            'pending_songs': pending_songs,
        }
        todo_context.update(global_context)
        self.render('todo.html', todo, todo_context)

        static = self.root_folder / 'static'

        if not static.exists():
            static.mkdir()

        subprocess.check_call([
            'rsync',
            '-ra',
            str(self.static_folder),
            str(self.root_folder.absolute()),
        ])

        libreto = self.root_folder / 'static/libreto/libreto.pdf'
        copy(str(self.libreto.absolute()), str(libreto.absolute()))
