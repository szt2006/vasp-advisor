{{TAGDEF|CMBJ|[real (array)]|calculated self-consistently}}

Description: defines the c parameter in the MBJ potential.
----

The {{TAG|CMBJ}} tag can be set in the following ways:
*Specify a constant that is used at every point of space \mathbf{r}CMBJ = c

*Specify one entry per atomic typeCMBJ = c_1 c_2 .. c_n where the order and number n is in accordance with atomic types in your {{FILE|POSCAR}} file. The MBJ exchange potential at a point \mathbf{r} will then be calculated using the parameter c_{i} belonging to the atomic species of the atomic site nearest to \mathbf{r}.

If {{TAG|CMBJ}} is not set, c is calculated at each electronic step as the average of \left\vert\nabla n\right\vert/n in the unit cell, as explained in the description of the {{TAG|METAGGA}} tag.
## Related tags and articles
{{TAG|METAGGA}},
{{TAG|CMBJA}},
{{TAG|CMBJB}},
{{TAG|CMBJE}},
{{TAG|SMBJ}},
{{TAG|RSMBJ}},
{{TAG|LASPH}},
{{TAG|LMAXTAU}},
{{TAG|LMIXTAU}}

{{sc|CMBJ|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionals
