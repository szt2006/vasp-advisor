{{TAGDEF|ALGO|[string]|Normal}}

Description: Selects the electronic-minimization algorithm and/or the many-body method:
:::* Electronic minimization (ground state)
:::** *Self-consistency cycle*: Normal (default), Fast, VeryFast, Exact, Subrot
:::** *Direct optimization*: All / Conjugate, Damped
:::** *Postprocessing*: Eigenval, None / Nothing
:::* Response functions, GW, BSE, and ACFDT/RPA
:::** CHI, TDHF, BSE, Timeev, ACFDT / RPA, ACFDTR / RPAR, and CRPA
:::** *GW variants*: EVGW0, EVGW, QPGW0, QPGW, GW0R, GWR, G0W0R, EVGW0R
----
{{Available|4.5}}
The {{TAG|ALGO}} tag has two kinds of settings: For a ground-state calculation, it selects the **electronic-minimization algorithm** (see Electronic-minimization algorithms section below); that may be one of the self-consistency-cycle minimizers, the direct optimizers, or the postprocessing modes. For many-body perturbation theory, it instead selects the algorithm for response functions, the GW variant, BSE, time evolution, and ACFDT/RPA. The stopping criterion is set using {{TAG|EDIFF}} and {{TAG|NELM}}. We recommend checking the output during the electronic minimization as described below to judge the convergence.
{{NB|tip|To recompute the density of states (DOS), obtain the projected DOS or carry out any postprocessing from existing orbitals (e.g., a {{FILE|WAVECAR}} from a previous run) *without* re-optimizing them, set {{TAG|NELM|1}}, {{TAG|LDIAG|False}}, and {{TAG|ALGO|None}}.  Or to additionally recompute the one-electron energies set {{TAG|ALGO|Eigenval}}.}}
## Electronic-minimization algorithms
For a self-consistent ground-state calculation, {{TAG|ALGO}} selects how the orbitals are optimized at each electronic step. Each value corresponds to a setting of the lower-level tag {{TAG|IALGO}}. The algorithms fall into two groups (see the *Class* column): the self-consistency-cycle methods iterate the charge density with a charge-density mixer, whereas the direct-optimization methods minimize the energy functional directly, updating the density from the orbitals without a charge mixer.
  {{TAG|ALGO}} !! Algorithm !! {{TAG|IALGO}} !! Class !! Notes
  Normal *(default)* || blocked Davidson || 38 || self-consistency cycle || Robust default, recommended for most calculations.
  Fast || blocked Davidson + RMM-DIIS || 68 || self-consistency cycle || Davidson for the initial phase, then RMM-DIIS; one Davidson sweep per ionic step (except the first). This setting is faster and cheaper per electronic step, but less robust and less reliable in the sense that it may diverge or cannot find the true minimum. Use to obtain a first estimate, but mind that orbitals (and hence forces, stress, etc.) may be less accurate compared to Normal or All. Updated in vasp.6.0.0; select Old Fast for the vasp.5 version.
  VeryFast || RMM-DIIS || 48 || self-consistency cycle || Fewest Hamiltonian evaluations but least robust. Not supported for hybrid functionals. Updated in vasp.6; select Old VeryFast for the vasp.5 version. Combine with {{TAG|LDIAG|.FALSE.}} to conserve the initial orbital order.
  Conjugate / All || blocked Davidson + all-band conjugate gradient || 58 || direct optimization || Simultaneous update of all orbitals. The two values are synonymous. Recommended together with the improved line-search algorithm ({{TAG|ISEARCH|1}}). Appropriate choice for magnetic systems and systems where {{TAG|ALGO|Normal}} failed.
  Damped || blocked Davidson + damped molecular dynamics || 53 || direct optimization || Damped velocity-friction dynamics for the orbitals. Robustness and time-to-solution strongly depend on setting {{TAG|TIME}} appropriately.
  Exact || exact diagonalization || 90 || self-consistency cycle || Full diagonalization; expensive and memory-heavy. Use when many empty states are required (restarting from preconverged orbitals) or for testing.
  Subrot || subspace rotation || 4 || self-consistency cycle || Diagonalization within the subspace spanned by the current orbitals. Rarely used stand-alone.
  Eigenval || recompute eigenvalues || 3 || postprocessing || Recompute one-electron energies, the density of states, and selected postprocessing from fixed orbitals (e.g., read from the {{FILE|WAVECAR}} file).
  None / Nothing || no orbital update || 2 || postprocessing || Recompute the density of states or postprocessing from fixed orbitals *and* one-electron energies (e.g., read from the {{FILE|WAVECAR}} file).

