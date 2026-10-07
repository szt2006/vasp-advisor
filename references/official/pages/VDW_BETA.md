{{DISPLAYTITLE:VDW_BETA}}
{{TAGDEF|VDW_BETA|[real]}}

Description: {{TAG|VDW_BETA}} sets the offset for the damping radius or the power for the zero-damping component in the DFT-D3 methods implemented in the simple-DFT-D3 package.
{{Available|6.6.0}}
----
{{TAG|VDW_BETA}} allows to set the value of a parameter in the following versions of DFT-D3 (only available in the simple-DFT-D3 package): 
*Offset \beta for the damping radius in the modified zero-damping function ({{TAG|IVDW}}=15 with {{TAG|SDFTD3_DAMPING}}=mzero).
*Power \beta for the zero-damping component in the optimized-power damping function ({{TAG|IVDW}}=15 with {{TAG|SDFTD3_DAMPING}}=optimizedpower). Note that \beta-6 corresponds to the values of \beta reported in Ref.{{cite|witte:jctc:2017}}.
## Related tags and articles
{{TAG|IVDW}},
{{TAG|SDFTD3_DAMPING}},
simple-DFT-D3

{{sc|VDW_BETA|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
