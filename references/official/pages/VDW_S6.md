{{DISPLAYTITLE:VDW_S6}}
{{TAGDEF|VDW_S6|[real]}}

Description: {{TAG|VDW_S6}} sets a parameter in the damping function of van der Waals methods.
----
{{TAG|VDW_S6}} allows to set the value of a parameter in the following methods: 
*Scaling s_{6} of the dipole-dipole dispersion of the DFT-D2 ({{TAG|IVDW}}=1), DFT-D3, DFT-D4 ({{TAG|IVDW}}=13), DFT-ulg ({{TAG|IVDW}}=3), and Tkatchenko-Scheffler methods  ({{TAG|IVDW}}=2 and 21). {{TAG|VDW_S6}} can be used for both implementations of DFT-D3: DFT-D3 ({{TAG|IVDW}}=11 or 12) and simple-DFT-D3 ({{TAG|IVDW}}=15).
*Steepness factor a_0 in DDsC ({{TAG|IVDW}}=4).
{{NB|mind|The setting of s_{6} with {{TAG|VDW_S6}} when {{TAG|IVDW}}{{=}}11 or 12 (VASP implementation of DFT-D3) is possible since VASP.6.6.0.}}
## Related tags and articles
{{TAG|IVDW}},
{{TAG|VDW_S8}},
DFT-D2,
DFT-D3,
simple-DFT-D3,
DFT-D4,
DFT-ulg,
Tkatchenko-Scheffler method,
Tkatchenko-Scheffler method with iterative Hirshfeld partitioning,
DDsC

{{sc|VDW_S6|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
