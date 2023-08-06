import json

import asstosrt
import webvtt

from .utils import needs_change, generate_cover, generate_thumbnail, generate_karaoke_ass
from . import logger


class Song:
    def __init__(self, path, root):
        self.name = path.name
        self.metadata = None
        self.original = None
        self.author = None
        self.date = None
        self.path = path
        self.root = root
        self.video = None
        self.video_type = None
        self.vtt = None
        self.srt = None
        self.karaoke_ass = None
        self.ass = None
        self.cover = None
        self.thumbnail = None
        self.files = []
        self.search_media()

    def search_media(self):
        for entry in self.path.iterdir():
            if entry.name == 'metadata.json':
                with entry.open('r') as metadatafile:
                    self.metadata = json.load(metadatafile)
                if 'name' in self.metadata:
                    self.name = self.metadata['name']
                if 'original' in self.metadata:
                    self.original = self.metadata['original']
                if 'author' in self.metadata:
                    self.author = self.metadata['author']
                if 'date' in self.metadata:
                    self.date = self.metadata['date']
            elif entry.name.endswith('mp4'):
                self.video = entry
                self.video_type = 'video/mp4'
                self.files.append(entry)
            elif entry.name.endswith('webm'):
                self.video = entry
                self.video_type = 'video/webm'
                self.files.append(entry)
            elif entry.name.endswith('ogv'):
                self.video = entry
                self.video_type = 'video/ogg'
                self.files.append(entry)
            elif entry.name.endswith('vtt'):
                self.vtt = entry
            elif entry.name == "{}.srt".format(self.path.name):
                self.srt = entry
                self.files.append(entry)
            elif entry.name == "{}.karaoke.ass".format(self.path.name):
                self.karaoke_ass = entry
                self.files.append(entry)
            elif entry.name == "{}.ass".format(self.path.name):
                self.ass = entry
                self.files.append(entry)
            elif entry.name == 'thumb.jpg':
                self.thumbnail = entry
            elif entry.name == 'cover.jpg':
                self.cover = entry
            elif entry.name == 'index.html':
                continue
            else:
                self.files.append(entry)

    def generate_missing(self, regenerate=False, karaoke_template_file=None):
        srt_ = self.path / "{}.srt".format(self.path.name)
        if regenerate or needs_change(srt_, (self.ass,)):
            logger.info("generating {}".format(srt_))
            self.srt = srt_
            with self.ass.open('r') as assfile, self.srt.open('w') as srtfile:
                srtfile.write(asstosrt.convert(assfile))
            self.files.append(self.srt)

        vtt = self.path / "{}.vtt".format(self.path.name)
        if regenerate or needs_change(vtt, (self.srt,)):
            logger.info("generating {}".format(vtt))
            self.vtt = vtt
            webvtt.from_srt(str(self.srt.absolute())).save(str(self.vtt.absolute()))

        cover = self.path / "cover.jpg"
        if regenerate or needs_change(cover, (self.video,)):
            logger.info("generating {}".format(cover))
            self.cover = cover
            generate_cover(self.video, self.cover)

        thumbnail = self.path / "thumb.jpg"
        if regenerate or needs_change(thumbnail, (self.cover,)):
            logger.info("generating {}".format(thumbnail))
            self.thumbnail = thumbnail
            generate_thumbnail(self.cover, self.thumbnail)

        karaoke_ass = self.path / "{}.karaoke.ass".format(self.path.name)
        karaoke_requirements = (
            self.metadata.get('karaoke', False),
            regenerate or needs_change(karaoke_ass, (self.ass, karaoke_template_file)),
        )
        if all(karaoke_requirements):
            logger.info("generating {}".format(karaoke_ass))
            self.karaoke_ass = karaoke_ass
            generate_karaoke_ass(str(karaoke_template_file), str(self.ass), str(karaoke_ass))

    @property
    def has_subtitles(self):
        return self.ass or self.srt or self.vtt

    @property
    def publish(self):
        return self.video and self.has_subtitles

    @property
    def pending(self):
        finished = self.ass and self.video
        return not finished


def load_songs(root_folder, generate=True, regenerate=False, karaoke_template_file=None):
    songs = []
    pending_songs = []
    for entry in root_folder.iterdir():
        if entry.name in ['static', 'playlist', 'home', 'todo']:
            continue
        if entry.is_dir() and (entry / 'metadata.json').exists():
            logger.info("building {}".format(entry.name))
            try:
                song = Song(entry, root_folder)
                if generate:
                    song.generate_missing(regenerate, karaoke_template_file)
            except Exception as e:
                logger.error("Error: %s", e)
                continue
            if song.publish:
                songs.append(song)
            if song.pending:
                pending_songs.append(song)

    songs.sort(key=lambda a: a.name)

    return songs, pending_songs
