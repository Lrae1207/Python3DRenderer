import math
import os
import pygame
from pygame.locals import *
import json
import time
import graphics
import fundamentals as base

# Function definitions
def rotate2D(x,y,r):
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

# File reading
def rel_dir (str):
    if (str[0] == "/") | (str[0] == "."):
        return str
    else:
        return os.path.dirname(__file__) + "/" + str

# Class definitions

# Collision Handling
class Collision:
    epicenter = base.Vector3(0,0,0)
    otherCollider = None

def sort_sweep_key(item):
    return item[0]

class CollisionManager:
    colliders = []

    def broad_sort_sweep(self,colliders): # Sort and sweep broad phase algorithm
        collision_pairs = []

        xpoints = []
        ypoints = []
        zpoints = []
        
        # Add each minimum and maximum extrusion on the XYZ axes to their respective arrays and then sort the array by their value along the axis
        for collider in colliders:
            point = (collider.minvertex[0],collider.id)
            xpoints.append(point)
            point = (collider.minvertex[1],collider.id)
            ypoints.append(point)
            point = (collider.minvertex[2],collider.id)
            zpoints.append(point)

            point = (collider.maxvertex[0],collider.id)
            xpoints.append(point)
            point = (collider.maxvertex[1],collider.id)
            ypoints.append(point)
            point = (collider.maxvertex[2],collider.id)
            zpoints.append(point)

            xpoints.sort(key=sort_sweep_key)
            ypoints.sort(key=sort_sweep_key)
            zpoints.sort(key=sort_sweep_key)
        
        relevant_x_ids = []
        relevant_y_ids = []
        relevant_z_ids = []

        for x in xpoints:
            if x[1] in relevant_x_ids: # If the id of the current point is the "end point" (has a higher value along the axis)
                relevant_x_ids.remove(x[1])
            else: # If the id of the current point is the "start point" (has a lower value along the axis)
                relevant_x_ids.append(x[1])

            for id in relevant_x_ids: # For every object whose end point has not been encountered yet
                if id > x[1]: # Put the higher id first so that removing duplicates is easier
                    collision_pairs.append((id,x[1]))
                else:
                    collision_pairs.append((x[1],id))

        for y in ypoints:
            if y[1] in relevant_y_ids: # If the id of the current point is the "end point" (has a higher value along the axis)
                relevant_y_ids.remove(y[1])
            else: # If the id of the current point is the "start point" (has a lower value along the axis)
                relevant_y_ids.append(y[1])

            for id in relevant_y_ids: # For every object whose end point has not been encountered yet
                if id > y[1]: # Put the higher id first so that removing duplicates is easier
                    collision_pairs.append((id,y[1]))
                else:
                    collision_pairs.append((y[1],id))

        for z in zpoints:
            if z[1] in relevant_z_ids: # If the id of the current point is the "end point" (has a higher value along the axis)
                relevant_z_ids.remove(z[1])
            else: # If the id of the current point is the "start point" (has a lower value along the axis)
                relevant_z_ids.append(z[1])

            for id in relevant_z_ids: # For every object whose end point has not been encountered yet
                if id > z[1]: # Put the higher id first so that removing duplicates is easier
                    collision_pairs.append((id,z[1]))
                else:
                    collision_pairs.append((z[1],id))

        return list(set(collision_pairs)) # Remove duplicates




    def calculateCollisions(self):
        # Broad phase
        possible_collisions = self.broad_sort_sweep(self.colliders)

