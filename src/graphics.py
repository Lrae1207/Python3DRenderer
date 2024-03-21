import pygame
import math
import time
import os
import platform
from PIL import Image
import ctypes
import fundamentals as base
    
class Face:
    color = base.RGBColor(0, 0, 0)
    indices = (0,0,0)
    shading_color = (0, 0, 0)
    texture = False

    def __init__(self, indices, color, texture=False):
        self.indices = indices
        self.color = color
        self.texture = texture

def rel_dir (str):
    if (str[0] == "/") | (str[0] == "."):
        return str
    else:
        return os.path.dirname(__file__) + "/" + str

def rotate_point (x, y, r):
  return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

def shoelace (pts):
    if len(pts) == 0:
        return 0
    area = 0
    point = 0
    for point in range(len(pts) - 1):
        area += pts[point][0] * pts[point + 1][1] - pts[point][1] * pts[point + 1][0]
    area += pts[len(pts) - 1][0] * pts[0][1] - pts[len(pts) - 1][1] * pts[0][0]
    return area

def normal (points):
    ab = base.Vector3(points[1].x - points[0].x, points[1].y - points[0].y, points[1].z - points[0].z)
    ac = base.Vector3(points[2].x - points[0].x, points[2].y - points[0].y, points[2].z - points[0].z)
    return base.CameraVector3(ab.x * ac.x, ab.y * ac.y, ab.z * ac.z)
                
