#!/usr/bin/env python3

import glob
import json
import logging
from pathlib import Path
from pprint import pprint
from tempfile import TemporaryFile, NamedTemporaryFile
from typing import List, Dict, Union
from zipfile import ZipFile, ZIP_DEFLATED

import click
import click_log

from fluidtopics.connector.model.metadata import SemanticMetadata
from fluidtopics.markdown import __version__ as md2ft_version
from fluidtopics.markdown.errors import MD2FTError
from fluidtopics.markdown.ftmap import FTMap
from fluidtopics.markdown.ftsession import FTSession
from fluidtopics.markdown.metadata import FT_ORIGIN_ID, FT_LANG, get_md_metas, MISSING_TITLE, MD2FT_MEDIA_DIR, MD2FT_AUDIENCE, MD2FT_ATTACHMENT_DIR
from fluidtopics.markdown.attachment import DEFAULT_ATTACHMENT_DIR, DEFAULT_MEDIA_DIR, collect_attachments

logger = logging.getLogger("fluidtopics.markdown")
click_log.basic_config(logger)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def prune_empty_dir(content: Dict[str, dict]) -> Dict[str, dict]:
    """Remove empty dir (i.e. content node with child) which doesn't have any non-empty child"""
    # end of recursion 1: node is empty
    if not content:
        return {}

    to_delete = []
    for k, node in content.items():
        if "childs" in node:
            new_childs = prune_empty_dir(node["childs"])
            # node is a directory without content and no child
            if FT_ORIGIN_ID in node["value"] and not new_childs:
                to_delete.append(k)
    for k in to_delete:
        del content[k]
    return content


def dir_content(
        curdir: Path,
        relto: Path,
        skip: List[Path],
        meta_include_list: List[str],
        implicit_meta: bool = False,
        dev_mode: bool = False,
) -> Dict[str, dict]:
    """Recursively Collect the directory content starting at curdir"""
    content = {}
    # Recursively loop over the curdir + sort dir using filename
    # we put README file first in any case in order to ensure proprer handling
    # of potential content in READMEs
    for file in sorted(curdir.iterdir(), key=lambda f: "    README.md" if f.name == "README.md" else f.name):
        if file.relative_to(relto) in skip:
            logger.debug(f"Skipping {file.as_posix()} as told.")
            continue
        relf_posix = file.relative_to(relto).as_posix()
        f_posix = file.as_posix()
        if file.is_dir():
            if file.name.startswith(".") or file.name.startswith("__"):
                continue
            dirdesc = file / "README.md"
            if dirdesc.exists():
                dirmetas, with_content, heading_title = get_md_metas(
                    dirdesc,
                    dev_mode=dev_mode
                )  # We handle default title for directory differently...
                logger.debug(f"Found directory description in {dirdesc}")
                skip.append(dirdesc.relative_to(relto))
                if meta_include_list:
                    audience = dirmetas.get(MD2FT_AUDIENCE, None)
                    if audience is None:
                        logger.warning(
                            f"Skipping {file.relative_to(relto).as_posix()} no audience given as meta while include_list = {meta_include_list}"
                        )
                        continue
                    elif audience not in meta_include_list:
                        logger.warning(
                            f"Skipping {file.relative_to(relto).as_posix()} as audience={audience} not in include_list = {meta_include_list}"
                        )
                        continue
                # If README with metas + content => create href
                if with_content:
                    content[relf_posix] = {
                        "value": {
                            "href": dirdesc.relative_to(relto).as_posix(),
                            SemanticMetadata.TITLE: heading_title,
                            "metas": dirmetas,
                        },
                        "childs": dir_content(
                            file,
                            relto,
                            skip,
                            meta_include_list,
                            implicit_meta,
                            dev_mode,
                        ),
                    }
                # if README with metas only => create ft:originID (ToC entry only)
                else:
                    content[relf_posix] = {
                        "value": {
                            FT_ORIGIN_ID: f_posix,
                            SemanticMetadata.TITLE: heading_title,
                            "metas": dirmetas,
                        },
                        "childs": dir_content(
                            file,
                            relto,
                            skip,
                            meta_include_list,
                            implicit_meta,
                            dev_mode,
                        ),
                    }
            # if no README => create ft:originID from dir title (ToC entry only)
            else:
                if not implicit_meta:
                    raise MD2FTError(
                        f'No README.md in directory {file} while in explicit mode, ' 
                         'Add README.md to directory or '
                         'add "media_dir" value to ROOT README.md if directory contains images'
                    )
                else:
                    # provide default value for directory description in implicit mode
                    content[relf_posix] = {
                        "value": {
                            FT_ORIGIN_ID: f_posix,
                            SemanticMetadata.TITLE: file.name,
                            "metas": {},
                        },
                        "childs": dir_content(
                            file,
                            relto,
                            skip,
                            meta_include_list,
                            implicit_meta,
                            dev_mode,
                        ),
                    }

        elif file.is_file() and file.match("*.md"):
            metas, topic_content, heading_title = get_md_metas(file, implicit_meta, str(file.relative_to(relto)) == 'README.md',
                                                   dev_mode=dev_mode)
            audience = metas.get(MD2FT_AUDIENCE, None)
            if meta_include_list:
                if audience is None:
                    logger.warning(
                        f"Skipping {file.relative_to(relto).as_posix()} no audience given as meta while include_list = {meta_include_list}"
                    )
                    continue
                elif audience not in meta_include_list:
                    logger.warning(
                        f"Skipping {file.relative_to(relto).as_posix()} as audience={audience} not in include_list = {meta_include_list}"
                    )
                    continue
            if topic_content.strip() or relf_posix != 'README.md':
                content[relf_posix] = {
                    "value": {
                        "href": relf_posix,
                        SemanticMetadata.TITLE: heading_title,
                        "metas": metas,
                    }
                }
    return content


