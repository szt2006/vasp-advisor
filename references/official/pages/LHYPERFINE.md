{{TAGDEF|LHYPERFINE|.TRUE. {{!}} .FALSE. | .FALSE.}}

Description: compute the hyperfine tensors at the atomic sites (available as of vasp.5.3.2).
----
To have VASP compute the hyperfine tensors at the atomic sites, set

 LHYPERFINE = .TRUE.
{{NB|mind|Spin-polarized calclulations {{TAG|ISPIN}} {{=}} 2 **must** be used.}}
{{NB|warning|Noncollinear calculations {{TAG|LNONCOLLINEAR}} {{=}} .TRUE. are not currently implemented for {{TAG|LHYPERFINE}}. There is not a warning message for this, which will be added in future releases, see  known issue 48.}}

The hyperfine tensor AI describes the interaction between a nuclear spin SI (located at site **R**I) and the electronic spin distribution Se (in most cases associated with a paramagnetic defect state) {{Cite|szasz:prb:2013}}:

:
E=\sum_{ij} S^e_i A^I_{ij} S^I_j

In general it is written as the sum of an isotropic part, the so-called Fermi contact term, and an anisotropic (dipolar) part.

The Fermi contact term is given by

:
(A^I_{\mathrm{iso}})_{ij}= \frac{2}{3}\frac{\mu_0\gamma_e\gamma_I}{\langle S_z\rangle}\delta_{ij}\int \delta_T(\mathbf{r})\rho_s(\mathbf{r}+\mathbf{R}_I)d\mathbf{r}

where ρs is the spin density, μ0 is the magnetic susceptibility of free space,
γe the electron gyromagnetic ratio, γI the nuclear gyromagnetic ratio of the nucleus at **R**I, and \langle S_z \rangle the expectation value of the *z*-component of the total electronic spin.

δT(**r**) is a smeared out δ function, as described in
the Appendix of Ref. {{Cite|bloechl:prb:2000}}.

The dipolar contributions to the hyperfine tensor are given by
:
(A^I_{\mathrm{ani}})_{ij}=\frac{\mu_0}{4\pi}\frac{\gamma_e\gamma_I}{\langle S_z\rangle}
\int \frac{\rho_s(\mathbf{r}+\mathbf{R}_I)}{r^3}\frac{3r_ir_j-\delta_{ij}r^2}{r^2} d\mathbf{r}

In the equations above *r*=|**r**|, *r*i the i-th component of **r**, and **r** is
taken relative to the position of the nucleus **R**I.

The nuclear gyromagnetic ratios should be specified by means of the {{TAG|NGYROMAG}}-tag.

A guide for calculating the hyperfine coupling constant is available.
{{NB|mind|The Zeroth Order Regular Approximation (ZORA) is used to account for the relativistic effects in the hyperfine tensor calculations.}}
## Output
As usual, all output is written to the {{FILE|OUTCAR}} file. VASP writes three blocks of data. The first is for the Fermi contact coupling parameter:

 Fermi contact (isotropic) hyperfine coupling parameter (MHz)
 -------------------------------------------------------------
  ion      A_pw      A_1PS     A_1AE     A_1c      A_tot
 -------------------------------------------------------------
   1       ...       ...       ...       ...       ...
  ..       ...       ...       ...       ...       ...

 -------------------------------------------------------------

with an entry for each ion on the {{FILE|POSCAR}} file.
Apw, A1PS, A1AE, and A1c are the plane wave, pseudo one-center, all-electron one-center, and one-center core contributions to the Fermi contact term, respectively.
The total Fermi contact term is given by Atot. 
{{NB|important|We have chosen **NOT** to include the core contributions A1c in Atot. These are important to add when comparing to experiment where they can contribute a significant proportion to the hyperfine coupling constant (up to ~50 % for 13C {{Cite|szasz:prb:2013}}). If you want them to be included, you should add them by hand to Atot: 

:
A_{tot + 1c} = A_{tot} + A_{1c} = (A_{pw} + A_{PS} + A_{AE}) + A_{1c}
 

Core electronic contributions to the Fermi contact term are calculated in the frozen valence approximation as proposed by Yazyev *et al.*{{Cite|yazyev:prb:2005}}.}}

The dipolar contributions are listed next:

 Dipolar hyperfine coupling parameters (MHz)
 ---------------------------------------------------------------------
  ion      A_xx      A_yy      A_zz      A_xy      A_xz      A_yz
 ---------------------------------------------------------------------
   1       ...       ...       ...       ...       ...       ...
  ..       ...       ...       ...       ...       ...       ...

 ---------------------------------------------------------------------

Again one line per ion in the {{FILE|POSCAR}} file.

The total hyperfine tensors are written as:

 Total hyperfine coupling parameters after diagonalization (MHz)
 (convention: |A_zz| > |A_xx| > |A_yy|)
 ----------------------------------------------------------------------
  ion      A_xx      A_yy      A_zz     asymmetry (A_yy - A_xx)/ A_zz
 ----------------------------------------------------------------------
   1       ...       ...       ...         ...
  ..       ...       ...       ...         ...

 ----------------------------------------------------------------------

i.e., the tensors have been diagonalized and rearranged.
{{NB|mind|The Fermi contact term is strongly dominated by the all-electron one-center contribution A1AE.
Unfortunately, this particular term is quite sensitive to the number and eigenenergy of the all-electron partial waves that
make up the one-center basis set, *i.e.*, to the particulars of the PAW dataset you are using.
As a result, the Fermi contact term may strongly depend on the choice of PAW dataset.}}
## Units
The Fermi contact term A is measured in following units

[A]=
\left[\mu_0\right]\times 
\left[g_e \mu_e\right]\times 
\left[g_j \mu_j\right]\times
\left[|\psi(0)|^2\right] = 
\frac{T^2m^3}{J}\times 
\frac{J}{T}\times 
\frac{MHz}{T}\times
\frac{1}{m^3} = MHz

with \mu_0=4\pi\times 10^{-7} T^2 m^3 J^{-1}, g_e\mu_e=9.28476377\times 10^{-24} J T^{-1}, |\psi(0)|^2=10^{30}m^{-3}. 
{{TAG|NGYROMAG}} is given in units of MHz/T.
## Advice
It is possible that your system relaxes to a non-magnetic solution, causing the hyperfine splitting to disappear (i.e. all zeros). If you think your system should be magnetic, you can enforce it using {{TAG|NUPDOWN}}, which will return the hyperfine splitting, cf. forum post: https://vasp.at/forum/viewtopic.php?t=16921. {{TAG|NUPDOWN}} will change the Total magnetic moment S= at the start of the hyperfine coupling section in the {{FILE|OUTCAR}}.  
{{NB|important|For some cells, the total magnetic moment S can be very small (grep " mag{{=}}" OSZICAR), near zero. In the above equations, the isotropic and anisotropic components of the hyperfine coupling parameter (AIiso and AIani) are calculated by dividing through by S (cf. ⟨Sz⟩). To avoid division by zero, S is reset to 1 when S < 10-3. Total magnetic moment S{{=}} is changed, changing the hyperfine coupling constants, too. These hyperfine coupling constants are likely not meaningful. In future versions of the code, there will be a warning message stating that S has been reset and the correct total magnetic moment will be printed.}}
## Related tags and articles
{{TAG|NGYROMAG}}

Calculating the hyperfine coupling constant

{{sc|LHYPERFINE|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:NMR
