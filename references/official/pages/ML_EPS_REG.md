{{DISPLAYTITLE:ML_EPS_REG}}
{{TAGDEF|ML_EPS_REG|[real]|1E-15}}

Description: Initial value for the threshold of the eigenvalues of the covariance matrix in the evidence approximation.
----
This threshold is used to determine which eigenvalues \lambda_{k} of the covariance matrix \mathbf{\Phi}^{\mathrm{T}}\mathbf{\Phi}/\sigma^{2}_{\mathrm{v}} are used in the optimization of the regularization parameters \sigma^{2}_{\mathrm{w}} and \sigma^{2}_{\mathrm{v}} determined by the following equations

\sigma^{2}_{\mathrm{w}}=\frac{|\mathbf{\bar{w}}|^{2}}{\gamma},

\sigma^{2}_{\mathrm{v}}=\frac{|\mathbf{T}-\mathbf{\phi}\mathbf{\bar{w}}|^{2}}{M-\gamma},

\gamma=\sum\limits_{k=1}^{N_{\mathrm{B}}} \frac{\lambda_{k}}{\lambda_{k}+1/\sigma^{2}_{\mathrm{w}}} 
.

All eigenvalues satisfying \lambda_{i} / \lambda_{\mathrm{max}}  > {{TAG|ML_EPS_REG}} are included in the above equations, whereas smaller eigenvalues are disregarded (they are anyway potentially inaccurate because of loss of significance).

If at any point during iterating the above equations, the quadratic norm of errors (eight column of REGR/REGRF in ML_LOGFILE) becomes too large (more than 1.2 times larger than in previous iterations), the code assumes that numerical issues
(loss of significance) have occurred, and  then {{TAG|ML_EPS_REG}} is automatically doubled. Furthermore, if the regression does not converge within 10 steps, {{TAG|ML_EPS_REG}} is also increased by a factor of 4. The maximum allowed iteration depths is 50 (the iteration number is the second entry of REGR/REGRF in ML_LOGFILE). When 50 iterations are reached, no force field is created and there is most likely something seriously wrong in the calculation.

The seventh entry of REGR/REGRF in the ML_LOGFILE shows the ratio of the regularization (\sigma_{v}^{2}/ \sigma_{w}^{2}) and the largest eigenvalue. Usually this number is a number with many varying digits. If this number becomes a "well rounded" number (e.g. 1.00000000E-14), this is an indication that the cap for the current {{TAG|ML_EPS_REG}} is reached. That means that regularization becomes crucial. 
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_IALGO_LINREG}}, {{TAG|ML_IREG}}, {{TAG|ML_SIGV0}}, {{TAG|ML_SIGW0}}

{{sc|ML_EPS_LOW|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Machine-learned force fields
