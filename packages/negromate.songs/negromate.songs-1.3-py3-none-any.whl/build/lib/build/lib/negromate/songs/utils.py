import subprocess
import ass
import time

from . import karaoke_templates


def needs_change(destination, dependencies):
    last_dependency_change = 0
    for dependency in dependencies:
        if dependency is None:
            return False
        last_dependency_change = max(
            last_dependency_change,
            dependency.lstat().st_mtime
        )

    if not destination.exists():
        return True

    return destination.lstat().st_mtime < last_dependency_change


def generate_cover(video, cover, second=2):
    command = [
        'ffmpeg',
        '-loglevel', 'quiet',
        '-i', str(video.absolute()),
        '-vcodec', 'mjpeg',
        '-vframes', '1',
        '-an',
        '-f', 'rawvideo',
        '-ss', str(second),
        '-y',
        str(cover.absolute()),
    ]
    subprocess.check_call(command)


def generate_thumbnail(cover, thumbnail, geometry="200x200"):
    command = [
        'convert',
        str(cover.absolute()),
        '-resize', geometry,
        str(thumbnail.absolute()),
    ]
    subprocess.check_call(command)


def generate_karaoke_ass(template_file, orig_file, target_file):
    with open(template_file, 'r') as template:
        template_subtitles = ass.parse(template)

    with karaoke_templates.Xephyr_env() as env:
        karaoke_templates.set_template(
            template_subtitles=template_subtitles,
            orig_file=orig_file,
            target_file=target_file,
        )
        time.sleep(2)
        karaoke_templates.apply_template(target_file, env)
        time.sleep(2)
