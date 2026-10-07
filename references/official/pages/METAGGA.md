{{TAGDEF|METAGGA|[string]|The functional specified by {{TAG|LEXCH}} in the {{FILE|POTCAR}} if {{TAG|GGA}} and {{TAG|XC}} are also not specified.}}

Description: Selects a meta-GGA exchange-correlation functional.
----
{{NB|mind|
*If you select a meta-GGA functional, make sure that you use  POTCAR files that are suited for meta-GGA functionals. However, note that this requirement does not concern the deorbitalized meta-GGAs, i.e. those that do not depend on the kinetic-energy density, like SCAN-L.
*Depending on the meta-GGA that is chosen, it may be recommended to use a PAW potential that is more accurate than the standard/recommended one. This is particularly the case with functionals (e.g., MBJ or the Minnesota functionals like M06-L) that are very different from the standard ones like PBE or SCAN. The reason is that for such *special* functionals, using a PAW potential that includes more states in the valence or that is harder may be required to obtain results that are closer to the results that would be obtained with an all-electron code. That also means that it may be a good idea to do test calculations with different PAW potentials.
*For accuracy, it is strongly recommended to set {{TAG|LASPH}}{{=}}.TRUE. to  account for aspherical contributions to the PAW one-centre terms. 
*Since VASP.6.4.0 it is possible to use hybrid functionals that mix meta-GGA and Hartree-Fock exchange ({{TAG|AEXX}}). Furthermore, two new tags, {{TAG|AMGGAX}} and {{TAG|AMGGAC}}, were created.
*The {{TAG|XC}} tag, available since VASP.6.4.3, can be used to specify any linear combination of LDA, {{TAG|GGA}} and {{TAG|METAGGA}} exchange-correlation functionals.
*The results obtained with the meta-GGA functionals that depend on the Laplacian of the density \nabla^2n (e.g., SCAN-L) may not be reliable for large values of the energy cutoff {{TAG|ENCUT}} due to numerical instability. According to some tests, it is not recommended to use values of {{TAG|ENCUT}} above 800 eV.}}
## Available functionals
This table lists the meta-GGA functionals available in VASP. There are essentially two types of meta-GGAs, that differ in the variable on which they depend (in addition to n and \nabla n): the kinetic-energy density \tau or the Laplacian of the density \nabla^2n. The names of functionals which end with "_X" and "_C" correspond to exchange-only and correlation functionals, respectively. Note that the implementation of \tau-dependent meta-GGA functionals is described in {{cite|sun:prb:11}}.
  style="text-align:center;" style=width:16em | METAGGA= !! style="text-align:center;"| Variable !! class="unsortable" | Description
  style="text-align:center;"| LIBXC || style="text-align:center;"| ||
Any MGGA from the external library Libxc.{{cite|marques:cpc:2012}}{{cite|lehtola:sx:2018}}{{cite|tran:arxiv:2026}}{{cite|libxc}} It is necessary to have Libxc >= 5.2.0 installed and VASP.6.3.0 or higher compiled with precompiler options. The {{TAG|LIBXC1}} and {{TAG|LIBXC2}} tags (where examples are shown) are also required.
  style="text-align:center;"| TPSS, TPSS_X or TPSS_C(1) || style="text-align:center;"| \tau ||
TPSS.{{cite|tao:prl:2003}}
  style="text-align:center;"| RTPSS, RTPSS_X or RTPSS_C(1) || style="text-align:center;"| \tau ||
revTPSS is a revised version of TPSS.{{cite|perdew:prl:2009}}
  style="text-align:center;"| M06L, M06L_X or M06L_C(1) || style="text-align:center;"| \tau ||
M06-L.{{cite|zhao:jcp:06}}
  style="text-align:center;"| MS0, MS0_X or MS0_C(1) || style="text-align:center;"| \tau ||
MS0 corresponds to \kappa=0.29, c=0.28771 and b=1.0.{{cite|sun:jcp:12}}{{cite|sun:jcp:13}}
Note that the correlation component, called vPBEc or regTPSS in the literature, is a GGA. Available since VASP.5.4.1.
  style="text-align:center;"| MS1, MS1_X or MS1_C(1) || style="text-align:center;"| \tau ||
MS1 corresponds to \kappa=0.404, c=0.18150 and b=1.0.{{cite|sun:jcp:13}}
Note that the correlation component, called vPBEc or regTPSS in the literature, is a GGA. Available since VASP.5.4.1.
  style="text-align:center;"| MS2, MS2_X or MS2_C(1) || style="text-align:center;"| \tau ||
