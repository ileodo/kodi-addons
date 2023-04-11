import os
from typing import List

import requests
import xbmc
import xbmcaddon
from bs4 import BeautifulSoup

from base_adapter import (
    SubtitleAdapterBase,
    SubtitleListItem,
    SubtitleDownloadedFile,
    SubtitleSearchInput,
)


class A4KAdapter(SubtitleAdapterBase):
    URL_BASE = "https://www.a4k.net"

    def __init__(self):
        super().__init__(xbmcaddon.Addon())
        self._session = requests.session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"
            }
        )

    @staticmethod
    def _map_language(language):
        lang_map = {
            "简体": ("简体", "zh"),
            "繁体": ("繁体", "zh"),
            "英文": ("英文", "en"),
            "双语": ("双语", "zh"),
        }
        return lang_map.get(language, "")

    def get_search_string(self, search_item: SubtitleSearchInput) -> str:
        if search_item.is_manual_search():
            return search_item.searchstring
        else:
            if len(search_item.tvshow_title()) > 0:
                return search_item.tvshow_title()
            else:
                return search_item.title()

    def search(self, item: SubtitleSearchInput) -> List[SubtitleListItem]:
        __LOG_CATEGORY__ = "SEARCH"

        search_term = self.get_search_string(item)
        self.log(__LOG_CATEGORY__, f"Searching term: {search_term}", level=xbmc.LOGINFO)

        url = f"{A4KAdapter.URL_BASE}/search?term={search_term}"
        http_response = self._session.get(url)

        http_body = http_response.content
        soup = BeautifulSoup(http_body, "html.parser")
        list_items = soup.find_all("li", class_="item")

        self.log("SEARCH", f"Found {len(list_items)} items")
        results = []

        for item in list_items:
            content_nodes = item.select(".content h3 a")
            if len(content_nodes) != 1:
                break
            content_node = content_nodes[0]

            # TODO process language
            lang_list = [
                A4KAdapter._map_language(x["data-content"])
                for x in list_items[0].find("div", class_="language").find_all("i")
            ]
            language_name, language_flag = lang_list[0]

            name = content_node.text.replace("字幕下载", "")
            file_ext = name.split(".")[-1]
            results.append(
                SubtitleListItem(
                    name=f"[{file_ext}]{name}",
                    item_id=content_node["href"],
                    time=item.find("div", class_="created").find("span").text,
                    language_code=language_flag,
                    language_name=language_name,
                    language_flag=language_flag,
                    rating=0,
                )
            )
        return results

    def download(self, item_id: str) -> SubtitleDownloadedFile:
        __LOG_CATEGORY__ = "DOWNLOAD"

        self.log(__LOG_CATEGORY__, f"Downloa url: {item_id}", level=xbmc.LOGINFO)

        http_response = self._session.get(f"{A4KAdapter.URL_BASE}{item_id}")
        http_body = http_response.content

        soup = BeautifulSoup(http_body, "html.parser")
        download_div = soup.find("div", class_="download")

        file_url = download_div.find("a", class_="green")["href"]
        file_response = self._session.get(f"{A4KAdapter.URL_BASE}{file_url}")
        return SubtitleDownloadedFile(
            file_name=os.path.basename(file_url),
            content_type=file_response.headers["Content-Type"],
            content_length=int(file_response.headers["Content-Length"]),
            content=file_response.content,
        )
