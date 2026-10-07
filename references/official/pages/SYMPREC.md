{{TAGDEF|SYMPREC|[real]|10^{-5}}}

Description: {{TAG|SYMPREC}} determines to which accuracy the positions in the {{FILE|POSCAR}} file must be specified (as of VASP.4.4.4).
----
{{TAG|SYMPREC}} determines how accurately the positions in the {{FILE|POSCAR}} file must be specified.
The default, {{TAG|SYMPREC}}=10-5, is usually large enough, even if the {{FILE|POSCAR}} file has been generated with single precision accuracy.
Increasing {{TAG|SYMPREC}} means that the positions in the {{FILE|POSCAR}} file can be specified with less accuracy (increasing fuzziness). Please also have a look at this section.
## Related tags and articles
{{TAG|ISYM}}

{{sc|SYMPREC|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Symmetry
