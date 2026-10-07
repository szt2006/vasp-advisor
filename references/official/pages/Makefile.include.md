{{DISPLAYTITLE:makefile.include}}

Writing a makefile.include file from scratch is not easy, so we suggest taking one of archetypical files that closely resembles your system as a starting point. It is necessary to customize it anyways to set appropriate paths etc. Optionally, you can enable additional features by setting precompiler flags or linking VASP to other libraries. For instance, we strongly recommend enabling HDF5 support.
{{NB|mind|Always use makefile.include files released together with the version of VASP that you are compiling. Old archetypical files may not work for newer releases and vice versa.}}
## Archetypical files
The templates contain information such as precompiler options, compiler options, and how to link libraries. Choose the template based on the compiler, parallelization etc. from the list below and mind the description:
### Intel Composer suite and oneAPI HPC toolkit (https://software.intel.com/content/www/us/en/develop/tools/oneapi/all-toolkits.html) for CPU and GPU
* makefile.include.oneapi: Parallelized using MPI, combined with MKL using the newer IFX compiler.
* makefile.include.oneapi_omp: Parallelized using MPI + OpenMP, combined with MKL, using the newer IFX compiler.
* makefile.include.oneapi_omp_off: OpenMP offloading port for Intel datacenter GPUs.
* makefile.include.intel: Parallelized using MPI, combined with MKL, using the older IFC compiler.
* makefile.include.intel_omp: Parallelized using MPI + OpenMP, combined with MKL, using the older IFC compiler.
* makefile.include.intel_ompi_mkl_omp: Parallelized using OpenMPI + OpenMP, combined with MKL, using the older IFC compiler.
* makefile.include.intel_serial: Not parallelized, strongly reduced feature-set, i.e., not suitable for production.
### GNU compilers for CPUs
* makefile.include.gnu: Parallelized using MPI, Free and Open-Source Software (FOSS) stack.
* makefile.include.gnu_omp: Parallelized using MPI + OpenMP, FOSS stack.
* makefile.include.gnu_ompi_mkl_omp: Parallelized using OpenMPI + OpenMP, combined with MKL.                   
* makefile.include.gnu_ompi_aocl: Parallelized using OpenMPI, combined with AMD Optimizing CPU Libraries (AOCL).        
* makefile.include.gnu_ompi_aocl_omp: Parallelized using OpenMPI + OpenMP, combined with AOCL.
### NVIDIA HPC-SDK (https://developer.nvidia.com/hpc-sdk) for CPU and GPU
* makefile.include.nvhpc: CPU version parallelized using MPI. 
* makefile.include.nvhpc_omp: CPU version parallelized using MPI + OpenMP.
* makefile.include.nvhpc_ompi_mkl_omp: CPU version parallelized using OpenMPI + OpenMP, combined with MKL.  
* makefile.include.nvhpc_acc: Ported to GPUs using OpenACC, parallelized using MPI .
* makefile.include.nvhpc_omp_acc: Ported to GPUs using OpenACC, parallelized using MPI + OpenMP.
* makefile.include.nvhpc_ompi_mkl_omp_acc: Ported to GPUs using OpenACC, parallelized using OpenMPI + OpenMP, combined with MKL.
### Cray compiler environment (CCE) for CPU and GPU
* makefile.include.cray: Parallelized using MPI for CPU
* makefile.include.cray_omp: Parallelized using MPI + OpenMP for CPU
* makefile.include.cray_omp_off: OpenMP offloading port for AMD datacenter GPUs.
### Others
* makefile.include.nec_aurora

* makefile.include.fujitsu_a64fx       
* makefile.include.fujitsu_a64fx_omp 
* makefile.include.aocc_ompi_aocl
* makefile.include.aocc_ompi_aocl_omp
* makefile.include.amdflang
* makefile.include.amdflang_omp

