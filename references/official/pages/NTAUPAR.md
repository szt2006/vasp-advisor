{{TAGDEF|NTAUPAR|[integer]}}
{{DEF|NTAUPAR|depends on {{TAG|MAXMEM}} |used in low scaling GW and RPA/ACFDT calculations.}}

Description: {{TAG|NTAUPAR}} available as of VASP.6, specifies the number of MPI groups sharing same imaginary time grid points. The default value of NTAUPAR is set to the largest possible value supported on the compute nodes to speed up the GW or RPA calculation.
----
NTAUPAR has the biggest impact on memory usage as well as total runtime for low-scaling GW and RPA calculations. If not found in the {{FILE|INCAR}}, NTAUPAR is set automatically based on the value of {{TAG|MAXMEM}} (the available memory for each rank on each compute node), such that the GW and RPA job fits in the RAM on each compute node. 

If {{TAG|MAXMEM}} is not set, VASP looks in "/proc/meminfo" for "MemAvailable" to set {{TAG|MAXMEM}} internally, otherwise the code uses the value provided in the {{FILE|INCAR}}. 

NTAUPAR={{TAG|NOMEGA}} is the maximum value possible, while NTAUPAR=1 is the smallest possible value. 
## Related tags and articles
{{TAG|NOMEGAPAR}}, 
{{TAG|NOMEGA}}

{{sc|NTAUPAR|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:GWCategory:ACFDTCategory:PerformanceCategory:ParallelizationCategory:Low-scaling GW and RPACategory:Memory
