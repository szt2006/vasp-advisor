{{DISPLAYTITLE:HILLS_BIN}}
{{TAGDEF|HILLS_BIN|[Integer]|{{TAG|NSW}}}}

Description: {{TAG|HILLS_BIN}} sets the number of steps after which the bias potential is updated in a metadynamics run (in case VASP was compiled with -Dtbdyn).
----
In metadynamics ({{TAG|MDALGO}}=11 {{!}} 21), the bias potential is given as 
:
\tilde{V}(t,\xi) = h \sum_{i=1}^{\lfloor t/t_G \rfloor} \exp{\left\{ -\frac{|\xi^{(t)}-\xi^{(i \cdot t_G)}|^2}{2
w^2} \right\}}.

Three parameters ({{TAG|HILLS_H}}, {{TAG|HILLS_W}}, and {{TAG|HILLS_BIN}}) must be provided by the user.

The number of steps after which the bias potential is updated is set by {{TAG|HILLS_BIN}}.
## Related tags and articles
Metadynamics,
{{TAG|HILLS_H}},
{{TAG|HILLS_W}},
{{FILE|HILLSPOT}},
{{TAG|MDALGO}}

{{sc|HILLS_BIN|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Advanced molecular-dynamics sampling
