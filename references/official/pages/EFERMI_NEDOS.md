{{DISPLAYTITLE:EFERMI_NEDOS}}
{{TAGDEF|EFERMI_NEDOS|[integer]|21}}

Description: Number of Gauss–Legendre integration points used to evaluate the Fermi–Dirac distribution and determine the Fermi level at finite temperature using the tetrahedron method only with {{TAGDEF|ISMEAR|−14 or -15}}.
{{Available|6.5.0}}

----

**EFERMI_NEDOS** sets the number of points in the Gauss–Legendre grid used to integrate the Fermi–Dirac distribution for determining the Fermi level within the  tetrahedron method when {{TAGDEF|ISMEAR|−14 or -15}}.  
Larger values improve accuracy, especially at low temperatures or with sharp features in the electronic DOS, but also increase computational cost.  
A brief convergence test is recommended in case very accurate occupancies are required, e.g., in the context of transport calculations.
{{NB|mind|**ELPH_FERMI_NEDOS** is a valid alternative way of writing this tag.}}
## Implementation details
At T=0, the integrated and differential densities of states are
$$
n(\epsilon)=\sum_{n\mathbf{k}}\theta(\epsilon-\epsilon_{n\mathbf{k}}), \qquad
g(\epsilon)=\sum_{n\mathbf{k}}\delta(\epsilon-\epsilon_{n\mathbf{k}}).
$$

At finite temperature,
$$
N_e(\epsilon_F,T)=
\sum_{n\mathbf{k}}f(\epsilon_{n\mathbf{k}}-\epsilon_F,T)
=\int g(\epsilon)f(\epsilon-\epsilon_F,T)\,d\epsilon.
\tag{1}
$$

With the substitution x = 1 - 2f(\epsilon-\epsilon_F,T),
$$
\epsilon = k_BT\ln\!\frac{1+x}{1-x}+\epsilon_F, \qquad
d\epsilon = -k_BT\,\frac{2}{x^2-1}\,dx,
$$
Eq. (1) becomes
$$
N_e(\epsilon_F,T)=
\frac{1}{2}\int_{-1}^{1}
n\!\left(k_BT\ln\!\frac{1+x}{1-x}+\epsilon_F\right)\,dx.
$$

In practice, this integral is discretized as
$$
N_e(\epsilon_F,T)\simeq
\frac{1}{2}\sum_{i=1}^{N}w_i\,
n\!\left(k_BT\ln\!\frac{1+x_i}{1-x_i}+\epsilon_F\right),
$$
where w_i and x_i are Gauss–Legendre weights and abscissas.  
The step functions \(\theta(\epsilon-\epsilon_{n\mathbf{k}})\) entering \(n(\epsilon)\) are evaluated using the tetrahedron method, with the number of energy points N given by {{TAG|EFERMI_NEDOS}}.
## Related tags and articles
{{TAG|ISMEAR}},
{{TAG|SIGMA}},
Smearing technique,
K-point integration

Category:INCAR tag
Category:Electronic occupancy
Category:Density of states
