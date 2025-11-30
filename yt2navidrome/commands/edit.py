import sys
from pathlib import Path

import click
from click_option_group import optgroup

from yt2navidrome.utils.ffmpeg import FFmpegHelper
from yt2navidrome.utils.logging import get_logger

logger = get_logger(__name__)


@click.command("edit")
@optgroup.group("Tag/Value")
@optgroup.option("-t", "--tag", help="Tag to add/modify")
@optgroup.option("-v", "--value", help="Value to insert into tag")
@click.argument("input_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
def edit(input_file: Path, tag: str, value: str) -> None:
    if not input_file.exists():
        logger.error(f"{input_file} not found. Exiting...")
        sys.exit(-1)

    # First we get the current value of the tag (if it exists)
    tags = FFmpegHelper.get_tags(input_file)
    current_tag_value = tags.get(tag)

    if current_tag_value:
        logger.info(f"Current value for {tag} = {current_tag_value}")
    else:
        logger.info(f"Tag {tag} does not have any value yet")

    # Then we edit the video file with the requested tag and value
    FFmpegHelper.add_metadata(input_file, {tag: value})

    # Finally we check the value of the modified tag from the video
    tags = FFmpegHelper.get_tags(input_file)
    new_tag_value = tags.get(tag, "ERROR")
    logger.info(f"{input_file.name} => {tag}: {new_tag_value}")
