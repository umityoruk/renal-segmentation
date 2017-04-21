# Test config file.
# Version number
set( GDCM_MAJOR_VERSION "2")
set( GDCM_MINOR_VERSION "6")
set( GDCM_BUILD_VERSION "3")
set( GDCM_VERSION       "2.6.3")

set(PACKAGE_VERSION "${GDCM_VERSION}")
if("${PACKAGE_FIND_VERSION}" STREQUAL "")
  # User did not request any particular version
  set(PACKAGE_VERSION_COMPATIBLE 1)
elseif("${PACKAGE_FIND_VERSION}" VERSION_EQUAL "${PACKAGE_VERSION}")
  # User did request exactly this version
  set(PACKAGE_VERSION_COMPATIBLE 1)
  set(PACKAGE_VERSION_EXACT 1)
elseif("${PACKAGE_FIND_VERSION}" VERSION_LESS "${PACKAGE_VERSION}")
  # User requested an older version
  set(PACKAGE_VERSION_COMPATIBLE 1)
else()
  message("REQUESTING: [${PACKAGE_FIND_VERSION}] but found: ${PACKAGE_VERSION}")
endif()
