import json
import logging
import os
import xml.etree.ElementTree as ET

import xmltodict

from .coco import COCOFile
from .exceptions import FileError, ParsingError
from .voc import PascalVOCFile

logger = logging.getLogger("picsellia-annotations")


def read_coco_file(file_path: str) -> COCOFile:

    if not os.path.exists(file_path):
        raise FileError("{} was not found".format(file_path))

    logger.debug("Parsing file..")

    try:
        with open(file_path, "r") as f:
            content = json.load(f)
            cocofile = COCOFile(**content)
    except Exception as e:
        raise ParsingError(str(e))

    return cocofile


def write_coco_file(cocofile: COCOFile) -> str:
    try:
        return cocofile.json()
    except Exception as e:  # pragma: no cover
        raise ParsingError(str(e))


def read_pascal_voc_file(
    file_path: str, check_polygon_consistency: bool = False
) -> PascalVOCFile:

    if not os.path.exists(file_path):
        raise FileError("{} was not found".format(file_path))

    logger.debug("Parsing file {}".format(file_path))

    try:
        tree = ET.parse(file_path)
        xmlstr = ET.tostring(tree.getroot(), encoding="utf-8", method="xml")
        content = xmltodict.parse(xmlstr)
        vocfile = PascalVOCFile(**content)

        # This will raises an error if polygon is not consistent
        if check_polygon_consistency:
            vocfile.annotation.object.polygon_to_list_coordinates()

    except Exception as e:
        raise ParsingError(str(e))

    return vocfile


def write_pascal_voc_file(
    voc: PascalVOCFile, output=None, pretty: bool = True, full_document: bool = False
) -> str:
    try:
        xmlstr = xmltodict.unparse(
            voc.dict(), output=output, full_document=full_document, pretty=pretty
        )
    except Exception as e:  # pragma: no cover
        raise ParsingError(str(e))

    return xmlstr
