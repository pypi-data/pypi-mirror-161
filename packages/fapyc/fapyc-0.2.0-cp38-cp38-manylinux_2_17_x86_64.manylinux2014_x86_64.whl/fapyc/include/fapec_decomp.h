/****************************************************************************
 *  FAPEC - Fully Adaptive Prediction Error Coder                           *
 *   (c) DAPCOM Data Services S.L. - http://www.dapcom.es                   *
 *   Entropy coding core patent: US20120166503 A1, 28-June-2012,            *
 *   "Method for fully adaptive calibration of a prediction error coder".   *
 *   Contact: jordi.portell@dapcom.es / fapec@dapcom.es                     *
 ****************************************************************************
 *   This software is property of DAPCOM Data Services S.L.                 *
 *   This C header file and the associated binary (compiled) libraries are  *
 *   subject to the license terms you should have received.                 *
 *   In particular, it is prohibited to install, use, integrate in another  *
 *   software or hardware system, or create derivative works, except as     *
 *   explicitly allowed by the license terms or by DAPCOM.                  *
 *   It is prohibited to copy, distribute, modify, sublicense, lease, rent, *
 *   loan, sell or reverse engineer without explicit permission of DAPCOM.  *
 ****************************************************************************/

/* Visibility options */
#ifndef _WIN32
	#define LINUX_VISIBLITY __attribute__ ((visibility("default")))
	#define WINDOWS_VISIBILITY
#else
	#define LINUX_VISIBLITY
	#ifdef F_LIB
		#define WINDOWS_VISIBILITY __declspec(dllexport)
	#else
		#define WINDOWS_VISIBILITY
	#endif
#endif

/****************************************************************************
 * FAPEC - high-performance professional data compressor and archiver.
 *
 * @file fapec_decomp.h:
 *
 * @brief Definition of the main decompression functions.
 *
 * FAPEC can be invoked at different levels:
 * - File: similar to invoking the command-line decompressor. It takes care of
 *   all "multi-parts" handling if applicable, identify decompression options
 *   from headers (metadata), rebuild from chunking, multi-thread if requested,
 *   recover from errors if applicable, etc.
 *   It allows decompressing directory trees or several files in a directory.
 *   It can also be used for decompressing just one single file, of course.
 *   This is the most "self-contained" use (all cases can be automatically
 *   handled by FAPEC).
 * - Buffer: quite equivalent to the File case for just 1 single file.
 * - Chunk: This is the most basic invocation level for FAPEC, it is the
 *   core decompression method. Please handle with care: here you need to take
 *   care of "de-chunking" and metadata yourself. That is: a compressed chunk
 *   won't be completely self-contained (you'll need to know and provide the
 *   decompression options). And you need to take care of eventual "de-chunking"
 *   when decompressing large buffers or files.
 * Here we provide functions to decompress from disk to disk (file), from
 * (self-contained) buffer to buffer (not available yet in this release),
 * from a file to a buffer, and from compressed chunk to decompressed chunk.
 ****************************************************************************/


#ifndef _FAPEC_DECOMPRESSOR_H_
#define _FAPEC_DECOMPRESSOR_H_

#include "fapec_opts.h"

/**
 * Main memory-based single-buffer decompression function
 *
 * It takes the buffer "buff" of size "buffSize" bytes,
 * decompresses it with "cmpCfg" configuration,
 * and returns the decompressed buffer in the same "buff" parameter
 * (updating "buffSize" with the decompressed buffer size in bytes).
 * It returns zero (or positive value to indicate some information from
 * the decompression, TBC) in case of success,
 * or -1 (or another negative value) to indicate a non-successful decompression.
 * The user does not have to worry about the buffer allocated in "buff": the
 * routine frees the available pointer there and allocates a new one for
 * the decompressed results. It means that such returned buffer must be freed by
 * the user!
 *
 * @param buff      Pointer to the buffer with compressed data to be restored.
 *                  It will be updated to point to the new buffer with
 *                  decompressed data.
 * @param buffSize  Compressed size of the buffer. It will
 *                  be updated to the restored (raw) size.
 * @param userOpts  User/runtime options.
 * @param cmpCfg    FAPEC decompression configuration.
 * @return Zero if successul, 1 to indicate that it's the last chunk for the
 *         part being decompressed, negative in case of errors.
 */
