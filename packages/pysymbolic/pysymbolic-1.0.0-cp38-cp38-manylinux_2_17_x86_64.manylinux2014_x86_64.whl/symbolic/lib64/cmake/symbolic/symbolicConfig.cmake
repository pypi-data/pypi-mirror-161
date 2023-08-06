############################################################
# CMake config for the symbolic library.
#
# Copyright 2020. All Rights Reserved.
#
# Created: April 1, 2020
# Authors: Toki Migimatsu
############################################################

include(CMakeFindDependencyMacro)

set(LIB_NAME symbolic)
set(LIB_BINARY_DIR /project/build/temp.linux-x86_64-cpython-38)

if(NOT TARGET ${LIB_NAME}::${LIB_NAME})
    include("${LIB_BINARY_DIR}/${LIB_NAME}Targets.cmake")
endif()
