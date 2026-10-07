{{DISPLAYTITLE:ML_LMAX2}}
{{TAGDEF|ML_LMAX2|[integer]}}
{{DEF|ML_LMAX2|3|for {{TAG|ML_LAFILT2}} {{=}} .TRUE.|6|else}}

Description: This tag specifies the maximum angular momentum quantum number L_\max of spherical harmonics used to expand atomic distributions within the machine learning force field method.
----
To construct an atomic environment descriptor the atomic probability density

\rho_{i}\left(\mathbf{r}\right) = \sum\limits_{j=1}^{N_{\mathrm{a}}} f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right),

where g\left(\mathbf{r}\right) is an approximation of the delta function, is expanded in terms of radial basis functions \chi_{nl}(r) and spherical harmonics Y_{lm}\left(\hat{\mathbf{r}}\right) (see this section for more details):

\rho_{i} \left( \mathbf{r} \right) = \sum\limits_{l=1}^{L_{\mathrm{max}}} \sum\limits_{m=-l}^{l} \sum\limits_{n=1}^{N^{l}_{ \mathrm{R}}} c_{nlm}^{i}\chi_{nl} \left( r \right) Y_{lm} \left( \hat{\mathbf{r}} \right),

The tag {{TAG|ML_LMAX2}} specifies the maximum angular momentum quantum number L_\max of spherical harmonics used in this expansion.
{{NB|mind|This tag is only relevant for the angular descriptor \rho^{(3)}_i(r). The corresponding number of expansion coefficients p_{n\nu l}^{i} scales **linearly** with L_\max (however the calculation of the spherical harmonics scales quadratically) and is also depending on {{TAG|ML_MRB2}} and the number of elements present.}}

By default an angular filtering (see {{TAG|ML_LAFILT2}} and {{TAG|ML_IAFILT2}}) with a filtering parameter of {{TAG|ML_AFILT2}}=0.002 is used where a value of {{TAG|ML_LMAX2}}=3 is perfectly safe for most applications. If you need to improve the accuracy, you might also try to increase it to {{TAG|ML_LMAX2}}=4. If the angular filter is switched off, we recommend to use a value of {{TAG|ML_LMAX2}}=6 (this is then the default value).
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_MRB1}}, {{TAG|ML_MRB2}}, {{TAG|ML_LAFILT2}}, {{TAG|ML_IAFILT2}}, {{TAG|ML_AFILT2}}

{{sc|ML_LMAX2|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
