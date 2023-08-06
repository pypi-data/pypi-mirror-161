# Pseudo Voigt

Someone models instrument response function as voigt profile. Since convolution with voigt profile is hard, I approximate voigt profile to linear combination of cauchy and gaussian distribution. Such approximated function is usually called pseudo voigt profile.

\begin{equation*}
{IRF}(t, {fwhm}, {eta}) = \eta C(t, {fwhm}) + (1-\eta)G(t, {fwhm})
\end{equation*}

where, ${fwhm}$ is unifrom full width at half maximum parameter and $\eta$ is the mixing parameter.

However, the paramter (${fwhm}$, $\eta$) in pseudo voigt profile shown in above is different from the parameter (${fwhm}_G$, ${fwhm}_L$) in voigt profile function.

To resolve such paramter mismatch, another type of pseudo voigt profile function is proposed.

\begin{align*}
{pv}(t, {fwhm}_G, {fwhm}_L) &= \eta({fwhm}_G, {fwhm}_L) C(t, {fwhm}({fwhm}_G, {fwhm}_L)) \\
&+ (1-\eta({fwhm}_G, {fwhm}_L)) G(t, {fwhm}({fwhm}_G, {fwhm}_L))
\end{align*}, where

\begin{align*}
{fwhm} &= ({fwhm}_G^5+2.69269{fwhm}_G^4{fwhm}_L+2.42843{fwhm}_G^3{fwhm}_L^2 \\
&+  4.47163{fwhm}_G^2{fwhm}_L^3+0.07842{fwhm}_G{fwhm}_L^4 \\
&+ {fwhm}_L^5)^{1/5} \\
\eta &= 1.36603({fwhm}_L/f)-0.47719({fwhm}_L/f)^2+0.11116({fwhm}_L/f)^3
\end{align*}

Such ${fwhm}$ and $\eta$ function are taken from [J. Appl. Cryst. (2000). **33**, 1311-1316](https://doi.org/10.1107/S0021889800010219).