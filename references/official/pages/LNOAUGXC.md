{{TAGDEF|LNOAUGXC|.TRUE. {{!}} .FALSE. |.FALSE.}}

Description: {{TAG|LNOAUGXC}} specifies if a {{TAG|METAGGA}} functional is evaluated with a density that is augmented or not.
----
{{NB|deprecated|The {{TAG|LNOAUGXC}} tag is obsolete and should not be used.}}
{{NB|mind|This tag is available since VASP.6.5.0 and is a replacement of the compiler option -DnoAugXCmeta that was available until VASP.6.4.3.}}
The Kohn-Sham kinetic-energy density 
:\tau_{\sigma}=\frac{1}{2}\sum_{i}\nabla\psi_{i\sigma}^{*}\cdot\nabla\psi_{i\sigma} 
should, in principle, be larger than the von Weizsäcker kinetic-energy density{{cite|kurth:ijqc:1999}} 
:\tau_{\sigma}^{\textrm{W}}=\frac{\left\vert\nabla n_{\sigma}\right\vert^{2}}{8 n_{\sigma}}. 
However, this may not always be the case, particularly within the PAW spheres, when the pseudo density is augmented with the compensation charge. If {{TAG|LNOAUGXC}}=.TRUE. is set in the {{FILE|INCAR}} file, then the pseudo density is not augmented, which should alleviate the breaking of the condition \tau_{\sigma}^{\textrm{W}}<\tau_{\sigma}.

A violation of \tau_{\sigma}^{\textrm{W}}<\tau_{\sigma} can make the calculations unstable depending on the meta-GGA functional.
## Related tags and articles
{{TAG|METAGGA}},
{{TAG|LTBOUNDLIBXC}}

{{sc|LNOAUGXC|Examples|Examples that use this tag}}
## References
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Projector-augmented-wave method
