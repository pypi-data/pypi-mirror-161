# Model

## Exponentical decay

In pump-probe time resolved spectroscopy, we usually model the dynamics as sum of the exponential decay. For simplicity, I will consider one exponential decay model.

\begin{equation*}
{Model}(t) = \begin{cases}
0& \text{if $t<0$}, \\
\exp(-kt)& \text{if $t \geq 0$}.
\end{cases}
\end{equation*}

where $k$ is rate constant, inverse of the life time.

## Damped Oscillation

One can observe vibrational feature in pump-probe time resolved spectroscopy experiment, such vibrational feature can be modeled to damped oscillation.

\begin{equation*}
{Model}(t) = \begin{cases}
0 & \text{if $t<0$}, \\
\exp(-kt)\cos(2\pi t/T+\phi) & \text{if $t \geq 0$}.
\end{cases}
\end{equation*}

where $k$ is damping constant, inverse of the lifetime of vibration, $T$ is the period of vibration and $\phi$ is phase factor.
One can view damped oscillation as generalized form of exponential decay.