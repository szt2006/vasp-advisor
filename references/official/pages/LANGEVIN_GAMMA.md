{{DISPLAYTITLE:LANGEVIN_GAMMA}}{{TAGDEF|LANGEVIN_GAMMA|[Real array]|NTYP&times;0}}

Description: {{TAG|LANGEVIN_GAMMA}} specifies the friction coefficients (in ps-1) for atomic degrees-of-freedom when using a Langevin thermostat (in case VASP was compiled with -Dtbdyn).
----
When using a Langevin thermostat{{Cite|allen:book:1991}} ({{TAG|MDALGO}}=3), the friction coefficients &gamma; for the atomic degrees-of-freedom are specified (in ps-1) using the {{TAG|LANGEVIN_GAMMA}}-tag.

One has to specify a separate friction coefficient for each of the NTYP atomic species found on the {{FILE|POTCAR}}-file. 
#### Practical example
Consider a system consisting of 16 hydrogen and 48 silicon atoms. Suppose that eight silicon atoms are considered to be Langevin atoms and the remaining 32 Si atoms are either fixed or Newtonian atoms. The Langevin and Newtonian (or fixed) atoms should be considered as different species, *i.e.*, the {{FILE|POSCAR}}-file should contain the line like this:

 Si H Si
 40 16 8

As only the final eight Si atoms are considered to be Langevin atoms, the {{FILE|INCAR}}-file should contain the following line defining the friction coefficients:

 LANGEVIN_GAMMA = 0.0   0.0   10.0

*i.e.*, for all non-Langevin atoms, &gamma; should be set to zero.
## Related tags and articles
{{TAG|LANGEVIN_GAMMA_L}},
{{TAG|MDALGO}}

{{sc|LANGEVIN_GAMMA|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Molecular dynamicsCategory:Thermostats
