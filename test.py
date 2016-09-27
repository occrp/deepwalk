import sys
from deepwalk import deepwalk


if __name__ == '__main__':
    for item in deepwalk(sys.argv[1]):
        print item
