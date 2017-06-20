from OpenGL.GL import *
from OpenGL.GLU import *

from helpers import *



neighbors_7 = []
for k in [0,1]:
    for j in [0,1]:
        for i in [0,1]:
            if i!=0 or j!=0 or k!=0:
                neighbors_7.append( (i,j,k) )

neighbors_26 = []
for k in [-1,0,1]:
    for j in [-1,0,1]:
        for i in [-1,0,1]:
            if i!=0 or j!=0 or k!=0:
                neighbors_26.append( (i,j,k) )



class Grid(object):
    def __init__(self, err_func, pos,dim,res, level):
        self.err_func = err_func
        
        self.pos = tuple(pos) #lower corner
        self.dim = tuple(dim) #physical size

        self.res = tuple(res) #resolution (cells)

        self.eps = ( dim[0]/res[0], dim[1]/res[1], dim[2]/res[2] ) #cells' physical size

        self.level = level
        self.min_sublevel = level
        self.max_sublevel = level

        self.coords = []
        self.errs = []

        self.points_neg = []
        self.points_err = []
        self.points_zero = []
        self.points_pos = []
        self.subgrids = {}

    def get_pos(self, i,j,k):
        xf = self.pos[0] + i*self.eps[0]
        yf = self.pos[1] + j*self.eps[1]
        zf = self.pos[2] + k*self.eps[2]
        return (xf,yf,zf)

    def subdiv_at(self, i,j,k, subdiv_res, max_level):
        subgrid = Grid( self.err_func, self.coords[k][j][i],self.eps,subdiv_res, self.level+1 )
        subgrid.calc( subdiv_res, max_level )
        self.subgrids[(i,j,k)] = subgrid
        self.max_sublevel = max([ self.max_sublevel, subgrid.max_sublevel ])
##    def subdiv_force(self):
##        

    def calc(self, subdiv_res, max_level):
        for k in range(self.res[2]+1):
            lvl_p=[]; lvl_e=[]
            for j in range(self.res[1]+1):
                row_p=[]; row_e=[]
                for i in range(self.res[0]+1):
                    pos = self.get_pos(i,j,k)
                    err = self.err_func(pos)
                    row_p.append( pos )
                    row_e.append( err )
                    if err != None:
                        if err>=0.0: self.points_pos.append(pos)
                        else:        self.points_neg.append(pos)
                    else:
                        self.points_err.append(pos)
                lvl_p.append(row_p); lvl_e.append(row_e)
            self.coords.append(lvl_p); self.errs.append(lvl_e)
##        found = [False,False,False]
##        for lvl in self.errs:
##            for row in lvl:
##                for err in row:
##                    if   err==None: found[1]=True
##                    elif err<  0.0: found[0]=True
##                    elif err>= 0.0: found[2]=True
##        print(found)
##        assert found[0] and found[2]
        if self.level < max_level:
            for k in range(self.res[2]):
                for j in range(self.res[1]):
                    for i in range(self.res[0]):
                        e000 = self.errs[k][j][i]
                        for ii,jj,kk in neighbors_7:
                            eiijjkk = self.errs[k+kk][j+jj][i+ii]
                            if ((e000==None) != (eiijjkk==None)) or ((e000!=None) and (sgn(e000)!=sgn(eiijjkk))):
                                self.subdiv_at(i,j,k, subdiv_res, max_level)
                                break
