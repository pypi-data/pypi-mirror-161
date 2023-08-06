from pathlib import Path
from fluidtopics.markdown.metadata import FT_ORIGIN_ID_COMPAT, FT_ORIGIN_ID
from typing import List, Optional, Iterable, Dict

from fluidtopics.connector import EditorialType
from lxml import etree

from fluidtopics.markdown.errors import MD2FTError

FT_MAP_TMPL = """<ft:map xmlns:ft="http://ref.fluidtopics.com/v3/ft#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ftmap.xsd">
    <ft:toc>
    </ft:toc>
</ft:map>
"""

ftns = "{http://ref.fluidtopics.com/v3/ft#}"


class FTMap:
    """Object representing a Fluitopics Map.
    An FT map governs the way the ToC of the various topics is setup by Fluidtopics.
    See: https://doc.antidot.net/r/3.9/Upload-FTML-Content-to-Fluid-Topics/Configure-FTML-Content
    """

    def __init__(self, title: str, origin_id: str,
                 editorial_type: str = EditorialType.BOOK.value, lang: str = "en-US"):
        self.title = title
        self.origin_id = origin_id
        self.editorial_type = editorial_type
        self.lang = lang
        self.attachments = []
        self.root = etree.XML(FT_MAP_TMPL)
        self.root.set(f"{ftns}lang", self.lang)
        self.root.set(f"{ftns}title", self.title)
        self.root.set(f"{ftns}originID", self.origin_id)
        self.root.set(f"{ftns}editorialType", self.editorial_type)

    def add_metas(
            self,
            toc_node: etree.Element,
            metas: Dict[str, dict],
            excluded_metas: List = None
    ) -> None:
        """Add a meta in <ft:metas> for the specified toc node"""
        if excluded_metas is None:
            excluded_metas = []
        metas_node = etree.SubElement(toc_node, f"{ftns}metas", nsmap=self.root.nsmap)
        for meta_name, meta_value in metas.items():
            if meta_name in excluded_metas:
                continue
            # Handle multi-valued meta
            if type(meta_value) == list:
                for value in meta_value:
                    attributes = {"key": meta_name}
                    sube = etree.SubElement(metas_node, f"{ftns}meta", attrib=attributes, nsmap=self.root.nsmap)
                    sube.text = str(value)
            else:
                attributes = {"key": meta_name}
                sube = etree.SubElement(metas_node, f"{ftns}meta", attrib=attributes, nsmap=self.root.nsmap)
                sube.text = str(meta_value)

    def add_attachments(self, attachments: List[dict]):
        """Add a map attachment to the publication
        see: https://doc.fluidtopics.com/r/Manage-Map-Attachments-in-Fluid-Topics/Manage-Map-Attachments/Manage-Map-Attachments-Synchronously/Manage-Map-Attachments-When-Uploading-FTML-Content/Upload-an-Ftmap-with-an-Attachment
        """
        if not attachments:
            return
        map_attachments_node = etree.SubElement(self.root, f"{ftns}attachments", nsmap=self.root.nsmap)
        self.attachments = attachments
        for attachment in self.attachments:
            suba = etree.SubElement(map_attachments_node, f"{ftns}attachment", nsmap=self.root.nsmap)
            for attachment_key, attachment_value in attachment.items():
                subae = etree.SubElement(suba, f"{ftns}{attachment_key}", nsmap=self.root.nsmap)
                subae.text = attachment_value

    def get_toptoc(self) -> etree.Element:
        return self.root.xpath("//ft:toc", namespaces=self.root.nsmap)[0]

    def remove_node(self, href_file: str):
        toc = self.get_toptoc()
        child = toc.xpath("//ft:node[@href = $ref]", ref=href_file, namespaces=self.root.nsmap)
        if child:
            child = child[0]
            toc.remove(child)
            if not toc.getchildren():
                raise MD2FTError(f"Cannot publish files, content would be empty")

    def populate_toc(
            self, tocnode: etree.Element,
            current: Optional[etree.Element],
            childs: Iterable[etree.Element]
    ) -> List[Path]:
        """Add a node and its child to the ToC"""
        collected_files = []
        if current is not None:
            attributes = {}
            if current.get("ft:title", None) is not None:
                attributes[f"{ftns}title"] = current.get("ft:title")
            if current.get(FT_ORIGIN_ID, None) is not None:
                attributes[f"{ftns}originID"] = current.get(FT_ORIGIN_ID)
            else:
                attributes["href"] = current.get("href")
                # FT cannot authorize automatic topic splitting for toc node with childs
                # see: https://doc.antidot.net/r/3.9/Upload-FTML-Content-to-Fluid-Topics/type
                if not childs:
                    attributes["type"] = "topics"
                collected_files.append(Path(attributes["href"]))

            tocnewnode = etree.SubElement(tocnode, f"{ftns}node", attrib=attributes, nsmap=self.root.nsmap)
            self.add_metas(tocnewnode, current["metas"])
        else:
            tocnewnode = tocnode
        for c in childs:
            nextchilds = c.get("childs", [])
            if nextchilds:
                nextchilds = nextchilds.values()
            collected_files.extend(self.populate_toc(tocnewnode, c['value'], nextchilds))
        return collected_files

    def to_string(self) -> str:
        return etree.tostring(self.root,
                              pretty_print=True,
                              encoding='utf-8',
                              xml_declaration=True)
