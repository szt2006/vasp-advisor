{{DISPLAYTITLE:ANDERSEN_PROB}}
{{TAGDEF|ANDERSEN_PROB|0&le;[real]&le;1|0}}

Description: {{TAG|ANDERSEN_PROB}} sets the collision probability for the Anderson thermostat (in case VASP was compiled with -Dtbdyn).
----
In the approach proposed by Andersen the system is thermally coupled to a fictitious heat bath with the desired temperature. The coupling is represented by stochastic impulsive forces that act occasionally on randomly selected particles. The collision probability is defined as an average number of collisions per atom and time-step. This quantity can be controlled by the flag {{TAG|ANDERSEN_PROB}}. The total number of collisions with the heat-bath is written in the file {{FILE|REPORT}} for each MD step.
{{NB|tip|Setting {{TAG|ANDERSEN_PROB}}{{=}}0, *i.e.*, no collisions with the heat-bath) generates the microcanonical (*NVE*) ensemble.}}
## Related tags and articles
{{TAG|MDALGO}}

{{sc|ANDERSEN_PROB|Examples|Examples that use this tag}}
## References
</references>

----

Category:INCAR tagCategory:Molecular dynamicsCategory:Thermostats