class Engine:
    # Lists
    objects = []
    debug_buffer = []

    # Booleans
    can_jump = True
    specstog = False
    specsHeld = False
    paused = False
    pause_held = False
    active = True

    # Numbers
    crosshairspread = 0
    speed = 0.025

    # Objects
    screen = None
    cam = None
    graphics = None
    window = None
    collision_manager = CollisionManager()

    def __init__(self, graphics):
        self.graphics = graphics
        self.cam = graphics.cam
        self.window = graphics.window

        self.specstog = False
        self.specsHeld = False
        self.paused = False
        self.crosshairspread = 0
        self.speed = 0.025
        self.pause_held = False
        self.screen = graphics.screen

        pygame.init()
        pygame.font.init()

        self.analytics_font = pygame.font.SysFont('cousine', 20)

        self.screen.fullwidth, self.screen.full = self.window.get_width(), self.window.get_height() #finds fullscreen dimensions

        self.clock = pygame.time.Clock()

        pygame.display.set_caption('Python (Pygame) - 3D Renderer')
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        pygame.mouse.set_visible(False)

        self.cam.drag = 0.8 # Actual camera drag
        self.cam.air_drag = 0.85 # Actual camera aerial drag

        self.objects = self.load_objects(rel_dir("scene_path.json"))
        self.graphics.objects = self.objects # Shares the objects with the renderer

    # Loads the objects from JSON files
    def load_objects (self, path):
        objlist = []
        with open(path) as file:
            scene = json.load(file)
            g.bgcolor = tuple(scene["bg_color"])
            g.ambient_light = base.RGBColor(tuple(scene["ambient"]))
            folder_path = rel_dir(scene["folder_path"])
            g.textures_path = rel_dir(scene["textures_path"])
        file.close()
        for objpath in scene["object_file_paths"]:
            with open(folder_path + objpath) as file:
                obj = json.load(file)
                vertices = []
                for vertex in obj["vertices"]:
                    vertices.append(base.Vector3(tuple(vertex)))
                faces = []
                for face in obj["faces"]:
                    faces.append(graphics.Face((tuple(face[0])), base.RGBColor(tuple(face[1]))))
                    #id, type, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces, light_color, light_direction, is_source, light_spread
                objlist.append(base.Object(obj["name"], obj["type"], base.Vector3(tuple(obj["position"])), base.Vector3(tuple(obj["orientation"])), base.Vector3(tuple(obj["origin"])), base.Vector3(tuple(obj["scale"])), obj["wire_thickness"], obj["visible"], obj["transparent"], obj["static"], vertices, faces, base.RGBColor(tuple(obj["light"]["color"])), base.Vector3(tuple(obj["light"]["direction"])), obj["light"]["spread"], obj["textures"]))
            file.close()
        return objlist

    # Update the game
    def update(self):
        t0 = time.perf_counter_ns()

        # Handle collisions
        self.collision_manager.calculateCollisions()
        cam = self.cam

        # Lock mouse in the middle
        if not self.paused:
            pygame.mouse.set_pos(self.window.get_width()/2, self.window.get_height()/2) #mouse "lock"

        # Update camera
        if (cam.position.y > 0): # In air
            # Apply air drag
            cam.velocity.x *= cam.air_drag
            cam.velocity.y *= cam.air_drag
            cam.velocity.z *= cam.air_drag

            # Gravity
            cam.velocity.y -= 0.1
        else: # Touching the ground
            # Apply drag
            cam.velocity.x *= cam.drag
            cam.velocity.y *= cam.drag
            cam.velocity.z *= cam.drag

            self.can_jump = True

        cam.position.x += cam.velocity.x
        cam.position.y += cam.velocity.y
        cam.position.z += cam.velocity.z

        if cam.position.y < 0:
            cam.position.y = 0
        
        # Update each object
        for obj in self.objects:
            if not obj.on_update == None:
                obj.on_update()

            # !! Physics update !!
            acceleration = base.Vector3(0,0,0)

            obj.transform.velocity.add_by_vector(acceleration, True)
            obj.transform.position.add_by_vector(obj.transform.velocity, True)

            pass

        return time.perf_counter_ns() - t0

    def handle_control(self):
        t0 = time.perf_counter_ns()
        keys = pygame.key.get_pressed()
        cam = self.cam

        # rotation
        rel = pygame.mouse.get_rel()

        if not self.paused: # When unpaused
            # Mouse sense
            cam.rotation.y += rel[0]*0.15
            cam.rotation.x -= rel[1]*0.15
            cam.rotation.x = base.clamp(-90,90,cam.rotation.x)
            
            # Renaming
            speed = self.speed

            # Movement keys
            if keys[pygame.K_LSHIFT]: #sprinting
                if speed < 0.05: # Smoothen acceleration to sprint speed
                    self.speed += 0.01
                if cam.focal_length > 300:
                    cam.focal_length -= 10
            else:
                if speed > 0.02: # Smoothen decceleration to walk speed
                    self.speed -= 0.005
                if cam.focal_length < 400:
                    cam.focal_length += 10
            if keys[pygame.K_w]: # Forward
                cam.velocity.z += speed*math.cos(math.radians(cam.rotation.y))
                cam.velocity.x += speed*math.sin(math.radians(cam.rotation.y))
            if keys[pygame.K_s]: # Back
                cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.y))
                cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.y))
            if keys[pygame.K_a]: # Left
                cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.y+90))
                cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.y+90))
            if keys[pygame.K_d]: # Right
                cam.velocity.z += speed*math.cos(math.radians(cam.rotation.y+90))
                cam.velocity.x += speed*math.sin(math.radians(cam.rotation.y+90))
            if keys[pygame.K_SPACE] and self.can_jump: # Jumping
                cam.velocity.y += 0.8
                self.can_jump = False
        else: # In pause menu
            if keys[pygame.K_e]: # Exits the game if e is pressed in pause
                self.active = False

            if keys[pygame.K_f]:
                if not self.specsHeld:
                    self.specstog = not self.specstog
                    self.specsHeld = True
            else:
                self.specsHeld = False

        # Pause handling
        if keys[pygame.K_ESCAPE]:
            if not self.pause_held: # So that down does not toggle repeatedly
                self.pause_held = True
                self.paused = not self.paused
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
                
                # Change the cursor if the menu is paused
                if self.paused:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            self.pause_held = False

        return time.perf_counter_ns() - t0

