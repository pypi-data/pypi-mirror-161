#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "surelog" for configuration "Release"
set_property(TARGET surelog APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(surelog PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/surelog/libsurelog.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS surelog )
list(APPEND _IMPORT_CHECK_FILES_FOR_surelog "${_IMPORT_PREFIX}/lib64/surelog/libsurelog.a" )

# Import target "antlr4_static" for configuration "Release"
set_property(TARGET antlr4_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(antlr4_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "uuid"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/surelog/libantlr4-runtime.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS antlr4_static )
list(APPEND _IMPORT_CHECK_FILES_FOR_antlr4_static "${_IMPORT_PREFIX}/lib64/surelog/libantlr4-runtime.a" )

# Import target "flatbuffers" for configuration "Release"
set_property(TARGET flatbuffers APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(flatbuffers PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/surelog/libflatbuffers.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS flatbuffers )
list(APPEND _IMPORT_CHECK_FILES_FOR_flatbuffers "${_IMPORT_PREFIX}/lib64/surelog/libflatbuffers.a" )

# Import target "uhdm" for configuration "Release"
set_property(TARGET uhdm APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(uhdm PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/uhdm/libuhdm.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS uhdm )
list(APPEND _IMPORT_CHECK_FILES_FOR_uhdm "${_IMPORT_PREFIX}/lib64/uhdm/libuhdm.a" )

# Import target "capnp" for configuration "Release"
set_property(TARGET capnp APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(capnp PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/uhdm/libcapnp.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS capnp )
list(APPEND _IMPORT_CHECK_FILES_FOR_capnp "${_IMPORT_PREFIX}/lib64/uhdm/libcapnp.a" )

# Import target "kj" for configuration "Release"
set_property(TARGET kj APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(kj PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/uhdm/libkj.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS kj )
list(APPEND _IMPORT_CHECK_FILES_FOR_kj "${_IMPORT_PREFIX}/lib64/uhdm/libkj.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
