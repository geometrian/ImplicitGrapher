#Formula for the innermost stable circular orbit, as reported by https://arxiv.org/pdf/1212.5758.pdf (eqn. 64)

#In prograde direction
def pro(pos):
    x,y,z=pos; M=1.0; a=x; Q=z; r=y
    tmp = M*r - Q*Q
    if tmp >= 0.0: return M*r*r*r - 6.0*M*M*r*r - 3.0*M*a*a*r + 9.0*M*Q*Q*r - 8.0*a*(tmp**(3.0/2.0)) + 4.0*Q*Q*(a*a-Q*Q)
    else:          return None

#In retrograde direction
def ret(pos):
    x,y,z=pos; M=1.0; a=x; Q=z; r=y
    tmp = M*r - Q*Q
    if tmp >= 0.0: return M*r*r*r - 6.0*M*M*r*r - 3.0*M*a*a*r + 9.0*M*Q*Q*r + 8.0*a*(tmp**(3.0/2.0)) + 4.0*Q*Q*(a*a-Q*Q)
    else:          return None