# Main
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

g = graphics.Graphics(window)
engine = Engine(g)

time_elapsed = 0 # Time since last frame
last_timestamp = time.perf_counter() # Last timestamp collected
tick = 0

while engine.active:
    current_timestamp = time.perf_counter()
    time_elapsed += current_timestamp - last_timestamp # Add change in time to the time_elapsed
    last_timestamp = current_timestamp
    if time_elapsed > 1 / g.frame_cap: # Do not update unless enough time has passed
        g.frame += 1

        # Handle events
        for gevent in pygame.event.get():
            pass
        
        # Print elapsed time ever n frames
        if g.frame % 20 == 0 and engine.specstog:
            g.reset_debug_buffer()
            g.debug_to_screen("time_since_last_frame(ms):" + str(round(time_elapsed * 1000)),engine.analytics_font)

            # Engine update
            g.debug_to_screen("engine:control(us):" + str(round(engine.handle_control()/1000)),engine.analytics_font)
            g.debug_to_screen("engine:update(us):" + str(round(engine.update()/1000)),engine.analytics_font)
            
            # Render objects
            g.debug_to_screen("graphics:render3D(us):" + str(round(g.render()/1000)),engine.analytics_font)

            # Render GUI
            g.debug_to_screen("graphics:render2D(us):" + str(round(g.gui()/1000)),engine.analytics_font)
            
            # Graphics data
            g.debug_to_screen("graphics:render3D:faces:" + str((g.rendered_faces)),engine.analytics_font)
            g.debug_to_screen("graphics:render3D:objects:" + str((g.rendered_objects)),engine.analytics_font)
            g.debug_to_screen("fps:" + str(round(1/time_elapsed)), engine.analytics_font)
        else:
            # Engine update
            engine.handle_control()
            engine.update()
            tick += 1
            
            # Render objects
            g.render()

            # Render GUI
            g.gui()

        pygame.display.flip() # Invert screen
        pygame.display.update() # Display new render
        time_elapsed = 0 # Reset elapsed time
quit()
