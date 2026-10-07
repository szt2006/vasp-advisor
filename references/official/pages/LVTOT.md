{{TAGDEF|LVTOT|[logical]|.FALSE.}}

Description: Determines whether the total local potential V_{\text{LOCPOT}}(\mathbf{r}) (in eV) is written to the {{FILE|LOCPOT}} file.
----

V_{\text{LOCPOT}}(\mathbf{r}) = 
V_{\text{ionic}}(\mathbf{r}) + 
\int \frac{n(\mathbf{r'})}{|\mathbf{r}-\mathbf{r'}|}d\mathbf{r'}+
V_{\text{xc}}(\mathbf{r})

where V_{\text{ionic}}(\mathbf{r}) is the ionic potential,
the second term is the Hartree potential, and 
V_{\text{xc}}(\mathbf{r}) is the (semi-)local exchange-correlation potential.

If {{TAG|LVTOT}}=.TRUE., the V_{\text{LOCPOT}}(\mathbf{r}) is written to the {{FILE|LOCPOT}} file and the {{FILE|POT}} file. The {{FILE|POT}} file additionally contains the augmentation part. 
{{NB|warning|{{TAG|LVHAR}}{{=}}T changes the content of the {{FILE|LOCPOT}} file.}}
{{TAG|WRT_POTENTIAL}} also gives access to the total local potential and offers more options.
## Related tags and articles
Computing the work function, {{TAG|LVHAR}}, {{FILE|LOCPOT}}, {{TAG|WRT_POTENTIAL}}, {{TAG|LVACPOTAV}}, {{FILE|POT}}

{{sc|LVTOT|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Electronic ground-state propertiesCategory:Potential
