/* create config.h for CMake */
/*
 * here is where system comupted values get stored these values should only
 * change when the target compile platform changes
 */

/* what byte order */
#ifndef __OPJ_CONFIGURE_H
#define __OPJ_CONFIGURE_H

/* #undef CMAKE_WORDS_BIGENDIAN */
#ifdef CMAKE_WORDS_BIGENDIAN
        #define OPJ_BIG_ENDIAN
#else
        #define OPJ_LITTLE_ENDIAN
#endif

#define PACKAGE_VERSION "1.4.0"

#define HAVE_INTTYPES_H
#define HAVE_MEMORY_H
#define HAVE_STDINT_H
#define HAVE_STDLIB_H
#define HAVE_STRINGS_H
#define HAVE_STRING_H
#define HAVE_SYS_STAT_H
#define HAVE_SYS_TYPES_H
#define HAVE_UNISTD_H


#endif /* __OPJ_CONFIGURE_H */
