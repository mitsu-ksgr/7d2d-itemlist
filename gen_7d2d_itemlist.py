#!/bin/python3
# coding: utf-8

import csv
import json
import os
import sys
import xml.etree.ElementTree as ET


DIR_PATH_ICON_IMG_DIR = "ItemIcons"
FILE_NAME_ITEMS_XML = "Config/items.xml"
FILE_NAME_LOCALIZATION_TXT = "Config/Localization.txt"


#-----------------------------------------------------------------------------
#   Utility Classes
#-----------------------------------------------------------------------------
class Localization:
    def __init__(self, file_path: str):
        self.src_path = file_path
        self.items = {}
        self.load()

    def load(self):
        self.items = {}
        with open(self.src_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # rename keys
                key = row["Key"]
                row["key"] = row.pop("Key")
                row["file"] = row.pop("File")
                row["type"] = row.pop("Type")
                row["used_in_main_menu"] = row.pop("UsedInMainMenu")
                row["no_translate"] = row.pop("NoTranslate")
                row["context"] = row.pop("Context / Alternate Text")

                # additional info
                row["is_desc"] = row["key"].endswith("Desc")

                self.items[row["key"]] = row

    def get(self, key):
        return self.items.get(key)

    def dump(self, key: str):
        dat = self.get(key)
        if dat is None:
            print(f"* {key} is invalid item key.")
            return

        print(f"* {key}")
        for k, v in dat.items():
            print(f"    - {k}: {v}")

    def dump_all(self):
        for key in self.items.keys():
            self.dump(key)


class ItemIconFileNameFinder:
    def __init__(self, icon_dir_path: str):
        self.icon_dir_path = icon_dir_path
        self.file_names = []
        self.load()

    def load(self):
        self.file_names = os.listdir(self.icon_dir_path)

    def find(self, key):
        k = f"{key}.png"
        if k in self.file_names:
            return k
        return None


def _read_prop(node, xpath, default = None):
    child = node.find(xpath)
    if child is None:
        return default
    return child.attrib["value"]

def _read_prop_as_list(node, xpath, default = []):
    child = node.find(xpath)
    if child is None:
        return default
    values = child.attrib["value"]
    return [v.strip() for v in values.split(",")]

class XMLItem:
    def __init__(self, root, node):
        self.key = None
        self.custom_icon = None
        self.extends_from = None
        self.tags = []
        self.unlocked_by = []
        self.parse(root, node)

    def parse(self, root, node):
        # Extends
        extends = node.find("./property[@name='Extends']")
        if extends is not None:
            extend_from = extends.attrib["value"]
            # TODO: support param1 attrib.
            #extend_params = extends.attrib["param1"]
            #if extend_params:
            #    extend_params = [v.strip() for v in extend_params.split(",")]

            src_node = root.find(f"item[@name='{extend_from}']")
            if src_node is not None:
                self.parse(root, src_node)
            self.extends_from = extend_from
        else:
            self.extends_from = None

        # Load params
        self.key = node.attrib["name"]
        self.tags = _read_prop_as_list(node, "./property[@name='Tags']", self.tags)
        self.custom_icon = _read_prop(node, "./property[@name='CustomIcon']", self.custom_icon)
        self.unlocked_by = _read_prop_as_list(node, "./property[@name='UnlockedBy']", self.unlocked_by)


class XMLItems:
    def __init__(sefl):
        self.items = []
        pass

    def parse(self, node):

        pass

class Item(object):
    def __init__(self, **kwargs):
        self.key = kwargs.get("key")
        self.icon_file_name = kwargs.get("icon_file_name")
        self.name_en = kwargs.get("name_en")
        self.name_ja = kwargs.get("name_ja")
        self.tags = kwargs.get("tags", [])
        self.unlocked_by = kwargs.get("unlocked_by", [])

        # Internal info
        self.extends_from = kwargs.get("extends_from")


    def to_dict(self):
        return {
            "key": self.key,
            "icon_file_name": self.icon_file_name,
            "name_en": self.name_en,
            "name_ja": self.name_ja,
            "tags": self.tags,
            "unlocked_by": self.unlocked_by,
        }


class ItemJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


#-----------------------------------------------------------------------------
#   Entrypoint
#-----------------------------------------------------------------------------
def load_items(data_dir_path: str):
    path_i18n_csv = f"{data_dir_path}/{FILE_NAME_LOCALIZATION_TXT}"
    path_icons_dir = f"{data_dir_path}/{DIR_PATH_ICON_IMG_DIR}"
    path_items_xml = f"{data_dir_path}/{FILE_NAME_ITEMS_XML}"

    try:
        i18n = Localization(path_i18n_csv)
        icon_finder = ItemIconFileNameFinder(path_icons_dir)
        xml_tree = ET.parse(path_items_xml)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    items = []
    root = xml_tree.getroot()
    for child in root:
        xi = XMLItem(root, child)
        loc = i18n.get(xi.key)
        icon_file_name = icon_finder.find(
            xi.custom_icon if xi.custom_icon else xi.key
        )
        items.append(Item(
            key = xi.key,
            icon_file_name = icon_file_name,
            name_en = loc.get("english") if loc else None,
            name_ja = loc.get("japanese") if loc else None,
            tags = xi.tags,
            unlocked_by = xi.unlocked_by,
            extends_from = xi.extends_from,
        ))
    return items


def dump_to_text(out_file, items):
    buf = []
    for item in items:
        buf.append(f"* {item.key}")
        buf.append(f"    Extend From     : {item.extends_from}")
        buf.append(f"    IconFileName    : {item.icon_file_name}")
        buf.append(f"    Name (en)       : {item.name_en}")
        buf.append(f"    Name (ja)       : {item.name_ja}")
        buf.append(f"    * Tags ({len(item.tags)})")
        if len(item.tags) == 0:
            buf.append("        - None")
        else:
            for tag in item.tags:
                buf.append(f"        - {tag}")
        buf.append(f"    * Unlocked By({len(item.unlocked_by)})")
        if len(item.unlocked_by) == 0:
            buf.append("        - None")
        else:
            for tag in item.unlocked_by:
                buf.append(f"        - {tag}")
    print("\n".join(buf), file=out_file)


def dump_to_json(out_file, items):
    print(
        json.dumps(items, cls=ItemJsonEncoder, indent=4, ensure_ascii=False),
        file=out_file)


def entrypoint(data_dir_path, out_format, out_path):
    items = load_items(data_dir_path)

    if out_path:
        out_file = open(out_path, 'w')
    else:
        out_file = sys.stdout

    try:
        if out_format == "json":
            dump_to_json(out_file, items)
        else:
            dump_to_text(out_file, items)
    finally:
        if out_file is not sys.stdout:
            out_file.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate 7daystodie item list.")
    parser.add_argument("data_dir_path", type=str,
        help="Path to 7daystodie/Data directory.")
    parser.add_argument("-f", "--format", type=str,
        choices=["text", "json"], default="text",
        help="Output format. text or json.")
    parser.add_argument("-o", "--output", type=str, metavar='OUTPUT_PATH',
        help="Output file path. if not specified, output to stdout.")
    args = parser.parse_args()

    data_dir_path = args.data_dir_path
    if data_dir_path.endswith('/'):
        data_dir_path = data_dir_path[:-1]

    entrypoint(data_dir_path, args.format, args.output)

