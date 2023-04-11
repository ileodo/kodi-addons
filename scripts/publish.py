#!/usr/bin/env python3
# *
# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

""" addons.xml generator """

from typing import List
import os
import sys
import hashlib

import argparse

from bs4 import BeautifulSoup


class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """

    def __init__(self, addons: List[str], xml_path: str, md5_path: str):
        # generate files
        self._generate_addons_file(addons, xml_path)
        self._generate_md5_file(xml_path, md5_path)
        # notify user
        print("Finished updating addons xml and md5 files")

    def _generate_addons_file(self, addons: List[str], xml_path: str):
        addon_soups = []

        for addon in sorted(addons):
            try:
                # skip any file or .svn folder or .git folder
                if not os.path.isdir(addon):
                    print(f"Could NOT find folder for addon: {addon}")
                    continue

                addon_path = os.path.join(addon, "addon.xml")
                if not os.path.exists(addon_path):
                    print(
                        f"Could NOT find addon.xml for addon: {addon}")
                    continue

                with open(addon_path, "r") as addon_xml:
                    addon_xml_cont = addon_xml.read()
                    soup = BeautifulSoup(addon_xml_cont, "xml")
                    addon_soups += soup.find_all("addon")


            except Exception as e:
                # missing or poorly formatted addon.xml
                print(f"Excluding {addon} for {e}")

        final_soup = BeautifulSoup("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <addons>
        </addons>
        """, "xml")
        for addon_node in addon_soups:
            final_soup.find("addons").append(addon_node)

        # save file
        self._save_file(final_soup.prettify().encode("utf-8"),
                        file=xml_path)
        self.remove_blanks_in_xml(xml_path)

    def _generate_md5_file(self, xml_path: str, md5_path: str):
        # create a new md5 hash
        m = hashlib.md5(open(xml_path, "r", encoding="UTF-8").read().encode(
            "UTF-8")).hexdigest()

        # save file
        self._save_file(m.encode("UTF-8"), file=md5_path)

    def _save_file(self, data: bytes, file: str):
        try:
            with open(file, "wb") as target_file:
                target_file.write(data)
        except Exception as e:
            # oops
            print(f"An error occurred saving {file} file!\n{e}")

    def remove_blanks_in_xml(self, file):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('addons', metavar='addon', type=str, nargs='+',
                        help='List of addons')
    parser.add_argument('-x', '--xml-path', type=str, default="addons.xml",
                        help='xml destination')
    parser.add_argument('-m', '--md5-path', type=str, default="addons.xml.md5",
                        help='md5 destination')
    args = parser.parse_args()

    Generator(args.addons, args.xml_path, args.md5_path)
