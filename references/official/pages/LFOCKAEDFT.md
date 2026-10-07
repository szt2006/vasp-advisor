{{TAGDEF|LFOCKAEDFT|[logical]}}

{{DEF|LFOCKAEDFT|False|most calculations|True|optimized-potential methods with shape restoration active}}

Description: Use the same charge augmentation for the Hartree and DFT exchange-correlation part as is used in the Fock exchange and
the many-body methods beyond DFT, such as RPA and MP2.
----
{{TAG|LFOCKAEDFT}} should be set only in exceptional cases. The Hartree as well
as the DFT part are usually calculated very accurately using the one-center
PAW spheres. Restoring the all-electron charge accurately on the plane-wave
grid potentially adds noise, but should not change the results (relative energies,
forces etc.).

That augmentation is shape restoration, controlled by {{TAG|LMAXFOCKAE}} and {{TAG|NMAXFOCKAE}}.
## Related tags and articles
{{TAG|LMAXFOCKAE}},
{{TAG|NMAXFOCKAE}},
{{TAG|QMAXFOCKAE}}, Projector-augmented-wave formalism

{{sc|LFOCKAEDFT|Howto|Workflows that use this tag}}
## References
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid functionalsCategory:Many-body perturbation theoryCategory:GW
