# Set minimum cmake version and policy
cmake_minimum_required(VERSION 3.13)
cmake_policy(VERSION 3.13)

# set c++ standard to c++17
set(CMAKE_CXX_STANDARD 17)

# use new option/variable policy
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)

# set project name and languages
project(omni LANGUAGES CXX C Fortran)

# set install RPATH
set(CMAKE_INSTALL_RPATH $ORIGIN)

# set project build output directories
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/omni_lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/omni_static)

# find openmp
find_package(OpenMP REQUIRED)

# detect blas and lapack; these are technically not required since armadillo
# will default back to it's own lapack/blas implementation at reduced
# performance, but we'd like to avoid that
find_package(BLAS REQUIRED)
find_package(LAPACK REQUIRED)

# include FetchContent module
include(FetchContent)

# create a python __init__.py in the binary directory for development testing
file(TOUCH ${PROJECT_BINARY_DIR}/__init__.py)

# download and include pybind11
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.9.2
)
FetchContent_GetProperties(pybind11)
if(NOT pybind11_POPULATED)
    set(PYBIND11_CPP_STANDARD -std=c++17)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()

# find armadillo library
find_package(Armadillo 11.0)
# setup the armadillo target if it was found
if(${ARMADILLO_FOUND})
    add_library(armadillo INTERFACE)
    target_include_directories(armadillo INTERFACE ${ARMADILLO_INCLUDE_DIRS})
    target_link_libraries(armadillo INTERFACE ${ARMADILLO_LIBRARIES})
# download and compile armadillo library, if it was not found on the system
else()
    message("-- Downloading and compiling Armadillo from source")
    FetchContent_Declare(
        armadillo
        GIT_REPOSITORY https://gitlab.com/conradsnicta/armadillo-code.git
        GIT_TAG        b5727433d342afca53aca0ee16ecf1caaa661821
    )
    FetchContent_GetProperties(armadillo)
    if(NOT armadillo_POPULATED)
        # we don't want armadillo to reset CMAKE_INSTALL_PREFIX
        # so set the initialized check back to FALSE if it is TRUE
        if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
            set(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT FALSE)
        endif()
        # force libdir to lib
        set(CMAKE_INSTALL_LIBDIR "lib")
        # set openblas provides lapack
        set(OPENBLAS_PROVIDES_LAPACK TRUE)
        # use static libs
        set(BUILD_SHARED_LIBS FALSE)
        FetchContent_Populate(armadillo)
        add_subdirectory(${armadillo_SOURCE_DIR} ${armadillo_BINARY_DIR})
        # Get the HDf5 include dir from armadillo
        get_directory_property(HDF5_INCLUDE_DIR DIRECTORY ${armadillo_SOURCE_DIR} DEFINITION ARMA_HDF5_INCLUDE_DIR)
    endif()
endif()

# Download and include bspline-fortran library
FetchContent_Declare(
    bspline-fortran
    GIT_REPOSITORY https://github.com/vanandrew/bspline-fortran.git
    GIT_TAG        c98236e58800b06f3207a0de0c3de1cb2a37f06e
)
FetchContent_GetProperties(bspline-fortran)
if(NOT bspline-fortran_POPULATED)
    include(CMakeAddFortranSubdirectory)
    include(FortranCInterface)
    FetchContent_Populate(bspline-fortran)
    cmake_add_fortran_subdirectory(
        ${bspline-fortran_SOURCE_DIR}
        PROJECT bspline-fortran NO_EXTERNAL_INSTALL)
    FortranCInterface_HEADER(${bspline-fortran_BINARY_DIR}/include/FCheader.h
        MACRO_NAMESPACE "FC_"
        SYMBOL_NAMESPACE "FC_"
        SYMBOLS bspline_sub_module:db3ink db3interp)
    target_include_directories(bspline-fortran INTERFACE ${bspline-fortran_BINARY_DIR}/include)
    # Setup the C interface interface for bspline
    add_library(bsplineinterface STATIC ${PROJECT_SOURCE_DIR}/include/bsplineinterface/bsplineinterface.h)
    target_include_directories(bsplineinterface PUBLIC ${PROJECT_SOURCE_DIR}/include/bsplineinterface)
    target_link_libraries(bsplineinterface PUBLIC bspline-fortran PRIVATE gfortran)
    set_target_properties(bsplineinterface PROPERTIES LINKER_LANGUAGE C)
