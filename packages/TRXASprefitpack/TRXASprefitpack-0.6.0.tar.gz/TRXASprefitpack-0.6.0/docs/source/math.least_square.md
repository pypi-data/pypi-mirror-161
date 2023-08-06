# Least Square Regression

## Chi squared and maximum likelyhood estimation

Suppose that our measurement data $y_i$ is independent each other and obeys $N(\bar{y}_i, \sigma_i)$.
Then likelihood function $\mathcal{L}(\bar{\mathbf{y}} | \mathbf{y})$ is given by

\begin{align*}
\mathcal{L}(\bar{\mathbf{y}} | \mathbf{y}) &= \prod_i P(\bar{y}_i | y_i) \\
&= C \exp \left ( - \frac{1}{2} \sum_i \left(\frac{y_i-\bar{y}_i}{\sigma_i}\right)^2 \right)
\end{align*}
, for some constant $C$.

Define $\chi^2$ as

\begin{equation*}
\chi^2 = \sum_i \left(\frac{y_i-\bar{y}_i}{\sigma_i}\right)^2
\end{equation*}

then, 

\begin{equation*}
P(\bar{\mathbf{y}} | \mathbf{y}) = C \exp \left(-\chi^2/2 \right)
\end{equation*}

So, the log likelihood function $\log \mathcal{L}(\bar{\mathbf{y}} | \mathbf{y})$ is
\begin{equation*}
\log \mathcal{L}(\bar{\mathbf{y}}, \mathbf{y}) = \log C - \frac{\chi^2}{2}
\end{equation*}

Thus, maximizing likelihood or log likelihood is same as minimizing $\chi^2$.

In common fitting process we estimate $\bar{y}_i$ as 

\begin{equation*}
\bar{y}_i = f(x_i, \mathbf{\theta})
\end{equation*}

, so our likelihood, log likelihood and chi squared function are the function of fitting paramter $\mathbf{\theta}$.

## Linear Least Square

Suppose that our fitting function $f(x, \mathbf{\theta})$ is the linear combination of some function $g_i(x)$ which does not depends on $\mathbf{\theta}$.

\begin{align*}
f(x, \mathbf{\theta}) &= \sum_i \theta_i g_i(x) \\
&= \mathbf{\theta}^T \mathbf{g}(x)
\end{align*}

Define matrix $G$ as

\begin{equation*}
G = \left [ \frac{g_j(x_i)}{\sigma_i} \right ]_{i,j}
\end{equation*}

and set $\mathbf{y}' = \mathbf{y}/\mathbf{\sigma}$ then

\begin{equation*}
\chi^2(\mathbf{\theta}) = \| G \mathbf{\theta} - \mathbf{y}' \|^2
\end{equation*}

To minimize $\chi^2$, we require

\begin{equation*}
\frac{\partial \chi^2}{\partial \theta_i} = 0
\end{equation*}

then we have following equation, which is usually called normal equation.

\begin{equation*}
\mathbf{\theta} = (G^T G)^{-1} G^T \mathbf{y}'
\end{equation*}

The $(G^T G)^{-1}$ is called paramter convariance matrix, which is denoted by ${Cov}$.

The standard error of paramter ${Err}(\mathbf{\theta})$ is defined as

\begin{equation*}
{Err}(\mathbf{\theta})^2 = \frac{\chi^2}{N-p} {diag}(Cov)
\end{equation*}

, where $N$ is the total number of data points and $p$ is the number of paramter.

Note that the $G$ is also the scaled jacobian of model function $f(x, \mathbf{\theta})$ with respect to paramter $\mathbf{\theta}$.

So, one can extend to definition of standard error of paramter in linear least square regression to non-linear one.

\begin{align*}
{Cov} &= (J^T J)^{-1} \\
{Err}(\mathbf{\theta})^2 &= \frac{\chi^2}{N-p} {diag}(Cov)
\end{align*}
, where $J$ is the scaled jacobian of non-linear model function $f(x, \mathbf{\theta})$ with respect to paramter $\mathbf{\theta}$.