{{NB|warning|Only the iterative self-consistency-cycle minimizers support potential-only functionals/methods, e.g., {{TAG|METAGGA|MBJ}} or {{TAG|LSFBXC|True}}. This is because direct optimization relies on the gradient of the energy and not just the potential.}}
{{NB|tip|Except for None, Nothing, Exact, and Eigenval (which must be spelled out), only the first letter determines the selected algorithm.}}
Conjugate, Subrot, Eigenval, None, and Nothing are supported as of vasp.5.2.9. The Old Fast/Old VeryFast variants (also of/fo and ov/vo) are available in vasp.6 and select the corresponding vasp.5 algorithms.
For more technical details, read {{TAG|IALGO}} and {{TAG|LDIAG}}.
### Recommendations
* **Most systems**: {{TAG|ALGO|Normal}} (blocked Davidson) is the most robust choice and the default.
* **Large systems and molecular dynamics**: RMM-DIIS (Fast or VeryFast) reduces the *O*(*N*3) orthonormalization cost and is faster for large cells; combine with {{TAG|LREAL|Auto}}. VeryFast needs good initial orbitals (it uses a large {{TAG|NELMDL}}) and is the least robust on its own. For MD calculations and structure optimization or metals, also mind that barely occupied bands are less optimized ({{TAG|WEIMIN}}).
* **Magnetic materials, DFT+U, meta-GGA, Hartree-Fock and hybrid functionals**: The direct optimizers {{TAG|ALGO|All}} (or Conjugate) are more robust and recommended; use the improved line search ({{TAG|ISEARCH|1}}). {{TAG|ALGO|VeryFast}} is **not** supported for hybrid functionals.
* **Metals or small-gap systems with Hartree–Fock / meta-GGA**: You may try {{TAG|ALGO|Damped}} with an appropriate time step ({{TAG|TIME}}) and a somewhat larger {{TAG|NBANDS}}, if other algorithms fail.
* **Potential-only functionals or methods** (e.g., {{TAG|METAGGA|MBJ}} or {{TAG|LSFBXC}}): use {{TAG|ALGO|Normal}}. Because these functionals provide only a potential and no consistent total energy, the iterative self-consistency-cycle minimizers work by applying the Hamiltonian repeatedly without taking the expression of the energy into account.
* **Elongated geometries, systems including vacuum, slabs, surfaces**: prefer the mixing (self-consistency-cycle) algorithms (Normal or Fast). These systems are prone to charge sloshing, which can be reduced by fine-tuning the mixing tags ({{TAG|AMIX}}, {{TAG|BMIX}}, …); see Troubleshooting electronic convergence. For fast convergence of the self-consistency cycle, {{TAG|LMAXMIX}} must be set appropriately, e.g., {{TAG|LMAXMIX|6}} for systems with *f* electrons. 
* **Preparing many empty states** (e.g., for GW or RPA), run {{TAG|ALGO|Exact}} after a normal ground-state calculation.
* **Postprocessing from a {{FILE|WAVECAR}}**: {{TAG|ALGO|Eigenval}} recomputes one-electron energies and the density of states; {{TAG|ALGO|None}} recomputes occupancies and the density of states.
## Output during the electronic minimization
At each electronic step, VASP writes one line to standard output and to the {{FILE|OSZICAR}} file. For example:

       N       E                     dE             d eps       ncg     rms          rms(c)
 DAV:   1     0.230591997322E+03    0.23059E+03   -0.16471E+04 13824   0.142E+03
 DAV:   2     0.128984547176E+02   -0.21769E+03   -0.20617E+03 12600   0.334E+02
 DAV:   3    -0.871201735783E+01   -0.21610E+02   -0.21211E+02 14288   0.100E+02
 DAV:   4    -0.952629881459E+01   -0.81428E+00   -0.81287E+00 15680   0.208E+01
 DAV:   5    -0.954352651394E+01   -0.17228E-01   -0.17224E-01 15640   0.295E+00    0.119E+01
 ...

