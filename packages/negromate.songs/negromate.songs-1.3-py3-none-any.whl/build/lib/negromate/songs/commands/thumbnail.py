from pathlib import Path

from negromate.songs.utils import generate_cover, generate_thumbnail

name = 'thumbnail'
help_text = 'Generate cover and thumbnail for a video.'


def options(parser, config, **kwargs):
    parser.add_argument(
        'video', help="Video of the song.", type=Path)
    parser.add_argument(
        'second', type=int,
        help='Take snapshot at this second.')


def run(args, **kwargs):
    video = args.video
    cover = video.parent / 'cover.jpg'
    thumbnail = video.parent / 'thumb.jpg'
    generate_cover(video, cover, args.second)
    generate_thumbnail(cover, thumbnail)
