from enum import Enum

import logging
import re
import yaml
from io import StringIO
from pathlib import Path
from typing import Tuple, Dict, TextIO, Optional

from fluidtopics.connector.model.metadata import SemanticMetadata
from fluidtopics.markdown.errors import MD2FTError

MISSING_TITLE = 'MISSING TITLE'
COVER_PAGE_TITLE = 'Preface'


class MetadataError(Exception):
    pass


class ContentBeforeHeading(Exception):
    pass


logger = logging.getLogger("fluidtopics.markdown")

RE_LINEMETA = re.compile(r'\s*\[_metadata_\:(\w*[\:\w*]*)\]\:\s*-\s*["\'](.+)["\']')
RE_YAMLMETA_BEGIN = re.compile(r'^---')
RE_YAMLMETA_END = re.compile(r'^---|^\.\.\.')
RE_H1_MD = re.compile("^# (.*)$")
RE_CODE_MD_BEGIN = re.compile(r'^```.*$')
RE_CODE_MD_END = re.compile(r'^```$')


class MetadataType(Enum):
    NoMeta = 1
    LineMeta = 2
    YamlMeta = 3


# List of meta data that ought to be single-valued
# See: https://doc.antidot.net/r/FT/3.7/empower-metadata/Metadata-in-Fluid-Topics/Semantic-Metadata


# The authorized single value semantic meta are given
# by the official fluidtopics API
# see: https://pypi.org/project/fluidtopics
FT_SEMANTIC_META = SemanticMetadata.ALL
# This one is authorized too for md2ft
FT_ORIGIN_ID = "ft:originId"
FT_ORIGIN_ID_COMPAT = "ft:originID"
FT_LANG = "ft:lang"
FT_SEMANTIC_META.add(FT_ORIGIN_ID)
FT_SEMANTIC_META.add(FT_ORIGIN_ID_COMPAT)
FT_SEMANTIC_META.add(FT_LANG)
SINGLE_VALUE_M2FT = set()
MD2FT_AUDIENCE = "audience"
SINGLE_VALUE_M2FT.add(MD2FT_AUDIENCE)
MD2FT_MEDIA_DIR = "media_dir"
SINGLE_VALUE_M2FT.add(MD2FT_MEDIA_DIR)
MD2FT_ATTACHMENT_DIR = "attachment_dir"
SINGLE_VALUE_M2FT.add(MD2FT_ATTACHMENT_DIR)

SINGLE_VALUE_META = SINGLE_VALUE_M2FT.union(FT_SEMANTIC_META)


def _detect_metadata(f: Path) -> MetadataType:
    """Detects which kind of markdown metadata is present in markdown file (if any)
    Metadata should be present on the very first line. If there is no metadata
    marker on the first line, it is assumed that there is no metadata in the file.
    """
    metatype = MetadataType.NoMeta
    with f.open('r') as mdfile:
        firstline = mdfile.readline()
        if RE_YAMLMETA_BEGIN.match(firstline):
            metatype = MetadataType.YamlMeta
        elif RE_LINEMETA.match(firstline):
            metatype = MetadataType.LineMeta
    return metatype


def _read_yaml_metas(mdfile: TextIO, md_content: StringIO, is_root_readme: bool = False) -> Tuple[Dict[str, str], StringIO, int, str]:
    metas = {}
    # skip first line which should be the YAML data begin marker
    _ = mdfile.readline()
    yamldata = StringIO()
    buffer = yamldata
    end_marker = False
    h1_count = 0
    content_written = False
    in_code_block = False
    title = MISSING_TITLE
    for k, line in enumerate(mdfile.readlines()):
        if RE_YAMLMETA_END.match(line):
            metas.update(yaml.safe_load(yamldata.getvalue()))
            buffer = md_content
            end_marker = True
            continue
        try:
            h1_count, content_written, in_code_block = _write_md_content(buffer, content_written, h1_count, line,
                                                                         in_code_block, md_content == buffer)
        except ContentBeforeHeading as e:
            raise ContentBeforeHeading(f"Cannot process file: <{mdfile.name}>") from e
        title = _get_heading_title(line, is_root_readme) or title
    if not end_marker:
        raise MetadataError("No yaml metadata end marker found ??")
    return metas, md_content, h1_count, title


def _write_md_content(buffer: StringIO, is_content_written: bool, h1_count: int, line: str, is_code_block: bool,
                      is_content: bool = True) -> Tuple[int, bool, bool]:
    if RE_H1_MD.match(line) and not is_code_block:
        h1_count += 1
        if is_content_written and h1_count == 1:
            raise ContentBeforeHeading(f"Content before first heading unsupported")
    else:
        if line.strip() and is_content:
            is_content_written = True
        if RE_CODE_MD_BEGIN.match(line) and not is_code_block:
            is_code_block = True
        elif RE_CODE_MD_END.match(line):
            is_code_block = False
        buffer.write(line)
    return h1_count, is_content_written, is_code_block


