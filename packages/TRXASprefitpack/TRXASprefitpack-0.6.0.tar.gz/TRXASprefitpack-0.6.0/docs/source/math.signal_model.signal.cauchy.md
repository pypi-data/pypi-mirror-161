# Signal, Cauchy IRF

## Exponential decay

When instrument response function is modeled as normalized cauchy distribution, experimental signal is modeled as convolution of exponentical decay and normalized cauchy distribution.

\begin{align*}
{Signal}_c(t) &= ({model} * {irf})(t) \\
&= \frac{1}{\pi} \int_0^{\infty} \frac{\gamma \exp(-kx)}{(x-t)^2+\gamma^2} \mathrm{d}x \\
&= \frac{1}{\pi} \Im\left(\int_0^{\infty} \frac{\exp(-kx)}{(x-t)-i\gamma} \mathrm{d}x \right)
\end{align*}

Assume $k > 0$, and let $u=k(x-t)-ik\gamma$, then $u(x)$ does not cross negative real axis. Thus,
\begin{align*}
{Signal}_c(t) &= \frac{1}{\pi} \exp(-kt) \Im\left(\exp(-ik\gamma) \int_{-kt-ik\gamma}^{\infty-ik\gamma} \frac{\exp(-u)}{u} \mathrm{d}u \right) \\
&= \frac{1}{\pi} \exp(-kt) \Im(\exp(-ik\gamma)E_1(-k(t+i\gamma))
\end{align*}

So, experimental signal could be modeled as

\begin{equation*}
{Signal_c}(t) = \begin{cases}
\frac{1}{2} + \frac{1}{\pi}\arctan\left(\frac{t}{\gamma}\right)& \text{if $k=0$}, \\
\frac{\exp(-kt)}{\pi} \Im(\exp(-ik\gamma)E_1(-k(t+i\gamma)))& \text{if $k>0$}.
\end{cases}
\end{equation*}

$E_1(z)$ is exponential integral, see [dlmf section 6.2](https://dlmf.nist.gov/6.2). 

### Implementation Note

At $|kt| > 200$, the following asymptotic expression is used.

\begin{equation*}
{Signal_c}(t) = -\frac{1}{\pi}\Im\left(\frac{1}{kt+i\gamma}\sum_{i=0}^{10} \frac{i!}{(kt+i\gamma)^i}\right)
\end{equation*}

## Damped oscillation

Define $\omega = 2\pi/T$.

Note that 

\begin{align*}
{Model}(t) &= \exp\left(-kt\right)\cos\left(\omega t +\phi\right) \\
&= \frac{1}{2}\exp\left(-kt\right)\left(\exp\left(i \omega t + i\phi\right) + \exp\left(-i\omega t - i\phi\right)\right)
\end{align*}

So, the convolution in the exponential decay section is divided by two parts. 

\begin{equation*}
{Model}(t) = \frac{1}{2\pi} \left(\Im\left(\int_0^{\infty} \frac{\exp(-kx+i\omega t)}{(x-t)-i\gamma} \mathrm{d}x \right)+\Im\left(\int_0^{\infty} \frac{\exp(-kx-i\omega t)}{(x-t)-i\gamma} \mathrm{d}x \right)\right)
\end{equation*}

With the proper choice of integral path or proper change of variable, one can derive the following equation.

Let

\begin{align*}
z_1 &=  -kt - \omega \gamma + i (\omega t - k\gamma) \\
z_2 &= -kt + \omega \gamma - i (\omega t + k \gamma)
\end{align*}

Then,

\begin{equation*}
{Model}(t) = \frac{1}{2\pi} \left(\Im\left(\exp\left(z_1+i\phi\right)\left(i \pi - \mathrm{Ei}(-z_1)\right)\right) + \Im\left(\exp\left(z_2-i\phi\right)E_1(z_2)\right)\right)
\end{equation*}
, where $\mathrm{Ei}(z)$ is the another exponential integral.

When $z$ is the complex number with $\Im z \neq 0$,

\begin{equation*}
\mathrm{Ei}(z) = -E_1(-z) + i \pi \cdot \mathrm{sgn} \left(\Im(z)\right)
\end{equation*}

So, the experimental signal can be expressed to

\begin{equation*}
{Model}(t) = \frac{1}{2\pi} \left(\Im\left(\exp\left(z_1+i\phi\right)\left(E_1(z_1) + i \pi \left(1+\mathrm{sgn}\left(\Im z_1 \right)\right)\right)\right) + \Im\left(\exp\left(z_2-i\phi\right)E_1(z_2)\right)\right)
\end{equation*}
