{{TAGDEF|LTHOMAS|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LTHOMAS}} selects a decomposition of the exchange functional based on Thomas-Fermi exponential screening.
----
If {{TAG|LTHOMAS}}=.TRUE. the decomposition of the exchange operator (in a range-separated hybrid functional) into a short range (SR) and a long range (LR) part will be based on Thomas-Fermi exponential screening:

:E_{\mathrm{xc}}^{\mathrm{hybrid}}=a_{\mathrm{SR}} E_{\mathrm{x,SR}}^{\mathrm{HF}}(\mu) + (1-a_{\mathrm{SR}})E_{\mathrm{x,SR}}^{\mathrm{SL}}(\mu) + E_{\mathrm{x,LR}}^{\mathrm{SL}}(\mu) + E_{\mathrm{c}}^{\mathrm{SL}}

The mixing a_{\mathrm{SR}} and screening \mu=k_{\rm TF} are controlled by the {{TAG|AEXX}} and {{TAG|HFSCREEN}} tags, respectively.

For typical semiconductors, a Thomas-Fermi screening length k_{\rm TF} of about 1.8 &Aring;-1 yields reasonable band gaps. In principle, however, the Thomas-Fermi screening length depends on the valence-electron density. VASP determines k_{\rm TF} from the number of valence electrons (read from the {{FILE|POTCAR}} file) and the volume (leading to an average density \bar{n}) and writes the corresponding value of k_{\rm TF}=\sqrt{4\bar{k}_{\rm F}/\pi}, where \bar{k}_{\rm F}=(3\pi^2\bar{n})^{1/3} to the {{FILE|OUTCAR}} file (**note that this value is only printed for information and is not used during the calculation**):
  Thomas-Fermi vector in A             =   2.00000

The setting of the sX-LDA functional is shown on the page listing the hybrid functionals.
{{NB|mind|
*If {{TAG|LTHOMAS}}{{=}}.TRUE., then {{TAG|LHFCALC}}{{=}}.TRUE. is automatically set.
*If {{TAG|LTHOMAS}}{{=}}.TRUE., then {{TAG|AEXX}}{{=}}1 is automatically set, but {{TAG|AEXX}} can be set to another value.}}
{{NB|important|
*When {{TAG|AEXX}}{{=}}1 (the default for {{TAG|LTHOMAS}}{{=}}.TRUE.), the correlation E_{\mathrm{c}}^{\mathrm{SL}} is not included. However, it can be included by setting {{TAG|ALDAC}}{{=}}1.0 and {{TAG|AGGAC}}{{=}}1.0.
*This functional should be used only with LDA ({{TAG|GGA}}{{=}}CA).}}
Since VASP counts the semi-core states and *d*-states as valence electrons, although these states do not contribute to the screening, the values reported by VASP are often not recommended.

Another important detail concerns the implementation of the local LDA part in VASP. Literature [see Eqs. (3.10), (3.14), and (3.15) in Ref. {{cite|seidl:prb:96}}] suggests to use in the enhancement factor F(z) a position-independent variable z=k_{\rm TF}/\bar{k}_{\rm F} where \bar{k}_{\rm F} is as defined above but using the average density \bar{n} in the unit cell.
However, implemented in VASP is a position-dependent variable z({\bf r})=k_{\rm TF}/k_{\rm F}({\bf r}), where k_{\rm F}({\bf r})=(3\pi^2 n({\bf r}))^{1/3} is the Fermi wave vector calculated with the local density n({\bf r}), while the constant k_{\rm TF} is set by {{TAG|HFSCREEN}}.
## Related tags and articles
{{TAG|LHFCALC}},
{{TAG|HFSCREEN}},
{{TAG|AEXX}},
{{TAG|LMODELHF}},
{{TAG|LRHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|LTHOMAS|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
