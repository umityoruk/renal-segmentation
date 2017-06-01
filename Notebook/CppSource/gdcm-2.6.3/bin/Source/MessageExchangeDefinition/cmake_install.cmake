# Install script for directory: /Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/bin/bin/libgdcmMEXD.a")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmMEXD.a" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmMEXD.a")
    execute_process(COMMAND "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/ranlib" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgdcmMEXD.a")
  endif()
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Headers")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/gdcm-2.6" TYPE FILE FILES
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAAbortPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAAssociateACPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAAssociateRJPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAAssociateRQPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAbstractSyntax.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmApplicationContext.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAReleaseRPPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAReleaseRQPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmARTIMTimer.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmAsynchronousOperationsWindowSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmBaseCompositeMessage.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmBaseNormalizedMessage.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmBasePDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmBaseQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmBaseRootQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCEchoMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCFindMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCMoveMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCommandDataSet.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCompositeMessageFactory.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCompositeNetworkFunctions.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmCStoreMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmDIMSE.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmFindPatientRootQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmFindStudyRootQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmImplementationClassUIDSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmImplementationUIDSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmImplementationVersionNameSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmMaximumLengthSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmModalityPerformedProcedureStepCreateQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmModalityPerformedProcedureStepSetQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmMovePatientRootQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmMoveStudyRootQuery.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNActionMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNCreateMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNDeleteMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNetworkEvents.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNetworkStateID.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNEventReportMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNGetMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNormalizedMessageFactory.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNormalizedNetworkFunctions.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmNSetMessages.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPDataTFPDU.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPDUFactory.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPresentationContext.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPresentationContextAC.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPresentationContextGenerator.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPresentationContextRQ.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmPresentationDataValue.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQueryBase.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQueryFactory.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQueryImage.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQueryPatient.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQuerySeries.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmQueryStudy.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmRoleSelectionSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmServiceClassApplicationInformation.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmServiceClassUser.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmSOPClassExtendedNegociationSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmTransferSyntaxSub.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULAction.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULActionAA.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULActionAE.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULActionAR.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULActionDT.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULBasicCallback.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULConnection.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULConnectionCallback.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULConnectionInfo.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULConnectionManager.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULEvent.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULTransitionTable.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmULWritingCallback.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmUserInformation.h"
    "/Users/umityoruk/Documents/PythonDev/NewSegmentation/Notebook/CppSource/gdcm-2.6.3/Source/MessageExchangeDefinition/gdcmWLMFindQuery.h"
    )
endif()

