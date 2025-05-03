import json
import pygame
from OpenGL.GL import *

class ConfigLoader:
    @staticmethod
    def load_settings():
        with open('config/settings.json') as f:
            return json.load(f)
    
    @staticmethod
    def load_shader(shader_type, path):
        with open(path) as f:
            source = f.read()
        return source
    
    @staticmethod
    def load_geometry():
        with open('data/cube_geometry.json') as f:
            data = json.load(f)
        return data
    
    @staticmethod
    def load_texture(path):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        image = pygame.image.load(path)
        image_data = pygame.image.tostring(image, "RGBA", 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        return texture