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

/****************************************************************************
 * FAPEC - high-performance professional data compressor and archiver.
 *
 * @file fapec_comp.h:
 *
 * @brief Definition of the main compression functions.
 *
 * FAPEC can be invoked at different levels:
 * - File: similar to invoking the command-line compressor. It takes care of
 *   all the headers (metadata) generation, "multi-parts" if applicable
 *   (in FAPEC one "part" corresponds to one file and one given compression
 *   setup), chunking, multi-thread if requested, etc.
 *   It allows compressing directory trees or several files in a directory,
 *   if the input parameters request so. It can also be used for compressing
 *   just one single file, of course.
 *   This is the most "self-contained" case (all metadata automatically
 *   handled by FAPEC).
 * - Buffer: equivalent to the File case for just 1 single file.
 *   The buffer will be self-contained regarding compression options
 *   (unless explicitly deactivated).
 * - Chunk: This is the most basic invocation level for FAPEC, it is the
 *   core compression method. Please handle with care: here you need to take
 *   care of "chunking" and metadata yourself. That is: a compressed chunk
 *   won't be completely self-contained (you'll need to know and provide the
 *   compression options when decompressing it). And you need to take care
 *   of eventual "chunking" when compressing large buffers or files: you can
 *   handle up to 384MB at once, in a single chunk, but preferably you should
 *   split it in smaller chunks (e.g. 1-16MB). Finally, in some cases
 *   (such as KWCD or FastQ) you should make sure to provide "aligned"
 *   chunks (each starting at the actual start of a meaningful data block)
 *   to get better compression performance.
 * Here we provide functions to compress from disk to disk (file), from
 * (self-contained) buffer to buffer, and from raw chunk to compressed chunk.
 ****************************************************************************/


#ifndef _FAPEC_COMPRESSOR_H_
#define _FAPEC_COMPRESSOR_H_

#include <stdlib.h>
#include "fapec_opts.h"

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



/**
 * Main memory-based single-buffer compression function
 *
 * It takes the buffer "buff" of size "buffSize" bytes,
 * compresses it with "cmpCfg" configuration,
 * ("userOpts" indicate some file-wide options),
 * and returns the compressed buffer in the same "buff" parameter
 * (updating "buffSize" with the compressed buffer size in bytes).
 * It returns zero (or a positive value to indicate some
 * information from the compression) in case of success,
 * or -1 (or another negative value) to indicate a non-successful compression.
 * The user does not have to worry about the buffer allocated in "buff": the
 * routine frees the available pointer there and allocates a new one for
 * the compressed results. It means that such returned buffer must be freed by
 * the user!
 *
 * @param buff      Pointer to the buffer with the raw data to be compressed.
 *                  It will be updated to point to the new buffer with
 *                  compressed data.
 * @param buffSize  Original (raw, uncompressed) size of the buffer. It will
 *                  be updated to the compressed size.
 * @param userOpts  User/runtime options.
 * @param cmpCfg    FAPEC compression configuration.
 * @return Zero if successul, 2 if the buffer could not be compressed (in
 *         which case the original buffer and size will be returned),
 *         negative in case of errors.
 */
