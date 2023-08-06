from libc.stdint cimport uint8_t


cdef extern from "lzokay.hpp" namespace "lzokay":
    cpdef enum class EResult(int):
        LookbehindOverrun,
        OutputOverrun,
        InputOverrun,
        Error,
        Success,
        InputNotConsumed,

    EResult decompress(const uint8_t* src, size_t src_size,
                       uint8_t* dst, size_t dst_size, size_t& out_size) nogil

    EResult compress(const uint8_t* src, size_t src_size,
                     uint8_t* dst, size_t dst_size, size_t& out_size) nogil
