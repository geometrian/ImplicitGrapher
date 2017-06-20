def f(pos):
    x,y,z = pos
    return 2.0*z*(z*z - 3.0*x*x)*(1.0 - y*y) + (x*x + z*z)**2 - (2.0*y*y - 1.0)*(1.0 - y*y)
