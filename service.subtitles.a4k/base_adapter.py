import os
import sys
import datetime
import urllib

from typing import List, Optional, ClassVar, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs


EXTS: Tuple = (".srt", ".sub", ".smi", ".ssa", ".ass", ".sup")
SUPPORTED_ARCHIVE_EXTS: Tuple = (
    ".zip",
    ".7z",
    ".tar",
    ".bz2",
    ".rar",
    ".gz",
    ".xz",
    ".iso",
    ".tgz",
    ".tbz2",
    ".cbr",
)
ACCESSIBLE_ARCHIVE_EXTS: Tuple = (".zip", ".rar")


@dataclass
class SubtitleSearchInput:
    languages: List[str]
    preferredlanguage: List[str]
    searchstring: Optional[str]

    def is_manual_search(self):
        return self.searchstring is not None

    def get_info(self, info_id):
        return xbmc.getInfoLabel(info_id)

    def year(self):
        return self.get_info("VideoPlayer.Year")

    def season(self):
        return self.get_info("VideoPlayer.Season")

    def episode(self):
        return self.get_info("VideoPlayer.Episode")

    def tvshow_title(self):
        return self.get_info("VideoPlayer.TVShowTitle")

    def original_title(self):
        return self.get_info("VideoPlayer.OriginalTitle")

    def title(self):
        return self.get_info("VideoPlayer.Title")


@dataclass
class SubtitleListItem:
    name: str
    item_id: str
    time: str
    language_code: str
    language_name: str
    language_flag: str
    rating: int

    MAX_RATING: ClassVar[int] = 5

    def getXmbcListItem(self):
        listitem = xbmcgui.ListItem(label=self.language_name, label2=self.name)
        listitem.setArt(
            {
                "icon": str(min(self.rating, self.MAX_RATING)),
                "thumb": self.language_flag,
            }
        )
        return listitem


@dataclass
class SubtitleDownloadedFile:
    file_name: str
    content_type: str
    content_length: int
    content: bytes

    MIN_SIZE: ClassVar[int] = 10

    def is_valid(self) -> bool:
        """
        check if downloaded file is valid based on extension and size
        :return:
        """
        return (
            self.is_subtitle() or self.is_supported_archive_exts()
        ) and self.content_length > self.MIN_SIZE

    def is_subtitle(self) -> bool:
        """
        check if downloaded file is a subtitle file
        :return:
        """
        return self.extension() in EXTS

    def is_supported_archive_exts(self):
        """
        check if downloaded file is a archive which is supported
        :return:
        """
        return self.extension() in SUPPORTED_ARCHIVE_EXTS

    def extension(self) -> str:
        """
        get the extension of the file, including dot.
        :return:
        """
        _, file_extension = os.path.splitext(self.file_name)
        return file_extension