##            while True:
##                found = False
##                for k in range(1,self.res[2]-1,1):
##                    for j in range(1,self.res[1]-1,1):
##                        for i in range(1,self.res[0]-1,1):
##                            for ii,jj,kk in neighbors_26:
##                                if (i+ii,j+jj,k+kk) in self.subgrids.keys():
##                                    at_least_to = self.subgrids[(i+ii,j+jj,k+kk)].max_sublevel
##                                    if (i,j,k) not in self.subgrids.keys():
##                                        self.subdiv_at(i,j,k, subdiv_res, max_level)
##                                        found = True
##                                    while self.subgrids[(i,j,k)].max_sublevel + 1 < at_least_to:
##                                        self.subgrids[(i,j,k)].subdiv_force()
##                                        self.max_sublevel = max([ self.max_sublevel,  self.subgrids[(i,j,k)].max_sublevel ])
##                                        found = True
##                if not found: break
        else:
            def line(data0,data1):
                p0,e0 = data0
                p1,e1 = data1
                if (e0!=None) and (e1!=None) and (sgn(e0)!=sgn(e1)):
                    denom = e0 - e1
                    if denom != 0.0:
                        t = e0 / denom
                        p = lerp_vec(p0,p1, t)
                        return [p]
                return []
            for k in range(self.res[2]):
                for j in range(self.res[1]):
                    for i in range(self.res[0]):
                        data000 = ( self.coords[k  ][j  ][i  ], self.errs[k  ][j  ][i  ] )
                        data100 = ( self.coords[k  ][j  ][i+1], self.errs[k  ][j  ][i+1] )
                        data010 = ( self.coords[k  ][j+1][i  ], self.errs[k  ][j+1][i  ] )
                        data110 = ( self.coords[k  ][j+1][i+1], self.errs[k  ][j+1][i+1] )
                        data001 = ( self.coords[k+1][j  ][i  ], self.errs[k+1][j  ][i  ] )
                        data101 = ( self.coords[k+1][j  ][i+1], self.errs[k+1][j  ][i+1] )
                        data011 = ( self.coords[k+1][j+1][i  ], self.errs[k+1][j+1][i  ] )
                        data111 = ( self.coords[k+1][j+1][i+1], self.errs[k+1][j+1][i+1] )

                        self.points_zero += line(data000,data100)
                        self.points_zero += line(data001,data101)
                        self.points_zero += line(data010,data110)
                        self.points_zero += line(data011,data111)

                        self.points_zero += line(data000,data010)
                        self.points_zero += line(data001,data011)
                        self.points_zero += line(data100,data110)
                        self.points_zero += line(data101,data111)

                        self.points_zero += line(data000,data001)
                        self.points_zero += line(data010,data011)
                        self.points_zero += line(data100,data101)
                        self.points_zero += line(data110,data111)
        return self.level

    def draw_points_neg(self):
        for p in self.points_neg: glVertex3f(*p)
        for subgrid in self.subgrids.values(): subgrid.draw_points_neg()
    def draw_points_err(self):
        for p in self.points_err: glVertex3f(*p)
        for subgrid in self.subgrids.values(): subgrid.draw_points_err()
    def draw_points_zero(self):
        for p in self.points_zero: glVertex3f(*p)
        for subgrid in self.subgrids.values(): subgrid.draw_points_zero()
    def draw_points_pos(self):
        for p in self.points_pos: glVertex3f(*p)
        for subgrid in self.subgrids.values(): subgrid.draw_points_pos()
        
    def draw_lines(self):
        if True:#len(self.subgrids) > 0:
            if True:#self.level in [3]:
                colors = [
                    (1.0,0.5,0.0),
                    #(1.0,1.0,0.0),
                    (0.5,1.0,0.0),
                    #(0.0,1.0,0.5),
                    (0.0,1.0,1.0),
                    #(0.0,0.5,1.0)
                ]
                glColor3f(*colors[self.level%len(colors)])
                for k in range(self.res[2]+1):
                    for j in range(self.res[1]+1):
                        glVertex3f(*self.coords[k][j][ 0])
                        glVertex3f(*self.coords[k][j][-1])
                for k in range(self.res[2]+1):
                    for i in range(self.res[0]+1):
                        glVertex3f(*self.coords[k][ 0][i])
                        glVertex3f(*self.coords[k][-1][i])
                for j in range(self.res[1]+1):
                    for i in range(self.res[0]+1):
                        glVertex3f(*self.coords[ 0][j][i])
                        glVertex3f(*self.coords[-1][j][i])
        for subgrid in self.subgrids.values():
            subgrid.draw_lines()