WINDOWS_VISIBILITY int fapec_compress_chunk(unsigned char **buff, size_t *buffSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Main memory-based input+output buffers compression function
 *
 * It takes the buffer "inBuff" of size "inBuffSize" bytes,
 * compresses it with "cmpCfg" configuration,
 * ("userOpts" indicate some file-wide options),
 * and returns the compressed buffer into the PRE-ALLOCATED "outBuff" parameter
 * (setting "outBuffSize" to the compressed buffer size in bytes).
 * IMPORTANT: outBuff must be preallocated with at least 1.2 x inBuffSize.
 * The value of *outBuffSize does not mind at all.
 * It returns zero (or a positive value to indicate some
 * information from the compression) in case of success,
 * or -1 (or another negative value) to indicate a non-successful compression.
 * Compared to fapec_compress_chunk(), this function is a bit more efficient
 * when we can reuse memory buffers (we avoid the need of allocating+freeing
 * them for every chunk). That is specially interesting when dealing with
 * tiny chunks.
 * Actually, fapec_compress_chunk() calls the present function.
 *
 * @param inBuff      Input buffer with the raw data to be compressed.
 * @param inBuffSize  Size of the input buffer.
 * @param outBuff     Pre-allocated output buffer.
 * @param outBuffSize Output buffer size is stored here.
 * @param userOpts    User/runtime options.
 * @param cmpCfg      FAPEC compression configuration.
 * @return Zero if successul, 2 if the buffer could not be compressed (in
 *         which case the original buffer and size will be returned),
 *         negative in case of errors.
 *
 */
WINDOWS_VISIBILITY int fapec_compress_chunk_reusebuff(unsigned char *inBuff, size_t inBuffSize,
		unsigned char *outBuff, size_t *outBuffSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Generate the FCC External Header.
 * @param isComp
 * @param isLast
 * @param dataSize
 * @param edac
 * @param outPtr (it must be preallocated!)
 * @return Size of the FCC EH
 */
WINDOWS_VISIBILITY int fapec_gen_fcceh(bool isComp, bool isLast, int dataSize, uint8_t edac,
        uint8_t *outPtr) LINUX_VISIBLITY;


/**
 * Main file-based compression function
 *
 * It takes the input file(s) "inFiles",
 * applies FAPEC on it using the configuration indicated in "cmpCfg",
 * and writes the compressed output on "outFile".
 * Either a fixed or automatic compression configuration will be used depending on "cmpCfg".
 * If autoconfigured, "cmpCfg" is updated to the compression options automatically selected for this file.
 * For simplicity, "cmpCfg" can be NULL, and in that case we internally default to auto-configuration
 * (and to verbose=0, overwrite=true and deleteInput=false; also, chunksize is set to 1MB).
 * Compression information (progress, result, etc.) is printed to stdout depending on the 'verbosity' level
 * indicated in cmpCfg.
 *
 * @param inFiles   Array of null-terminated strings indicating the input file and folder names
 *                  (including relative or absolute paths if needed) to be compressed.
 * @param numFiles  Number of files or folders provided through the inFiles array.
 * @param outFile   Output (.fapec) file where all input file(s) will be compressed.
 * @param userOpts  User/runtime options.
 * @param cmpCfg    FAPEC compression configuration. If NULL, auto-config is selected.
 * @return Zero if successful, negative if errors.
 */
WINDOWS_VISIBILITY int fapec_compress_file(char **inFiles, int numFiles, char *outFile,
        int userOpts, void *cmpCfg) LINUX_VISIBLITY;


/**
 * Function for buffer-to-buffer compression
 *
 * It takes an input buffer *inBuff of inSize bytes,
 * allocates the necessary output buffer *outBuff
 * (which will be at most inSize bytes plus a small overhead of some ~1K),
 * compresses inBuff into outBuff using FAPEC
 * (with the configuration given in "cmpCfg", or automatic if that's NULL),
 * resizes the resulting buffer to just the actual size generated,
 * and returns such size through outSize.
 * The user is responsible of freeing *outBuff when done!
 *
 * @param inBuff    Input buffer with the data to be compressed.
 * @param outBuff   Pointer to the (internally allocated) output, compressed buffer.
 * @param inSize    Input buffer size.
 * @param outSize   Output (compressed) size will be stored here.
 * @param userOpts  User/runtime options.
 * @param cmpCfg    FAPEC compression configuration. If NULL, auto-config is selected.
 * @return Zero if successful, negative if errors.
 */
WINDOWS_VISIBILITY int fapec_compress_buff2buff(unsigned char *inBuff, unsigned char **outBuff,
		int64_t inSize, int64_t *outSize,
		int userOpts, void *cmpCfg) LINUX_VISIBLITY;


#endif
