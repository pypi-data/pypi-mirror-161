from pathlib import Path

from ..loader import load_songs

name = 'songs'
help_text = 'Update song database'
initial_config = {
    'generate': 'yes',
    'regenerate': 'no',
    'karaoke_template_file': '~/negro_mate/karaoke_templates/karaoke.ass',
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))
    parser.add_argument(
        '-g', '--generate', action='store_const', const='yes',
        default=config['songs']['generate'],
        help="Generate missing files, defaults to {}".format(
            config['songs']['generate']))
    parser.add_argument(
        '-r', '--regenerate', action='store_const', const='yes',
        default=config['songs']['regenerate'],
        help="Regenerate missing files, defaults to {}".format(
            config['songs']['regenerate']))
    parser.add_argument(
        '-k', '--karaoke-template', type=Path,
        default=config['songs']['karaoke_template_file'],
        help="Ass file with the karaoke template, defaults to {}".format(
            config['songs']['karaoke_template_file']))


def run(args, **kwargs):
    generate = args.generate == 'yes'
    regenerate = args.regenerate == 'yes'
    songs, pending_songs = load_songs(
        root_folder=args.song_folder.expanduser(),
        generate=generate, regenerate=regenerate,
        karaoke_template_file=args.karaoke_template.expanduser())

    print(
        "#######\n"
        " Songs\n"
        "#######"
    )
    for s in songs:
        print(s.name)
    print(
        "###############\n"
        " Pending songs\n"
        "###############"
    )
    for s in pending_songs:
        print(s.name)
    total_songs = len(songs)
    songs_with_karaoke = len(list(s for s in songs if s.metadata['karaoke']))
    percent = int(songs_with_karaoke / total_songs * 100) if total_songs else 0
    print("Total songs: {}. With karaoke: {} ({}%)".format(total_songs, songs_with_karaoke, percent))
