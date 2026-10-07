{{DISPLAYTITLE:HILLS_H}}{{TAGDEF|HILLS_H|[Real]|10^{-3}}}

Description: {{TAG|HILLS_H}} specifies the height of the Gaussian hill (in eV) used in metadynamics (in case VASP was compiled with -Dtbdyn).
----
In metadynamics ({{TAG|MDALGO}}=11 {{!}} 21), the bias potential is given as 
:
\tilde{V}(t,\xi) = h \sum_{i=1}^{\lfloor t/t_G \rfloor} \exp{\left\{ -\frac{|\xi^{(t)}-\xi^{(i \cdot t_G)}|^2}{2
w^2} \right\}}.

Thre parameters ({{TAG|HILLS_H}}, {{TAG|HILLS_W}}, and {{TAG|HILLS_BIN}}) must be provided by the user.

The height of the Gaussian hills h (in eV) is set by {{TAG|HILLS_H}}.
## Related tags and articles
Metadynamics,
{{TAG|HILLS_W}},
{{TAG|HILLS_BIN}},
{{FILE|HILLSPOT}},
{{TAG|MDALGO}}

{{sc|HILLS_H|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Advanced molecular-dynamics sampling
