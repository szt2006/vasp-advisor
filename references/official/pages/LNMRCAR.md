{{TAGDEF|LNMRCAR|.TRUE. {{!}} .FALSE.|.TRUE.}}

Description: Write the {{FILE|NMRCAR.magres}} file for EFG calculations and chemical shielding calculations.
----

When calculating the chemical shieldings or calculating the electric field gradient, {{TAG|LNMRCAR|T}} writes the {{FILE|NMRCAR.magres}} in Magres format (https://www.ccpnc.ac.uk/docs/magres). Mind that, while the Magres format does not clearly state if the macroscopic susceptibility should be included, here it is included in the chemical shielding.
## Related tags and articles
{{TAG|LCHIMAG}}, {{TAG|LEFG}}

Calculating the chemical shieldings 

Calculating the electric field gradient

{{sc|LNMRCAR|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:NMR