def _create_zip_file(output: str, pinput: Path, image_dir: str, ftmap: FTMap, collected_files: List[Path],
                     dev_mode: bool):
    attached_files = [attachment["filePath"] for attachment in ftmap.attachments]
    logger.debug(f"Attached files: {attached_files}")
    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as archive:
        # NB: we need to use glob.glob and not pathlib.Path.rglob
        #     because of: https://bugs.python.org/issue33428
        #     see also: https://stackoverflow.com/questions/46529760/getting-glob-to-follow-symlinks-in-python
        for fn in glob.glob(f"{str(pinput)}/**/*", recursive=True):
            f = Path(fn)
            if f.match("*.ftmap"):
                continue
            if (
                f.is_dir()
                or ((pinput / Path(image_dir)) in f.parents)
                or (f.relative_to(pinput).as_posix() in attached_files)
            ):
                archive.write(f, arcname=f.relative_to(pinput))
            elif f.is_file() and f.suffix.lower() in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".svg",
            ]:
                logger.debug(f"f={f}, arcname={f.relative_to(pinput)}")
                archive.write(f, arcname=f.relative_to(pinput))
            elif f.relative_to(pinput) in collected_files:
                # get MD content with stripped-out metadata
                _, md_content, _ = get_md_metas(f, dev_mode=dev_mode)
                if md_content == '':
                    logger.info(f'{f.relative_to(pinput)} has no content, it will be ignored')
                    ftmap.remove_node(f.relative_to(pinput).name)
                    continue
                archive.writestr(str(f.relative_to(pinput)), md_content)
            else:
                logger.debug(f"{f.relative_to(pinput)} not collected in archive.")

        archive.writestr("generated.ftmap", data=ftmap.to_string())


