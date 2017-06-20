from OpenGL.GL import *
from OpenGL.GLU import *

import grid_cell

from helpers import *



class Grid(object):
    def __init__(self, err_func, pos,dim):        
        self.pos = tuple(pos) #lower corner
        self.dim = tuple(dim) #physical size

        self.root = grid_cell.Cell(err_func, 0, pos,dim)

    def calc(self, min_level,max_level):
        self.root.subdiv_to_at_least(min_level)
        self.root.subdiv_refine(max_level)
        self.root.calc()

##        self.root.children[0b000].subdiv()
##        self.root.children[0b000].children[0b111].subdiv()

        self.dl_pts_err=glGenLists(1); self.dl_pts_neg=glGenLists(1); self.dl_pts_zero=glGenLists(1); self.dl_pts_pos=glGenLists(1)
        glNewList(self.dl_pts_err, GL_COMPILE); glBegin(GL_POINTS); self.root.draw_points(0); glEnd(); glEndList()
        glNewList(self.dl_pts_neg, GL_COMPILE); glBegin(GL_POINTS); self.root.draw_points(1); glEnd(); glEndList()
        glNewList(self.dl_pts_zero,GL_COMPILE); glBegin(GL_POINTS); self.root.draw_points(2); glEnd(); glEndList()
        glNewList(self.dl_pts_pos, GL_COMPILE); glBegin(GL_POINTS); self.root.draw_points(3); glEnd(); glEndList()

        self.dls_grids = []
        level = 0
        while True:
            dl = glGenLists(1)
            glNewList(dl, GL_COMPILE)
            
            glBegin(GL_LINES)
            exists = self.root.draw_grid(level)
            glEnd()
            
            glEndList()

            if not exists: break
            else:
                self.dls_grids.append(dl)
                level += 1