The leading label marks the algorithm (and phase) used in that step. SCF runs from scratch always begin with a delay ({{TAG|NELMDL}} non-self-consistent blocked-Davidson sweeps) at fixed density, so the first steps for Fast, VeryFast, All, Damped (and all steps for Normal) are labeled DAV::
  Label !! Algorithm
  DAV: || blocked Davidson ({{TAG|IALGO}}=38; {{TAG|ALGO}}=Normal and the initial phase of Fast, VeryFast, All and Damped)
  RMM: || RMM-DIIS ({{TAG|IALGO}}=48; {{TAG|ALGO}}=VeryFast and the main phase of Fast)
  SDA: / CGA: || steepest-descent / conjugate-gradient all-band step ({{TAG|IALGO|58}}; {{TAG|ALGO}}=All or Conjugate)
  DMP: || damped dynamics ({{TAG|IALGO|53}}; {{TAG|ALGO|Damped}})
  DIA: || (subspace) diagonalization ({{TAG|ALGO|Exact}} or Subrot)
  EIG: || eigenvalue recomputation ({{TAG|ALGO|Eigenval}})
  NONE || no orbital update ({{TAG|ALGO|None/Nothing}})

The columns are:
* **N**: index of the electronic (self-consistency) step.
* **E**: total (free) energy in eV at this step.
* **dE**: change of the total energy with respect to the previous step.
* **d eps**: change of the band-structure energy (sum of one-electron eigenvalues) due to the orbital optimization in this step. This should be comparable with **dE** of the subsequent step.
* **ncg**: number of evaluations of the Hamiltonian acting on an orbital (*H*&Psi;) in this step.
* **rms**: root-mean-square norm of the residual vector |(\mathbf{H}-\epsilon\mathbf{S})\Psi\rangle, i.e., how well the current orbitals solve the eigenvalue problem.
* The **last column** depends on the algorithm:
** For the iterative self-consistency-cycle minimizers, as well as the postprocessing modes, it is **rms(c)**, the root-mean-square change of the charge density in the charge-density mixer. For the iterative self-consistency-cycle minimizers, it appears only once charge-density mixing has started, i.e., after the {{TAG|NELMDL}} non-self-consistent steps.
** For the direct-minimization algorithms ({{TAG|ALGO|All/Conjugate}} and Damped), which update the density directly without a density mixer, the column is headed **ort** instead and reports the orthonormality error of the orbitals.

The electronic loop stops once the energy change **dE** drops below the threshold set by {{TAG|EDIFF}}, or after {{TAG|NELM}} steps. See Setting up an electronic minimization for guidance on choosing these tags, and {{TAG|IALGO}} for further details on the algorithms.
{{NB|tip|In order to judge convergence:
* Plot the total energy **E** minus the final total energy (**E** of the last step) as a function of electronic steps. The decay should be exponential. You may observe accidental stopping or very slow convergence if E-E_{final} is noisy.
* Plot **rms(c)** as a function of electronic steps **N**. Large values indicate the electronic density is still changing and perhaps fluctuating (charge sloshing).
}}
### Line-search output (direct optimizers)
For {{TAG|ALGO|All/Conjugate}}, each step also prints the diagnostics of the conjugate-gradient line minimization ({{TAG|ISEARCH}}), for example:

 CGA:   8    -0.815350365436E+01   -0.26844E+00   -0.26700E+00   896   0.102E+00   0.183E-02
 gam= 0.117 g(H,U,f)=  0.861E-01 0.436E-02 0.112E-01 ort(H,U,f) =-0.290E-01 0.260E-01 0.476E-02
 gam= 0.117 trial= 0.425  step=  1.5048 mean=  0.4252
  continued last = 0.638  step=  0.9339 harm=  0.9495 4th-ord=  0.9585 spline=  0.9339
  steps along line     -0.425E-04  0.425E-04  0.425E+00  0.143E+01  0.957E+00  0.638E+00
  energies along line   0.433E-05 -0.433E-05 -0.372E-01 -0.389E-01 -0.565E-01 -0.492E-01

* **gam** is the conjugate-gradient coefficient that mixes the previous search direction into the current one.
* **g(H,U,f)** are the norms of the energy gradient with respect to the three optimized degrees of freedom: the orbital coefficients (*H*), the subspace rotation (*U*), and the partial occupancies (*f*).
* **ort(H,U,f)** is the overlap of the current gradient with the previous search direction for each of these; it should be close to zero when the preceding line minimization was accurate.
* **trial**, **step**, and **mean** are the trial step length, the step actually taken, and the running mean of the trial step.
* **continued last … harm / 4th-ord / spline** are refined optimal-step estimates from a harmonic (second-order), fourth-order-polynomial, and spline fit when extra points are sampled along the line.
* **steps along line** and **energies along line** list the trial step lengths probed along the search direction and the corresponding total energies, from which the minimum is located.
## ALGO for response functions, GW, and ACFDT/RPA
The following tags are available as of VASP.5.X.

*{{TAG|ALGO|CHI}} calculates the response functions only.