def do_collect(
        input: str,
        output: str,
        included_audiences: List[str],
        implicit_meta: bool,
        dev_mode: bool = False,
):
    """Collect markdown files and create FT Archive with a book FT Map
    built from the metadata found in the markdown files (unless implicit_meta is True)
    The created archive may then be uploaded to FT portal using `upload`.
    """
    input_path = Path(input)
    root_readme = list(input_path.glob("README.md"))
    metas = None
    root_readme_title = MISSING_TITLE
    # We always collect metas from root README is there is some
    if root_readme:
        root_readme = root_readme[0]
        metas, root_content, root_readme_title = get_md_metas(root_readme, dev_mode=dev_mode)
    if implicit_meta:
        logger.debug("Implicit meta MODE")
        implicit_metas_values = {
            # if implicit meta is set to True, build the title from pinput dir name
            MD2FT_MEDIA_DIR: DEFAULT_MEDIA_DIR,
            SemanticMetadata.TITLE: f"{input_path.name}",
            FT_ORIGIN_ID: input,
            "Category": "Technical Notes",
            MD2FT_AUDIENCE: "internal",
        }
        # Replace provided metas value if any
        if metas:
            implicit_metas_values.update(metas)
        metas = implicit_metas_values

    if metas is None and not implicit_meta:
        raise MD2FTError(f"No README.md found in {input_path}")

    logger.debug(f"root metas = {metas}")
    # Get media_dir value or use default one (images/)
    image_dir = metas.get(MD2FT_MEDIA_DIR, DEFAULT_MEDIA_DIR)
    skipped = [Path(image_dir)]

    attachment_dir = Path(metas.get("attachment_dir", DEFAULT_ATTACHMENT_DIR))
    map_attachments = collect_attachments(input_path, attachment_dir)
    if map_attachments:
        skipped.append(attachment_dir)

    # skip root README iff there is NO content in it
    # and we are in not implicit mode
    if not implicit_meta and not root_content:
        skipped.append(root_readme.relative_to(input_path))
    # Recursively collect md files beginning at pinput
    collected = dir_content(
        input_path,
        input_path,
        skipped,
        meta_include_list=included_audiences,
        implicit_meta=implicit_meta,
        dev_mode=dev_mode,
    )
    # Clean up empty dirs (i.e. which do not contain md files)
    collected = prune_empty_dir(collected)
    logger.debug(f"collected= {collected}")
    if SemanticMetadata.TITLE not in metas and root_readme_title == MISSING_TITLE:
        raise MD2FTError(f"No ft:title in {root_readme}.")
    if FT_ORIGIN_ID not in metas:
        raise MD2FTError(f"No ft:originID in {root_readme}.")
    # Init FTMAP with mandatory prop: ft:title, ft:originID
    ftmap = FTMap(
        title=root_readme_title,
        origin_id=metas[FT_ORIGIN_ID],
        editorial_type=metas.get(SemanticMetadata.EDITORIAL_TYPE, "book"),
        lang=metas.get(FT_LANG, "en-US"),
    )
    if "metas" in metas:
        ft_metas = json.loads(metas["metas"].replace("'", '"'))
        ft_metas = {k: v["value"] for k, v in ft_metas.items()}
        logger.warning("Using '[_metadata_:metas]:-' for metadata is deprecated")
        logger.warning("Use '[_metadata_:key]:- \"value\"' for each metadata")
    else:
        ft_metas = metas
    logger.debug(f"FT metas = {ft_metas}")
    ftmap.add_metas(ftmap.root, ft_metas)
    ftmap.add_attachments(map_attachments)
    # Build FTMAP ToC with collected items + return files list to be zipped
    collected_files = ftmap.populate_toc(ftmap.get_toptoc(), None, collected.values())
    if len(collected_files) == 0:
        raise MD2FTError(f"0 collected file, check your input ({input}) directory and/or --include rules.")
    logger.info(f"Collected {len(collected_files)} markdown files in FTMap.")
    logger.debug(f"FTMap collected_files= {collected_files}")
    _create_zip_file(output, input_path, image_dir, ftmap, collected_files, dev_mode=dev_mode)


def do_publish(
        zip: Path,
        ft_session: FTSession,
        source_id: str,
        dry_run: bool,
):
    """Upload and publish an FT Archive to an FT portal."""

    if type(zip) == str:
        zipfile = {"file": ("md2ft_" + Path(zip).name, Path(zip).open("rb"))}
    else:
        zipfile = {"file": ("md2ft_" + Path(zip.name).name, zip)}

    if dry_run:
        logger.info(f"DRY RUN: {zipfile['file'][0]} file NOT published.")
        return

    answer = ft_session.post(f"/api/admin/khub/sources/{source_id}/upload",
                             files=zipfile,
                             json_result=False,
                             check_status=False)
    if answer.ok:
        logger.info(f"{zipfile['file'][0]} file published on {ft_session.portal_base_url}.")
        pprint(answer.json())
    elif answer.status_code == 404:
        raise MD2FTError(f"Error while publishing <{zipfile['file'][0]}> on <{ft_session.portal_base_url}>, "
                         f"{answer.json()['message']} (for url={answer.url})")
    else:
        raise MD2FTError(f"Error while publishing <{zipfile['file'][0]}> on <{ft_session.portal_base_url}>,"
                         f"source: <{source_id}>, status: <{answer.status_code}>, url: {answer.url})")


def _get_meta_values(key: str, metadatas: List[dict], first_value_only: bool):
    "Extract a meta FT API json"
    meta = next((keys for keys in metadatas if keys["key"] == key), None)
    if meta is not None:
        if first_value_only:
            return meta["values"][0]
        else:
            return meta["values"]
    else:
        if first_value_only:
            return None
        else:
            return []


