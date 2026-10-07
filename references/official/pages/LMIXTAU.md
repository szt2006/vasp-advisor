{{TAGDEF|LMIXTAU|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: send the kinetic-energy density through the density mixer as well.
----
In many cases, the density-mixing scheme works well enough without passing the kinetic-energy density through the mixer. Therefore VASP uses {{TAG|LMIXTAU}}=.FALSE. per default. However, when the self-consistency cycle fails to converge for one of the algorithms exploiting density mixing, e.g, {{TAG|IALGO}}=38 or 48, we recommend setting {{TAG|LMIXTAU}}=.TRUE..
## Related tags and articles
{{TAG|METAGGA}},
{{TAG|LMAXTAU}}

{{sc|LMIXTAU|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Density mixing
