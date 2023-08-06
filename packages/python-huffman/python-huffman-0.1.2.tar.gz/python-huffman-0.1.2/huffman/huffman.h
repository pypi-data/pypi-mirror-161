#ifndef HUFFMAN_HUFFMAN_H
#define HUFFMAN_HUFFMAN_H

#include <stdint.h>
#include <stdio.h>

#ifdef PYTHON
#include "Python.h"
#define malloc(...) PyMem_Malloc(__VA_ARGS__)
#define free(...) PyMem_Free(__VA_ARGS__)
#endif

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT extern
#endif /* _WIN32 */

#ifdef __cplusplus
extern "C" {
#endif

DLLEXPORT int huffman_encode_file(FILE* in, FILE* out);

DLLEXPORT int huffman_decode_file(FILE* in, FILE* out);

DLLEXPORT int huffman_encode_memory(const unsigned char* bufin,
			  uint32_t bufinlen,
			  unsigned char** pbufout,
			  uint32_t* pbufoutlen);

DLLEXPORT int huffman_decode_memory(const unsigned char* bufin,
			  uint32_t bufinlen,
			  unsigned char** bufout,
			  uint32_t* pbufoutlen);

#ifdef __cplusplus
}
#endif

#endif
