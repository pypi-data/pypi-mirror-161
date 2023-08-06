# Associated Difference Spectrum

Suppose that there are $k$ excited species, which contrbute difference absorption spectrum.
Then transient difference absorption spectrum $\Delta A(E, t)$ is represented by

\begin{equation*}
\Delta A(E, t) = \sum_{i=1}^k c_i(E) y_i(t)
\end{equation*}
, where $c_i(E)$ and $y_i(t)$ is difference absorption coefficient and population of $i$th excited species, respectively.

Suppose that one measure difference absorption spectrum with energy point $E_1,\dotsc, E_n$ and time point $t_1, \dotsc, t_m$.

Denote 
\begin{align*}
\Delta A &= \left[A(E_i, t_j)\right]_{i,j} \\
C &= \left[c_i(E_j)\right]_{i,j} \\
Y &= \left[y_i(t_j)\right]_{i,j}
\end{align*}

Then $\Delta A$, $C$ and $Y$ is $n \times m$, $k \times n$ and $k \times m$ matrix, respectively.

Moreover
\begin{equation*}
\Delta A = C^T Y
\end{equation*}

Thus if one knows population matrix of excited species $Y$ and want to deduced associated difference spectrum matrix $C$, one should solve above equation.
If $m<k$ such equation is under determined, so to determine associated difference spectrum matrix $C$ one need to measure $m \geq k$ time points.
However every experimental spectrum has unsystematic error, to correct such kind of error, one should measure at least $k+1$ time points.

Suppose that one have measured $m \geq k+1$ time points with error $\mathrm{Err}$. Then such system is overdetermined, so our problem is changed to find best associated difference spectrum matrix $C$ which minimizes 
\begin{equation*}
\chi^2 = \left \| \frac{\Delta A-C^T Y}{\mathrm{Err}} \right\|^2
\end{equation*}

To find such best $C$, fix energy point $E_i$ and denote scaled population matrix $Y' = Y/\mathrm{Err}(E_i)$ and scaled transient absorption spectrum matrix $\Delta A'(E_i) = \Delta A(E_i)/\mathrm{Err}(E_i)$. Then by the orthogonal projection theorem, the best coefficient $C(E_i)$ at energy point $E_i$ given as
\begin{equation*}
C(E_i) = (Y'Y'^T)^{-1}Y'\left(\Delta A'(E_i)\right)^T
\end{equation*}
The inverse of $Y'Y'^T$ is called covarient matrix $\mathrm{Cov} = (Y'Y'^T)^{-1}$.
The error $\sigma(E_i)$ of estimated associated difference spectrum matrix $C(E_i)$ at energy point $E_i$ is estimated to
\begin{equation*}
\sigma(E_i) = \sqrt{\frac{\chi^2}{m-k}}\sqrt{\mathrm{diag}\left(Cov\right)}
\end{equation*}




