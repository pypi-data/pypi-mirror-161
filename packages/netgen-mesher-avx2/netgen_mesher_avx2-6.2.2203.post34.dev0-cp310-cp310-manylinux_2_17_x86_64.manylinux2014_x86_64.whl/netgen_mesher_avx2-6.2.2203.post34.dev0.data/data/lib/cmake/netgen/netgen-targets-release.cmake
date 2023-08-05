#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ngcore" for configuration "Release"
set_property(TARGET ngcore APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ngcore PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libngcore.so"
  IMPORTED_SONAME_RELEASE "libngcore.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS ngcore )
list(APPEND _IMPORT_CHECK_FILES_FOR_ngcore "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libngcore.so" )

# Import target "nggui" for configuration "Release"
set_property(TARGET nggui APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nggui PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libnggui.so"
  IMPORTED_SONAME_RELEASE "libnggui.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS nggui )
list(APPEND _IMPORT_CHECK_FILES_FOR_nggui "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libnggui.so" )

# Import target "togl" for configuration "Release"
set_property(TARGET togl APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(togl PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libtogl.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS togl )
list(APPEND _IMPORT_CHECK_FILES_FOR_togl "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libtogl.a" )

# Import target "nglib" for configuration "Release"
set_property(TARGET nglib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nglib PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libnglib.so"
  IMPORTED_SONAME_RELEASE "libnglib.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS nglib )
list(APPEND _IMPORT_CHECK_FILES_FOR_nglib "${_IMPORT_PREFIX}/lib/python3.10/site-packages/netgen_mesher_avx2.libs/libnglib.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
