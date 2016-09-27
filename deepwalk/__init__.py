
from deepwalk.item import Item


def deepwalk(base_directory):
    for item in Item(base_directory, base_directory).walk():
        yield item
