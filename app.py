import pygame
import numpy as np
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.GLU import *
from config_loader import ConfigLoader
from shader_manager import ShaderManager

class BumpMappingApp:
    def __init__(self):
        
        self.settings = ConfigLoader.load_settings()
        self.rotate_x = 0
        self.rotate_y = 0
        self.light_pos = self.settings["light"]["initial_position"]
        
        self.init_pygame()
        self.init_opengl()
        self.load_resources()
        self.init_shaders()
        self.init_buffers()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.settings["window"]["width"], self.settings["window"]["height"]),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(self.settings["window"]["title"])

    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)  # Dodaj to!
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.settings["opengl"]["clear_color"])
        glMatrixMode(GL_PROJECTION)
        gluPerspective(
            self.settings["opengl"]["projection"]["fov"],
            (self.settings["window"]["width"]/self.settings["window"]["height"]),
            self.settings["opengl"]["projection"]["near"],
            self.settings["opengl"]["projection"]["far"]
        )
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(*self.settings["camera"]["initial_translation"])

    def load_resources(self):
        geometry_data = ConfigLoader.load_geometry()
        self.vertices = np.array(geometry_data["vertices"], dtype=np.float32)
        self.normal_map = ConfigLoader.load_texture("textures/normal_map.png")

    def init_shaders(self):
        vertex_source = ConfigLoader.load_shader(GL_VERTEX_SHADER, "config/shaders/vertex.glsl")
        fragment_source = ConfigLoader.load_shader(GL_FRAGMENT_SHADER, "config/shaders/fragment.glsl")
        self.program = ShaderManager.create_program(vertex_source, fragment_source)
        glUseProgram(self.program)

    def init_buffers(self):
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Pobierz lokalizacje atrybutów
        position_loc = glGetAttribLocation(self.program, "position")
        normal_loc = glGetAttribLocation(self.program, "normal")
        tangent_loc = glGetAttribLocation(self.program, "tangent")
        bitangent_loc = glGetAttribLocation(self.program, "bitangent")
        texcoord_loc = glGetAttribLocation(self.program, "texcoord")

        # Konfiguracja atrybutów (14 elementów na wierzchołek)
        stride = 14 * 4  # 14 * sizeof(float)
        offsets = [0, 3, 6, 9, 12]  # Offsety w skali floatów
        
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offsets[0]*4))
        
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offsets[1]*4))
        
        glEnableVertexAttribArray(tangent_loc)
        glVertexAttribPointer(tangent_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offsets[2]*4))
        
        glEnableVertexAttribArray(bitangent_loc)
        glVertexAttribPointer(bitangent_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offsets[3]*4))
        
        glEnableVertexAttribArray(texcoord_loc)
        glVertexAttribPointer(texcoord_loc, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offsets[4]*4))

    def render_frame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Aktualizuj macierz widoku
        glLoadIdentity()
        glTranslatef(0, 0, -5)
        glRotatef(self.rotate_y, 0, 1, 0)
        glRotatef(self.rotate_x, 1, 0, 0)
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        
        # Pobierz uniformy
        modelview_loc = glGetUniformLocation(self.program, "modelview")
        projection = glGetFloatv(GL_PROJECTION_MATRIX)
        
        # Przekaż parametry do shaderów
        glUniformMatrix4fv(modelview_loc, 1, GL_FALSE, modelview)
        glUniformMatrix4fv(glGetUniformLocation(self.program, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(self.program, "light_pos"), *self.light_pos)
        
        # Aktywuj teksturę
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.normal_map)
        glUniform1i(glGetUniformLocation(self.program, "normal_map"), 0)
        
        # Rysuj sześcian
        glDrawArrays(GL_QUADS, 0, 24)  # 24 wierzchołki (6 ścian * 4 wierzchołki)
        def run(self):
            while True:
                self.handle_events()
                self.render_frame()
                pygame.display.flip()
                pygame.time.wait(10)

    def run(self):
        while True:
            self.handle_events()
            self.render_frame()
            pygame.display.flip()
            pygame.time.wait(10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.rotate_y -= 5
                elif event.key == pygame.K_RIGHT:
                    self.rotate_y += 5
                elif event.key == pygame.K_UP:
                    self.rotate_x -= 5
                elif event.key == pygame.K_DOWN:
                    self.rotate_x += 5
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                self.light_pos[0] = (x/self.settings["window"]["width"])*10 -5
                self.light_pos[1] = ((self.settings["window"]["height"]-y)/self.settings["window"]["height"])*10 -5
