#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cmeel-example::cmeel-example" for configuration "Release"
set_property(TARGET cmeel-example::cmeel-example APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cmeel-example::cmeel-example PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcmeel-example.so.0.0.0"
  IMPORTED_SONAME_RELEASE "libcmeel-example.so.0.0.0"
  )

list(APPEND _IMPORT_CHECK_TARGETS cmeel-example::cmeel-example )
list(APPEND _IMPORT_CHECK_FILES_FOR_cmeel-example::cmeel-example "${_IMPORT_PREFIX}/lib/libcmeel-example.so.0.0.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