class Graphics:
    graphics_accel = None

    rendered_faces = 0
    rendered_objects = 0
    textures_path = ""
    screen = base.Screen()
    objects = []
    
    bgcolor = (255, 255, 255)
    specstog = False
    specsHeld = False
    crosshairspread = 0
    speed = 0.025
    ambient_light = (0, 0, 0)

    debug_text_buffer = []

    clock = None
    cam = base.Camera()
    window = None

    frame = 0
    frame_cap = 60

    def __init__(self,window):
        self.window = window
        #if platform.system() == "Linux": # SO only works on linux
            #graphics_accel = ctypes.CDLL("./accel-linux/graphics.so")
    
    def accel_shoelace(self,pts):
        #if platform.system() == "Linux":
            #x,y = zip(*pts)
            #return self.graphics_accel.shoelace(x,y) # No clue if this actually works 
        return shoelace(pts)

    def apply_changes (self, obj, vertex):
        x, y, z = vertex.x, vertex.y, vertex.z
        t = obj.transform

        # Scaling
        x *= t.scale.x
        y *= t.scale.y
        z *= t.scale.z

        # Rotation
        y, z = rotate_point(y - t.origin.y, z - t.origin.z, math.radians(t.orientation.x))
        x, z = rotate_point(x - t.origin.x, z - t.origin.z, math.radians(t.orientation.y))
        x, y = rotate_point(x - t.origin.x, y - t.origin.y, math.radians(t.orientation.z))
        
        # Offset
        x += t.position.x
        y += t.position.y
        z += t.position.z

        return base.Vector3(x, y, z)
    
    def perspective (self, position, rotation, vertex):
        x, y, z = vertex.x - position.x, vertex.y - position.y, vertex.z - position.z
        pitch, yaw, roll = math.radians(rotation.x), math.radians(rotation.y), math.radians(rotation.z)
        x, z = rotate_point(x, z, yaw)
        y, z = rotate_point(y, z, pitch)
        x, y = rotate_point(x, y, roll)
        return base.Vector3(x, y, z)
    
    def draw_texture (self, facepts, texture, scrn, shading=(1, 1, 1)):
        facepts.sort(key=lambda x: x[1])
        top = [facepts[0], facepts[1]]
        bottom = [facepts[2], facepts[3]]
        top.sort(key=lambda x: x[0])
        bottom.sort(key=lambda x: x[0])
        facepts = [top[0], top[1], bottom[0], bottom[1]]
        image = Image.open(texture, "r")
        texture = list(image.getdata())
        for y in range(image.height): # *Interpolation Magic Below*
            for x in range(image.width):
                topcoord1 = (facepts[0][0] + (x/image.width*(facepts[1][0] - facepts[0][0])), facepts[0][1] + (x/image.width*(facepts[1][1] - facepts[0][1])))
                topcoord2 = (facepts[0][0] + ((x + 1)/image.width*(facepts[1][0] - facepts[0][0])), facepts[0][1] + ((x + 1)/image.width*(facepts[1][1] - facepts[0][1])))
                bottomcoord1 = (facepts[2][0] + (x/image.width*(facepts[3][0] - facepts[2][0])), facepts[2][1] + (x/image.width*(facepts[3][1] - facepts[2][1])))
                bottomcoord2 = (facepts[2][0] + ((x + 1)/image.width*(facepts[3][0] - facepts[2][0])), facepts[2][1] + ((x + 1)/image.width*(facepts[3][1] - facepts[2][1])))
                tl = (topcoord1[0] + (y/image.height*(bottomcoord1[0] - topcoord1[0])), topcoord1[1] + (y/image.height*(bottomcoord1[1] - topcoord1[1])))
                tr = (topcoord2[0] + (y/image.height*(bottomcoord2[0] - topcoord2[0])), topcoord2[1] + (y/image.height*(bottomcoord2[1] - topcoord2[1])))
                bl = (topcoord1[0] + ((y + 1)/image.height*(bottomcoord1[0] - topcoord1[0])), topcoord1[1] + ((y + 1)/image.height*(bottomcoord1[1] - topcoord1[1])))
                br = (topcoord2[0] + ((y + 1)/image.height*(bottomcoord2[0] - topcoord2[0])), topcoord2[1] + ((y + 1)/image.height*(bottomcoord2[1] - topcoord2[1])))
                pts = [tl, tr, br, bl]
                pixcolor = (texture[y * image.width + x][0], texture[y * image.width + x][1], texture[y * image.width + x][2])
                r = pixcolor[0]*shading[0]
                g = pixcolor[1]*shading[1]
                b = pixcolor[2]*shading[2]
                if r > 255: r = 255
                if g > 255: g = 255
                if b > 255: b = 255
                pygame.draw.polygon(scrn, (r, g, b), pts, 0)

    def bake_lighting (self):
        for obj in self.objects:
            for face in obj.faces:
                    face.shading_color = (self.ambient_light.r/255, self.ambient_light.g/255, self.ambient_light.b/255)
        for light in self.objects:
            if light.type == "light":
                list = self.objects
                for obj in list:
                    if obj.visible & (obj.type != "light"):
                        vertices = []
                        for vertex in obj.vertices:
                            x, y, z = vertex.x, vertex.y, vertex.z
                            if not obj.locked:

                                vert = self.apply_changes(obj, vertex)
                                x, y, z = vert.x, vert.y, vert.z

                            vertices.append(self.perspective(light.transform.position, light.mesh.light_direction, base.Vector3(x, y, z)))

                        for face in obj.faces:
                            offscreen = True
                            show = True
                            points = []
                            planepts = []
                            for index in face.indices:
                                x, y, z = vertices[index].x, vertices[index].y, vertices[index].z + 0.00000001
                                if z < 0:
                                    show = False
                                points.append(((x * light.mesh.light_spread/z), (-y * light.mesh.light_spread/z)))
                                if (x * light.mesh.light_spread/z <= self.window.get_width()) & (y * light.mesh.light_spread/z <= self.window.get_height()):
                                    offscreen = False
                                planepts.append(base.Vector3(x, y, z))

                            area = self.accel_shoelace(points)
                            if (area > 0) & ((not offscreen)):
                                dist_from_center = math.sqrt(points[0][0] * points[0][0] + points[0][1] * points[0][1])
                                distance = math.sqrt((light.transform.position.x - planepts[0].x)*(light.transform.position.x - planepts[0].x) + (light.transform.position.y - planepts[0].y)*(light.transform.position.y - planepts[0].y) + (light.transform.position.z - planepts[0].z)*(light.transform.position.z - planepts[0].z))
                                if dist_from_center == 0:
                                    brightness = area / distance / 999
                                else:
                                    brightness = area / distance / 10 / dist_from_center
                                r = face.shading_color[0] + (light.mesh.light_color.r/255) * brightness
                                g = face.shading_color[1] + (light.mesh.light_color.g/255) * brightness
                                b = face.shading_color[2] + (light.mesh.light_color.b/255) * brightness
                                face.shading_color = (r, g, b)

    # Render 3D elements
    def render(self):
        t0 = time.perf_counter_ns()
        self.bake_lighting()
        objlist = self.objects
        self.window.fill(self.bgcolor)
        zbuffer = []

        self.rendered_objects = 0
        for obj in objlist:
            cam = self.cam
            if obj.visible:
                self.rendered_objects += 1
                locked = obj.locked
                vertices = []
                for vertex in obj.vertices:
                    x, y, z = vertex.x, vertex.y, vertex.z
                    if not locked:

                        vert = self.apply_changes(obj, vertex)
                        x, y, z = vert.x, vert.y, vert.z

                        # Lock Vertices For Static Objects
                        if obj.static:
                            obj.vertices[obj.vertices.index(vertex)] = base.Vector3(x, y, z)
                            obj.locked = True

                    vertices.append(self.perspective(cam.position, cam.rotation, base.Vector3(x, y, z)))

                self.rendered_faces = 0
                for face in obj.faces:
                    show = True
                    points = []
                    depthval = 0
                    planepts = []
                    for index in face.indices:
                        x, y, z = vertices[index].x, vertices[index].y, vertices[index].z + 0.000000001
                        
                        if z < 0: # Do not render clipping or out-of-scope objects
                            show = False
                        
                        points.append(((x * cam.focal_length/z+self.window.get_width()/2) * (self.window.get_width() / self.screen.fullwidth), (-y * cam.focal_length/z+self.window.get_height()/2)*(self.window.get_height() / self.screen.full)))
                        planepts.append(base.Vector3(x, y, z))
                        
                        depthval += z # add z to the sum of the z values

                    if len(obj.textures) > 0:
                        texture = self.textures_path + obj.textures[face.texture]
                    else:
                        texture = False

                    depthval /= len(face.indices) # depthval now stores the z of the object's center
                    if show:
                        self.rendered_faces += 1
                    if show & ((shoelace(points) > 0) | obj.mesh.transparent):
                        zbuffer.append([face.color, points, obj.mesh.wire_thickness, depthval, face.shading_color, obj.type, texture, obj.mesh.transparent])

        zbuffer.sort(key=lambda x: x[3], reverse=True) # Sort z buffer by the z distance from the camera

        for f in zbuffer: # Draw each face
            shading = f[4]
            shading = list(shading)
            if shading[0] > 1.3: shading[0] = 1.3
            if shading[1] > 1.3: shading[1] = 1.3
            if shading[2] > 1.3: shading[2] = 1.3
            shading = tuple(shading)
            if (not f[7]) | (f[6] == False):
                if f[5] == "light":
                    r, g, b = (f[0].r, f[0].g, f[0].b)
                else:
                    r = int(f[0].r*shading[0])
                    g = int(f[0].g*shading[1])
                    b = int(f[0].b*shading[2])
                    if r > 255: r = 255
                    if g > 255: g = 255
                    if b > 255: b = 255
                try:
                    pygame.draw.polygon(self.window, (r, g, b), f[1], f[2])
                except:
                    pygame.draw.polygon(self.window, f[0].to_tuple(), f[1], f[2])
            if f[6] != False:
                if len(f[1]) >= 4:
                    if f[5] == "light":
                        self.draw_texture(f[1], f[6], self.window)
                    else:
                        self.draw_texture(f[1], f[6], self.window, f[4])
        index = 0
        for text in self.debug_text_buffer:
            self.window.blit(text,(5,index * 20))
            index += 1
        
        return time.perf_counter_ns() - t0
    
    def reset_debug_buffer(self):
        self.debug_text_buffer = []

    # Print string to the debug buffer
    def debug_to_screen(self,string,font):
        text = font.render(string,False,(0,0,0),(255,255,255))
        self.debug_text_buffer.append(text)

    # Render 2D UI elements
    def gui(self):
        t0 = time.perf_counter_ns()
        crosshairspread = self.speed * 100
        
        #crosshairs
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2-10-crosshairspread, self.window.get_height()/2), (self.window.get_width()/2-crosshairspread, self.window.get_height()/2)) #horizontal left
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2+crosshairspread, self.window.get_height()/2), (self.window.get_width()/2+10+crosshairspread, self.window.get_height()/2)) #horizontal right
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2-10-crosshairspread), (self.window.get_width()/2, self.window.get_height()/2-crosshairspread)) #vertical top
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2+crosshairspread), (self.window.get_width()/2, self.window.get_height()/2+10+crosshairspread)) #vertical vertical bottom
        
        if self.specstog: # Show spects
            pass
        return time.perf_counter_ns()-t0
