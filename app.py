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
        # Scale the vertices by 2.0 to make the cube bigger
        self.vertices = np.array(geometry_data["vertices"], dtype=np.float32) * 1.2
        self.uvs = np.array(geometry_data["uvs"], dtype=np.float32)
        self.normals = np.array(geometry_data["normals"], dtype=np.float32)
        self.tangents = np.array(geometry_data["tangents"], dtype=np.float32)
        self.bitangents = np.array(geometry_data["bitangents"], dtype=np.float32)
        self.indices = np.array(geometry_data["indices"], dtype=np.uint32) if geometry_data["indices"] else None
        self.normal_map = ConfigLoader.load_texture("textures/brick.png")

        # Check for matching lengths
        n = len(self.vertices)
        if not all(len(arr) == n for arr in [self.uvs, self.normals, self.tangents, self.bitangents]):
            raise ValueError(f"Geometry attribute array lengths do not match: "
                             f"vertices={len(self.vertices)}, uvs={len(self.uvs)}, normals={len(self.normals)}, "
                             f"tangents={len(self.tangents)}, bitangents={len(self.bitangents)}")

    def init_shaders(self):
        vertex_source = ConfigLoader.load_shader(GL_VERTEX_SHADER, "config/shaders/vertex.glsl")
        fragment_source = ConfigLoader.load_shader(GL_FRAGMENT_SHADER, "config/shaders/fragment.glsl")
        self.program = ShaderManager.create_program(vertex_source, fragment_source)
        glUseProgram(self.program)

    def init_buffers(self):
        # Interleave attributes: position, normal, tangent, bitangent, uv
        vertex_count = len(self.vertices)
        interleaved = []
        for i in range(vertex_count):
            interleaved.extend(self.vertices[i])
            interleaved.extend(self.normals[i])
            interleaved.extend(self.tangents[i])
            interleaved.extend(self.bitangents[i])
            interleaved.extend(self.uvs[i])
        interleaved = np.array(interleaved, dtype=np.float32)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, interleaved.nbytes, interleaved, GL_STATIC_DRAW)

        if self.indices is not None and len(self.indices) > 0:
            self.ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        else:
            self.ebo = None

        stride = (3 + 3 + 3 + 3 + 2) * 4  # 14 floats per vertex

        # Attribute locations
        position_loc = glGetAttribLocation(self.program, "position")
        normal_loc = glGetAttribLocation(self.program, "normal")
        tangent_loc = glGetAttribLocation(self.program, "tangent")
        bitangent_loc = glGetAttribLocation(self.program, "bitangent")
        texcoord_loc = glGetAttribLocation(self.program, "texcoord")

        offsets = [0, 3, 6, 9, 12]
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
        glTranslatef(0, 0, -3)  # Changed from -5 to -3
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
        if self.ebo is not None:
            glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(GL_QUADS, 0, len(self.vertices))

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
