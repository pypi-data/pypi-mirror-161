import os
import subprocess
import time
from contextlib import contextmanager

import ass


@contextmanager
def Xephyr_env(display=":2", *args, **kwargs):
    env = os.environ.copy()
    xephyr = subprocess.Popen(["Xephyr", display], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env['DISPLAY'] = display
    try:
        yield env
    finally:
        xephyr.kill()


def set_template(template_subtitles, orig_file, target_file=None):
    if target_file is None:
        target_file = orig_file

    with open(orig_file, 'r') as orig:
        subtitles = ass.parse(orig)

    new_events = []
    for dialogue in template_subtitles.events:
        new_events.append(dialogue)

    for dialogue in subtitles.events:
        if dialogue.effect.startswith('code'):
            continue
        if dialogue.effect.startswith('template'):
            continue
        new_events.append(dialogue)

    subtitles.events = new_events

    with open(target_file, 'w', encoding='utf-8-sig') as target:
        subtitles.dump_file(target)


def run(command, env, wait=None):
    subprocess.Popen(
        command,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if wait is not None:
        time.sleep(wait)


def apply_template(subtitles, env):
    run(["aegisub-3.2", subtitles], env=env, wait=2)

    # Si pide confirmación para cargar video ignorar el popup
    run(["xdotool", "key", "Escape"], env=env, wait=0.1)

    # abrir el menú de automatización, bajar dos y darle a aplicar template
    run(["xdotool", "key", "alt+u"], env=env, wait=0.1)
    run(["xdotool", "key", "Down"], env=env, wait=0.1)
    run(["xdotool", "key", "Down"], env=env, wait=0.1)
    run(["xdotool", "key", "Return"], env=env, wait=2)

    # guardar
    run(["xdotool", "key", "ctrl+s"], env=env)

    # cerrar programa
    run(["xdotool", "key", "ctrl+q"], env=env)


def update_karaoke_songs(songs, template_file, regenerate=False):
    from negromate.songs.utils import needs_change

    with open(template_file, 'r') as template:
        template_subtitles = ass.parse(template)

    with Xephyr_env() as env:
        for song in songs:
            if song.metadata.get('karaoke'):
                target = song.path / "{}.karaoke.ass".format(song.path.name)
                if regenerate or needs_change(target, (song.ass, template_file)):
                    set_template(
                        template_subtitles=template_subtitles,
                        orig_file=str(song.ass),
                        target_file=str(target)
                    )
                    time.sleep(2)
                    apply_template(str(target), env)
                    time.sleep(2)
