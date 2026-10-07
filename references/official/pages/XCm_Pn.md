{{DISPLAYTITLE:XCm_Pn}}
{{TAGDEF|XCm_Pn|[real]}}

Description: {{TAG|XCm_Pn}}, where m=1, 2, \ldots and n=1, 2, \ldots allows to modify the parameters in a semilocal functional.
----

The {{TAG|XCm_Pn}} tag allows to modify the parameters in the semilocal functional set with the {{TAG|XC}} tag. In {{TAG|XCm_Pn}}, m=1, 2, \ldots refers to the mth component of the functional and n=1, 2, \ldots to the nth parameter of this mth functional component.

The {{TAG|XCm_Pn}} tag can be used for functionals that are implemented in VASP or in Libxc.
* Functionals in VASP:
: The number of functionals with modifiable parameters is for the moment very limited and concerns only a few MGGAs. Among the functionals listed at {{TAG|METAGGA}}, there is MS0, MS1, and MS2,{{cite|sun:jcp:12}}{{cite|sun:jcp:13}} for instance. The functionals with modifiable parameters can be found by searching for "XC%PARAM" in the subroutine SET_XC_DATA in the setex.F file.

* Functionals in Libxc:
:For many of the functionals implemented in the library of exchange-correlation functionals Libxc{{cite|marques:cpc:2012}}{{cite|lehtola:sx:2018}}{{cite|tran:arxiv:2026}}{{cite|libxc}} it is possible to modify the parameters. If a functional from Libxc has modifiable parameters, then they are listed in {{FILE|OUTCAR}} below "Parameters of Libxc functionals:" as Pn (n=1, 2, \ldots). Note that {{TAG|LIBXC1_Pn}} and {{TAG|LIBXC2_Pn}} are equivalent to {{TAG|XCm_Pn}} when the functional is set with the tag {{TAG|GGA}} or {{TAG|METAGGA}}.

More information about the mixing and screening parameters in hybrid functionals can be found at {{TAG|LIBXC1_Pn}}.
{{NB|mind|{{TAG|XCm_Pn}} is available since VASP.6.4.3.}}
### Examples
* In the GGA PBE functional,{{cite|perdew:prl:1996}} as implemented in Libxc, the default parameters \mu=0.21951 in exchange and \beta=0.066725 in correlation are changed to \mu=10/81\approx0.12345679 and \beta=0.046 to get the PBEsol functional{{cite|perdew:prl:2008}} (of course, the simpler way to use PBEsol from Libxc would be to call it directly with "{{TAG|XC}}=GGA_X_PBE_SOL GGA_C_PBE_SOL"). This example is equivalent to the one given for {{TAG|LIBXC1_Pn}}.
 {{TAG|XC}} = GGA_X_PBE GGA_C_PBE
 XC1_P2 = 0.12345679    #parameter mu, which is the 2nd parameter in GGA_X_PBE
 XC2_P1 = 0.046         #parameter beta, which is the 1st parameter in GGA_C_PBE

* In the MGGA MS1 functional the default parameters \kappa=0.404, c=0.18150 and b=1.0 in exchange (see Table I in Ref. {{cite|sun:jcp:13}}) are changed to \kappa=0.504, c=0.14601 and b=4.0 to get the MS2 functional.
 {{TAG|XC}} = MS1
 XC1_P1 = 0.504    #parameter kappa, which is the 1st parameter in MS0, MS1, and MS2
 XC1_P2 = 0.14601  #parameter c, which is the 2nd parameter in MS0, MS1, and MS2
 XC1_P3 = 4.0      #parameter b, which is the 3rd parameter in MS0, MS1, and MS2
## Related tags and articles
{{TAG|XC}},
{{TAG|XC_C}},
{{TAG|GGA}},
{{TAG|METAGGA}},
{{TAG|LIBXC1}},
{{TAG|LIBXC2}},
{{TAG|LIBXC1_Pn}},
{{TAG|LIBXC2_Pn}}
## References
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
