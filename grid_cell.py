from OpenGL.GL import *
from OpenGL.GLU import *

from helpers import *



class Link(object):
    def __init__(self, lower,upper):
        self.lower = lower
        self.upper = upper
    def other(self, obj):
        if self.lower==obj: return self.upper
        return self.lower

class Cell(object):
    def __init__(self, err_func, level, pos,eps):
        self.err_func = err_func
        
        self.level = level

        self.children = None
        self.points = [
            [], #err
            [], #neg
            [], #zero
            []  #pos
        ]
        self.neighbors = [ None for direction in range(6) ]

        #Values at lower corner
        self.pos = pos
        self.eps = eps
        self.err = err_func(self.pos)
        if self.err != None:
            if self.err>=0.0: self.points[3].append(pos)
            else:             self.points[1].append(pos)
        else:
            self.points[0].append(pos)

    def subdiv(self):
        #Ensure that our neighbors are either the same size or one level smaller than us, so that the
        #   subdivision will not be invalid.
        def subdiv_neighbors():
            for direction in range(6):
                neighbor_record = self.neighbors[direction]
                if type(neighbor_record) == type([]):
                    #Four neighbors in this direction are smaller than us
                    pass
                elif neighbor_record != None:
                    #Neighbor is either the same size as or larger than us
                    neighbor = neighbor_record.other(self)
                    if neighbor.level == self.level - 1:
                        #Neighbor is larger than us.  Make it the same size as us.
                        neighbor.subdiv()
                        return True #Need to start over because our former neighbor just split, changing our self.neighbors.
            return False
        while subdiv_neighbors(): pass

        #Subdivide the neighbor links as-necessary
        for direction in range(6):
            neighbor_record = self.neighbors[direction]
            if type(neighbor_record) == type([]):
                #We have four smaller neighbors in this direction
                pass
            elif neighbor_record != None:
                #We have one equal-size neighbor in this direction; update to have four links with it
                link = self.neighbors[direction]
                neighbor = link.other(self)
                newlinks = [ Link(link.lower,link.upper) for i in range(4) ]
                self.    neighbors[direction  ] = newlinks
                neighbor.neighbors[direction^1] = newlinks
            else:
                self.    neighbors[direction  ] = [ None for i in range(4) ]
        
        #Generate children
        half_eps = sc_vec(0.5,self.eps)
        half_pos = vec_add(self.pos,half_eps)
        self.children = [
            Cell(self.err_func, self.level+1, [self.pos[0],self.pos[1],self.pos[2]], half_eps), #0b000
            Cell(self.err_func, self.level+1, [self.pos[0],self.pos[1],half_pos[2]], half_eps), #0b001
            Cell(self.err_func, self.level+1, [self.pos[0],half_pos[1],self.pos[2]], half_eps), #0b010
            Cell(self.err_func, self.level+1, [self.pos[0],half_pos[1],half_pos[2]], half_eps), #0b011
            Cell(self.err_func, self.level+1, [half_pos[0],self.pos[1],self.pos[2]], half_eps), #0b100
            Cell(self.err_func, self.level+1, [half_pos[0],self.pos[1],half_pos[2]], half_eps), #0b101
            Cell(self.err_func, self.level+1, [half_pos[0],half_pos[1],self.pos[2]], half_eps), #0b110
            Cell(self.err_func, self.level+1, [half_pos[0],half_pos[1],half_pos[2]], half_eps)  #0b111
        ]

        #Update neighbors' links to point to children
        def update_and_connect_link(axis, link,child):
            if link != None:
                if link.lower == self:
                    link.lower = child
                    child.neighbors[2*axis+1] = link
                else:
                    link.upper = child
                    child.neighbors[2*axis  ] = link
        #   X
        update_and_connect_link( 0, self.neighbors[0][0b00],self.children[0b000] )
        update_and_connect_link( 0, self.neighbors[0][0b10],self.children[0b001] )
        update_and_connect_link( 0, self.neighbors[0][0b01],self.children[0b010] )
        update_and_connect_link( 0, self.neighbors[0][0b11],self.children[0b011] )
        update_and_connect_link( 0, self.neighbors[1][0b00],self.children[0b100] )
        update_and_connect_link( 0, self.neighbors[1][0b10],self.children[0b101] )
        update_and_connect_link( 0, self.neighbors[1][0b01],self.children[0b110] )
        update_and_connect_link( 0, self.neighbors[1][0b11],self.children[0b111] )
        #   Y
        update_and_connect_link( 1, self.neighbors[2][0b00],self.children[0b000] )
        update_and_connect_link( 1, self.neighbors[2][0b10],self.children[0b100] )
        update_and_connect_link( 1, self.neighbors[2][0b01],self.children[0b001] )
        update_and_connect_link( 1, self.neighbors[2][0b11],self.children[0b101] )
        update_and_connect_link( 1, self.neighbors[3][0b00],self.children[0b010] )
        update_and_connect_link( 1, self.neighbors[3][0b10],self.children[0b110] )
        update_and_connect_link( 1, self.neighbors[3][0b01],self.children[0b011] )
        update_and_connect_link( 1, self.neighbors[3][0b11],self.children[0b111] )
        #   Z
        update_and_connect_link( 2, self.neighbors[4][0b00],self.children[0b000] )
        update_and_connect_link( 2, self.neighbors[4][0b10],self.children[0b100] )
        update_and_connect_link( 2, self.neighbors[4][0b01],self.children[0b010] )
        update_and_connect_link( 2, self.neighbors[4][0b11],self.children[0b110] )
        update_and_connect_link( 2, self.neighbors[5][0b00],self.children[0b001] )
        update_and_connect_link( 2, self.neighbors[5][0b10],self.children[0b101] )
        update_and_connect_link( 2, self.neighbors[5][0b01],self.children[0b011] )
        update_and_connect_link( 2, self.neighbors[5][0b11],self.children[0b111] )

        #Insert links between children
        def add_link(axis, lower,upper):
            link = Link(lower,upper)
            lower.neighbors[2*axis+1] = link
            upper.neighbors[2*axis  ] = link
        #   X
        add_link(0, self.children[0b000],self.children[0b100])
        add_link(0, self.children[0b001],self.children[0b101])
        add_link(0, self.children[0b010],self.children[0b110])
        add_link(0, self.children[0b011],self.children[0b111])
        #   Y
        add_link(1, self.children[0b000],self.children[0b010])
        add_link(1, self.children[0b001],self.children[0b011])
        add_link(1, self.children[0b100],self.children[0b110])
        add_link(1, self.children[0b101],self.children[0b111])
        #   Z
        add_link(2, self.children[0b000],self.children[0b001])
        add_link(2, self.children[0b010],self.children[0b011])
        add_link(2, self.children[0b100],self.children[0b101])
        add_link(2, self.children[0b110],self.children[0b111])

        self.neighbors = None #This is now the children's responsibility
    def subdiv_to_at_least(self, level):
        if self.level < level and self.children == None:
            self.subdiv()
        if self.children != None:
            for child in self.children:
                child.subdiv_to_at_least(level)
    def subdiv_refine(self, max_level):
        if self.children==None and self.level<max_level:
            e000 = self.err
            if self.neighbors[1] != None:
                if type(self.neighbors[1])==type([]): e100=self.neighbors[1][0b00].upper.err
                else:                                 e100=self.neighbors[1]      .upper.err
            else:                                     e100=None
            if self.neighbors[3] != None:
                if type(self.neighbors[3])==type([]): e010=self.neighbors[3][0b00].upper.err
                else:                                 e010=self.neighbors[3]      .upper.err
            else:                                     e010=None
            if self.neighbors[5] != None:
                if type(self.neighbors[5])==type([]): e001=self.neighbors[5][0b00].upper.err
                else:                                 e001=self.neighbors[5]      .upper.err
            else:                                     e001=None
            for eiijjkk in [e100,e010,e001]:
                if ((e000==None) != (eiijjkk==None)) or ((e000!=None) and (sgn(e000)!=sgn(eiijjkk))):
                    self.subdiv()
                    break
        if self.children != None:
            for child in self.children:
                child.subdiv_refine(max_level)
        else:
            #will calc
            pass

    def calc(self):
        if self.children != None:
            for child in self.children:
                child.calc()
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
            def data_from(node):
                return ( node.pos, node.err )
            data000 = data_from(self)
            if self.neighbors[1] != None:
                if type(self.neighbors[1])==type([]): data100=data_from(self.neighbors[1][0b00].upper)
                else:                                 data100=data_from(self.neighbors[1]      .upper)
                self.points[2] += line(data000,data100)
            if self.neighbors[3] != None:
                if type(self.neighbors[3])==type([]): data010=data_from(self.neighbors[3][0b00].upper)
                else:                                 data010=data_from(self.neighbors[3]      .upper)
                self.points[2] += line(data000,data010)
            if self.neighbors[5] != None:
                if type(self.neighbors[5])==type([]): data001=data_from(self.neighbors[5][0b00].upper)
                else:                                 data001=data_from(self.neighbors[5]      .upper)
                self.points[2] += line(data000,data001)

    def draw_points(self, ind):
        if self.children != None:
            for child in self.children:
                child.draw_points(ind)
        else:
            for p in self.points[ind]: glVertex3f(*p)

    def draw_grid(self, if_level):
        if self.level == if_level:
            if self.children!=None or len(self.points[2])>0:
                top = vec_add(self.pos,self.eps)
##                glColor3f(1,0,0)
                glVertex3f(*self.pos); glVertex3f(top[0],self.pos[1],self.pos[2])
                glVertex3f(*self.pos); glVertex3f(self.pos[0],top[1],self.pos[2])
                glVertex3f(*self.pos); glVertex3f(self.pos[0],self.pos[1],top[2])

##                if self.children == None:
##                    glColor3f(0,0.5,0.5)
##                    for direction in range(6):
##                        neighbor_record = self.neighbors[direction]
##                        if type(neighbor_record) == type([]):
##                            for i in range(4):
##                                neighbor = neighbor_record[i].other(self)
##                                glVertex3f(*vec_add( self.    pos, sc_vec(0.5,self.    eps) ))
##                                glVertex3f(*vec_add( neighbor.pos, sc_vec(0.5,neighbor.eps) ))
##                        elif neighbor_record != None:
##                            neighbor = neighbor_record.other(self)
##                            glVertex3f(*vec_add( self.    pos, sc_vec(0.5,self.    eps) ))
##                            glVertex3f(*vec_add( neighbor.pos, sc_vec(0.5,neighbor.eps) ))
            
            return True
        if self.children != None:
            found = False
            for child in self.children:
                found |= child.draw_grid(if_level)
            return found
        return False
