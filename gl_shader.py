from OpenGL.GL import *
from OpenGL.GL.ARB.shader_objects import *
from OpenGL.GL.ARB.vertex_shader import *
from OpenGL.GL.ARB.fragment_shader import *


try: input=raw_input
except: pass


def _get_processed_log(log):
    result = ""
    for line in log.split(b"\n"):
        line = line.decode()
        if not line: continue
        result += line + "\n"
    return result


class ShaderBase(object):
    def __init__(self,source,type):
        self.source = source
        
        self.shader = glCreateShaderObjectARB(type)
        
        glShaderSourceARB(self.shader,[source]) #Crucial for AMD compatibility to have []
        glCompileShaderARB(self.shader)

        status = glGetShaderiv(self.shader,GL_COMPILE_STATUS)
        if status != GL_TRUE:
            print("#### Compile Failed ####")
            print(self.get_log())
            input("ENTER to continue")
    def __del__(self):
        glDeleteObjectARB(self.shader)

    def get_log(self):
        return _get_processed_log(glGetShaderInfoLog(self.shader))

class ShaderVertex(ShaderBase):
    def __init__(self,source):
        ShaderBase.__init__(self,source,GL_VERTEX_SHADER_ARB)

class ShaderFragment(ShaderBase):
    def __init__(self,source):
        ShaderBase.__init__(self,source,GL_FRAGMENT_SHADER_ARB)


class Program(object):
    def __init__(self,shaders):
        self.shaders = shaders
        
        self.program = glCreateProgramObjectARB()        
        for shader in self.shaders:
            glAttachObjectARB(self.program,shader.shader)
        glLinkProgramARB(self.program)

        status = glGetProgramiv(self.program,GL_LINK_STATUS)
        if status != GL_TRUE:
            print("#### Link Failed ####")
            print(self.get_log())
            input("ENTER to continue")
        glValidateProgramARB(self.program)
        status = glGetProgramiv(self.program,GL_VALIDATE_STATUS)
        if status != GL_TRUE:
            print("#### Validation Failed ####")
            input("ENTER to continue")

        self.symbol_locations = {}
    def __del__(self):
        glDeleteObjectARB(self.program)

    def get_location(self,symbol):
        if not symbol in self.symbol_locations.keys():
            self.symbol_locations[symbol] = glGetUniformLocation(self.program,symbol.encode())
            if self.symbol_locations[symbol] == -1:
                print("Cannot get the location of symbol \""+symbol+"\"!")
        return self.symbol_locations[symbol]
    def pass_int(self,symbol,i):
        glUniform1i(self.get_location(symbol),i)
    def pass_float(self,symbol,f):
        glUniform1f(self.get_location(symbol),f)
    def pass_bool(self,symbol,b):
        glUniform1i(self.get_location(symbol),b)
    def pass_vec2(self,symbol,v):
        glUniform2f(self.get_location(symbol),v[0],v[1])
    def pass_vec3(self,symbol,v):
        glUniform3f(self.get_location(symbol),v[0],v[1],v[2])
    def pass_vec4(self,symbol,v):
        glUniform4f(self.get_location(symbol),v[0],v[1],v[2],v[3])
    def pass_texture(self,texture,number):
        glActiveTexture(GL_TEXTURE0+number-1)
        active_texture = glGetIntegerv(GL_ACTIVE_TEXTURE) - GL_TEXTURE0
        if texture == None:
            glBindTexture(GL_TEXTURE_2D,0)
        else:
            texture.bind()
            glUniform1i(self.get_location("tex2D_"+str(number)),active_texture)
        glActiveTexture(GL_TEXTURE0)

    def save(self, filename):
        file = open(filename,"w")
        data = ""
        for shader in self.shaders:
            data += shader.source
            data += "\n"
        file.write(data)
        file.close()

    def get_log(self):
        return _get_processed_log(glGetProgramInfoLog(self.program))

    @staticmethod
    def use(program=None):
        if program == None:
            glUseProgramObjectARB(0)
        else:
            glUseProgramObjectARB(program.program)
        
