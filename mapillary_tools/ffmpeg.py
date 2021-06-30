import json
import os
import subprocess


# author https://github.com/stilldavid


def get_ffprobe(path):
    """
    Gets information about a media file
    TODO: use the class in ffprobe.py - why doesn't it use json output?
    """
    try:
        with open(os.devnull, "w") as fp:
            subprocess.check_call(["ffprobe", "-h"], stdout=fp, stderr=fp)
    except FileNotFoundError:
        raise RuntimeError(
            "ffprobe not found. Please make sure it is installed in your PATH. See https://github.com/mapillary/mapillary_tools#video-support for instructions"
        )

    if not os.path.isfile(path):
        raise RuntimeError(f"No such file: {path}")

    j_str = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            path,
        ]
    )

    try:
        j_obj = json.loads(j_str)
    except json.JSONDecodeError:
        raise RuntimeError(f"Error JSON decoding {j_str}")

    return j_obj


def extract_stream(source, dest, stream_id):
    """
    Get the data out of the file using ffmpeg
    @param filename: mp4 filename
    """
    if not os.path.isfile(source):
        raise RuntimeError(f"No such file: {source}")

    subprocess.check_output(
        [
            "ffmpeg",
            "-i",
            source,
            "-y",  # overwrite - potentially dangerous
            "-nostats",
            "-loglevel",
            "0",
            "-codec",
            "copy",
            "-map",
            "0:" + str(stream_id),
            "-f",
            "rawvideo",
            dest,
        ]
    )
