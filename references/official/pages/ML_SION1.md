{{DISPLAYTITLE:ML_SION1}}
{{TAGDEF|ML_SION1|[real]|0.5}}

Description: This tag specifies the width \sigma_\text{atom} of the Gaussian functions used for broadening the atomic distributions of the radial descriptor \rho^{(2)}_i(r) within the machine learning force field method.
----
The radial descriptor is constructed from

\rho_{i}^{(2)}\left(r\right) = \frac{1}{4\pi} \int \rho_{i}\left(r\hat{\mathbf{r}}\right) d\hat{\mathbf{r}}, \quad \text{where} \quad
\rho_{i}\left(\mathbf{r}\right) = \sum\limits_{j=1}^{N_{\mathrm{a}}} f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right)

and g\left(\mathbf{r}\right) is the following approximation of the delta function:

 
g\left(\mathbf{r}\right)=\frac{1}{\sqrt{2\sigma_{\mathrm{atom}}\pi}}\mathrm{exp}\left(-\frac{|\mathbf{r}|^{2}}{2\sigma_{\mathrm{atom}}^{2}}\right).

The tag {{TAG|ML_SION1}} sets the width \sigma_\text{atom} of the above Gaussian function (see this section for more details).
{{BOX|tip|Our test calculations indicate that {{TAG|ML_SION1}} {{=}} {{TAG|ML_SION2}} results in an optimal training performance. Furthermore, a value of 0.5 was found to be a good default value for both. However, the best choice is somewhat system-dependent. For instance, a smaller value for {{TAG|ML_SION1}} can increase the number of local reference configurations, and hence ultimately the quality of the MLFF. See also here.
}}
The unit of {{TAG|ML_SION1}} is \AA.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_SION2}}, {{TAG|ML_RCUT1}}, {{TAG|ML_RCUT2}}, {{TAG|ML_MRB1}}, {{TAG|ML_MRB2}}

{{sc|ML_SION1|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
