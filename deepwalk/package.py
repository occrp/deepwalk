import os
import shutil
import logging
from tempfile import mkdtemp
from pkg_resources import iter_entry_points

log = logging.getLogger(__name__)


class Package(object):
    TYPES = {}

    def __init__(self, item):
        self.item = item

    @property
    def temp_path(self):
        if not hasattr(self, '_temp_path') or self._temp_path is None:
            self._temp_path = mkdtemp(prefix='deepwalk')
        return self._temp_path

    def unpack(self):
        pass

    def safe_unpack(self):
        try:
            self.unpack()
        except Exception as ex:
            log.exception(ex)

    def cleanup(self):
        try:
            if self._temp_path is not None and os.path.isdir(self.temp_path):
                shutil.rmtree(self.temp_path)
        except Exception as ex:
            log.exception(ex)
        self._temp_path = None

    def bid(self):
        if self.item.is_dir:
            return -1
        return self.bid_file()

    def bid_file(self):
        return -1

    @classmethod
    def types(cls):
        if not len(cls.TYPES):
            for ep in iter_entry_points('deepwalk.package'):
                cls.TYPES[ep.name] = ep.load()
        return cls.TYPES.values()

    @classmethod
    def by_item(cls, item):
        best_type = None
        best_bid = 0
        for type_cls in cls.types():
            type_ = type_cls(item)
            bid = type_.bid()
            # print [item, type_cls, bid]
            if bid is not None and bid > best_bid:
                best_bid = bid
                best_type = type_
        return best_type