MS2 corresponds to \kappa=0.504, c=0.14601 and b=4.0.{{cite|sun:jcp:13}}
Note that the correlation component, called vPBEc or regTPSS in the literature, is a GGA. Available since VASP.5.4.1.
  style="text-align:center;"| SCAN, SCAN_X or SCAN_C(1) || style="text-align:center;"| \tau ||
SCAN.{{cite|sun:prl:15}} May possibly lead to numerical instabilities. rSCAN or r^{2}SCAN are more stable and should give similar results. Available since VASP.5.4.4.
  style="text-align:center;"| RSCAN, RSCAN_X or RSCAN_C(1) || style="text-align:center;"| \tau ||
rSCAN is a regularized version of SCAN that is numerically more stable.{{cite|bartok:jcp:19}}
  style="text-align:center;"| R2SCAN, R2SCAN_X or R2SCAN_C(1) || style="text-align:center;"| \tau ||
r^{2}SCAN is a regularized version of SCAN that is numerically more stable.{{cite|furness:jpcl:20}} Available since VASP.6.2.0, or in version 5.4.4 by patch 4 (https://gitlab.com/dhamil/r2scan-subroutines/-/tree/master/vasp_patch_files).
  style="text-align:center;"| SREGTM1, SREGTM2 or SREGTM3 || style="text-align:center;"| \tau ||
sregTM{{cite|francisco_a:jcp:2023}} versions 1, 2 or 3 of a regularized Tao-Mo functional.{{cite|tao:prl:2016}} Available since VASP.6.4.3.
  style="text-align:center;"| TASK_X(2) || style="text-align:center;"| \tau || TASK exchange.{{cite|aschebrock:prr:2019}} Available since VASP.6.5.0.
  style="text-align:center;"| LAK, LAK_X or LAK_C || style="text-align:center;"| \tau || LAK.{{cite|lebeda:prl:2024}} Available since VASP.6.5.0.
  style="text-align:center;"| MSPBEL, MSRPBEL or MSB86BL || style="text-align:center;"| \tau ||
MS-PBEl, MS-RPBEl or MS-B86bl.{{cite|smeets:jpca:2019}} Available since VASP.6.5.0.
  style="text-align:center;"| RMSPBEL, RMSRPBEL or RMSB86BL || style="text-align:center;"| \tau ||
rMS-PBEl, rMS-RPBEl or rMS-B86bl.{{cite|cai:jpcc:2024}} Available since VASP.6.5.0.
  style="text-align:center;"| SCANL || style="text-align:center;"| \nabla^2n ||
SCAN-L{{cite|mejia-rodriguez:pra:2017}}{{cite|mejia-rodriguez:prb:2018}} is a deorbitalized version of SCAN. Available since VASP.6.4.0.
  style="text-align:center;"| RSCANL || style="text-align:center;"| \nabla^2n ||
rSCAN-L is a deorbitalized version of rSCAN. Available since VASP.6.4.0.
  style="text-align:center;"| R2SCANL || style="text-align:center;"| \nabla^2n ||
r^2SCAN-L is a deorbitalized versions of r^2SCAN.{{cite|mejia-rodriguez:prb:2020}}{{cite|kaplan:prm:2022}} Available since VASP.6.4.0.
  style="text-align:center;"| OFR2 || style="text-align:center;"| \nabla^2n ||
Orbital-free regularized-restored SCAN (OFR2).{{cite|kaplan:prm:2022}} Available since VASP.6.4.0. 
  style="text-align:center;"| SREGTM2L || style="text-align:center;"| \nabla^2n ||
v2-sregTM-L is a deorbitalized versions of v2-sregTM.{{cite|francisco_b:jcp:2023}} Available since VASP.6.4.0.
  style="text-align:center;"| MBJ(3) || style="text-align:center;"| \nabla^2n,\tau ||
Modified Becke-Johnson potential.{{cite|becke:jcp:06}}{{cite|tran:prl:09}} The {{TAG|CMBJA}}, {{TAG|CMBJB}} and {{TAG|CMBJE}} tags correspond to \alpha, \beta and the power e=1/2 (that can be modified) in Eq. (3) of Ref. {{cite|tran:prl:09}}, respectively. The default values are \alpha=-0.012, \beta=1.023 bohr^{1/2} and e=1/2.{{cite|tran:prl:09}}
  style="text-align:center;"| LMBJ(3) || style="text-align:center;"| \nabla^2n,\tau ||
The local MBJ (LMBJ) potential.{{cite|rauch:jctc:2020}}{{cite|rauch:prb:2020}} The {{TAG|CMBJA}}, {{TAG|CMBJB}}, {{TAG|CMBJE}}, {{TAG|SMBJ}}, and {{TAG|RSMBJ}} tags correspond to \alpha, \beta, the power e=1 (that can be modified) of \bar{g}, \sigma and r_{s}^{\mathrm{th}} in Eqs. (5)-(7) of Ref. {{cite|rauch:prb:2020}}, respectively. The default values are (see erratum of Ref. {{cite|rauch:prb:2020}}) \alpha=0.488, \beta=0.5 bohr, e=1, \sigma=2 \AA (=3.78 bohr), and r_{s}^{\mathrm{th}}=7 bohr (which corresponds to n_{\mathrm{th}}=6.96\times10^{-4} e/bohr^{3}).

(1) The exchange-only and correlation-only implementations are available since VASP.6.4.3.

(2) In Ref. {{cite|aschebrock:prr:2019}} TASK exchange is combined with LDA-PW92 correlation.{{cite|perdew1992}} This can be done with {{TAG|XC}}=TASK_X PW92_C in {{FILE|INCAR}}.

(3) A few points about the MBJ and LMBJ potentials:
:*These are *potential-only* methods, *i.e.*, there is no corresponding exchange-correlation energy E_{xc}. The used expression for E_{xc} is LDA, which is an arbitrary choice. This means that MBJ and LMBJ calculations can never be self-consistent with respect to the total energy, and thus we cannot compute Hellmann-Feynman forces (*i.e.*, no ionic relaxation, etc.). Actually, these potentials aim solely at a description of the electronic properties, primarily the band gap, or magnetic moments.
:*MBJ and LMBJ calculations may converge very slowly, so the number of maximum electronic steps ({{TAG|NELM}}) should be set higher than usual.
:*In the presence of an extended vacuum region (e.g., surfaces) or an interface, the average of |\nabla n|/n has no meaning. Therefore, MBJ calculations should be done with a fixed value of c, which can be done with the {{TAG|CMBJ}} tag., or alternatively with the LMBJ that was proposed for the purpose to be applicable to systems with vacuum or interfaces.
## POTCAR files: required information
Calculations with a meta-GGA that depends on the kinetic-energy density require {{FILE|POTCAR}} files that include information on the kinetic-energy density of the core electrons. Almost all recent {{FILE|POTCAR}} files do fulfill this requirement, but there are some notable exceptions like O_GW. To check whether a particular {{FILE|POTCAR}} contains this information, type:
 grep kinetic POTCAR

This should yield at least the following lines (for each element on the file):
 kinetic energy-density
 mkinetic energy-density pseudized
and for PAW datasets with partial core corrections:
 kinetic energy density (partial)
{{NB|mind|For {{FILE|POTCAR}} files without core electrons (H, He, Li_sv, Be_sv, and _GW variants thereof) the grep command given above will not return the line about pseudized kinetic energy-density, since all electrons are considered as valence. These potentials can nevertheless be used for all meta-GGA functionals.}}
## Aspherical contributions related to one-center terms
{{TAG|LASPH}} =.TRUE. should be selected if a meta-GGA functional is selected. If {{TAG|LASPH}} =.FALSE.,
the one-center contributions are only calculated for a spherically averaged density and kinetic-energy
density. This means that the one-center contributions to the Kohn-Sham potential are also spherical. 
Since the PAW method describes the entire space using plane waves, errors are often small even
if the non-spherical contributions to the Kohn-Sham potential are neglected inside the PAW spheres
(additive augmentation, as opposed to the APW or FLAPW method where the plane wave contribution only
describes the interstitial region between the atoms). Anyhow, if the density is strongly non-spherical
around some atoms in your structure, {{TAG|LASPH}} =.TRUE. must be selected. Non-spherical terms are particularly encountered
in d- and f-elements, dimers, molecules, and solids with strong directional bonds.
## Convergence issues
If convergence problems are encountered, it is recommended to preconverge the
calculations using the PBE functional and start the calculation from the {{FILE|WAVECAR}} file corresponding to the PBE ground state. Furthermore,
{{TAG|ALGO}} = A (conjugate gradient algorithm for orbitals) is often more stable
than charge density mixing, in particular if the system contains vacuum regions.
## Related tags and articles
{{TAG|LIBXC1}},
{{TAG|LIBXC2}},
{{TAG|GGA}},
{{TAG|XC}},
{{TAG|CMBJ}},
{{TAG|CMBJA}},
{{TAG|CMBJB}},
{{TAG|CMBJE}},
{{TAG|SMBJ}},
{{TAG|RSMBJ}},
{{TAG|LASPH}},
{{TAG|LMAXTAU}},
{{TAG|LMIXTAU}},
{{TAG|LASPH}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
Band-structure calculation using meta-GGA functionals

{{sc|METAGGA|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Exchange-correlation functionals
