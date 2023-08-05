import unittest
import tempfile
import shutil
import io
import mock

from dslibrary.utils.file_utils import FileOpener, connect_to_filesystem, write_stream_with_read_on_close, \
    adapt_fsspec_storage_options, is_breakout_path


class TestFileUtils(unittest.TestCase):

    def test_FileOpener_local_file(self):
        tmp_f = tempfile.mkdtemp()
        fo = FileOpener(tmp_f)
        with fo.open("x", mode="w") as f_w:
            f_w.write("abc")
        with fo.open("x", mode="r") as f_r:
            self.assertEqual(f_r.read(), "abc")
        shutil.rmtree(tmp_f)

    def test_FileOpener_s3(self):
        tmp_f = tempfile.mkdtemp()
        fo = FileOpener(tmp_f)
        def opener(uri, **kwargs):
            self.assertEqual(uri, "s3://bucket/file.csv")
            self.assertEqual(kwargs, {'mode': 'r', 'key': 'K', 'secret': 'S'})
            return io.StringIO("x")
        with mock.patch("fsspec.open", opener):
            with fo.open("s3://bucket/file.csv", mode="r", access_key="K", secret_key="S") as f_r:
                d = f_r.read()
        self.assertEqual(d, "x")
        shutil.rmtree(tmp_f)

    def test_write_stream_with_read_on_close(self):
        log = []
        f_w = write_stream_with_read_on_close('w', 'r', on_close=lambda fh: log.append(fh.read()))
        f_w.write("abc")
        f_w.write("def")
        f_w.close()
        assert log == ["abcdef"]

    def test_connect_to_filesystem(self):
        tmp_f = tempfile.mkdtemp()
        fs = connect_to_filesystem(tmp_f, for_write=True)
        with fs.open("x", mode="w") as f_w:
            f_w.write("abc")
        with fs.open("x", mode="r") as f_r:
            self.assertEqual(f_r.read(), "abc")
        self.assertEqual(fs.ls(), [{'name': 'x', 'size': 3, 'type': 'file'}])
        self.assertEqual(fs.stat("x"), {'name': 'x', 'size': 3, 'type': 'file'})
        assert fs.exists("x") is True
        assert fs.exists("y") is False
        shutil.rmtree(tmp_f)

    def test_adapt_fsspec_storage_options(self):
        self.assertEqual(adapt_fsspec_storage_options({"access_key": "K"}), {'storage_options': {'key': 'K'}})
        self.assertEqual(adapt_fsspec_storage_options({"key": "K"}), {'storage_options': {'key': 'K'}})
        self.assertEqual(adapt_fsspec_storage_options({"storage_options": {"x": 1}, "access_key": "K", "z": 2}), {'storage_options': {'key': 'K', 'x': 1}, 'z': 2})

    def test_is_breakout_path(self):
        self.assertEqual(True,  is_breakout_path("../x"))
        self.assertEqual(False, is_breakout_path("x/.."))
        self.assertEqual(True,  is_breakout_path("x/../.."))
        self.assertEqual(False, is_breakout_path("x/y/../.."))
        self.assertEqual(False, is_breakout_path("x/y/../../z"))
        self.assertEqual(True,  is_breakout_path("x/y/../../z/../.."))
        self.assertEqual(False, is_breakout_path("./"))
        self.assertEqual(True,  is_breakout_path("./.."))

