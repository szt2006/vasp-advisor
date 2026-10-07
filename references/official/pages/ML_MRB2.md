{{DISPLAYTITLE:ML_MRB2}}
{{TAGDEF|ML_MRB2|[integer]|8}}

Description: This tag sets the number N_\text{R}^l (for all l) of radial basis functions used to expand the angular descriptor within the machine learning force field method. 
----
The angular descriptor is constructed from

\rho_{i}^{(3)}\left(r,s,\theta\right) = \iint d\hat{\mathbf{r}} d\hat{\mathbf{s}}  \delta\left(\hat{\mathbf{r}}\cdot\hat{\mathbf{s}} - \mathrm{cos}\theta\right) \sum\limits_{j=1}^{N_{a}} \sum\limits_{k \ne j}^{N_{a}} \rho_{ik} \left(r\hat{\mathbf{r}}\right) \rho_{ij} \left(s\hat{\mathbf{s}}\right), \quad \text{where} \quad
\rho_{ij}\left(\mathbf{r}\right) = f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right)

and g\left(\mathbf{r}\right) is an approximation of the delta function. In practice, the continuous function above is transformed into a discrete set of numbers p_{n\nu l}^{i} by expanding it into a set of radial basis functions \chi_{nl}(r) and Legendre polynomials P_{l}\left(\mathrm{cos}\theta\right) (see this section for more details):

\rho_{i}^{(3)}\left(r,s,\theta\right) = \sum\limits_{l=1}^{L_{\mathrm{max}}} \sum\limits_{n=1}^{N^{l}_{\mathrm{R}}}\sum\limits_{\nu=1}^{N^{l}_{\mathrm{R}}} \sqrt{\frac{2l+1}{2}} p_{n\nu l}^{i}\chi_{nl}\left(r\right)\chi_{\nu l}\left(s\right)P_{l}\left(\mathrm{cos}\theta\right).

The tag {{TAG|ML_MRB2}} sets the number N_\text{R}^l of radial basis functions to use in this expansion. The same number is used for all l.
{{NB|mind|The number of angular descriptor expansion coefficients p_{n\nu l}^{i} scales **quadratically** with N_\text{R}^l set by this tag. It also depends on {{TAG|ML_LMAX2}} and the number of elements.}}
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_LMAX2}}, {{TAG|ML_MRB1}}, {{TAG|ML_W1}}, {{TAG|ML_RCUT2}}, {{TAG|ML_SION2}}

{{sc|ML_MRB2|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