WINDOWS_VISIBILITY int fapec_decomp_chunk(unsigned char **buff, size_t *buffSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Main memory-based input+output buffers decompression function
 *
 * It takes the buffer "inBuff" of size "inBuffSize" bytes,
 * decompresses it with "cmpCfg" configuration,
 * ("userOpts" indicate some file-wide options),
 * and returns the decompressed buffer in "outBuff" parameter
 * (updating "outBuffSize" with the decompressed buffer size in bytes).
 * IMPORTANT: outBuff must be preallocated with the adequate ChunkSize; the
 * actual size returned will be updated in outBuffSize.
 * It returns zero (or positive value to indicate some information from
 * the decompression, TBC) in case of success,
 * or -1 (or another negative value) to indicate a non-successful decompression.
 * Compared to fapec_decomp_chunk(), this function is a bit more efficient
 * when we can reuse memory buffers (we avoid the need of allocating+freeing
 * them for every chunk). That is specially interesting when dealing with
 * tiny chunks.
 * Actually, fapec_decomp_chunk() calls the present function.
 *
 * @param inBuff      Input buffer with the data to be decompressed.
 * @param inBuffSize  Size of the input buffer.
 * @param outBuff     Pre-allocated output buffer.
 * @param outBuffSize Output buffer size is stored here.
 * @param userOpts    User/runtime options.
 * @param cmpCfg      FAPEC compression configuration.
 * @return Zero if successul, 1 to indicate that it's the last chunk for the
 *         part being decompressed, negative in case of errors.
 */
WINDOWS_VISIBILITY int fapec_decomp_chunk_reusebuff(unsigned char *inBuff, size_t inBuffSize,
		unsigned char *outBuff, size_t *outBuffSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Get the compressed chunk size
 *
 * It takes a buffer with a FAPEC compressed chunk
 * and returns its original (raw, uncompressed) size in bytes
 * (from the chunk internal header).
 *
 * @param inBuff      Input buffer with the data to be decompressed.
 * @param inBuffSize  Size of the input buffer.
 * return Number of bytes that will be generated when decompressing
 *        this chunk, or negative in case of problems. Specifically,
 *        it may return the raw bytes size with negative sign if the
 *        format of the chunk is different to that of the present code.
 */
WINDOWS_VISIBILITY int fapec_get_rawchunksize(unsigned char *inBuff,
		size_t inBuffSize) LINUX_VISIBLITY;


/**
 * Decode an FCC External Header.
 * @param inPtr
 * @param edac
 * @param isComp
 * @param isLast
 * @return dataSize, or negative if errors
 */
WINDOWS_VISIBILITY int fapec_decode_fcceh(uint8_t *inPtr,
        uint8_t edac, bool *isComp, bool *isLast) LINUX_VISIBLITY;


/**
 * Main file-based decompression function
 *
 * It takes the input file "inFile", checks its consistency and loads the necessary
 * configuration from it, decompresses it, and writes the compressed output on "outFile".
 * "cmpCfg" should only be needed for "raw-only" compression cases, i.e. when
 * we don't store the compression header. Otherwise one can simply provide NULL here.
 * Decompression information (progress, result, etc.) is printed to stdout depending
 * on the 'verbosity' level indicated in cmpCfg.
 *
 * @param inFile   Input (.fapec) file to be decompressed.
 * @param outFile  For single-file .fapec archives, output filename to use.
 * @param userOpts    User/runtime options.
 * @param cmpCfg      FAPEC compression configuration. Freed before returning.
 * @return Zero if successul, negative in case of errors.
 */
WINDOWS_VISIBILITY int fapec_decomp_file(char *inFile, char *outFile, int userOpts, void *cmpCfg)
	LINUX_VISIBLITY;


/**
 * File-to-buffer decompression function
 *
 * It takes the input file "inFile", checks its consistency and loads the necessary
 * configuration from it, decompresses it, and writes the compressed output into
 * a new buffer (internally allocated with the necessary size) into "outBuff".
 * The size is returned through outSize.
 * When returning, the user does not need to worry about freeing cmpCfg (in case
 * it was allocated at all; you can safely pass null here).
 * Note that in case of multi-part files it only decompresses the first part (for now).
 * The user is responsible of freeing *outBuff when done!
 * The function returns 0 or a positive value if successful,
 * or a negative value in case of problems.
 */
WINDOWS_VISIBILITY int fapec_decomp_file2buff(char *inFile, unsigned char **outBuff, int64_t *outSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Function for buffer-to-buffer decompression:
 * It takes an input buffer *inBuff of inSize bytes,
 * allocates the necessary output buffer *outBuff
 * (we know beforehand the decompressed size thanks to the FAPEC compressed headers),
 * decompresses inBuff into outBuff
 * (with the configuration contained in the compressed buffer,
 * or if "raw-only", with the one given in "cmpCfg"),
 * and returns such size through outSize.
 * The user is responsible of freeing *outBuff when done!
 * The cmpCfg is already freed before returning.
 * It returns 0 or positive if OK, or negative in case of problems.
 */
WINDOWS_VISIBILITY int fapec_decomp_buff2buff(unsigned char *inBuff, unsigned char **outBuff,
		int64_t inSize, int64_t *outSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


#endif
