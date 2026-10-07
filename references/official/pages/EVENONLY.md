{{TAGDEF|EVENONLY|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|EVENONLY}}=.TRUE. selects a subset of **k**-points for the representation of the Fock exchange potential, with *C*1=*C*2=*C*3=1, and *n*1+*n*2+*n*3 even.
----
One may restrict the sum over **q** in the Fock exchange potential (or one of its short range counterparts) to a subset, {**q****k**}, of the full (*N*1&times;*N*2&times;*N*3)  **k**-point set, {**k**}, for which the following holds

:
\mathbf{q_k} = \mathbf{b}_1 \frac{n_1 C_1}{N_1} + \mathbf{b}_2 \frac{n_2 C_2}{N_2}
+ \mathbf{b}_3 \frac{n_3 C_3}{N_3},\quad(n_i=0,..,N_i-1)

where **b**1,2,3 are the reciprocal lattice vectors of the primitive cell,
and *C*i is the integer grid reduction factor along reciprocal lattice direction
**b**i.

{{TAG|EVENONLY}}=.TRUE. selects a subset of **k**-points with *C*1=*C*2=*C*3=1, and *n*1+*n*2+*n*3 even. It reduces the computational work load for HF type calculations by a factor two, but is only sensible for high symmetry cases (such as sc, fcc or bcc cells).

{{NB|warning|there are circumstances under which **NKRED** and **NKREDX**,**Y**,**Z** should not be used!}}
## Related tags and articles
{{TAG|NKRED}},
{{TAG|NKREDX}},
{{TAG|NKREDY}},
{{TAG|NKREDZ}},
{{TAG|ODDONLY}},
downsampling

{{sc|EVENONLY|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
