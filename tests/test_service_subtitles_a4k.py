import sys
import os
import tempfile
import pytest
import urllib

sys.path.append("./service.subtitles.a4k")

from adapter import A4KAdapter as SubtitleAdapter
from base_adapter import SubtitleSearchInput, SubtitleDownloadedFile
from unittest import TestCase


class TestPlugin(TestCase):

    def test_search(self):
        sa = SubtitleAdapter()
        results = sa.search(SubtitleSearchInput(languages=[], preferredlanguage=[], searchstring="流浪地球"))

        self.assertTrue(len(results) > 0)
        self.assertEqual("[zip]流浪地球 中文字幕 / 流浪地球  / The Wandering Earth 字幕 流浪地球(简繁字幕)The.Wandering.Earth.2019.720p.BluRay.x264-WiKi.zip", results[0].name)
        self.assertEqual("/subtitle/108502", results[0].item_id)
        self.assertTrue(len(results[0].time) > 0)
        self.assertEqual("zh", results[0].language_code)
        self.assertEqual("简体", results[0].language_name)
        self.assertEqual("zh", results[0].language_flag)
        self.assertEqual(0, results[0].rating)


    def test_download_zip(self):
        sa = SubtitleAdapter()
        download: SubtitleDownloadedFile = sa.download("/subtitle/108502")

        self.assertEqual("a4k.net_1591786049_0.zip", download.file_name)
        self.assertEqual("application/zip", download.content_type)
        self.assertEqual(74180, download.content_length)
        self.assertTrue(isinstance(download.content, bytes))
        self.assertEqual(74180, len(download.content))
        self.assertEqual(".zip", download.extension())


    def test_load_single_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sa = SubtitleAdapter()
            download: SubtitleDownloadedFile = sa.download("/subtitle/131634")
            loaded_path = sa.load(download, tmp_dir)
            self.assertIsNotNone(loaded_path)
            self.assertRegex(loaded_path, rf"{tmp_dir}")
            self.assertRegex(loaded_path, r"sub_.+\.ass")
            self.assertEqual(211624, os.stat(loaded_path).st_size)

    def test_get_param_dict(self):
        self.assertEqual({
            "a": "b"
        }, SubtitleAdapter._get_param_dict("?a=b"))

        self.assertEqual({
            "a": "b",
            "x": "12"
        }, SubtitleAdapter._get_param_dict("?a=b&x=12"))
        self.assertEqual({
            "a": "b",
            "x": "你好啊！"
        }, SubtitleAdapter._get_param_dict("?a=b&x=%E4%BD%A0%E5%A5%BD%E5%95%8A%EF%BC%81"))

        self.assertEqual({
            "a": "b",
            "x": "你好啊！"
        }, SubtitleAdapter._get_param_dict("?a=b&x=你好啊！"))

        self.assertEqual({
            "a": "b",
            "x": "12"
        }, SubtitleAdapter._get_param_dict("?a=b&x=12/"))

    def test_dummy(self):
        self.assertEqual(
            "action=download&item_id=%E4%BD%A0%E5%A5%BD%E5%95%8A%EF%BC%81"
            , urllib.parse.urlencode({
                "action": "download",
                "item_id": "你好啊！"
            }))

    @pytest.mark.skip
    def test_load_archive_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sa = SubtitleAdapter()
            download: SubtitleDownloadedFile = sa.download("/subtitle/108502")
            loaded_path = sa.load(download, tmp_dir)
            self.assertIsNotNone(loaded_path)
            self.assertRegex(loaded_path, rf"{tmp_dir}")
            self.assertRegex(loaded_path, r"sub_.+\.ass")
            self.assertEqual(211624, os.stat(loaded_path).st_size)