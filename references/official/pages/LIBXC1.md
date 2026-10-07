{{TAGDEF|LIBXC1|[string] or [integer]}}

Description: {{TAG|LIBXC1}} specifies the exchange or exchange-correlation functional from the library of exchange-correlation functionals Libxc{{cite|marques:cpc:2012}}{{cite|lehtola:sx:2018}}{{cite|tran:arxiv:2026}}{{cite|libxc}}.
----
{{NB|important| This feature is available from VASP.6.3.0 onwards that needs to be compiled with -DUSELIBXC.}}
{{TAG|LIBXC1}} and {{TAG|LIBXC2}} can be set to a label (string) or number (integer) associated with a functional listed on the Libxc website{{cite|libxc_list}}, e.g., GGA_X_PBE and 101 for PBE exchange. The label indicates if this is an exchange (X), correlation (C), or exchange-correlation (XC) functional, and which family it belongs to, namely LDA (LDA or HYB_LDA), GGA (GGA or HYB_GGA) or meta-GGA (MGGA or HYB_MGGA). If {{TAG|LIBXC1}} corresponds to an exchange functional, then it can be used in combination with {{TAG|LIBXC2}} for the correlation functional.

Libxc is a separate library package that has to be downloaded{{cite|libxc}} and compiled before VASP is compiled with the corresponding precompiler options and links to the libraries.

Calculations with Laplacian-dependent meta-GGA functionals and meta-GGA-based hybrid functionals are possible since VASP.6.4.0.
{{NB|important|To get correct results with meta-GGA functionals (see discussion at {{TAG|LTBOUNDLIBXC}}), it is necessary to use Libxc from version 5.2.0 onwards (or the master version for the latest implemented functionals) and to compile it with the option --disable-fhc.}}
## How to
The allowed possibilities for {{TAG|LIBXC1}} and {{TAG|LIBXC2}} are the following:
*Both {{TAGDEF|LIBXC1}} and {{TAG|LIBXC2}} are specified and correspond to exchange and correlation functionals, respectively.
*Only {{TAGDEF|LIBXC1}} is specified and corresponds to an exchange or exchange-correlation functional. {{NB|warning|If {{TAGDEF|LIBXC1}} is an exchange-correlation functional, then {{TAGDEF|LIBXC2}} can not be used.|:}}
*{{TAGDEF|LIBXC1}} and {{TAG|LIBXC2}} can correspond to functionals of different families, e.g., a meta-GGA and a GGA, respectively.

Regarding other tags in {{FILE|INCAR}} related to Libxc:
*One also has to specify {{TAG|GGA}} = LIBXC for LDA, GGA and GGA-based hybrid functionals or {{TAG|METAGGA}} = LIBXC for meta-GGA functionals and meta-GGA-based hybrid functionals. Note that if one of the tags ({{TAGDEF|LIBXC1}} or {{TAGDEF|LIBXC2}}) corresponds to a meta-GGA, while the other corresponds to a GGA or LDA, then {{TAG|METAGGA}} = LIBXC (and not {{TAG|GGA}} = LIBXC) has to be specified.
*Many of the functionals implemented in Libxc have parameters that can be modified. This can be done via the tags {{TAG|LIBXC1_Pn}} and {{TAG|LIBXC2_Pn}}, where n=1, 2, \ldots.
*The tag {{TAG|LTBOUNDLIBXC}}, which is .FALSE. by default, allows to enforce the lower bound on the kinetic-energy density (\tau_{\sigma}^{\mathrm{W}}<\tau_{\sigma}) with \tau_{\sigma}=\max(\tau_{\sigma},\tau_{\sigma}^{\mathrm{W}}) before \tau_{\sigma} is used in a meta-GGA functional from Libxc.

For calculations with hybrid functionals ({{TAG|LHFCALC}}=True), the following provides some explanations:
*The Libxc functionals whose tag starts with HYB already include the mixing parameter. Therefore, for them, the {{TAG|ALDAX}}, {{TAG|ALDAC}}, {{TAG|AGGAX}}, {{TAG|AGGAC}}, {{TAG|AMGGAX}}, and {{TAG|AMGGAC}} tags can not be used (more information on how to modify the mixing and screening parameters can be found at {{TAG|LIBXC1_Pn}}). However, it is still necessary to set {{TAG|AEXX}} at the proper value.
*If the semilocal component of the hybrid functional is constructed using Libxc functionals that do not contain HYB in the tag, then {{TAG|ALDAX}}, {{TAG|AGGAX}}, {{TAG|ALDAC}}, and {{TAG|AGGAC}} will be used and multiply
:E_{\mathrm{x}}^{\mathrm{LDA}}=\int\epsilon_{\mathrm{x}}^{\mathrm{LDA}}(n)d^{3}r
:\Delta E_{\mathrm{x}}^{\mathrm{GGA}}=\int\left(\epsilon_{\mathrm{x}}^{\mathrm{GGA}}(n,\nabla n) - \epsilon_{\mathrm{x}}^{\mathrm{LDA}}(n)\right)d^{3}r
:E_{\mathrm{c}}^{\mathrm{LDA}}=\int\epsilon_{\mathrm{c}}^{\mathrm{LDA}}(n)d^{3}r
:\Delta E_{\mathrm{c}}^{\mathrm{GGA}}=\int\left(\epsilon_{\mathrm{c}}^{\mathrm{GGA}}(n,\nabla n) - \epsilon_{\mathrm{c}}^{\mathrm{LDA}}(n)\right)d^{3}r
:respectively, where \epsilon_{\mathrm{x}}^{\mathrm{LDA}}(n)=-\left(3/4\right)\left(3/\pi\right)^{1/3}n^{4/3} and \epsilon_{\mathrm{c}}^{\mathrm{LDA}}(n)=\epsilon_{\mathrm{c}}^{\mathrm{GGA}}(n,\nabla n=0).
## Examples of {{FILE|INCAR}}
*PBE{{cite|perdew:prl:1996}}
 {{TAG|GGA}} = LIBXC
 {{TAG|LIBXC1}} = GGA_X_PBE # or 101
 {{TAG|LIBXC2}} = GGA_C_PBE # or 130

*SCAN{{cite|sun:prl:15}}
 {{TAG|METAGGA}} = LIBXC
 {{TAG|LIBXC1}} = MGGA_X_SCAN # or 263
 {{TAG|LIBXC2}} = MGGA_C_SCAN # or 267

*PBEh (PBE0){{cite|adamo:jcp:1999}}
 {{TAG|LHFCALC}} = .TRUE.
 {{TAG|AEXX}} = 0.25
 {{TAG|GGA}} = LIBXC
 {{TAG|LIBXC1}} = HYB_GGA_XC_PBEH # or 406

*SCAN0
 {{TAG|LHFCALC}} = .TRUE.
 {{TAG|AEXX}} = 0.25
 {{TAG|METAGGA}} = LIBXC
 {{TAG|LIBXC1}} = MGGA_X_SCAN # or 263
 {{TAG|LIBXC2}} = MGGA_C_SCAN # or 267
## Related tags and articles
{{TAG|LIBXC2}},
{{TAG|LIBXC1_Pn}},
{{TAG|LIBXC2_Pn}},
{{TAG|LTBOUNDLIBXC}},
{{TAG|GGA}},
{{TAG|METAGGA}},
{{TAG|LHFCALC}},
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
List of hybrid functionals

{{sc|LIBXC1|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
