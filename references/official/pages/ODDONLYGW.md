{{TAGDEF|ODDONLYGW|[logical]|.FALSE.}}

Description: {{TAG|ODDONLYGW}} allows to avoid the inclusion of the \Gamma point in the evaluation of response functions (in {{TAG|GW calculations}}).

----

The independent particle polarizability  \chi_{{\mathbf{q}}}^0 ({\mathbf{G}}, {\mathbf{G}}', \omega) is given by:

\chi_{{\mathbf{q}}}^0 ({\mathbf{G}}, {\mathbf{G}}', \omega) =
\frac{1}{\Omega} \sum_{n,n',{\mathbf{k}}}2 w_{{\mathbf{k}}}  (f_{n'{\mathbf{k}}+{\mathbf{q}}} - f_{n{\mathbf{k}}})  
\times  \frac{\langle \psi_{n{\mathbf{k}}}| e^{-i ({\mathbf{q}}+{\mathbf{G}}){\mathbf{r}}} | \psi_{n'{\mathbf{k}}+{\mathbf{q}}}\rangle
\langle \psi_{n'{\mathbf{k}}+{\mathbf{q}}}| e^{i ({\mathbf{q}}+{\mathbf{G}}'){\mathbf{r'}}} | \psi_{n{\mathbf{k}}}\rangle}
 { \epsilon_{n'{\mathbf{k}}+{\mathbf{q}}}-\epsilon_{n{\mathbf{k}}} -  \omega - i \eta } 

If the \Gamma point is included in the summation over \mathbf{k}, convergence is very slow for some materials  (e.g. GaAs).

To deal with this problem the flag {{TAG|ODDONLYGW}} has been included.
In the automatic mode,  the \mathbf{k}-grid is given by (see Sec. \ref{sec:autok}): 

  \vec{k} = \vec{b}_{1} \frac{n_{1}}{N_{1}} + \vec{b}_{2} \frac{n_{2}}{N_{2}}  + \vec{b}_{3} \frac{n_{3}}{N_{3}} ,\qquad  n_1=0...,N_1-1 \quad  n_2=0...,N_2-1 \quad  n_3=0...,N_3-1. 
## Related tags and articles
{{TAG|EVENONLYGW}},
{{TAG|GW calculations}}

{{sc|ODDONLYGW|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:GW