def do_unpublish(
        ft_session: FTSession,
        source_id: str,
        dry_run: bool,
        do_it: bool,
        select: str,
):
    """
    Delete selected publications by :
    - lastEdtion : the old version of the publications (older than the last publish)
    - title : delete the publication with the corresponding title
    """
    if not dry_run:

        # Get all the maps from md2ft source
        list_maps_json = ft_session.get(f"/api/admin/khub/publications?ft:sourceId={source_id}")

        # Exit if no publication or source does not exist
        if list_maps_json["count"] == 0:
            logger.info(
                f"No publications in this source_id or the <{source_id}> source doesn't exist"
            )
            return

        # Prepare documents dictionary for the specified source id
        documents = dict()
        for map in list_maps_json["items"]:
            documents[map["id"]] = map["metadata"]

        selection = select.split("=")
        metaname = selection[0]
        if len(selection) > 1:
            metavalue = selection[1]
        else:
            metavalue = None

        logger.debug(
            f"Selecting documents with metaname={metaname} and metavalue={metavalue}..."
        )
        if metaname == "ft:lastEdition":
            # Get the maxDate (ie the last date of publish)
            latestDates = [
                _get_meta_values(metaname, metas, True) for metas in documents.values()
            ]
            logger.debug(f"latest dates are: {latestDates}")
            latestDate = max(latestDates)
            logger.debug(f"latest date is: {latestDate}")
            # Remove the newest publication to have a dict of publication to delete
            selected_documents = {
                key: metas
                for key, metas in documents.items()
                if _get_meta_values(metaname, metas, True) != latestDate
            }
        else:
            # Filter the map to only delete documents with given metavalue for metaname
            selected_documents = {
                key: metas
                for key, metas in documents.items()
                if metavalue in _get_meta_values(metaname, metas, False)
            }

        if selected_documents:
            # Iter on each publication to delete
            for id_to_delete, metas in selected_documents.items():
                # Delete the publication if enable
                if do_it:
                    answer = ft_session.delete(f"/api/admin/khub/maps/{id_to_delete}")
                    logger.info(
                        f" ID MAP {id_to_delete} deleted on {ft_session.portal_base_url}."
                    )
                    pprint(answer)
                else:
                    logger.info(
                        f"Would delete document id={id_to_delete} (whose metas={metas}) on {ft_session.portal_base_url}."
                    )
            if not do_it:
                logger.info(
                    "If you want to delete the previous publications do add --do-it parameter"
                )
        else:
            logger.info(
                f"No publications selected with <<{select}>> from source_id : {source_id} on portal {ft_session.portal_base_url}"
            )
    else:
        logger.info(
            f"DRY RUN: No publications deleted from source_id : {source_id} on portal."
        )


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(md2ft_version)
@click_log.simple_verbosity_option(logger, default="INFO", show_default=True)
def cli():
    pass


collect_opts = [
    click.argument(
        "input",
        nargs=1,
        required=True,
        metavar="<documentation_root_dir>",
        type=click.Path(file_okay=False, dir_okay=True, readable=True),
    ),
    click.option(
        "--include",
        "included_audiences",
        metavar="<audience tag>",
        multiple=True,
        required=False,
        help="Only the Markdown file(s) whose 'audience' metadata value is listed here will be collected.",
    ),
    click.option(
        "--implicit-meta",
        is_flag=True,
        default=False,
        show_default=True,
        help="Do not require metadata in Markdown file.",
    ),
    click.option(
        "--dev-mode",
        is_flag=True,
        default=False,
        show_default=True,
        help="Ignore files without a meta ft:title or a # first section title.",
    ),
]

publish_opts = [
    click.argument(
        "portal_base_url",
        metavar="<FT_portal_base_url>",
        required=True,
        type=click.STRING,
    ),
    click.option(
        "-a",
        "--api-key",
        type=click.STRING,
        metavar="<apikey>",
        help="The FT API Key",
        envvar='MD2FT_API_KEY',
        show_envvar=True,
    ),
    click.option(
        "-u",
        "--user",
        type=click.STRING,
        metavar="<user>",
        help="The FT user",
        envvar='MD2FT_USER',
        show_envvar=True,
    ),
    click.option(
        "-p",
        "--passwd",
        type=click.STRING,
        metavar="<password>",
        help="The FT password",
        envvar=['MD2FT_PASSWD', 'MD2FT_PASSWORD'],
        show_envvar=True,
    ),
    click.option(
        "-s",
        "--source-id",
        type=click.STRING,
        default="ftml",
        show_default=True,
        metavar="<source_id>",
        help="The FT source ID",
    ),
    click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        show_default=True,
        help="Do all steps besides actual push to FT portal.",
    ),
]


