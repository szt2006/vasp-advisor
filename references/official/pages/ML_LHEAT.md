{{DISPLAYTITLE:ML_LHEAT}}
{{TAGDEF|ML_LHEAT|[logical]|.FALSE.}}

Description: This tag specifies whether the heat flux is calculated or not in the machine learning force field method.
----
The heat flux within machine learning force fields is decomposed into atomic contributions written as

\mathbf{q}(t) = \sum\limits_{i=1}^{N_{a}} \frac{d}{dt} \left( \mathbf{r}_{i} E_{i} \right),

E_{i}=\frac{m_{i} \left|\mathbf{v}_{i} \right|^{2}}{2} + U_{i}

where \mathbf{r}_{i}, \mathbf{v}_{i} and E_{i} denote the position vector, velocity and energy of atom i, respectively. The number of atoms in the system is denoted by N_{a}. The heat flux can be further rewritten as

\mathbf{q}(t) = \sum\limits_{i=1}^{N_{a}} \mathbf{v}_{i} E_{i} + \sum\limits_{i=1}^{N_{a}} \mathbf{r}_{i} \left( m_{i} \mathbf{v}_{i} \cdot \frac{d\mathbf{v}_{i}}{dt} + \sum\limits_{j=1}^{N_{a}} \mathbf{v}_{j} \cdot \nabla_{j} U_{i} \right). 

Using the equation of motions

m_{i} \frac{d \mathbf{v}_{i}}{dt} = - \sum\limits_{j=1}^{N_{a}} \nabla_{i} U_{j}

the heat flux can be simplified to

\mathbf{q}(t) = \sum\limits_{i=1}^{N_{a}} \mathbf{v}_{i} E_{i} - \sum\limits_{i=1}^{N_{a}} \sum\limits_{j=1}^{N_{a}} \mathbf{r}_{i} \left( \mathbf{v}_{i} \cdot \nabla_{i} U_{j} \right) + \sum\limits_{i=1}^{N_{a}} \sum\limits_{j=1}^{N_{a}} \mathbf{r}_{i} \left( \mathbf{v}_{j} \cdot \nabla_{j} U_{i} \right) = \sum\limits_{i=1}^{N_{a}} \mathbf{v}_{i} E_{i} + \sum\limits_{i=1}^{N_{a}} \sum\limits_{j=1}^{N_{a}} \left( \mathbf{r}_{i} - \mathbf{r}_{j} \right) \left( \mathbf{v}_{j} \cdot \nabla_{j} U_{i} \right). 

Finally (in a post-processing step), the thermal conductivity at temperature T in the Green-Kubo formalism can be calculated from the correlation of the heat flux \mathbf{q} as

\kappa = \frac{1}{3Vk_{b}T^{2}} \int\limits_{0}^{\infty} \langle \mathbf{q}(t) \cdot \mathbf{q}(0) \rangle dt,

where V and k_{b} denotes the volume of the system and the Boltzmann constant, respectively.

 

The heat flux is written to the file {{TAG|ML_HEAT}}.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_LEATOM}}

{{sc|ML_LHEAT|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
