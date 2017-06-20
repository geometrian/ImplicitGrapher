from math import *



POWER = 8.0
n = 64

def length(v):
    return ( v[0]*v[0] + v[1]*v[1] + v[2]*v[2] )**0.5

def f(pos):
    #http://www.fractalforums.com/programming/inaccurate-mandelbulb-de-for-far-distances/
    l = length(pos)
    if l>3.0+1.0: return l-3.0

    #http://blog.hvidtfeldts.net/index.php/2011/09/distance-estimated-3d-fractals-v-the-mandelbulb-different-de-approximations/

    z = pos
    dr = 1.0
    for i in range(n):
        r = length(z)
        if r>6.0 or r<0.001: break

        #Convert to polar coordinates
        theta = acos(z[2]/r)
        phi = atan2(z[1],z[0])
        dr = (r**(POWER-1.0))*POWER*dr + 1.0

        #Scale and rotate the point
        zr = r ** POWER
        theta *= POWER
        phi *= POWER

        #Convert back to Cartesian coordinates
        s_theta = sin(theta)
        z = [
            zr*s_theta*cos(  phi),
            zr*s_theta*sin(  phi),
            zr*        cos(theta)
        ]
        z[0]+=pos[0]; z[1]+=pos[1]; z[2]+=pos[2]

    if r > 0.0:
        return 0.5*log(r)*r/dr
    else:
        return 0.0
