{{DISPLAYTITLE:VDW_SR}}
{{TAGDEF|VDW_SR|[real]}}

Description: {{TAG|VDW_SR}} sets a parameter in the damping function of van der Waals methods.
----
{{TAG|VDW_SR}} allows to set the value of a parameter in the following methods:
*Radii scaling s_{r,6} in the dipole-dipole zero-damping function of DFT-D3. {{TAG|VDW_SR}} can be used for both implementations of DFT-D3: DFT-D3 ({{TAG|IVDW}}=11) and simple-DFT-D3 ({{TAG|IVDW}}=15 with {{TAG|SDFTD3_DAMPING}}=zero or mzero).
*Radii scaling s_{R} in the damping function of the Tkatchenko-Scheffler methods ({{TAG|IVDW}}=2 and 21).
*Radii scaling \beta in the damping function of the many-body dispersion energy methods ({{TAG|IVDW}}=202 and 263).
*TT-damping factor b_0 in DDsC ({{TAG|IVDW}}=4).
## Related tags and articles
{{TAG|IVDW}},
{{TAG|VDW_SR}},
DFT-D3,
simple-DFT-D3,
Tkatchenko-Scheffler method,
Tkatchenko-Scheffler method with iterative Hirshfeld partitioning,
Many-body dispersion energy,
Many-body dispersion energy with fractionally ionic model for polarizability,
DDsC

{{sc|VDW_SR|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
