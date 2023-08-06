from cpython cimport array
import array
from libc.stdint cimport uint8_t

from lzokay_wrap cimport (
    decompress as c_decompress,
    compress as c_compress,
    EResult as c_EResult,
)


class LookbehindOverrun(Exception):
    pass


class OutputOverrun(Exception):
    pass


class InputOverrun(Exception):
    pass


class Error(Exception):
    pass


class InputNotConsumed(Exception):
    pass


result_mapping = {
    c_EResult.LookbehindOverrun: LookbehindOverrun,
    c_EResult.OutputOverrun: OutputOverrun,
    c_EResult.InputOverrun: InputOverrun,
    c_EResult.Error: Error,
    c_EResult.InputNotConsumed: InputNotConsumed,
}


cpdef int compress_worst_size(s: int):
    return s + s // 16 + 64 + 3


def decompress(data: bytes, expected_output_size: int = None) -> bytes:
    data_size = len(data)

    cdef size_t curren_array_size = data_size
    if expected_output_size is not None:
        curren_array_size = expected_output_size
    
    cdef size_t actual_out_size = 0    
    cdef array.array b = array.array('B')
    array.resize(b, curren_array_size)
    
    cdef c_EResult code = c_EResult.OutputOverrun
    cdef const uint8_t* data_bytes = data
    while code == c_EResult.OutputOverrun:
        with nogil:
            code = c_decompress(data_bytes, data_size, b.data.as_uchars, curren_array_size, actual_out_size)

        if code == c_EResult.OutputOverrun:
            curren_array_size *= 2
            array.resize(b, curren_array_size)
    
    array.resize(b, actual_out_size)

    if code in result_mapping:
        raise result_mapping[code]()

    return b.tobytes()

    
def compress(data: bytes) -> bytes:
    cdef const uint8_t* data_bytes = data
    cdef size_t data_size = len(data)
    cdef size_t expected_out_size = compress_worst_size(data_size)

    cdef array.array b = array.array('B')
    array.resize(b, expected_out_size)
    
    # Results from c_compress
    cdef c_EResult code
    cdef size_t actual_out_size = 0

    with nogil:
        code = c_compress(data_bytes, data_size, b.data.as_uchars, expected_out_size, actual_out_size)
    
    array.resize(b, actual_out_size)

    if code in result_mapping:
        raise result_mapping[code]()

    return b.tobytes()

    