{{TAGDEF|LVHAR|[logical]|.FALSE.}}

Description: Determines whether the local potential V_{\text{ionic}}(\mathbf{r}) +V_{\text{hartree}}(\mathbf{r})  (in eV) is written to the {{FILE|LOCPOT}} file.
----

V_{\text{ionic}}(\mathbf{r})+V_{\text{hartree}}(\mathbf{r}) =
V_{\text{ionic}}(\mathbf{r}) + 
\int \frac{n(\mathbf{r'})}{|\mathbf{r}-\mathbf{r'}|}d\mathbf{r'}

where V_{\text{ionic}}(\mathbf{r}) is the ionic potential as mimicked by the pseudopotentials and V_{\text{hartree}}(\mathbf{r}) is the Hartree potential.

The local potential is written to the {{FILE|LOCPOT}} file and hence to the same file as the local potential for {{TAG|LVTOT}}=T. Carefully check that the {{FILE|LOCPOT}} file contains the potential you expect.
{{TAG|WRT_POTENTIAL}} also gives access to the ionic and Hartree potentials and offers more options.
{{NB|warning|Setting {{TAG|LVHAR}}{{=}}True will set {{TAG|LVTOT}}{{=}}False.}}
See {{TAG|LOCPOT}} to find out how to write V_{\text{ionic}}(\mathbf{r}) +V_{\text{hartree}}(\mathbf{r})  in VASP < 5.2.12.
## Related tags and articles
Computing the work function, {{TAG|LVTOT}}, {{FILE|LOCPOT}}, {{TAG|WRT_POTENTIAL}}, {{TAG|LVACPOTAV}}

{{sc|LVHAR|Examples|Examples that use this tag}}

Category:INCAR tagCategory:ElectrostaticsCategory:Potential
