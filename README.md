# pitree

https://chillistore.proxy.chilliwebs.com/storage/Projects/pitree/static/


sympy 

sp.sympify("x**2").evalf(subs={'x': 4, 't': 5})


expr = sp.sympify("x**2")
f = sp.lambdify('x', expr, "numpy")
data = np.linspace(1, 750, 750)
f(data)

sp.lambdify('x', sp.sympify("x**2"), "numpy")(data)


sp.lambdify('x', sp.sympify("ceil(sin(x*2))"), "numpy")(data)


\operatorname{round}\left(\frac{\left(\sin\left(x\cdot\frac{\pi}{4}\right)\ \right)}{2}+.5\right)

\operatorname{round}\left(3\sin\left(\tan\left(\frac{x}{3}\right)\right)\right)+3

\operatorname{round}\left(\operatorname{mod}\left(x,5\right)\right)
