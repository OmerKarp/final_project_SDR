find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_ORI_OMER gnuradio-ori_omer)

FIND_PATH(
    GR_ORI_OMER_INCLUDE_DIRS
    NAMES gnuradio/ori_omer/api.h
    HINTS $ENV{ORI_OMER_DIR}/include
        ${PC_ORI_OMER_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_ORI_OMER_LIBRARIES
    NAMES gnuradio-ori_omer
    HINTS $ENV{ORI_OMER_DIR}/lib
        ${PC_ORI_OMER_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-ori_omerTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_ORI_OMER DEFAULT_MSG GR_ORI_OMER_LIBRARIES GR_ORI_OMER_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_ORI_OMER_LIBRARIES GR_ORI_OMER_INCLUDE_DIRS)
