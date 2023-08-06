# Signal, Gaussian IRF

## Exponential decay

When instrument response function is modeled as normalized gaussian distribution, experimental signal is modeled as convolution of exponentical decay and normalized gaussian distribution.

\begin{align*}
{Signal}_g(t) &= ({model} * {irf})(t) \\
&= \frac{1}{\sigma \sqrt{2\pi}} \int_0^{\infty} \exp(-kx)\exp\left(-\frac{(x-t)^2}{2\sigma^2}\right) \mathrm{d}x 
\end{align*}
Let $u=(x-t)/(\sigma\sqrt{2})$ then
\begin{align*}
{Signal}_g(t) &= \frac{\exp(-kt)}{\sqrt{\pi}} \int_{-t/(\sigma\sqrt{2})}^{\infty} \exp(-u^2-k\sigma\sqrt{2}u) \mathrm{d} u \\
&= \frac{\exp((k\sigma)^2/2-kt)}{\sqrt{\pi}} \int_{-t/(\sigma\sqrt{2})}^{\infty} \exp\left(-\left(u+\frac{k\sigma}{\sqrt{2}}\right)^2\right) \mathrm{d} u
\end{align*}
Let $v=u+(k\sigma)/\sqrt{2}$ then
\begin{align*}
{Signal}_g(t) &= \frac{\exp((k\sigma)^2/2-kt)}{\sqrt{\pi}} \int_{(k\sigma)/\sqrt{2}-t/(\sigma\sqrt{2})}^{\infty} \exp(-v^2) \mathrm{d} v \\
&= \frac{1}{2}\exp\left(\frac{(k\sigma)^2}{2}-kt\right)\mathrm{erfc}\left(\frac{1}{\sqrt{2}}\left(k\sigma - \frac{t}{\sigma}\right)\right)
\end{align*}

Let 

\begin{equation*}
z = k\sigma - \frac{t}{\sigma}
\end{equation*}

then, experimental signal could be modeled as

\begin{equation*}
{Signal}_g(t) = \frac{1}{2}\exp\left(k\sigma z - (k\sigma)^2/2\right)\mathrm{erfc}\left(\frac{z}{\sqrt{2}}\right)
\end{equation*}

$\mathrm{erfc}(x)$ is complementary error function, see [dlmf section 7.2](https://dlmf.nist.gov/7.2).

This is also equivalent to

\begin{equation*}
{Signal}_g(t) = \frac{1}{2}\exp\left(-\frac{t^2}{2\sigma^2}\right)\mathrm{erfcx}\left(\frac{z}{\sqrt{2}}\right)
\end{equation*}

$\mathrm{erfcx}(x)$ is scaled complementary error function, see [dlmf section 7.2](https://dlmf.nist.gov/7.2).

### Implementation Note

When $x>0$, $\mathrm{erfc}(x)$ deverges and when $x<0$, $\exp(-x)$ deverges.
To tame such divergency, I use following implementation.

\begin{equation*}
{Signal}_g(t) = \begin{cases}
\frac{1}{2}\exp\left(-\frac{t^2}{2\sigma^2}\right)\mathrm{erfcx}\left(\frac{z}{\sqrt{2}}\right) & \text{if $z>0$}, \\
\frac{1}{2}\exp\left(k\sigma z - (k\sigma)^2/2\right)\mathrm{erfc}\left(\frac{z}{\sqrt{2}}\right) & \text{otherwise}.
\end{cases}
\end{equation*}

## Damped oscillation

Note that 

\begin{align*}
{Model}(t) &= \exp\left(-kt\right)\cos\left(2\pi\frac{t}{T}+\phi\right) \\
&= \Re\left(\exp\left(i\phi\right)\exp\left(-kt+2\pi i \frac{t}{T}\right)\right)
\end{align*}

So let $k_{cplx} = k - (2\pi/T)i$ then ${Model}(t) = \Re\left(\exp\left(i\phi\right)\exp\left(-k_{cplx}t\right)\right)$.
Thus we can view the convolution of damped oscillation and gaussian irf function as the complex extension of the convolution of exponential decay and gaussian irf function.
Hence, let 
\begin{equation*}
z_{cplx} = k_{cplx}\sigma - \frac{t}{\sigma}
\end{equation*} 
then, the experimental signal can be modeled to 

\begin{equation*}
{Signal}_g(t) = \Re\left(\exp\left(i\phi\right)\exp\left(-\frac{t^2}{2\sigma^2}\right)w\left(\frac{iz_{cplx}}{\sqrt{2}}\right)\right)
\end{equation*}

, where $w(z)$ is the Faddeeva function, the complex extension of $\mathrm{erfcx}$ function, see [dlmf section 7.2](https://dlmf.nist.gov/7.2).

### Implementation Note 

When $\Re\left(z_{cplx} \right)>0$, Faddeeva function $w(iz_{cplx})$ is bounded. However when $\Re\left(z_{cplx}\right)<0$, Faddeeva function deverges quickly.
To tame such behavior, I use following symmetric relation for Faddeeva function.

\begin{equation*}
w(-z) = 2\exp\left(-z^2\right) - w(z)
\end{equation*}

Resulting the following implmentation.

\begin{equation*}
{Signal}_g(t) = \begin{cases}
\frac{1}{2}\exp\left(-\frac{t^2}{2\sigma^2}\right)w\left(\frac{iz_{cplx}}{\sqrt{2}}\right) & \text{if $\Re\left(z_{cplx}\right)>0$}, \\
\exp\left(k_{cplx}\sigma z - (k_{cplx}\sigma)^2/2\right) - \frac{1}{2}\exp\left(-\frac{t^2}{2\sigma^2}\right)w\left(-\frac{iz_{cplx}}{\sqrt{2}}\right) & \text{otherwise}.
\end{cases}
\end{equation*}








