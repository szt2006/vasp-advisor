{{DISPLAYTITLE:ML_RCUT1}}
{{TAGDEF|ML_RCUT1|[real]|8.0}}

Description: Sets the cutoff radius R_\text{cut} for the radial descriptor \rho^{(2)}_i(r) in \AA.
----
The radial descriptor for machine-learned force fields is constructed from

\rho_{i}^{(2)}\left(r\right) = \frac{1}{4\pi} \int \rho_{i}\left(r\hat{\mathbf{r}}\right) d\hat{\mathbf{r}}, \quad \text{where} \quad
\rho_{i}\left(\mathbf{r}\right) = \sum\limits_{j=1}^{N_{\mathrm{a}}} f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right)

and g\left(\mathbf{r}\right) is an approximation of the delta function. A basis set expansion of \rho^{(2)}_i(r) yields the expansion coefficients c_{n00}^{i}, which are used in practice to describe the atomic environment; refer to the theory of machine-learned force fields for details. The tag {{TAG|ML_RCUT1}} sets the cutoff radius R_\text{cut} at which the cutoff function f_{\mathrm{cut}}\left(r_{ij}\right) decays to zero.
{{NB|mind|The cutoff radius determines how many neighbor atoms N_\mathrm{a} are considered to describe each central atom's environment. Hence, important features may be missed if the cutoff radius is too small. On the other hand, a large cutoff radius increases the computational cost of the descriptor as the cutoff sphere contains more neighbor atoms. A good compromise is always system-dependent. Therefore, different values should be tested to achieve satisfying accuracy **and** speed.}}

The unit of the cut-off radius is \AA.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_RCUT2}}, {{TAG|ML_W1}}, {{TAG|ML_SION1}}, {{TAG|ML_SION2}}, {{TAG|ML_MRB1}}, {{TAG|ML_MRB2}} 

{{sc|ML_RCUT1|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
