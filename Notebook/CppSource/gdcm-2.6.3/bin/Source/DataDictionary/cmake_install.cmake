# Install script for directory: /Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary

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

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "DebugDevel")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/bin/libgdcmDICT.a")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmDICT.a" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmDICT.a")
    execute_process(COMMAND "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/ranlib" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmDICT.a")
  endif()
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Headers")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/gdcm-2.6" TYPE FILE FILES
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmCSAHeaderDict.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmCSAHeaderDictEntry.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmDict.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmDictConverter.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmDictEntry.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmDicts.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmGlobal.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmGroupDict.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmSOPClassUIDToIOD.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmTagKeywords.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmTagToType.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/gdcmUIDs.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Libraries")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gdcm-2.6/XML" TYPE FILE FILES
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/CSAHeader.xml"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/Part6.xml"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/Part7.xml"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/UIDs.xml"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/DataDictionary/cp699.xml"
    )
endif()

