import pytest

import lzokay


@pytest.mark.parametrize("data", [
    b"Hello World",
    b"Hello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello Worldello World",
])
def test_compress_and_decompress(data):

    compressed = lzokay.compress(data)
    print(compressed)

    decompressed = lzokay.decompress(compressed)

    assert decompressed == data
