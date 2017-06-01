# Install script for directory: /Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Headers")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/gdcm-2.6/gdcmjpeg" TYPE FILE FILES
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jchuff.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jconfig.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jdct.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jdhuff.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jerror.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jinclude.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jlossls.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jlossy.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jmemsys.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jmorecfg.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jpegint.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jpeglib.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Utilities/gdcmjpeg/jversion.h"
    )
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Utilities/gdcmjpeg/8/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Utilities/gdcmjpeg/12/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Utilities/gdcmjpeg/16/cmake_install.cmake")

endif()

