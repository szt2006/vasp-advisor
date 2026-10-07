As a license holder (https://vasp.at), you can download the source code of VASP from the VASP Portal (https://vasp.at) (and verify your download with the accompanying checksums file). If your system fulfills the  requirements, you can install VASP.6.X.X by following the steps below. There are two separate ways to install VASP:
# With the traditional makefile.include templates included in the /path/to/vasp.x.x.x/arch directory. See section Install VASP with makefile.include.
# Using the CMake build system. See section Install VASP with CMake.

There is a separate guide to installing VASP.5.X.X.
## Requirements
For the compilation of VASP one needs:

* Compilers for Fortran (at least F2008 compliant), C, and C++. For instance, one of the following compiler suites:
:- gcc (https://gcc.gnu.org)
:- intel-oneapi-base-kit (https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#base-kit)+intel-oneapi-hpc-kit (https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#hpc-kit)
:- NVIDIA HPC-SDK (https://developer.nvidia.com/hpc-sdk)
:- AOCC (https://developer.amd.com/amd-aocc) (for AMD CPUs)
{{NB|mind| For the GPU ports of VASP on must use the compilers from the NVIDIA HPC-SDK (https://developer.nvidia.com/hpc-sdk) (>{{=}}21.2) (to run on NVIDIA GPUs), the  HPE Cray compiler environment CCE (https://cpe.ext.hpe.com/docs/25.03/cce/index.html) (>{{=}} 19.0) (to run on AMD GPUs), or the Intel Intel Fortran Compiler IFX (https://www.intel.com/content/www/us/en/developer/tools/oneapi/fortran-compiler.html) (>{{=}}2025.3.0) (to run on Intel GPUs)|:}}

* Numerical libraries: FFTW, BLAS, LAPACK, and ScaLAPACK. For example, one of the following combinations:
:- intel-oneapi-mkl (https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#base-kit)
:- FFTW (http://www.fftw.org) + OpenBLAS (https://www.openblas.net) + ScaLAPACK (http://www.netlib.org/scalapack)
:- NVIDIA HPC-SDK (https://developer.nvidia.com/hpc-sdk) (comes with OpenBLAS and ScaLAPACK) + FFTW (http://www.fftw.org)
:- AOCL (https://developer.amd.com/amd-aocl) (for AMD CPUs)

* An implementation of the Message Passing Interface (MPI). For instance, one of the following:
:- intel-oneapi-mpi (https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#hpc-kit)
:- OpenMPI (https://www.open-mpi.org)
:- NVIDIA HPC-SDK (https://developer.nvidia.com/hpc-sdk) (comes with OpenMPI)

These are the required components to build VASP. Additionally, we strongly recommend enabling HDF5 support by providing a suitable HDF5 library in the makefile.include file (see the HDF5 section here). Optional features available through external libraries such as libxc, libbeef, and others can also be found here. 

To find a combination of compilers and libraries that works, have a look at our list of validated toolchains. On a personal computer, i.e., your desktop machine or laptop, you may use these validated instructions.
## Install VASP with makefile.include
### Step 1: Download
:Download the source code of VASP from the VASP Portal (https://vasp.at|), copy it to the desired location on your machine, and unzip the file to obtain the folder /path/to/vasp.x.x.x and reveal its content.
### Step 2: Prepare makefile.include
:Create a makefile.include starting from a template in /path/to/vasp.x.x.x/arch that resembles your system:

:cp arch/makefile.include.your_choice  ./makefile.include

:Adapt your makefile.include file to your system and select optional features.
### Step 3: Make
:Build VASP with

: make DEPS=1 -jN <target>

:where  DEPS=1 -jN is optional and selects the parallel mode of make with N being the number of jobs you want to run, and <target> corresponds to std, gam, ncl or  all. This builds the standard, gamma-only, noncollinear or all versions of VASP. The executables are vasp_std, vasp_gam, and vasp_ncl, respectively, which are located at /path/to/vasp.X.X.X/bin/.
### Step 4: Test
:Run the test suite with 

: make test

:to confirm the build was successful.
{{NB|tip|If there are issues, the VASP Forum https://www.vasp.at/forum/viewforum.php?f=2 installation issues is the appropriate place to seek support.|:}}
{{NB|warning|VASP.6.1.0, VASP.6.1.1, and VASP.6.1.2 have a potentially serious issue related to the test suite. Please read about it in the known issues.|:}}
### Step 5: Install
:Copy the executables to the system $PATH or append /path/to/vasp.x.x.x/bin/ to the environment variable with

: export PATH=$PATH:/path/to/vasp.x.x.x/bin

:for instance in your ~/.bashrc. Consider also setting ulimit -s unlimited and OMP_STACKSIZE=512m before running the program (or put it in your job script / ~/.bashrc) to ensure sufficient stack memory for each OpenMP thread (if OpenMP support was activated) and prevent segmentation faults caused by large stack allocations in the code.
## Install VASP with CMake
As an alternative to the traditional Makefile-based build system, VASP can also be compiled using the CMake (https://cmake.org/) build infrastructure provided on 
github.com/vasp-dev/cmake (https://github.com/vasp-dev/cmake). This method configures the build automatically detecting compilers and external libraries on the fly. Requires cmake version 3.24 or later.
### Step 1: Download VASP
Download the VASP source code from the VASP Portal (https://vasp.at|) and unpack:

tar -xf vasp.X.X.X.tgz
cd vasp.X.X.X
### Step 2: Download CMake files
Next obtain the CMake build infrastructure from our github repository (https://github.com/vasp-dev/cmake):

git clone -b 6.6.x https://github.com/vasp-dev/cmake.git

run now the following command to prepare the build system:

bash cmake/setup.sh

this will create symbolic links of the CMakeLists.txt files in the source directory.
### Step 3: CMake Configure
Create a separate build directory and configure the project using CMake:

mkdir cmake_build
cd cmake_build
cmake /your/vasp/directory \
  -DVASP_OPENMP=ON \
  -DVASP_HDF5=ON

During configuration CMake automatically searches for required dependencies such as MPI, BLAS/LAPACK, ScaLAPACK, and FFTW. If necessary, their locations can be provided using standard CMake variables (e.g. BLA_VENDOR  for BLAS/LAPACK configuration).

Optional features (e.g. HDF5 support) can be enabled via additional CMake options, -DVASP_HDF5=ON etc. See also the README.md file in the cmake repository for more details on available options.
### Step 4: Build
Compile VASP using:

make -jN

where `N` is the number of parallel build jobs. This will by default build all targets. You can specify which VASP version is build via targets" `vasp_std`, `vasp_gam`, or `vasp_ncl`.

This produces the standard VASP executables (e.g. `vasp_std`, `vasp_gam`, and `vasp_ncl`) in the build/bin directory.
### Step 5: Test
Run the test suite to verify the installation:

make test

Note, that cmake will copy the testsuite into the build dir for running the testsuite.
### Step 6: Install
Optionally install the executables to a chosen location via `-DCMAKE_INSTALL_PREFIX` during configuration, and then run:

make install

Alternatively, copy the generated executables to a directory included in your `$PATH`. Consider also setting ulimit -s unlimited and OMP_STACKSIZE=512m before running the program (or put it in your job script / ~/.bashrc) to ensure sufficient stack memory for each OpenMP thread (if OpenMP support was activated) and prevent segmentation faults caused by large stack allocations in the code.
## Subdirectories in vasp.6.x.x
The build system of VASP (as of versions >= 5.4.1) comprises the following subdirectories:

                   vasp.x.x.x (root directory)
  ------------------------------------------------
  |        |         |          |         |
        arch     bin     build      src     testsuite   tools
  ----------------------
  |      |        |       
                             lib   parser  fftlib  vaspml

;/path/to/vasp.x.x.x/
:Holds the high-level makefile and several subdirectories.

;/path/to/vasp.x.x.x/src
:Holds the source files of VASP and a low-level makefile.

;/path/to/vasp.x.x.x/src/lib
:Holds the source of the VASP library (used to be vasp.X.lib) and a low-level makefile.

;/path/to/vasp.x.x.x/src/parser
:Holds the source of the {{TAG|LOCPROJ}} parser (as of versions >= 5.4.4) and a low-level makefile.

;/path/to/vasp.x.x.x/src/fftlib
:Holds the source of the fftlib library that may be used to cache fftw plans.

;/path/to/vasp.x.x.x/src/vaspml
:Holds the source of the vaspml library containing machine-learning features (versions >= 6.5.0).

;/path/to/vasp.x.x.x/arch
:Holds a collection of makefile.include.* files.
	
;/path/to/vasp.x.x.x/build
:The different versions of VASP, i.e., the standard, gamma-only, non-collinear versions will be built in separate subdirectories of this directory.

;/path/to/vasp.x.x.x/bin
:Here make will store the executables.

;/path/to/vasp.x.x.x/testsuite
:Holds a suite of correctness tests to check your build.

;/path/to/vasp.x.x.x/tools
:Holds several python scripts related to the use of HDF5 input/output files.
## Validated Toolchains via CI
Please find on this toolchains page a comprehensive guid on which software stacks and versions are validated by our CI. Makefiles for those validated toolchains can be found in the arch subdirectory in VASP, or on this separate page.
## Install on a common Linux distribution
If you plan to install VASP on any of the big linux distributions e.g. Debian, Ubuntu, Fedora, or Rocky Linux, please take a closer look on the separate page for Personal computer installations. There you also find instructions for Max OS X on M-series chips. For installation under Windows 11, please use WSL to install one of the supported distributions first.
## Related sections
Toolchains,
makefile.include,
Precompiler options,
Compiler options,
Linking to libraries,
Validation tests,
GPU ports of VASP

Category:VASP
Category:Installation
Category:Performance
Category:GPU
