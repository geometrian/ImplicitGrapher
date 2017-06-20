def sgn(x):
    if x>=0.0: return 1.0
    return -1.0
def clamp(x, l,h):
    if x<l: return l
    if x>h: return h
    return x
def lerp_sc(s0,s1,t):
    return s0*(1.0-t) + s1*t
def lerp_vec(p0,p1,t):
    return [
        p0[0]*(1.0-t) + p1[0]*t,
        p0[1]*(1.0-t) + p1[1]*t,
        p0[2]*(1.0-t) + p1[2]*t
    ]
def vec_sub(v0,v1): return [v0[i]-v1[i] for i in range(len(v0))]
def vec_add(v0,v1): return [v0[i]+v1[i] for i in range(len(v0))]
def sc_vec(s,v): return [s*v[i] for i in range(len(v))]
def vec_cross(a,b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]
def vec_dot(v0,v1): return sum([v0[i]*v1[i] for i in range(len(v0))])
def vec_length_sq(v): return vec_dot(v,v)
def vec_length(v): return vec_length_sq(v)**0.5
def vec_normalize(v): return sc_vec(1.0/vec_length(v),v)
