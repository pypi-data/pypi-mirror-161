from sympy import *

t,a,b,c,d=symbols('t a b c d')

print(integrate(a/pow(t+b,c),t))
print(diff(a/pow(t+b,c),t))

#print(integrate(a/t**b,t))

