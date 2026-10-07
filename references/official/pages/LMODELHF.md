{{TAGDEF|LMODELHF|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LMODELHF}} selects dielectric-dependent range-separated hybrid functionals with {{TAG|AEXX}} and {{TAG|BEXX}} for the exact Hartree-Fock exchange at long- and short-range, respectively.
----
By setting {{TAG|LMODELHF}}=.TRUE. various types of range-separated hybrid functionals using the error function for the screening can be specified. The general form of hybrid functionals that can be constructed with {{TAG|LMODELHF}} is given by

:E_{\mathrm{xc}}^{\mathrm{hybrid}}=a_{\mathrm{SR}} E_{\mathrm{x,SR}}^{\mathrm{HF}}(\mu) + a_{\mathrm{LR}} E_{\mathrm{x,LR}}^{\mathrm{HF}}(\mu) + (1-a_{\mathrm{SR}})E_{\mathrm{x,SR}}^{\mathrm{SL}}(\mu) + (1-a_{\mathrm{LR}})E_{\mathrm{x,LR}}^{\mathrm{SL}}(\mu) + E_{\mathrm{c}}^{\mathrm{SL}}

where
*a_{\mathrm{SR}} ({{TAG|BEXX}}) and a_{\mathrm{LR}} ({{TAG|AEXX}}) are the **mixing parameters (fraction of HF exchange) at short and long range**, respectively.
*\mu ({{TAG|HFSCREEN}}) is the **screening parameter** that determines the separation between short range (SR) and long range (LR).

Examples of such functionals are those proposed in Refs. {{cite|skone:prb:2016}}{{cite|chen2018nonempirical}}{{cite|cui2018doubly}}. These hybrid functionals are based on a common model for the dielectric function, but differ in the way how the range-separation parameters are obtained from first-principles calculations. Their connection and performance have been discussed for instance in Ref. {{cite|liu2019assessing}}. In principle,
they can be considered to be a smartly constructed approximation to COH-SEX (local Coulomb hole plus screened exchange),
albeit fulfilling many important constraints that the exact exchange correlation functional must observe.

The corresponding functional has been available in VASP since VASP.5.2 released in 2009 (before the two publications), although the gradient contribution had been erroneously implemented in all VASP.5 releases and is only correct in VASP.6. The related bug fix has been made available by the authors of Ref. {{cite|cui2018doubly}}. The nonlocal exchange part of the functional has also been used and documented in Ref. {{cite|bokdam:scr:2016}} and is covered in Improving the dielectric function.

An example of tags to specify in the INCAR file is given for the DD-RSH-CAM functional:{{cite|chen2018nonempirical}}{{cite|cui2018doubly}}

 {{TAGBL|LHFCALC}} = .TRUE.
 {{TAGBL|LMODELHF}} = .TRUE.
 {{TAGBL|AEXX}} = \varepsilon_{\infty}^{-1}
 {{TAGBL|BEXX}} = 1.0   #The default value. Available since VASP.6.6.0.
 {{TAGBL|HFSCREEN}} = \mu
 {{TAGBL|GGA}} = PE

where \varepsilon_{\infty}^{-1} is the inverse dielectric constant and \mu is the screening parameter.
{{TAG|AEXX}} and {{TAG|BEXX}} specify the amount of exact exchange in the long and short range, respectively, that is for short ( \mathbf{G} \to 0 ) and large ( \mathbf{G} \to \infty ) wave vectors, respectively. The screening parameter {{TAG|HFSCREEN}} determines how quickly the nonlocal exchange changes from {{TAG|AEXX}} to {{TAG|BEXX}}.

Other examples of dielectric-dependent range-separated functionals proposed in the literature{{cite|skone:prb:2016}}{{cite|chen2018nonempirical}}{{cite|cui2018doubly}} can be found here and their corresponding INCAR files at list of hybrid functionals.
{{NB|mind|
*If {{TAG|LMODELHF}}{{=}}.TRUE., then {{TAG|LHFCALC}}{{=}}.TRUE. is automatically set.
*The {{TAG|BEXX}} tag is available only since VASP.6.6.0. {{TAG|BEXX}} was hard-coded to 1 in versions prior to VASP.6.6.0.
}}

Specifically, in VASP, the  Coulomb kernel  4 \pi e^2 / (\mathbf{q}+\mathbf{G})^2 in the exact exchange is multiplied by a model for the dielectric function  \epsilon^{-1} (\mathbf{q}+\mathbf{G}):

: \epsilon^{-1} (\mathbf{q}+\mathbf{G})=1-(1-{{\varepsilon}_{\infty}^{-1}})\text{exp}\left(-\frac{|\mathbf{q+G}|^2}{4{\mu}^2}\right).

where  \mu   corresponds to {{TAG|HFSCREEN}}, and   {{\varepsilon}_{\infty}^{-1}}  is specified by {{TAG|AEXX}}. In real space this correspond to a Coulomb kernel 
: V(r) =\left[1-\left(1-{{\varepsilon}_{\infty}^{-1}}\right)\text{erf}( {\mu} r)\right] \frac{e^2}{r} .

The remaining part of the exchange is handled by an appropriate semi-local exchange correlation functional. For further detail we refer to the literature listed below.

Typical values for {{TAG|HFSCREEN}} are listed in the table below
 AlP  1.24
 AlAs 1.18
 AlSb 1.13
 BN   1.7
 CdO  1.34
 CdS  1.19
 CdSe 1.18
 CdTe 1.07
 C    1.70
 GaN  1.39
 GaP  1.24
 GaAs 1.18
 GaSb 1.12
 Ge   1.18
 InP  1.14
 InAs 1.09
 InSb 1.05
 LiF  1.47
 MgO  1.39
 SiC  1.47
 Si   1.26
 ZnO  1.34
 ZnS  1.27
 ZnSe 1.20
 ZnTe 1.12
These values have been obtained from fits of the dielectric function using the Nanoquanta kernel and partially self-consistent GW calculations as used in Ref. {{cite|grueneis2014ionization}}. The values can be also estimated from simple dimensional scaling relations of the valence electron density. Furthermore band gap predictions are not very sensitive to the choice of {{TAG|HFSCREEN}}.
## Related tags and articles
{{TAG|LHFCALC}},
{{TAG|HFSCREEN}},
{{TAG|AEXX}},
{{TAG|BEXX}},
{{TAG|LTHOMAS}},
{{TAG|LRHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism,
## References
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
