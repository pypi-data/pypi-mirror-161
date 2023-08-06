#cython: language_level=3
cdef extern from "mp2hudcolor.c":
    void mp2hudcolor(char* input_filename, char* output_filename, float r, float g, float b)

cpdef mp2hudcolor_c(input_filename: str, output_filename: str, r: float, g: float, b: float):
    mp2hudcolor(input_filename.encode(), output_filename.encode(), r, g, b)