def _read_legacy_metas(mdfile: TextIO, md_content: StringIO, is_root_readme: bool) -> Tuple[Dict[str, str], StringIO, int, str]:
    metas = {}
    h1_count = 0
    is_content_written = False
    is_code_block = False
    title = MISSING_TITLE
    for line in mdfile:
        m = RE_LINEMETA.match(line)
        if m:
            key, value = (m.group(1), m.group(2))
            # case insensitivity title compatibility
            if key.lower() == "title":
                metas["title"] = value
            else:
                # create a multi-valued meta, from list of repeated meta
                if key in metas:
                    if type(metas[key]) == list:
                        metas[key].append(value)
                    else:
                        metas[key] = [metas[key], value]
                else:
                    metas[key] = value
        else:
            h1_count, is_content_written, is_code_block = _write_md_content(md_content, is_content_written, h1_count,
                                                                            line, is_code_block)
            title = _get_heading_title(line, is_root_readme) or title
    return metas, md_content, h1_count, title


def _get_heading_title(line: str, is_root_readme: bool) -> Optional[str]:
    heading_match = RE_H1_MD.match(line)
    if is_root_readme:
        return COVER_PAGE_TITLE
    if heading_match:
        return heading_match.group(1)
    return None


def get_md_metas(f: Path, implicit_meta: bool = False, is_root_readme: bool = False,
                 dev_mode: bool = False) -> Tuple[Dict[str, str], str, str]:
    """Get markdown metadata from a file and verify other MD content is there too"""
    metatype = _detect_metadata(f)
    # at the end the md_content will contain the md data with the metadata stripped-out
    md_content = StringIO()
    h1_count = 0
    is_content_written = False
    is_code_block = False
    logger.debug(f"MD file={f}, MetadataType={metatype}")
    with f.open('r') as mdfile:
        if metatype == MetadataType.LineMeta:
            metas, md_content, h1_count, title = _read_legacy_metas(mdfile, md_content, is_root_readme)
        elif metatype == MetadataType.YamlMeta:
            metas, md_content, h1_count, title = _read_yaml_metas(mdfile, md_content, is_root_readme)
        elif metatype == MetadataType.NoMeta:
            # when no meta is present in file we should at least
            # handle H1 header as ft:title.
            metas = {}
            title = MISSING_TITLE
            for line in mdfile:
                h1_count, is_content_written, is_code_block = _write_md_content(md_content, is_content_written,
                                                                                h1_count, line, is_code_block)
                title = _get_heading_title(line, is_root_readme) or title

    if h1_count > 1:
        raise MetadataError(f'Several H1 in content is unsupported (in {f})')

    metas = _handle_implicit_and_legacy_metas(metas, f,
                                              metatype, implicit_meta)
    if FT_ORIGIN_ID_COMPAT in metas:
        logger.warning(f"Using {FT_ORIGIN_ID_COMPAT}' for origin Id is deprecated please use {FT_ORIGIN_ID} instead")
        metas[FT_ORIGIN_ID] = metas[FT_ORIGIN_ID_COMPAT]
        del metas[FT_ORIGIN_ID_COMPAT]
    metas = _check_multivalued_metas(metas, f)
    if SemanticMetadata.TITLE not in metas and title == MISSING_TITLE and not dev_mode:
        raise MD2FTError(f"No ft:title in {f}.")
    if is_root_readme:
        metas.pop(SemanticMetadata.TITLE, None)
        metas.pop(MD2FT_ATTACHMENT_DIR, None)
    return metas, md_content.getvalue(), title


def _handle_implicit_and_legacy_metas(metas: Dict[str, str],
                                      f: Path,
                                      metatype: MetadataType,
                                      implicit_meta: bool) -> Dict[str, str]:
    logger.debug(f"metatype={metatype}, metas={metas}")
    # Handle implicit meta and compatibility
    if not metas and implicit_meta:
        metas = {SemanticMetadata.TITLE: f.stem}
    # Handle meta compatibility format
    if SemanticMetadata.TITLE not in metas and "title" in metas:
        logger.warning("Using '[_metadata_:title]:-' for title is deprecated")
        logger.warning("Use '[_metadata_:ft:title]:- \"your title\"'")
        metas[SemanticMetadata.TITLE] = metas["title"]
        del metas["title"]
    if FT_ORIGIN_ID_COMPAT not in metas and "originID" in metas:
        logger.warning("Using '[_metadata_:originID]:-' for originID is deprecated")
        logger.warning("Use '[_metadata_:ft:originID]:- \"your originID\"'")
        metas[FT_ORIGIN_ID] = metas["originID"]
        del metas["originID"]
    return metas


def _check_multivalued_metas(metas: Dict[str, str], f) -> Dict[str, str]:
    # Check that ft semantic metadata are in the list of authorized meta
    # and that some meta are not multivalued
    for k, v in metas.items():
        if (type(v) == list):
            if len(v) == 0:
                raise MetadataError(f"meta {k} is an array with no value (in file {f})")
            elif len(v) == 1:
                # replace list with a single value
                metas[k] = v[0]
        logger.debug(f"Check meta {k} with value {v} (type={type(v)})")
        if k.startswith("ft:") and k not in FT_SEMANTIC_META:
            raise MetadataError(f"Fluid Topics Semantic meta {k} cannot be set (value = {v} in file {f})")
        if (k in SINGLE_VALUE_META) and (type(v) == list) and len(v) > 1:
            raise MetadataError(f"meta {k} cannot be multi-valued (current = {v} in file {f})")
    return metas
