{{TAGDEF| LSFBXC |.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: Removes sources and drains from the exchange-correlation B field.
----

With {{TAG|LSFBXC}}=T, the sources and drains are removed from the exchange-correlation (XC) B field{{cite|sharma:jctc:2018}} at each step of the electronic minimization. Thus, any XC potential can be constrained to correspond to a Maxwellian magnetic field at the cost of becoming a potential-only XC functional, since there is no correction applied to the XC energy. In other words, it is strictly necessary to optimize the Kohn-Sham orbitals using iterative methods, e.g. {{TAGDEF|ALGO|Normal}}, and it is *not* possible to use direct optimizers, e.g. {{TAGDEF|ALGO|Conjugate}}, etc., as they require consistency between XC energy and XC potential.

Moore et al. implemented the same feature in a parallel work{{cite|guy:patch:2024}}{{cite|guy:arxiv:2024}} and performed more extensive applications. Whether the two implementations are identical has not been tested, and no publication is associated with the present implementation (by Marie-Therese Huebsch) using {{TAG|LSFBXC}}.
## Related tags and articles
{{TAG|XC}}, {{TAG|GGA}}
## References
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Magnetism
