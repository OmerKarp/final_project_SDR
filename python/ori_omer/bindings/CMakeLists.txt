# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT ori_omer_sources)
    message(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT ori_omer_sources)

########################################################################
# Check for pygccxml
########################################################################
gr_python_check_module_raw("pygccxml" "import pygccxml" PYGCCXML_FOUND)

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND ori_omer_python_files python_bindings.cc)

gr_pybind_make_oot(ori_omer ../../.. gr::ori_omer "${ori_omer_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(
    TARGET ori_omer_python
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:ori_omer_python>
            ${PROJECT_BINARY_DIR}/test_modules/gnuradio/ori_omer/)

install(
    TARGETS ori_omer_python
    DESTINATION ${GR_PYTHON_DIR}/gnuradio/ori_omer
    COMPONENT pythonapi)
