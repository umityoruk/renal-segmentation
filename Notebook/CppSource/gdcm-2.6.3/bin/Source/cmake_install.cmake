# Install script for directory: /Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source

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

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/Common/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/Attribute/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/DataDictionary/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/DataStructureAndEncodingDefinition/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/InformationObjectDefinition/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/MediaStorageAndFileFormat/cmake_install.cmake")
  include("/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/Source/MessageExchangeDefinition/cmake_install.cmake")

endif()