def verify_credentials(portal_base_url: str, creds: dict, dry_run: bool) -> Union[FTSession, None]:
    if dry_run:
        logger.info(f"DRY RUN authentication on {portal_base_url}")
        return None
    ft_session = FTSession(portal_base_url)
    if creds.get("api_key") is not None:
        logger.info("Using API Key credentials")
        ft_session.set_api_key(creds.get("api_key"))
        return ft_session
    if creds.get("user") is not None and creds.get("password") is not None:
        logger.info("Using user/passwd credentials")
        ft_session.login(creds.get("user"), creds.get("password"))
        return ft_session
    raise click.UsageError("You must specify either an API Key (--api-key) or user **and** passwd (--user/--passwd)")


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


@cli.command("collect")
@add_options(collect_opts)
@click.option(
    "-o",
    "--output",
    "output",
    metavar="<archive_file>",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="output path of the FT Archive to be created",
    show_default=True,
    default="ftml_content.zip",
)
def collect(
        input: str,
        output: str,
        included_audiences: List[str],
        implicit_meta: bool,
        dev_mode: bool,
):
    """Collect documentation and create an FT Archive based on the metadata found in
    the Markdown files (unless implicit_meta is set as True).
    The archive may then be published to a Fluid Topics portal using the `publish` command.
    """
    do_collect(input, output, included_audiences, implicit_meta, dev_mode)
    logger.info(f"Written FT Archive in: {output}.")
    logger.info(f"You can push the archive to FT portal with:")
    logger.info(f"  md2ft publish {output} <ft_portal_url>")


@cli.command("collect_and_publish")
@add_options(collect_opts)
@add_options(publish_opts)
def collect_and_publish(
        input: str,
        included_audiences: List[str],
        implicit_meta: bool,
        dev_mode: bool,
        portal_base_url: str,
        api_key: str,
        user: str,
        passwd: str,
        source_id: str,
        dry_run: bool,
):
    """Collect upload and publish documentation to an FT portal."""
    session = verify_credentials(portal_base_url, {"api_key": api_key, "user": user, "password": passwd}, dry_run)
    with NamedTemporaryFile(mode="r+b", suffix=".zip") as tempzip:
        logger.debug(f"tempzip={tempzip.name}")
        do_collect(input, tempzip, included_audiences, implicit_meta)
        # rewind the file for next read
        tempzip.seek(0)
        do_publish(tempzip, session, source_id, dry_run)


@cli.command("publish")
@click.argument(
    "zip",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@add_options(publish_opts)
def publish(
        zip: Path,
        portal_base_url: str,
        api_key: str,
        user: str,
        passwd: str,
        source_id: str,
        dry_run: bool,
):
    """Upload and publish an FT Archive to an FT portal."""
    session = verify_credentials(portal_base_url, {"api_key": api_key, "user": user, "password": passwd}, dry_run)
    do_publish(zip, session, source_id, dry_run)


@cli.command("unpublish")
@add_options(publish_opts)
@click.option(
    "--do-it",
    is_flag=True,
    default=False,
    show_default=True,
    help="Confirm the unpublish of all documents, otherwise it just show them",
)
@click.option(
    "--select",
    metavar="<metaname>[=<metavalue>]",
    default="ft:lastEdition",
    show_default=True,
    help="""Unpublish selected documents:

    - ft:lastEdition : Delete all publications older than the latest ones from an FT portal (from last md2ft publish)\n
    - metaname=<metavalue> : Delete publications with the given <metavalue> for <metaname>
    """,
)
def delete_book(
        portal_base_url: str,
        api_key: str,
        user: str,
        passwd: str,
        source_id: str,
        dry_run: bool,
        do_it: bool,
        select: str,
):
    """Delete selected publications from an FT portal.

    The default selection is using ft:lastEdition metadata.
    """
    session = verify_credentials(portal_base_url, {"api_key": api_key, "user": user, "password": passwd}, dry_run)
    do_unpublish(session, source_id, dry_run, do_it, select)


if __name__ == "__main__":
    cli()
