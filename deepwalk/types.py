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


class BundlePackage(Package):

    def unpack_members(self, pack):
        # Some archives come with non-Unicode file names, this
        # attempts to avoid that issue by naming the destination
        # explicitly.
        for name in pack.namelist():
            out_path = os.path.join(self.temp_path, name)
            if os.path.exists(out_path):
                continue
            if not out_path.startswith(self.temp_path):
                continue
            if not os.path.exists(os.path.dirname(out_path)):
                os.makedirs(os.path.dirname(out_path))
            try:
                in_fh = pack.open(name)
                try:
                    with open(out_path, 'w') as out_fh:
                        shutil.copyfileobj(in_fh, out_fh)
                finally:
                    in_fh.close()
            except Exception as ex:
                log.debug("Failed to unpack %s: %s", out_path, ex)


class ZipPackage(BundlePackage):

    IGNORE_EXT = ['docx', 'xlsx', 'pptx', 'ods', 'odt']

    def unpack(self):
        # log.info("Reading ZIP file: %r", self.item)
        with zipfile.ZipFile(self.item.real_path, 'r') as zf:
            self.unpack_members(zf)

    def bid_file(self):
        if self.item.extension in self.IGNORE_EXT:
            return
        if zipfile.is_zipfile(self.item.real_path):
            return 7


class RarPackage(BundlePackage):

    def unpack(self):
        with rarfile.RarFile(self.item.real_path) as rf:
            self.unpack_members(rf)

    def bid_file(self):
        if rarfile.is_rarfile(self.item.real_path):
            return 10
        return -1


class TarPackage(Package):

    def unpack(self):
        with tarfile.open(name=self.item.real_path, mode='r:*') as tf:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tf, self.temp_path)

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
        args = [SEVENZ_BIN, 'x', '-y', '-r', '-bd',
                '-o%s' % self.temp_path, self.item.real_path]
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
