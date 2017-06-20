#Simple function that defines the disgned distance to a sphere.
#   For a sphere defined by:
#       (x-a)² + (y-b)² + (z-c)² - r² = 0
#   The signed distance to the surface (positive outside, negative
#   inside) is given by:
#       d = ||<x,y,z> - <a,b,c>|| - r

def f(pos):
    a,b,c = 0,0,0
    r = 0.8

    x,y,z = pos

    dx = x - a
    dy = y - b
    dz = z - c

    dist = (dx*dx + dy*dy + dz*dz)**0.5

    return dist - r
