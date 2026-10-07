{{TAGDEF|NKREDX|[integer]|1}}

Description: {{TAG|NKREDX}} specifies a reduction factor for the **q**-point grid representation of the exact exchange potential along reciprocal space direction **b**1.
----
One may restrict the sum over **q** in the Fock exchange potential (or one of its short range counterparts) to a subset, {**q****k**}, of the full (*N*1&times;*N*2&times;*N*3)  **k**-point set, {**k**}, for which the following holds

:
\mathbf{q_k} = \mathbf{b}_1 \frac{n_1 C_1}{N_1} + \mathbf{b}_2 \frac{n_2 C_2}{N_2}
+ \mathbf{b}_3 \frac{n_3 C_3}{N_3},\quad(n_i=0,..,N_i-1)

where **b**1,2,3 are the reciprocal lattice vectors of the primitive cell,
and *C*i is the integer grid reduction factor along reciprocal lattice direction
**b**i. This leads to a reduction in the computational workload by a factor:

:
\frac{1}{C_1 C_2 C_3}

In case one sets {{TAG|NKRED}}, the grid reduction factors will be uniformly set to *C*1=*C*2=*C*3={{TAG|NKRED}}. If one wants to specify separate grid reduction factors for *C*1, *C*2, and *C*3 one should use *C*1={{TAG|NKREDX}}, *C*2={{TAG|NKREDY}}, and *C*3={{TAG|NKREDZ}}, respectively.

{{NB|warning|there are circumstances under which **NKRED** and **NKREDX**,**Y**,**Z** should not be used!}}
## Related tags and articles
{{TAG|NKRED}},
{{TAG|NKREDY}},
{{TAG|NKREDZ}},
{{TAG|EVENONLY}},
{{TAG|ODDONLY}},
downsampling

{{sc|NKREDX|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
