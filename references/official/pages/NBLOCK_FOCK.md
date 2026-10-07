{{TAGDEF|NBLOCK_FOCK|[integer]}}
{{DEF|NBLOCK_FOCK|64|**CPU build** |32|**GPU build** (OpenACC/OpenMP offload))|OMP_NUM_THREADS|**CPU build** that is compiled with OpenMP support and threading is active (OMP_NUM_THREADS&nbsp;>&nbsp;1)}}
{{DISPLAYTITLE:NBLOCK_FOCK}}
Description: Sets the number of orbitals that are processed simultaneously when computing the action of the Fock potential.
----

Instead of computing the action of the Fock potential on one orbital at a time, up to {{TAG|NBLOCK_FOCK}} orbitals are gathered and processed at once. This enables the use of matrix-matrix operations rather than matrix-vector operations, which is beneficial for performance on modern hardware.

Tuning {{TAG|NBLOCK_FOCK}} can significantly affect both the performance and memory consumption of hybrid functional calculations. Especially on GPUs, {{TAG|NBLOCK_FOCK}} should be tuned carefully to achieve optimal performance.
{{NB|tip|On GPU architectures, the optimal value of {{TAG|NBLOCK_FOCK}} depends strongly on the specific hardware and the number of bands. It is recommended to experiment with values in the range 16-64.}}
## Related tags and articles
{{TAG|NSIM}},
{{TAG|LHFCALC}},
{{TAG|AEXX}},
{{TAG|HFSCREEN}},
{{TAG|NCORE}},
{{TAG|NPAR}},
{{TAG|KPAR}},
{{TAG|PRECFOCK}}

{{sc|NBLOCK_FOCK|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:PerformanceCategory:Hybrid functionalsCategory:parallelization
