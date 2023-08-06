from . import version
from _lzokay import decompress, compress, compress_worst_size

__ALL__ = [
    "decompress",
    "compress",
    "compress_worst_size",
    "VERSION",
    "__version__",
]


__version__ = version.version
VERSION = version.version