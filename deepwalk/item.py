import os
import logging
from normality import slugify

from deepwalk.package import Package
from deepwalk.util import string_value

log = logging.getLogger(__name__)


class Item(object):

    def __init__(self, real_path, name_path, temporary=False):
        self.real_path = os.path.abspath(os.path.normpath(real_path))
        self.name_path = name_path
        self.is_dir = os.path.isdir(self.real_path)
        self.is_file = os.path.isfile(self.real_path)
        self.temporary = temporary

    def walk(self):
        yield self
        for item in self.children:
            for sitem in item.walk():
                yield sitem

    @property
    def children(self):
        if self.is_dir:
            for child in os.listdir(self.real_path):
                file_name = string_value(child)
                if file_name is None:
                    log.error("Could not decide file name: %r", child)
                    continue
                real_path = os.path.join(self.real_path, file_name)
                if not os.path.exists(real_path):
                    log.error("Invalid path: %r", real_path)
                yield Item(real_path, os.path.join(self.name_path, file_name),
                           temporary=self.temporary)

        if self.package is not None:
            self.package.safe_unpack()
            yield Item(self.package.temp_path, self.name_path,
                       temporary=True)
            self.package.cleanup()

    @property
    def package(self):
        if not hasattr(self, '_package'):
            self._package = Package.by_item(self)
        return self._package

    @property
    def extension(self):
        name, ext = os.path.splitext(self.real_path)
        if len(ext):
            return slugify(ext, '')

    def __repr__(self):
        return '<Item(%r, %r, %s)>' % (self.name_path, self.real_path,
                                       self.is_dir)
