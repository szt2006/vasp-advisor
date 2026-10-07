{{DISPLAYTITLE:ML_RCUT2}}
{{TAGDEF|ML_RCUT2|[real]|5.0}}

Description: This flag sets the cutoff radius R_\text{cut} for the angular descriptor \rho^{(3)}_i(r) in the machine learning force field method. The unit of the cut-off radius is \AA.
----
The angular descriptor is constructed from

\rho_{i}^{(3)}\left(r,s,\theta\right) = \iint d\hat{\mathbf{r}} d\hat{\mathbf{s}}  \delta\left(\hat{\mathbf{r}}\cdot\hat{\mathbf{s}} - \mathrm{cos}\theta\right) \sum\limits_{j=1}^{N_{a}} \sum\limits_{k \ne j}^{N_{a}} \rho_{ik} \left(r\hat{\mathbf{r}}\right) \rho_{ij} \left(s\hat{\mathbf{s}}\right), \quad \text{where} \quad
\rho_{ij}\left(\mathbf{r}\right) = f_{\mathrm{cut}}\left(r_{ij}\right) g\left(\mathbf{r}-\mathbf{r}_{ij}\right)

 
and g\left(\mathbf{r}\right) is an approximation of the delta function. A basis set expansion of \rho^{(3)}_i(r) yields the expansion coefficients p_{n\nu l}^{i} which are used in practice to describe the atomic environment (see this section for details). The tag {{TAG|ML_RCUT2}} sets the cutoff radius R_\text{cut} at which the cutoff function f_{\mathrm{cut}}\left(r_{ij}\right) decays to zero.
{{NB|mind|The cutoff radius determines how many neighbor atoms N_\mathrm{a} are taken into account to describe each central atom's environment. Hence, important features may be missed if the cutoff radius is set to a too small value. On the other hand, a large cutoff radius increases the computational cost as the cutoff sphere contains more neighbor atoms. A larger cutoff can also significantly degrade the learning efficiency. A good compromise is system-dependent, therefore different values should be tested to achieve satisfactory accuracy **and** speed.}}

For materials containing only H, B, C, O, N, and F (i.e. organic molecules, polymers), the learning efficiency might increase when ML_RCUT2 is set to values around 4  \AA (that is, less training data are required to achieve a specific accuracy), wheres for materials with very long bonds, a larger value around 6  \AA can improve the accuracy,
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_RCUT1}}, {{TAG|ML_W1}}, {{TAG|ML_SION1}}, {{TAG|ML_SION2}}, {{TAG|ML_MRB1}}, {{TAG|ML_MRB2}} 

{{sc|ML_RCUT1|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
