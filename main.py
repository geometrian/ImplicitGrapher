from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os, traceback
if sys.platform in ["win32","win64"]: os.environ["SDL_VIDEO_CENTERED"]="1"
from math import *
from grid import Grid
from helpers import *
import gl_shader
pygame.display.init()
pygame.font.init()

screen_size = [1024,768]
multisample = 16
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("[Program] - [Author] - [Version] - [Date]")
if multisample:
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS,1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES,multisample)
pygame.display.set_mode(screen_size,OPENGL|DOUBLEBUF)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

glEnable(GL_TEXTURE_2D)
glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE)
glTexEnvi(GL_POINT_SPRITE,GL_COORD_REPLACE,GL_TRUE)

glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)

prog_pts = gl_shader.Program([
    gl_shader.ShaderVertex(
"""uniform float size;
void main() {
    vec4 v_eye = gl_ModelViewMatrix * gl_Vertex;
    float dist = length(v_eye.xyz);
    gl_PointSize = size / dist;
    gl_Position = gl_ProjectionMatrix * v_eye;
}"""
    ),
    gl_shader.ShaderFragment(
"""uniform vec3 color;
void main() {
    gl_FragData[0] = vec4(color,1);
}"""
    )
])


def err_n(pos):
    x,y,z=pos; M=1.0; a=x; Q=z; r=y
    tmp = M*r - Q*Q
    if tmp >= 0.0: return M*r*r*r - 6.0*M*M*r*r - 3.0*M*a*a*r + 9.0*M*Q*Q*r - 8.0*a*(tmp**(3.0/2.0)) + 4.0*Q*Q*(a*a-Q*Q)
    else:          return None
def err_p(pos):
    x,y,z=pos; M=1.0; a=x; Q=z; r=y
    tmp = M*r - Q*Q
    if tmp >= 0.0: return M*r*r*r - 6.0*M*M*r*r - 3.0*M*a*a*r + 9.0*M*Q*Q*r + 8.0*a*(tmp**(3.0/2.0)) + 4.0*Q*Q*(a*a-Q*Q)
    else:          return None

print("Generating data . . .")
if 0:
    err_func=err_n; sc=[
        1.0,
        9.5,
        1.5
    ]
else:
    err_func=err_p; sc=[
        2.0,
        6.3,
        1.2
    ]
res = 16
grid = Grid( err_func, (0.0,0.0,0.0),(sc[0],sc[1],sc[2]) )
points = grid.calc(5,7)



print("Done!")

print("3D Implicit Grapher")
print("  Left Click + Drag -> Move camera")
print("  Right Click + Drag -> Rotate camera")
print("  G -> Toggle grid")
print("  P -> Toggle extra points")



camera_rot = [-120.0,20.0]
camera_radius = 2.5
camera_center = [ 0.5, 0.5, 0.5 ]
def get_camera_pos():
    return (
        camera_center[0] + camera_radius*cos(radians(camera_rot[0]))*cos(radians(camera_rot[1])),
        camera_center[1] + camera_radius                            *sin(radians(camera_rot[1])),
        camera_center[2] + camera_radius*sin(radians(camera_rot[0]))*cos(radians(camera_rot[1]))
    )
draw_grid = False
draw_extra_pts = False
def get_input():
    global camera_rot, camera_radius, camera_center
    global draw_grid, draw_extra_pts
    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = pygame.mouse.get_pos()
    mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if   event.type == QUIT: return False
        elif event.type == KEYDOWN:
            if   event.key == K_ESCAPE: return False
            elif event.key == K_g:
                draw_grid = not draw_grid
            elif event.key == K_p:
                draw_extra_pts = not draw_extra_pts
        elif event.type == MOUSEBUTTONDOWN:
            if   event.button == 4: camera_radius *= 0.9
            elif event.button == 5: camera_radius /= 0.9
    if mouse_buttons[0]:
        camera_pos = get_camera_pos()
        V = vec_normalize(vec_sub(camera_pos,camera_center))
        X=vec_cross(V,[0,1,0]); l=vec_length(X)
        if l > 0.0:
            X = sc_vec(1.0/l,X)
            Y = vec_cross(X,V)
            rate = 0.002 * camera_radius
            camera_center = vec_add( vec_add(camera_center,sc_vec(rate*mouse_rel[0],X)), sc_vec(rate*mouse_rel[1],Y) )
    if mouse_buttons[2]:
        camera_rot[0] += mouse_rel[0]
        camera_rot[1] += mouse_rel[1]
        camera_rot[1] = clamp(camera_rot[1],-89.0,89.0)
    return True
def draw():
    #Clear
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    #Setup projection and view
    glViewport(0,0,screen_size[0],screen_size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, float(screen_size[0])/float(screen_size[1]), 0.001,100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    camera_pos = get_camera_pos()
    gluLookAt(
        camera_pos[0],camera_pos[1],camera_pos[2],
        camera_center[0],camera_center[1],camera_center[2],
        0,1,0
    )

    #Draw points and grid
    glPushMatrix()
    glScalef( 1.0/sc[0], 1.0/sc[1], 1.0/sc[2] )
    
    glEnable(GL_PROGRAM_POINT_SIZE)
    gl_shader.Program.use(prog_pts)
    if draw_extra_pts:
        prog_pts.pass_float("size",3.0); prog_pts.pass_vec3("color",[1.0,1.0,0.0]); glCallList(grid.dl_pts_err) #invalid
        prog_pts.pass_float("size",3.0); prog_pts.pass_vec3("color",[1.0,0.0,0.0]); glCallList(grid.dl_pts_neg) #negative err
        prog_pts.pass_float("size",3.0); prog_pts.pass_vec3("color",[0.0,1.0,0.0]); glCallList(grid.dl_pts_pos) #positive err
    prog_pts.pass_float("size",9.0); prog_pts.pass_vec3("color",[1.0,0.0,1.0]); glCallList(grid.dl_pts_zero) #solved 0 err
    gl_shader.Program.use(None)
    glDisable(GL_PROGRAM_POINT_SIZE)

    if draw_grid:
        level = 0
        colors = [
            (1.0,0.5,0.0),
            #(1.0,1.0,0.0),
            (0.5,1.0,0.0),
            #(0.0,1.0,0.5),
            (0.0,1.0,1.0),
            #(0.0,0.5,1.0)
        ]
        glLineWidth(0.1)
        for dl in grid.dls_grids:
            glColor3f(*colors[level%len(colors)])
            glCallList(dl)
            level += 1
    
    glPopMatrix()

    #Draw bounding box and axes
    glLineWidth(2.0)
    glColor3f(*[0.5]*3)
    glBegin(GL_LINES)
    points = []
    for k in [0,1]:
        for j in [0,1]:
            for i in [0,1]: points.append((i,j,k))
    for p0 in points:
        for p1 in points:
            diffs = (p0[0]^p1[0]) + (p0[1]^p1[1]) + (p0[2]^p1[2])
            if diffs == 1:
                glVertex3f(*p0); glVertex3f(*p1)
    glEnd()
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(1,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,1,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,1)
    glEnd()

    glColor3f(1,1,1)

    #Flip
    pygame.display.flip()
def main():
    global prog_pts
    clock = pygame.time.Clock()
    while True:
        if not get_input(): break
        draw()
        clock.tick(60)
    del prog_pts
    pygame.quit()
if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()
