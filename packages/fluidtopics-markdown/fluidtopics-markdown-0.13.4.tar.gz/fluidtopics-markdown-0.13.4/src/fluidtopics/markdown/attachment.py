from pathlib import Path
import logging
from typing import List
import yaml

DEFAULT_MEDIA_DIR = 'images'
DEFAULT_ATTACHMENT_DIR = 'attachments'

logger = logging.getLogger("fluidtopics.markdown")


def collect_attachments(input_path: Path, attachment_reldir: Path) -> List[dict]:
    """Collect the attachments in the specified directory."""
    map_attachments = []
    attachment_dir = input_path / attachment_reldir
    logger.debug(f"Looking for attachment in {attachment_dir}")
    if attachment_dir.exists():
        # examine directory for attachments
        att_files = sorted(attachment_dir.iterdir())
        last = None
        # Iterate over the attachment files and find pairs of attachment and meta files
        # we know that meta file (if there is one exists) shall follow the
        # attachment file because the were sorted
        for current in att_files:
            if last is not None and current.name == last.name + ".yml":
                # this is the metadata of the previous attachment file
                map_attachments[-1].update(yaml.safe_load(current.open('r').read()))
            else:
                map_attachments.append({'filePath': current.relative_to(input_path).as_posix()})
            last = current
        logger.debug(f"map attachments {len(map_attachments)}: {map_attachments}")

    return map_attachments
