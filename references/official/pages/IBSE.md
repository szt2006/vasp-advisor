{{TAGDEF|IBSE|0 {{!}} 1 {{!}} 2 {{!}} 3 |2}}

Description: {{TAG|IBSE}} can be used to select the algorithm for solving the Bethe-Salpeter or Casida equation.
----
The following options are available to solve the Bethe-Salpeter or Casida equation:
*{{TAG|IBSE}} = 0: Exact diagonalization with old BSE driver
*{{TAG|IBSE}} = 1: Time evolution
*{{TAG|IBSE}} = 2:  Exact diagonalization
*{{TAG|IBSE}} = 3: Lanczos algorithm

{{TAG|IBSE|2}} and {{TAG|IBSE|0}} yield exactly the same results but the old driver ({{TAG|IBSE|0}}) is typically much slower and will be deprecated in the future.
{{NB|mind| {{TAG|IBSE|2}} and {{TAG|IBSE|3}} are only available for VASP version 6.5.0 and above.}}
## Scientific output
Not all solvers provide all types of scientifically relevant output. The table below summarises for each value of IBSE what kinds of results can be obtained. 
  rowspan="2" | Output type !! rowspan="2" | Output file(s) !! colspan="4" | IBSE
  0 !! 1 !! 2 !! 3
  Dielectric function
  {{FILE|vasprun.xml}}, {{FILE|vaspout.h5}} || Yes || Yes || Yes || Yes
  Optical transitions
  {{FILE|vasprun.xml}}, {{FILE|vaspout.h5}} || Yes || No || Yes || Yes
  BSE fatbands1
  {{FILE|BSEFATBAND}}, {{FILE|vaspout.h5}} || Yes || No || Yes || No
  Exciton wavefunction1,2
  {{FILE|CHG}}.X (X = excitonic state index), {{FILE|vaspout.h5}} || Yes || No || Yes || No
  colspan="6" style="background: ; font-size: 90%;" |
1 Only written if {{TAG|NBSEEIG}} is set in the INCAR

2 Only written if one of {{TAG|BSEHOLE}} or {{TAG|BSEELECTRON}} is set in the INCAR
## Performance output
Besides the numerical results, different solvers will write different information on the OUTCAR. In the following examples we used a small bulk-LiF unit cell on a sparse k-grid.
### IBSE = 0,2
The old  and new BSE driver perform exact diagonalization of the BSE Hamiltonian. At the end they only provide information on how long it took to diagonalize the matrix and how long it needed to compute the optical amplitudes.
### IBSE = 1
At the end of the run the time-evolution solver will write to the OUTCAR the relevant parameters used in its execution, as well as how long it took to perform the full computation. 

 Time evolution parameters used:
 -------------------------------

 Calculating BSE spectra using full res.-antires. coupling
 Matrix rank:       2430

  Omega_max:   94.2354
 Broadening:    0.4000
      T_max:   25.0000
    BSEPREC:  Accurate
     Scheme:  3rd order update equations

 Number of time steps:     9423

 First time step:  0.265293E-02 1/eV
 Last  time step:  0.265293E-02 1/eV

 dOmega  :  0.01000
 N_Omega :   9425

 CPU time (time steps)        55.76sec

    BSE_TE:  cpu time     60.0951: real time     65.1642
### IBSE = 3
The Haydock-Lanczos solver terminates the calculation once the trace of the dielectric function converges. At the end, information about convergence of the dielectric function along each direction is written to the OUTCAR file.  

 Parameters set for Lanczos algorithm
   Threshold:  0.1000000E-04
   Maximum energy:   94.235
    Number of energy steps:         1000
    Number of iterations needed to reach set accuracy:         250
    Final accuracy along all directions:
    x          0.6277122E-05
    y          0.4480512E-05
    z          0.1392376E-04
    xy         0.1792577E-04
    yz         0.4541156E-05
    zx         0.1034294E-04
## Related tag and articles
{{TAG|IBSE}},
{{TAG|BSEPREC}},
{{TAG|NBANDSV}},
{{TAG|NBANDSO}},
{{TAG|CSHIFT}},
{{TAG|OMEGAMAX}},
BSE calculations,
Time-dependent density-functional theory calculations,
Bethe-Salpeter equations
----
Category:INCAR tag Category:Many-body perturbation theoryCategory:Bethe-Salpeter equations
