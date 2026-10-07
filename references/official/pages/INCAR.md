The {{FILE|INCAR}} file is the central input file of VASP, which determines *what to do and how to do it*. The INCAR tags specified in the {{FILE|INCAR}} file select the algorithms and set the parameters that VASP uses during the calculation. VASP will use reasonable default values, which we recommend using when unsure. Yet, the settings in the {{FILE|INCAR}} file are the main source of errors and false results, so we suggest carefully checking the meaning of the set INCAR tags. Regarding the format, each statement consists of the name of a tag, the equal sign **=**, and the values assigned to the tag (tag = values). For instance, an {{FILE|INCAR}} file for a density-functional-theory calculation might read
   {{TAG|ALGO}}  = Normal # alorithm for electron optimization
   {{TAG|ISMEAR}}= -1     # Fermi smearing
   {{TAG|SIGMA}} = 0.05   # width of the smearing in eV
{{NB|tip|VASP writes its interpretation of the data in the {{FILE|INCAR}} file to the {{FILE|OUTCAR}} file. Please verify that it agrees with the intended setup.}}
## Format
The {{TAG|INCAR}} file is a tagged format free-ASCII file. That is, each statement follows a *tag = values* syntax. Typically, each line contains a single statement, but it is possible to combine multiple statements on a single line, separating them by a semicolon **;**, e.g.,
   {{TAG|ISMEAR}}= -1 ;  {{TAG|SIGMA}} = 0.05

For better readability, long lines can be split with a backslash **\** . Avoid blanks after the backslash because some versions of VASP cannot parse those. For instance,
   {{TAG|MAGMOM}}  = 0 0 1.0 0 0 -1.0 \
             0 0 1.0 0 0 -1.0 \
             6*0 
is the same as
   {{TAG|MAGMOM}}  = 0 0 1.0 0 0 -1.0 0 0 1.0 0 0 -1.0 0 0 0 0 0 0
Alternatively, enclose all the values in quotes **"** to ignore line breaks between the quotes, e.g.,
   {{TAG|WANNIER90_WIN}} = "
   Begin Projections
   Si:sp3
   End Projections
   "
Some newer features of VASP use nested tags (e.g. {{TAG|KERNEL_TRUNCATION/LTRUNCATE}} or {{TAG|PLUGINS/STRUCTURE}}). You can either specify these tags directly like
   {{TAG|KERNEL_TRUNCATION/LTRUNCATE|T}}
or use curly braces to encapsulate multiple ones to avoid repeating the prefix
   PLUGINS {
      STRUCTURE = T
      NEIGHBOR_CUTOFF = 5.0
   }
This syntax is also used to set specific tags on specific {{TAG|IMAGES}}.

For comments, VASP ignores any text after a hashtag **#** or exclamation mark **!**. Use this to add comments anywhere to the {{FILE|INCAR}} file. A comment prefix (#!) is often unnecessary because VASP ignores all text that does not fit the statement format (tag = values). In this case, do not use any syntax relevant character (=;") because it may break the parsing of the {{FILE|INCAR}} file. VASP generally ignores empty lines, but we have encountered issues due to lines with tabs for some compilers.

A typical (relatively complex) {{FILE|INCAR}}:

 {{TAG|SYSTEM}} = Rhodium surface calculation
 
 start parameters for this Run (automatic defaults, hence not often required)
   {{TAG|ISTART}} =      0    #  job   : 0-new  1- orbitals from WAVECAR
   {{TAG|ICHARG}} =      2    #  charge: 1-file 2-atom 10-const
 
 electronic optimization
   {{TAG|ENCUT}}  = 300.00 eV # defaults from POTCAR, but wise to include
   {{TAG|ALGO}}  =  Normal    # alorithm for electron optimization, can be also FAST or ALL
   {{TAG|NELM}}   = 60        # of ELM steps, sometimes default is too small 
   {{TAG|EDIFF}}  = 1E-06     # stopping-criterion for ELM
  broadening and DOS related values; this works almost always
   {{TAG|SIGMA}}  =    0.05;  {{TAGBL|ISMEAR}} =  0   ! broadening in eV, -4-tet -1-fermi 0-gaus
 
 ionic relaxation
   {{TAG|EDIFFG}} =  -1E-02   # stopping-criterion for IOM (all forces smaller 1E-2)
   {{TAG|NSW}}    =  20       # number of steps for IOM
   {{TAG|IBRION}} =  2        # CG for ions, often 1 (RMM-DISS) is faster
   {{TAG|POTIM}}  =  .5       # step for ionic-motion (for MD in fs)
 performance optimization
   {{TAG|KPAR}}   =    4      # make 4 groups, each group working on one set of k-points 
   {{TAG|NCORE}}  =    4      # one orbital handled by 4 cores 
   {{TAG|LREAL}}  =    A      # real space projection; slightly less accurate but faster
## Related tags and articles
*A comprehensive list of all **INCAR** tags and related articles.
* Other important input files include {{FILE|KPOINTS}}, {{FILE |POSCAR}}, and {{FILE |POTCAR}} 
----

Category:FilesCategory:Input files
