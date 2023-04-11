#!/usr/bin/env python3
# Based on https://github.com/taxigps/xbmc-addons-chinese/blob/master/release.py

""" plugin release tool"""

import os, zipfile, shutil
from bs4 import BeautifulSoup
import argparse

def cp(src, dst):
    if os.path.exists(src):
        shutil.copyfile(src, dst)

def remove_blanks_in_xml(file):
    from xml.dom import minidom
    from xml.dom.minidom import Node

    def remove_blanks(node):
        for x in node.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                remove_blanks(x)

    xml = minidom.parse(file)
    remove_blanks(xml)
    xml.normalize()
    with open(file, 'w') as result:
        result.write(xml.toprettyxml(indent=" " * 4))

def release(addon, version, destination_base):
    # Create dest folder
    dest = os.path.join(destination_base, addon)
    if not os.path.exists(dest):
        os.mkdir(dest)

    # zip repo
    zipname = os.path.join(destination_base, addon, f"{addon}-{version}.zip")
    f = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(addon):
        for filename in filenames:
            f.write(os.path.join(dirpath,filename))
    f.close()

    # copy icon
    cp(os.path.join(addon, "icon.png"), os.path.join(destination_base, addon, "icon.png"))
    # copy change log
    cp(os.path.join(addon, "changelog.txt"), os.path.join(destination_base, addon, f"changelog-{version}.txt"))

def get_version(addon):
    with open(f"{addon}/addon.xml", "r") as file_addon:
        addon_cont = file_addon.read()
    soup = BeautifulSoup(addon_cont, "xml")

    return soup.find("addon").attrs.get("version", "unknown")


def update_addon(addon):
    with open(f"{addon}/changelog", "r") as file_changelog:
        changelog_cont = file_changelog.read()

    with open(f"{addon}/addon.xml", "r") as file_addon:
        addon_cont = file_addon.read()

    soup = BeautifulSoup(addon_cont, "xml")
    extension_node = soup.find("extension", point="xbmc.addon.metadata")
    new_node = extension_node.find("news")
    if new_node is None:
        new_node = soup.new_tag("news")
        new_node.string = f"\n{changelog_cont}\n"
        extension_node.append(new_node)
    else:
        new_node.string = f"\n{changelog_cont}\n"

    with open(f"{addon}/addon.xml", "w") as file_addon:
        file_addon.write(soup.prettify())
    remove_blanks_in_xml(f"{addon}/addon.xml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('addons', metavar='addon', type=str, nargs='+',
                        help='List of addons')
    parser.add_argument('-u', '--update-change-log', action='store_true',
                        help='Update changelog in addon.xml')
    parser.add_argument('-d', '--dest', type=str, required=True,
                        help='release destination')
    args = parser.parse_args()

    if not os.path.exists(args.dest):
        os.mkdir(args.dest)

    for addon in args.addons:
        version = get_version(addon)
        if args.update_change_log:
            update_addon(addon)
        release(addon, version, args.dest)