*{{TAG|ALGO|TDHF}} selects TDHF (or  TDDFT) calculations using the VASP internal Cassida code see BSE calculations, (available as of VASP.5.2.12)

*{{TAG|ALGO|BSE}} selects BSE calculations using the VASP internal Cassida code see BSE calculations, (available as of VASP.5.4.1)

*{{TAG|ALGO|Timeev}} performs a delta-pulse in time and then performs timepropagation

*{{TAG|ALGO|ACFDT}} selects RPA total energy calculations see ACFDT/RPA calculations

*{{TAG|ALGO|RPA}} synonymous to ACFDT see ACFDT/RPA calculations (available as of VASP.5.3.1)

GW tags have been renamed in VASP as follows
  < 5.2.12
  scGW
  scGW0
  GW
  GW0
  N/A
  N/A
  >= 5.2.12, < 6
  QPGW
  QPGW0
  GW
  GW0
  N/A
  N/A
  >= 6
  QPGW
  QPGW0
  EVGW
  EVGW0
  GWR
  GW0R

*{{TAG|ALGO|EVGW0}} selects single-shot *G*0*W*0 calculations or partially self-consistent *GW* calculations. The orbitals (wavefunctions) of the previous groundstate calculations are maintained, and G0W0 calculations are performed. If {{TAG|NELM}} is set, several iterations are performed, and the QP energies are updated in the calculation of *G* (for details, see EVGW0 calculations).

*{{TAG|ALGO|EVGW}} selects partially self-consistent (eigenvalue-self-consistent) *GW* calculations. The orbitals of the previous ground-state calculation are maintained; over {{TAG|NELM}} iterations the QP energies are updated in the calculation of *G* AND *W* (for details, see self-consistent EVGW and QPGW calculations).

*{{TAG|ALGO|QPGW0}} selects self-consistent *GW* calculations including off-diagonal components of the self-energy. A full update of the QP energies AND one-electron orbitals is performed in the calculation of *G* only (for details see QPGW0 calculations).

*{{TAG|ALGO|QPGW}} selects self-consistent *GW* calculations, including off-diagonal components of the self-energy. A full update of the QP energies AND one-electron orbitals is performed in the calculations of *G* AND *W* (for details, see QPGW calculations).

Following tags are available as of VASP.6

*{{TAG|ALGO|RPAR}} selects low scaling RPA total energy calculations (for details see ACFDT/RPA calculations)

*{{TAG|ALGO|ACFDTR}} synonym for RPAR (for details see ACFDT/RPA calculations)

*{{TAG|ALGO|ACFDTRK}} in combination with {{TAG|LMP2LT|True}} selects the low scaling MP2 total energy calculations (for details see the MP2 ground state Tutorial)

*{{TAG|ALGO|GW0R}} selects self-consistent GW0 calculations, where only the Green's function *G* is updated from the corresponding Dyson. The screened potential *W* remains unchanged after the first iteration. {{TAG|NELM}} iteration cycles are performed (see self-consistent GW calculations).

*{{TAG|ALGO|GWR}} selects self-consistent GW calculations, where both, *G* and *W* are updated from the corresponding Dyson equation. {{TAG|NELM}} iteration cycles are performed. (for details see self-consistent GW calculations).

*{{TAG|ALGO|G0W0R}} selects single-shot GW calculations, non-interacting *G* and *W* are determined from Kohn-Sham system and {{TAG|NELM}} tag is ignored. Use this tag for single-shot QP energies and first-order corrections to the density matrix (for details, see single-shot GW calculations).
{{NB|important|Changes as of VASP.6.3:}}
*{{TAG|NELMGW}} replaces {{TAG|NELM}} in self-consistent GW calculations.

*{{TAG|ALGO|CRPA}} selects constrained RPA calculations.
{{NB|important|available as of VASP.6.4:}}
*{{TAG|ALGO|EVGW0R}} selects the low-scaling analog of EVGW0, that is the low-scaling partially self-consistent GW calculations, where non-interacting *G* and *W* are determined from Kohn-Sham system and {{TAG|NELMGW}} specifies the number of self-consistent loops for *G*. *W* is kept on the Kohn-Sham level.
## Related tags and articles
Setting up an electronic minimization, BSE calculations, GW calculations, ACFDT/RPA_calculations

{{TAG|IALGO}},
{{TAG|LDIAG}},
{{TAG|NELM}},
{{TAG|NELMDL}},
{{TAG|EDIFF}},
{{TAG|LMAXMIX}}

{{sc|ALGO|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Electronic minimizationCategory:Many-body perturbation theoryCategory:GWCategory:Bethe-Salpeter equations