Such paramter error estimation is called, Asymptotic Standard Errors.
However, strictly speaking, Asymptotic Standard Error estimation should not be used in non-linear least square regression.

Our package `TRXASprefitpack` provides alternative error paramter estimation method based on `F-test`.

## Alternative Paramter Error Estimation

Define $\chi^2_i(x)$ as

\begin{equation*}
\chi^2_i (x) = {arg}\,{min}_{\mathbf{\theta}, \theta_i = x} \chi^2 (\theta)
\end{equation*}

Then the number of paramter corresponding to $\chi^2_i$ is $P-1$.

### F-test based paramter error estimation

Let $\chi^2_0 = \chi^2(\theta_0)$ be the minimum chi square value.
One can estimates confidence interval of $i$th optimal paramter $\theta_{0, i}$ with significant level $\alpha$ by

\begin{equation*}
F_{\alpha}(1, n-p) = \frac{\chi^2_i(\theta)-\chi^2_0}{\chi^2_0/(n-p)}
\end{equation*}

## Compare two different fit

Assume that model 2 is the restriction of model 1. Then you can compare two model based on f-test.

## Seperation Scheme

Suppose that

\begin{equation*}
f(t, \mathbf{\theta}_{l}, \mathbf{\theta}_{nl}) = \mathbf{\theta}_{l}^T \mathbf{g}(t, \mathbf{\theta}_{nl})
\end{equation*}

Then

\begin{equation*}
 {arg}\,{min}_{\mathbf{\theta}_l, \mathbf{\theta_{nl}}} \chi^2 = 
 {\arg}\,{min}_{\mathbf{\theta}} \left({\arg}\,{min}_{\mathbf{\theta}_l} \chi^2(\mathbf{\theta}_l, \mathbf{\theta})\right)
\end{equation*}

The optimization problem

\begin{equation*}
{\arg}\,{min}_{\mathbf{\theta}_l} \chi^2(\mathbf{\theta}_l, \mathbf{\theta})
\end{equation*}

is just linear least square problem described in linear least square section and we know exact solution of such problem.
Let $\mathbf{\theta}_{l} = \mathbf{C}(\mathbf{\theta})$ be the least norm solution of the linear least square problem and define
$\chi'^2(\mathbf{\theta}) = \chi^2(\mathbf{C}(\mathbf{\theta}), \mathbf{\theta})$ then

\begin{align*}
{arg}\,{min}_{\mathbf{\theta}} \chi'^2 &= {arg}\,{min}_{\mathbf{\theta}_l, \mathbf{\theta_{nl}}} \chi^2 \\
\frac{\partial \chi^2}{\partial \mathbf{\theta}_l} \Big |_{\mathbf{\theta}_l = \mathbf{C}(\mathbf{\theta}), \mathbf{\theta}_{nl} = \mathbf{\theta}} &= 0
\end{align*}

So, by chain rule the gradient of $\chi'^2(\mathbf{\theta})$ is

\begin{align*}
\frac{\partial \chi'^2}{\partial \mathbf{\theta}} &= 
\frac{\partial \chi^2}{\partial \mathbf{\theta}_l} \Big |_{\mathbf{\theta}_l = \mathbf{C}(\mathbf{\theta})} 
\frac{\partial \mathbf{C}(\mathbf{\theta})}{\partial \mathbf{\theta}} + \frac{\partial \chi^2}{\partial \mathbf{\theta}} \\
&= \frac{\partial \chi^2}{\partial \mathbf{\theta}}
\end{align*}

Because of $\frac{\partial \mathbf{C}(\mathbf{\theta})}{\partial \mathbf{\theta}}$ term, it is hard to obtain analytic hessian of $\chi'^2/2$ which is used to
estimate the Asymptotic Standard Errors.

However, implementing separation scheme will speed up optimization process.
Since, it reduces dimension of optimization problem but gradient is same as original $\chi^2$ function.