An advanced system administrator might benefit from a more detailed discussion about the precompiler options, compiler options, and how to link libraries.
## Customize
Open the selected template of the archetypical files and add the required information as explained in the comments towards the end of the file. 
Then, add any optional feature as listed below. For more details see the list of precompiler options.
### HDF5 support (strongly recommended, and mandatory for some features)
----
The HDF5 library is is needed for reading and writing HDF5 files such as {{FILE|vaspin.h5}}, {{FILE|vaspout.h5}} and {{FILE|vaspwave.h5}}.
The library is available for download on the HDF5 official website (https://www.hdfgroup.org/solutions/hdf5/).
To activate HDF5 support add the following in the VASP makefile.include

 CPP_OPTIONS+= -DVASP_HDF5
 HDF5_ROOT  ?= /path/to/your/hdf5/installation
 LLIBS      += -L$(HDF5_ROOT)/lib -lhdf5_fortran
 INCS       += -I$(HDF5_ROOT)/include

Available for VASP >{{=}} 6.2.0.
{{NB|mind|If you are statically linking to HDF5, you will need to include: <b>-I$(HDF5_ROOT)/mod/static</b> after INCS +{{=}} -I$(HDF5_ROOT)/include .}}
{{NB|warning|This is required to perform some features of VASP, e.g. electron-phonon coupling, and is required for py4vasp.}}
### fftlib (recommended when using OpenMP)
----
When you plan to run VASP on multiple OpenMP threads and you are not using the FFTs from the Intel-MKL library, you should link against fftlib (included in the VASP distribution).
To do so, uncomment the corresponding sections in the makefile.include.*_omp files. In makefile.include.gnu_omp, for instance, that would be:

 # For the fftlib library (recommended)
 CPP_OPTIONS+= -Dsysv
 FCL        += fftlib.o
 CXX_FFTLIB  = g++ -fopenmp -std=c++11 -DFFTLIB_THREADSAFE
 INCS_FFTLIB = -I./include -I$(FFTW_ROOT)/include
 LIBS       += fftlib
 LLIBS      += -ldl
### Wannier90 (optional)
----
To include the Wannier90 program, download the library from the source (http://www.wannier.org) and compile libwannier.a.
{{NB|important|In case of Wannier90 3.x, you should compile a serial version by removing COMMS{{=}}mpi in the make.inc of Wannier90.}} Then, execute make lib to build the Wannier90 library. To activate this feature set the following:

 CPP_OPTIONS    += -DVASP2WANNIER90
 WANNIER90_ROOT ?= /path/to/your/wannier90/installation
 LLIBS          += -L$(WANNIER90_ROOT)/lib -lwannier
{{NB|mind| VASP version <{{=}} 6.1.x are compatible with Wannier90 <{{=}} 1.2. To interface VASP 6.1.x with Wannier90 2.x, set -DVASP2WANNIER90v2 instead. As of VASP 6.2.x only Wannier90 2.x and 3.x are supported.}}
### Libxc (optional)
----
To include the Libxc library of exchange-correlation functionals, install the library from the source (https://libxc.gitlab.io/download/) and install it. Note that to get correct results with meta-GGA functionals (see discussion at {{TAG|LTBOUNDLIBXC}}), it is necessary to use Libxc from version 5.2.0 onwards (or the master version from gitlab (https://gitlab.com/libxc/libxc) for the latest implemented functionals) and to compile it with the option --disable-fhc. For instance, with GNU Autotools the steps to compile Libxc are (note that shared libraries are built by default since Libxc version 7.1.0)
 autoreconf -i (necessary is the executable configure is not already present)
 ./configure --prefix=PATH/TO/LIBXC --disable-fhc --disable-shared
 make
 make install

Then, add the following in the VASP makefile.include

 CPP_OPTIONS += -DUSELIBXC
 LIBXC_ROOT  ?= /path/to/your/libxc/installation
 LLIBS       += -L$(LIBXC_ROOT)/lib -lxcf03 -lxc
 INCS        += -I$(LIBXC_ROOT)/include
### Libbeef (optional)
----
To include the BEEF van der Waals functionals, install the library from the source on GitHub (https://github.com/vossjo/libbeef) and add the following in the VASP makefile.include

 CPP_OPTIONS  += -Dlibbeef
 LIBBEEF_ROOT ?= /path/to/your/libbeef/installation
 LLIBS        += -L$(LIBBEEF_ROOT)/lib -lbeef
### DFT-D4 and simple-DFT-D3 (optional)
----
To link to the DFT-D4 and/or simple-DFT-D3 packages of van der Waals methods, install
* the modular computation tool chain library (mctc-lib) from https://github.com/grimme-lab/mctc-lib (must be installed before DFT-D4 and simple-DFT-D3)
* the DFT-D4 package from https://github.com/dftd4/dftd4, which should in principle find the mctc-lib pre-installation
* the simple-DFT-D3 package from https://github.com/dftd3/simple-dftd3, which should in principle find the mctc-lib pre-installation
Then, the VASP makefile.include should include the following lines:

 # DFT-D4
 CPP_OPTIONS += -DDFTD4
 DFTD4_ROOT  ?= /path/to/your/dft4/installation
 LLIBS       += -L$(DFTD4_ROOT)/lib64 -ldftd4 -lmulticharge
 INCS        += -I$(DFTD4_ROOT)/include
 # simple-DFT-D3
 CPP_OPTIONS += -DSDFTD3
 SDFTD3_ROOT ?= /path/to/your/simple-dft3/installation
 LLIBS       += -L$(SDFTD3_ROOT)/lib64 -ls-dftd3
 INCS        += -I$(SDFTD3_ROOT)/include
 # mctc-lib
 MCTC_ROOT   ?= /path/to/your/mctc-lib/installation
 LLIBS       += -L$(MCTC_ROOT)/lib64 -lmctc-lib
 INCS        += -I$(MCTC_ROOT)/include
{{NB|mind|
*The API of DFT-D4 has been modified starting with version 4.0.0. The adaptation has been made in VASP.6.6.0. Versions of DFT-D4 with the old API (v3.7.0 and older) can still be compiled with VASP.6.6.0 by using -DDFTD4_API_V3 instead of -DDFTD4.
*The pre-installation of mctc-lib is not strictly required. If it is not the case, then it will be installed automatically during the installation of DFT-D4 and simple-DFT-D3. However, it is strongly recommended to pre-install mctc-lib, otherwise problems with the GNU compiler may occur if both DFT-D4 and simple-DFT-D3 are installed.}}
### ELPA (optional)
----

To include the ELPA eigenvalue solvers, install the library from the source on GitLab (https://gitlab.mpcdf.mpg.de/elpa/elpa) and add the following in the VASP makefile.include

 CPP_OPTIONS += -DELPA
 ELPA_ROOT   ?= /path/to/your/elpa/installation
 LLIBS       += -L$(ELPA_ROOT)/lib -lelpa
 INCS        += -I$(ELPA_ROOT)/include/elpa-<version>/elpa
 INCS        += -I$(ELPA_ROOT)/include/elpa-<version>/modules
{{NB|mind| In the above you need to replace <version> by the correct designation of your ELPA version.}}
### libMBD (optional)
----

To include the library libMBD of many-body dispersion methods, install the library from the source on GitHub (https://github.com/libmbd/libmbd) and add the following in the VASP makefile.include

 CPP_OPTIONS += -DLIBMBD 
 LIBMBD_ROOT ?= /path/to/your/libMBD/installation
 LLIBS       += -L$(LIBMBD_ROOT)/build/src -lmbd
 INCS        += -I$(LIBMBD_ROOT)/build/src/modules/
{{NB|mind|To run a calculation the path to libmbd.so has to be added (either in .bashrc or in the terminal): LD_LIBRARY_PATH{{=}}$LD_LIBRARY_PATH:/path/to/your/libMBD/installation/build/src. Alternatively you need to compile libmbd with cmake -DBUILD_SHARED_LIBS{{=}}OFF which will produce a static library libmbd.a}}
{{NB|important|It is recommended to compile libMBD without ScaLAPACK/MPI using cmake -DENABLE_SCALAPACK_MPI{{=}}OFF, otherwise nudged elastic bands (NEB) calculations will not run properly and produce wrong results.}}
### Plugins (optional)
----

Create a new conda (https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) environment. Alternative environment creation packages should work, but we have not tested them.
    conda create -n vasp_plugin python=3.10
Enter the create vasp_plugin conda environment
    conda activate vasp_plugin
Navigate to the plugins directory within VASP source code,
    cd /src/plugins
Install the VASP Python package through pip (https://pip.pypa.io/en/stable/installation)
    pip install .
{{NB|mind|Make sure to be within the conda environment when you compile VASP.}}
Add the following lines to your makefile.include
    CPP_OPTIONS+= -DPLUGINS
    LLIBS      += $(shell python3-config --ldflags --embed) -lstdc++
    CXX_FLAGS   = $(shell python3 -m pybind11 --includes) -std=c++11
{{NB|mind|When running VASP with the Python interface you will need to add the lib directory of your Python to LD_LIBRARY_PATH. You can do this by running export LD_LIBRARY_PATH{{=}}$LD_LIBRARY_PATH:$(python3-config --prefix)/lib}}
### SCPC (optional)
----
The Self-Consistent Potential Correction (SCPC) method is implemented in VASP version 6.2 and later. A patch to add SCPC functionality to VASP 5.4.4, along with various bug fixes for the implementation in VASP 6, can be obtained from the authors (https://github.com/aradi/SCPC-Method). 

To compile the VASP with SCPC support, you need the DL_MG (https://bitbucket.org/dlmgteam/dl_mg_code_public/downloads/) and PSPFFT (https://code.ornl.gov/reubendb/pspfft) libraries to solve the Poisson equations and handle isolated potentials. After downloading and compiling these libraries, activate SCPC support during VASP compilation by adding the following snippet to the end of the makefile.include file, adjusting the paths to match your DL_MG and PSPFFT installation: 

  # SCPC METHOD
  CPP_OPTIONS += -DSCPC
  SCPC_LIBEXT  = /scpc/libext 
  DLMGROOT   = $(SCPC_LIBEXT)/dl_mg 
  PSPFFTROOT = $(SCPC_LIBEXT)/pspfft 
  INCS      += -I$(DLMGROOT)/include 
  INCS      += -I$(PSPFFTROOT)/include 
  LLIBS     += -L$(DLMGROOT)/lib -ldlmg 
  LLIBS     += -L$(PSPFFTROOT)/lib -lpspfft
### VASPml (experimental)
----
The VASPml library is a {{VASP}}-internal C++ library, providing functionality related to machine-learned force fields. The VASPml library is automatically built alongside {{VASP}} if -Dlibvaspml is added to the CPP_OPTIONS precompiler options in the makefile.include file. In addition, a few more compiler settings regarding the C++ compiler, include paths and VASPml options may be required. The makefile.include templates provided in {{VASP}}'s arch directory contain pre-filled blocks corresponding to the VASPml build. Uncomment the VASPml-related lines and fill with values according to your toolchain. For example, when using the GCC toolchain with OpenBLAS the makefile.include section may look like this:
 ...
 # For machine learning library VASPml (experimental)
 CPP_OPTIONS += -Dlibvaspml
 CXX_ML       = mpic++
 CXXFLAGS_ML  = -O3 -std=c++17 -Wall -Wextra
 INCLUDE_ML   = -I$(OPENBLAS_ROOT)/include
 ...
Apart from the mandatory -Dlibvaspml and optional precompiler flags VASPml requires to set its own compiler, flags and include path:
* CXX_ML: This should be a C++17-compatible C++ compiler with MPI support (usually an MPI wrapper corresponding to the selected toolchain, e.g. mpic++, mpicxx, mpicpx or mpinc++).
* CXXFLAGS_ML: Specifies the flags for the C++ compiler. Typically, here the optimization level (-O3) and the compliance with C++17 is specified.
* INCLUDE_ML: Include flags for the required dependencies should be added here. {{NB|tip|For some toolchains it is not necessary to explicitly add paths here because the compilers automatically include the correct directories (e.g. Intel oneAPI, NVHPC). In other cases (e.g. GNU compiler with openBLAS) the given path must contain the desired C++ headers of the dependencies:
* CBLAS: cblas.h
* LAPACKE: lapacke.h|:}}

The VASPml project (source code and related files) is located within the src/vaspml directory relative to the {{VASP}} root folder. Upon compilation it is copied to the build/std, build/gam and/or build/ncl build folders, just like all other {{VASP}} sources. If the VASPml library was successfully compiled libvaspml.a will be located in build/std/vaspml/lib/ (similarly for the gam and ncl versions). However, it is usually not necessary to check its presence because the {{VASP}} build will handle this (and fail if VASPml cannot be built).
#### GRACE support
Optionally, VASPml may be compiled with support for GRACE machine-learned force fields. However, there are two  additional dependencies to third-party software (libtensorflow (https://www.tensorflow.org/install/lang_c) and cppflow (https://github.com/serizba/cppflow)) which must be installed beforehand:
:* **libtensorflow (https://www.tensorflow.org/install/lang_c)**: This is a pre-compiled C library which runs TensorFlow models. Its website provides downloadable archives but we actually recommend a simpler way of installing it (and all of its dependencies) via conda (https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) and pip:
{{CB|conda create -n tf python{{=}}3.12
conda activate tf
pip install --upgrade pip
pip install tensorflow[and-cuda]|::}}
::This will install all necessary libraries and header files into a directory which can be identified by running 
{{CB|dirname $(python -c 'import tensorflow as tf; print(tf.__file__)' 2>/dev/null)|::}}
::in a shell while the conda environment is still active. This path is required below in the TENSORFLOW_ROOT variable.
:* **cppflow (https://github.com/ACEworksGmbH/cppflow)**: This is a C++ library which simplifies loading of TensorFlow models. Because it is a header-only library, no separate build process and linking is required to use it. To prepare its use for VASPml, just download it from its website and save it to a directory of your preference. For example, use git clone git@github.com:ACEworksGmbH/cppflow.git or download and unpack an archive from here (https://github.com/ACEworksGmbH/cppflow/releases). {{NB|important|Starting with {{VASP}} 6.6.1 the cppflow from the original author (https://github.com/serizba/cppflow) is not sufficient, please always use the ACEWorks fork (https://github.com/ACEworksGmbH/cppflow).|::}}

Finally, with the mandatory dependencies installed, extra lines need to be added in the makefile.include to build {{VASP}} with GRACE support. As of {{VASP}} 6.6.0 the makefile.include.gnu contains an example block, similar to this:
 ...
 # Support for GRACE force fields (requires VASPml, experimental)
 CPP_OPTIONS     += -DVASPML_ENABLE_GRACE
 CPPFLOW_ROOT    ?= /path/to/your/cppflow/installation
 TENSORFLOW_ROOT ?= /path/to/your/tensorflow/installation
 INCLUDE_ML      += -I$(CPPFLOW_ROOT)/include -I$(TENSORFLOW_ROOT)/include
 LLIBS           += $(TENSORFLOW_ROOT)/libtensorflow_cc.so.2 $(TENSORFLOW_ROOT)/libtensorflow_framework.so.2
 LLIBS           += -Wl,-rpath,$(TENSORFLOW_ROOT)
 ...
{{NB|tip|The conda environment created for downloading the libtensorflow library is neither required for compiling nor for running {{VASP}}! With the line LLIBS           +{{=}} -Wl,-rpath,$(TENSORFLOW_ROOT) the path to the Tensorflow library is imprinted into the {{VASP}} binary and hence no environment is required to load it at runtime.}}
## Related articles
Installing VASP.6.X.X,
Compiler options,
Precompiler options,
Linking to libraries,
GPU ports of VASP,
VASPml library,
Toolchains,
Validation tests,
Known issues

----

Category:VASPCategory:InstallationCategory:PerformanceCategory:GPU
