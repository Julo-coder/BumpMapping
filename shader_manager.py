from OpenGL.GL import *

class ShaderManager:
    @staticmethod
    def compile_shader(source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            error = glGetShaderInfoLog(shader)
            raise RuntimeError(f"Shader error: {error}")
        return shader

    @staticmethod
    def create_program(vertex_source, fragment_source):
        program = glCreateProgram()
        vertex_shader = ShaderManager.compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = ShaderManager.compile_shader(fragment_source, GL_FRAGMENT_SHADER)
        
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)
        
        if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
            error = glGetProgramInfoLog(program)
            raise RuntimeError(f"Program error: {error}")
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        return program