#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "symbolic::symbolic" for configuration "Release"
set_property(TARGET symbolic::symbolic APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(symbolic::symbolic PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "VAL::VAL"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libsymbolic.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libsymbolic.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS symbolic::symbolic )
list(APPEND _IMPORT_CHECK_FILES_FOR_symbolic::symbolic "${_IMPORT_PREFIX}/lib/libsymbolic.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
