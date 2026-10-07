{{DISPLAYTITLE:ML_MRB1}}
{{TAGDEF|ML_MRB1|[integer]|12}}

Description: This tag sets the number N_\text{R}^0 of radial basis functions used to expand the radial descriptor \rho^{(2)}_i(r) within the machine learning force field method.
----
The radial descriptor is constructed from

\rho_{i}^{(2)}\left(r\right) = \frac{1}{4\pi} \int \rho_{i}\left(r\hat{\mathbf{r}}\right) d\hat{\mathbf{r}}, \quad \text{where} \quad
\rho_{i}\left(\mathbf{r}\right) = \sum\limits_{j=1}^{N_{\mathrm{a}}} f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right)

and g\left(\mathbf{r}\right) is an approximation of the delta function. In practice, the continuous function above is transformed into a discrete set of numbers by expanding it into a set of radial basis functions \chi_{n0}(r) (see this section for more details):

\rho_{i}^{(2)}\left(r\right) = \frac{1}{\sqrt{4\pi}} \sum\limits_{n=1}^{N^{0}_{\mathrm{R}}} c_{n00}^{i} \chi_{n0}\left(r\right).

The tag {{TAG|ML_MRB1}} sets the number N_\text{R}^0 of radial basis functions to use in this expansion.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_MRB2}}, {{TAG|ML_W1}}, {{TAG|ML_RCUT1}}, {{TAG|ML_SION1}}

{{sc|ML_MRB1|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