endif()

# setup GLOBAL compile options
# use native if COMPILE_ARCH env variable not specified
set(COMPILE_ARCH $ENV{COMPILE_ARCH})
if(NOT DEFINED COMPILE_ARCH)
    set(COMPILE_ARCH "native")
endif()
message("-- Setting march=${COMPILE_ARCH}")
add_compile_options(-flto -O3 -march=${COMPILE_ARCH})

# Download and include optimlib library
FetchContent_Declare(
    optimlib
    GIT_REPOSITORY https://github.com/kthohr/optim.git
    GIT_TAG        dfe0e230ca3bf001662bc4a8e2fddcba4fe7cc63
)
FetchContent_GetProperties(optimlib)
if(NOT optimlib_POPULATED)
    FetchContent_Populate(optimlib)
    # Add optimlib library
    file(GLOB OPTIMLIB_SOURCES ${optimlib_SOURCE_DIR}/src/*/*.cpp)
    add_library(optimlib STATIC ${OPTIMLIB_SOURCES})
    target_include_directories(optimlib PUBLIC ${optimlib_SOURCE_DIR}/include ${HDF5_INCLUDE_DIR})
    target_link_libraries(optimlib PRIVATE OpenMP::OpenMP_CXX armadillo)
    target_compile_definitions(optimlib PUBLIC -DOPTIM_ENABLE_ARMA_WRAPPERS)
    target_compile_options(optimlib PRIVATE -ffp-contract=fast -DNDEBUG -DARMA_NO_DEBUG)
endif()

# find fftw3
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake_aux)
find_package(FFTW REQUIRED COMPONENTS DOUBLE_OPENMP_LIB)

# display all warnings
add_compile_options(-Wall)

# Add fft interface
add_library(fftarma STATIC ${PROJECT_SOURCE_DIR}/src/fftarma.cpp)
target_include_directories(fftarma PUBLIC ${PROJECT_SOURCE_DIR}/include/fftarma)
target_link_libraries(fftarma PRIVATE OpenMP::OpenMP_CXX FFTW::DoubleOpenMP armadillo)

# Add omniimg library
add_library(omniimg STATIC ${PROJECT_SOURCE_DIR}/src/omniimg.cpp)
target_include_directories(omniimg PUBLIC ${PROJECT_SOURCE_DIR}/include/omniimg)
target_link_libraries(omniimg PUBLIC armadillo)

# Add omnitable library
add_library(omnitable STATIC ${PROJECT_SOURCE_DIR}/src/omnitable.cpp)
target_include_directories(omniimg PUBLIC ${PROJECT_SOURCE_DIR}/include/omnitable)
target_link_libraries(omnitable PUBLIC omniimg)

# Add resample library
add_library(resample STATIC ${PROJECT_SOURCE_DIR}/src/resample.cpp)
target_include_directories(resample PUBLIC ${PROJECT_SOURCE_DIR}/include/resample)
target_link_libraries(resample PRIVATE armadillo omnitable bsplineinterface)

# Add regression library
add_library(regression STATIC ${PROJECT_SOURCE_DIR}/src/regression.cpp)
target_include_directories(regression PUBLIC ${PROJECT_SOURCE_DIR}/include/regression)
target_link_libraries(regression PRIVATE armadillo omnitable resample fftarma)

# Add transform library
add_library(transform STATIC ${PROJECT_SOURCE_DIR}/src/transform.cpp)
target_include_directories(transform PUBLIC ${PROJECT_SOURCE_DIR}/include/transform)
target_link_libraries(transform PRIVATE armadillo omnitable resample)

# add optimize library
add_library(optimize STATIC ${PROJECT_SOURCE_DIR}/src/optimize.cpp)
target_include_directories(optimize PUBLIC ${PROJECT_SOURCE_DIR}/include/optimize)
target_link_libraries(optimize PUBLIC optimlib PRIVATE resample armadillo omnitable)

# Add pyinterface
pybind11_add_module(omni MODULE ${PROJECT_SOURCE_DIR}/src/omniinterface.cpp)
target_link_libraries(omni PRIVATE resample omnitable optimize regression transform)

# set install omni target
install(TARGETS omni LIBRARY DESTINATION lib)
