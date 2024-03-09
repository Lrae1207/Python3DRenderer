# File for shared classes between engine and renderer
import math
import os

# Function definitions
def rotate2D(x,y,r):
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

def clamp(min,max,x):
    if x < min:
        return min
    if x > max:
        return max
    return x

# File reading
def rel_dir (str):
    if (str[0] == "/") | (str[0] == "."):
        return str
    else:
        return os.path.dirname(__file__) + "/" + str

# Class definitions
    
# Fundemental classes

# Triple tuple representing 3d coordinates, 3d rotation, 3d movement, etc.
class Vector3:
    x, y, z = 0, 0, 0

    def __init__(self, x, y=0, z=0):
        if (type(x) is int) | (type(x) is float):
            self.x, self.y, self.z = x, y, z
        elif type(x) is tuple:
            self.x, self.y, self.z = x[0], x[1], x[2]

    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    # Returns (x1-x2,y1-y2,z1-z2)
    def subtract_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x-v3.x,self.y-v3.y,self.z-v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1+x2,y1+y2,z1+z2)
    def add_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x+v3.x,self.y+v3.y,self.z+v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1*x2,y1*y2,z1*z2)
    def multiply_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x*v3.x,self.y*v3.y,self.z*v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1/x2,y1/y2,z1/z2)
    def divide_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x/v3.x,self.y/v3.y,self.z/v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1-n,y1-n,z1-n)
    def subtract_by_num(self,num,set_this_vector):
        v = Vector3(self.x-num,self.y-num,self.z-num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1+n,y1+n,z1+n)
    def add_by_num(self,num,set_this_vector):
        v = Vector3(self.x+num,self.y+num,self.z+num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1*n,y1*n,z1*n)
    def multiply_by_num(self,num,set_this_vector):
        v = Vector3(self.x*num,self.y*num,self.z*num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1/n,y1/n,z1/n)
    def divide_by_num(self,num,set_this_vector):
        v = Vector3(self.x/num,self.y/num,self.z/num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    def rotate_by_euler(self,rotation):
        self.y, self.z = rotate2D(self.y, self.z, rotation.x)
        self.x, self.z = rotate2D(self.x, self.z, rotation.y)
        self.x, self.y = rotate2D(self.x, self.y, rotation.z)
        
# Double tuple representing 2d coordinates, 2d rotation, 2d movement, etc.
class Vector2:
    x, y = 0, 0

    def __init__(self, x, y=0):
        if (type(x) is int) | (type(x) is float):
            self.x, self.y = x, y
        elif type(x) is tuple:
            self.x, self.y = x[0], x[1]

    def to_tuple(self):
        return (self.x, self.y)

class Screen:
    full = 0
    fullwidth = 0

class RGBColor:
    r, g, b = 0, 0, 0

    def __init__(self, r, g=0, b=0):
        if type(r) is int:
            self.r, self.g, self.b = r, g, b
        elif type(r) is tuple:
            self.r, self.g, self.b = r[0], r[1], r[2]

    def to_tuple(self):
        return(self.r, self.g, self.b)

class MeshColor:
    transparent = True

    light_color = RGBColor(0, 0, 0)
    light_direction = Vector3(0, 0, 0)
    light_spread = 0

    wire_thickness = 0
    wire_color = RGBColor(0,0,0)
    
# Represents the positional and physical components of an object that the engine needs to process
class Transform:
    points = [] # List of Vector3s that represent the object's points
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0)
    origin = Vector3(0,0,0)
    scale = Vector3(0, 0, 0)

    # Physics properties
    velocity = Vector3(0,0,0)

    drag_factor = 1
    air_drag_factor = 1

    collider = None

# Game Object
class Object:
    static = True
    locked = False

    id = ""
    type = ""

    visible = True

    vertices = [] # List of all points as Vector3 
    faces = [] # List of all faces as faces
    
    mesh = MeshColor()
    transform = Transform()

    on_update = None

    def __init__ (self, id, type, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces, light_color, light_direction, light_spread, textures):
        self.id = id
        self.type = type
        self.transform.position = position
        self.transform.rotation = orientation
        self.transform.origin = origin
        self.rotationscale = scale
        self.mesh.wire_thickness = wire_thickness
        self.visible = visible
        self.mesh.transparent = transparent
        self.static = static
        self.vertices = vertices
        self.faces = faces
        self.mesh.light_color = light_color
        self.mesh.light_direction = light_direction
        self.mesh.light_spread = light_spread
        self.textures = textures

    def set_color (self, color): # Set the entire object to a color
        for face in self.faces:
            face.color = color

# Represents camera controlled by the cam.velocity
class Camera:
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0) # x = rotation.y, y = rotation.x, z = roll
    velocity = Vector3(0,0,0)
    drag = 0.8
    air_drag = 0.8
    focal_length = 400