class SubtitleAdapterBase(ABC):
    def __init__(self, addon: xbmcaddon.Addon):
        """
        Construct a SubtitleAdapterBase
        :param addon: xmbcaddon, provide meta data of the addon
        """
        __LOG_CATEGORY__ = "__INIT__"

        self._addon = addon
        self._addon_id = self._addon.getAddonInfo("id")
        self._addon_name = self._addon.getAddonInfo("name")
        self._addon_profile = xbmcvfs.translatePath(self._addon.getAddonInfo("profile"))
        self._addon_temp = xbmcvfs.translatePath(
            os.path.join(self._addon_profile, "temp")
        )

    def log(self, category, msg, level=xbmc.LOGDEBUG):
        xbmc.log(f"[{self._addon_name}]::{category} - {msg}", level=level)

    @abstractmethod
    def search(self, item: SubtitleSearchInput) -> List[SubtitleListItem]:
        """

        :param item: SubtitleSearchIterm
        :return: List search result
        """
        pass

    @abstractmethod
    def download(self, item_id: str) -> SubtitleDownloadedFile:
        """

        :param item_id: id of the item to be downloaded
        :return:
        """
        pass

    def search_handler(self, handle: int, item: SubtitleSearchInput):
        """
        UI Handler for Search action
        :param handle: a xmbc handle
        :param item: SearchInput
        :return:
        """

        __LOG_CATEGORY__ = "SEARCH_HANDLER"

        subtitles_list = self.search(item)
        for it in subtitles_list:
            listitem = it.getXmbcListItem()
            paramstring = urllib.parse.urlencode(
                {"action": "download", "item_id": it.item_id}
            )
            url = f"plugin://{self._addon_id}/?{paramstring}"
            xbmcplugin.addDirectoryItem(
                handle=handle, url=url, listitem=listitem, isFolder=False
            )
        xbmcplugin.endOfDirectory(handle)

    def download_handler(self, handle: int, item_id: str):
        """
        UI Handler for Download action
        :param handle: a xmbc handle
        :param item_id: id for the download item
        :return:
        """
        __LOG_CATEGORY__ = "DOWNLOAD_HANDLER"

        subtitle_file = self.download(item_id)
        subtitle_path = self.load(subtitle_file, self._addon_temp)
        if subtitle_path is None:
            self.log(
                __LOG_CATEGORY__,
                f"Failed to download file with item_id: {item_id}",
                level=xbmc.LOGERROR,
            )

        listitem = xbmcgui.ListItem(label=subtitle_path)
        xbmcplugin.addDirectoryItem(
            handle=handle, url=subtitle_path, listitem=listitem, isFolder=False
        )

        xbmcplugin.endOfDirectory(handle)

    def load(self, file: SubtitleDownloadedFile, tmp_path: str) -> Optional[str]:
        __LOG_CATEGORY__ = "LOAD"

        if not file.is_valid():
            self.log(__LOG_CATEGORY__, f"Invalid file: {file}", level=xbmc.LOGERROR)
            return None

        store_path = self.save_file(file, tmp_path)

        if file.is_subtitle():
            self.log(__LOG_CATEGORY__, f"single sub file: {store_path}")
            return store_path

        if file.is_supported_archive_exts():
            # libarchive requires the access to the file, so sleep a while to ensure the file.
            xbmc.sleep(500)
            list_sub_files = self.unpack(store_path)
            self.log(
                __LOG_CATEGORY__, f"list of sub file in archive file: {list_sub_files}"
            )

            if len(list_sub_files) == 1:
                return list_sub_files[0][1]
            elif len(list_sub_files) > 1:
                dlist = [x[0] for x in list_sub_files]

                self.log(
                    __LOG_CATEGORY__, f"first two char in archive is {file.content[:2]}"
                )
                # hack to fix encoding problem of zip file after Kodi 18
                # TODO Do we need this ??
                # if file.content[:2] == b'PK':
                #     self.log(__LOG_CATEGORY__, f"met PK in {file.file_name}")
                #     try:
                #         dlist = [x.encode('CP437').decode('gbk') for x in dlist]
                #     except:
                #         dlist = [x[0] for x in list_sub_files]

                sel = xbmcgui.Dialog().select("请选择压缩包中的字幕", dlist)
                if sel == -1:
                    sel = 0
                    # TODO: allow reselect?
                return list_sub_files[sel][1]

        return None

    def save_file(self, sub_file: SubtitleDownloadedFile, base_path) -> str:
        """
        Save SubtitleDownloadFile to local file system
        :param sub_file: SubtitleDownloadedFile
        :param base_path:
        :return: absolute path of the saved file in local file system
        """

        __LOG_CATEGORY__ = "SAVE_FILE"

        if not xbmcvfs.exists(base_path):
            xbmcvfs.mkdirs(base_path)

        # TODO clean previous downloaded files
        # dirs, files = xbmcvfs.listdir(base_path)
        # for f in files:
        #     xbmcvfs.delete(os.path.join(base_path, f))

        dist_path = os.path.join(
            base_path,
            f"sub_{datetime.datetime.now().isoformat()}{sub_file.extension()}",
        )
        self.log(__LOG_CATEGORY__, f"saving file {sub_file.file_name} to {dist_path}")
        with open(dist_path, "wb") as saved_file:
            saved_file.write(sub_file.content)

        self.log(__LOG_CATEGORY__, f"file {sub_file.file_name} saved to {dist_path}")

        return dist_path

    def unpack(self, archive_file_path) -> List[Tuple[str, str]]:
        """

        :param archive_file_path:
        :return:
        """

        __LOG_CATEGORY__ = "UNPACK"

        _, archive_extension = os.path.splitext(archive_file_path)
        archive_schema = archive_extension[1:]
        archive_filename = os.path.basename(archive_file_path)

        if archive_extension not in ACCESSIBLE_ARCHIVE_EXTS:
            self.log(
                __LOG_CATEGORY__,
                f"Unknown file ext: {archive_filename}",
                level=xbmc.LOGERROR,
            )
            return []

        archive_fullpath = f"{archive_schema}://{urllib.parse.quote_plus(xbmcvfs.translatePath(archive_file_path))}"
        self.log(__LOG_CATEGORY__, f"Recursively searching: {archive_fullpath}")

        all_sub_files: List[Tuple[str, str]] = []  # [("title", "file_full_path")]
        queue: List[List[str]] = [[archive_fullpath]]

        while len(queue) > 0:
            base = queue.pop(0)
            base_path = os.path.join(*base)
            current_dirs, current_files = xbmcvfs.listdir(base_path)

            for current_dir in current_dirs:
                if current_dir in ("__MACOSX", ".git"):
                    continue
                c = base.copy()
                c.append(current_dir)
                queue.append(c)

            for current_file in current_files:
                if not current_file.endswith(EXTS):
                    continue
                c = base.copy()
                c.append(current_file)
                file_ext = current_file.split(".")[-1]

                title = f"[{file_ext}]{current_file}"
                file_full_path = os.path.join(*c)

                self.log(__LOG_CATEGORY__, f"Found subtitle: {file_full_path}")
                all_sub_files.append((title, file_full_path))
        self.log(__LOG_CATEGORY__, f"In total: {len(all_sub_files)} subtitles")
        return all_sub_files

    def router(self, handle: int, paramstring: str):
        """
        Router for plugin requests
        :param handle: normally sys.argv[1]
        :param paramstring: normally sys.argv[2]
        :return:
        """
        __LOG_CATEGORY__ = "ROUTER"

        params = SubtitleAdapterBase._get_param_dict(paramstring)
        self.log(__LOG_CATEGORY__, f" request: {params}", level=xbmc.LOGINFO)
        action = params["action"]

        if action == "search" or action == "manualsearch":
            languages = params.get("languages").split(",")
            preferredlanguage = params.get("preferredlanguage").split(",")
            searchstring = params.get("searchstring", None)
            self.search_handler(
                handle, SubtitleSearchInput(languages, preferredlanguage, searchstring)
            )

        elif action == "download":
            self.download_handler(handle, params["item_id"])
        else:
            self.log(__LOG_CATEGORY__, f" unknow action: {action}", level=xbmc.LOGERROR)

    @staticmethod
    def _get_param_dict(paramstring):
        from urllib import parse

        url_query = paramstring.replace("?", "")

        if len(url_query) >= 1:
            if url_query[-1] == "/":
                url_query = url_query[0:-1]

        return dict(parse.parse_qsl(url_query))
