def f(pos):
    cx,cy,cz = 0,0,0
    r = 0.8

    x,y,z = pos

    dx = x - cx
    dy = y - cy
    dz = z - cz

    dist = (dx*dx + dy*dy + dz*dz)**0.5

    return dist - r
