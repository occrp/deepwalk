import os
import logging
import shutil
import subprocess
import bz2
import gzip
import rarfile
import zipfile
import tarfile

from deepwalk.package import Package

log = logging.getLogger(__name__)

UNZIP_BIN = os.environ.get('UNZIP_BIN', 'unzip')
UNRAR_BIN = os.environ.get('UNRAR_BIN', 'unrar')
SEVENZ_BIN = os.environ.get('SEVENZ_BIN', '7z')
BUNZIP2_BIN = os.environ.get('BUNZIP2_BIN', 'bunzip2')


def quote_arg(arg):
    # arg = arg.replace('"', '\\"')
    # return '"%s"' % arg
    return arg


class ZipPackage(Package):

    IGNORE_EXT = ['docx', 'xlsx', 'pptx', 'ods', 'odt']

    def unpack(self):
        args = [UNZIP_BIN, '-n', '-qq', self.item.real_path,
                '-d', self.temp_path]
        subprocess.call(args)

    def bid_file(self):
        if self.item.extension in self.IGNORE_EXT:
            return
        if zipfile.is_zipfile(self.item.real_path):
            return 6


class RarPackage(Package):
    free_version = None

    def test_version(self):
        if self.free_version is None:
            output = subprocess.check_output(UNRAR_BIN)
            self.free_version = 'freeware' in output

    def unpack(self):
        self.test_version()
        if self.free_version:
            args = [UNRAR_BIN, 'x', '-y', '-inul', self.item.real_path,
                    self.temp_path]
        else:
            args = [UNRAR_BIN, '-x', self.item.real_path,
                    self.temp_path]
        subprocess.call(args)

    def bid_file(self):
        if rarfile.is_rarfile(self.item.real_path):
            return 7
        return -1


class TarPackage(Package):

    def unpack(self):
        with tarfile.open(name=self.item.real_path, mode='r:*') as tf:
            tf.extractall(self.temp_path)

    def bid_file(self):
        if tarfile.is_tarfile(self.item.real_path):
            return 6
        return -1


class ExtensionPackage(Package):

    def bid_file(self):
        if self.item.extension in self.EXTENSIONS:
            return 4
        return -1


class SevenZipPackage(ExtensionPackage):
    EXTENSIONS = ['7z', '7zip']

    def unpack(self):
        args = [SEVENZ_BIN, 'x', self.item.real_path, '-y', '-r',
                '-bb0', '-bd', '-oc:%s' % self.temp_path]
        subprocess.call(args)


class SingleFilePackage(ExtensionPackage):

    def unpack(self):
        file_name = os.path.basename(self.item.name_path)
        base, ext = os.path.splitext(file_name)
        if ext.strip('.').strip() in self.EXTENSIONS:
            file_name = base
        file_name = os.path.join(self.temp_path, file_name)
        self.unpack_file(file_name)

    def unpack_file(self, file_name):
        pass


class GzipPackage(SingleFilePackage):
    EXTENSIONS = ['gz', 'tgz']

    def unpack_file(self, file_name):
        with gzip.GzipFile(self.item.real_path) as src:
            with open(file_name, 'wb') as dst:
                shutil.copyfileobj(src, dst)


class BZ2Package(SingleFilePackage):
    EXTENSIONS = ['bz', 'tbz', 'bz2', 'tbz2']

    def unpack_file(self, file_name):
        with bz2.BZ2File(self.item.real_path) as src:
            with open(file_name, 'wb') as dst:
                shutil.copyfileobj(src, dst)
