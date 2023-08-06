from .PyVertex import wolfvertex

my=wolfvertex(1.0,2.0,3.0)
c=my.coords

c[0]=3.
d=my.coords
print(my.x,c[0],d[0])