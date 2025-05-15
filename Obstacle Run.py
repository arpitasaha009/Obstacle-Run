from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Game variables
player_lane = 1
player_jump_height = 0
jump_in_progress = False
player_character = 0
score = 0
lives = 3
game_over = False
cheat_mode = False
game_speed = 5
game_speed_factor = 1.0
animation_time = 0
trees = []
road_width = 500
tree_spawn_time = time.time()
tree_positions = [-300, 300]

# Game objects
class GameObject:
    def __init__(self, z_pos, lane, obj_type):
        self.z_pos = z_pos
        self.lane = lane
        self.obj_type = obj_type
        self.collected = False

class Tree(GameObject):
    def __init__(self, z_pos, side):
        super().__init__(z_pos, 0, 3)
        self.side = side

class RoadMarking:
    def __init__(self, z_pos, is_yellow=True):
        self.z_pos = z_pos
        self.is_yellow = is_yellow

diamonds = []
obstacles = []
powerups = []
road_markings_left = []
road_markings_right = []
last_spawn_time = time.time()
last_marking_spawn_time = time.time()
last_jump_time = 0
last_animation_update = time.time()

# Lane positions (x-coordinates)
lane_positions = [-150, 0, 150]

# Camera-related variables
camera_pos = (0, 300, 550)

fovY = 90
GRID_LENGTH = 2000
MARKING_LENGTH = 50
MARKING_GAP = 50


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800) 
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    global animation_time
    
    glPushMatrix()
    
    # Position player in the correct lane
    glTranslatef(lane_positions[player_lane], 30 + player_jump_height, 0)
    
    # Select character based on player_character value
    if player_character == 0:  
        draw_male_character(animation_time)
    else:  
        draw_female_character(animation_time)
    
    glPopMatrix()


def draw_male_character(anim_time):
    anim_factor = math.sin(anim_time * 10)
    
    # Head - sphere
    glPushMatrix()
    glTranslatef(0, 100, 0)  

    glTranslatef(0, anim_factor * 2, 0)
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    gluSphere(gluNewQuadric(), 10, 10, 10)
    
    # hair
    glColor3f(0.3, 0.2, 0.1) 
    glTranslatef(0, 2, -2)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()
    
    # Arm
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5)  

    glTranslatef(15, 90, 0)  
    glRotatef(-anim_factor * 30 + 180, 1, 0, 0)  
    glRotatef(20, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 20, 8, 8)

    glTranslatef(0, 0, 20)
    glRotatef(20 + anim_factor * 15, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 4, 3.5, 20, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5)  

    glTranslatef(-15, 90, 0)  
    glRotatef(anim_factor * 30 + 180, 1, 0, 0)  
    glRotatef(-20, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 20, 8, 8)
 
    glTranslatef(0, 0, 20)
    glRotatef(20 - anim_factor * 15, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 4, 3.5, 20, 8, 8)
    glPopMatrix()

    # Body/Torso 
    glPushMatrix()
    glColor3f(0.2, 0.4, 0.8)  # Blue shirt
    glTranslatef(0, 60, 0)

    glRotatef(anim_factor * 3, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 15, 12, 30, 10, 10)
    glPopMatrix()
    
    # Pants
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.7)  # Dark blue 
    glTranslatef(0, 45, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 12, 16, 15, 10, 10)
    glPopMatrix()
    
    # Leg
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.7) 
    
    glTranslatef(8, 30, 0)
    glRotatef(anim_factor * 30, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 5, 15, 8, 8)

    glTranslatef(0, 0, 15)
    glRotatef(-abs(anim_factor) * 30, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 15, 8, 8)

    glTranslatef(0, 2, 15)
    glutSolidCube(8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.2, 0.2, 0.7) 

    glTranslatef(-8, 30, 0)

    glRotatef(-anim_factor * 30, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 5, 15, 8, 8)
    
    glTranslatef(0, 0, 15)
    glRotatef(-abs(-anim_factor) * 30, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 15, 8, 8)

    glTranslatef(0, 2, 15)
    glutSolidCube(8)
    glPopMatrix()


def draw_female_character(anim_time):

    anim_factor = math.sin(anim_time * 10)
    
    # Head - sphere
    glPushMatrix()
    glTranslatef(0, 100, 0)
    glTranslatef(0, anim_factor * 2, 0)
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    gluSphere(gluNewQuadric(), 10, 10, 10)
    
    # hair
    glColor3f(0.8, 0.6, 0.2)  # Golden-brown color

    glPushMatrix()
    glTranslatef(0, -5, -5)
    glRotatef(anim_factor * 5, 1, 0, 0)  
    gluSphere(gluNewQuadric(), 12, 10, 10)
    glPopMatrix()
 
    glTranslatef(0, 5, 0)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()
    
    # Arm
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5)  # Skin color

    glTranslatef(15, 90, 0)
    glRotatef(-anim_factor * 35 + 180, 1, 0, 0)  
    glRotatef(20, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 3.5, 20, 8, 8)

    glTranslatef(0, 0, 20)
    glRotatef(20 + anim_factor * 15, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3.5, 3, 20, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5)  

    glTranslatef(-15, 90, 0)

    glRotatef(anim_factor * 35 + 180, 1, 0, 0)  
    glRotatef(-20, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 3.5, 20, 8, 8)

    glTranslatef(0, 0, 20)
    glRotatef(20 - anim_factor * 15, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3.5, 3, 20, 8, 8)
    glPopMatrix()
    
    # Body/Torso 
    glPushMatrix()
    glColor3f(0.8, 0.2, 0.6)  # Pink top
    glTranslatef(0, 60, 0)

    glRotatef(anim_factor * 3, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 12, 10, 30, 10, 10)
    glPopMatrix()
    
    # Leg
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5) 

    glTranslatef(6, 30, 0)
    glRotatef(anim_factor * 25, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 15, 8, 8)

    glTranslatef(0, 0, 15)
    glRotatef(-abs(anim_factor) * 30, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 3.5, 15, 8, 8)

    glTranslatef(0, 2, 15)
    glutSolidCube(7)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.8, 0.6, 0.5) 

    glTranslatef(-6, 30, 0)

    glRotatef(-anim_factor * 25, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 15, 8, 8)

    glTranslatef(0, 0, 15)

    glRotatef(-abs(-anim_factor) * 30, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 3.5, 15, 8, 8)

    glTranslatef(0, 2, 15)
    glutSolidCube(7)
    glPopMatrix()

    # Skirt
    glPushMatrix()
    glColor3f(0.4, 0.2, 0.8)  # Purple 
    glTranslatef(0, 45, 0)

    glRotatef(anim_factor * 5, 1, 0, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 18, 15, 10, 10)
    glPopMatrix()


def draw_diamond(lane, z_pos):
    glPushMatrix()

    glTranslatef(lane_positions[lane], 120, z_pos)
    glRotatef(45, 0, 1, 0) 
    glRotatef(45, 1, 0, 0)

    glColor3f(0, 1, 1)  # Cyan
    glutSolidCube(30)
    
    glPopMatrix()


def draw_obstacle(lane, z_pos):
    glPushMatrix()
    
    glTranslatef(lane_positions[lane], 30, z_pos)
    glColor3f(0.8, 0.6, 0.2)  # Golden-brown

    glPushMatrix()
    glTranslatef(-25, 0, 0)
    glutSolidCube(40)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 5, 0)
    glutSolidCube(45)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(25, 0, 0)
    glutSolidCube(40)
    glPopMatrix()
    
    glPopMatrix()


def draw_powerup(lane, z_pos):
    glPushMatrix()

    glTranslatef(lane_positions[lane], 80, z_pos)
    
    # Draw a heart-shaped power-up
    glColor3f(1, 0, 0)  # Red color for heart

    glPushMatrix()
    glTranslatef(-10, 0, 0)
    glRotatef(45, 0, 0, 1)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(10, 0, 0)
    glRotatef(-45, 0, 0, 1)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -12, 0)
    glRotatef(180, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 20, 0, 25, 12, 1)
    glPopMatrix()
    
    glPopMatrix()


# draw a road marking
def draw_road_marking(x_pos, z_pos, is_yellow):
    glPushMatrix()
    
    glTranslatef(x_pos, 1, z_pos)
    if is_yellow:
        glColor3f(1.0, 1.0, 0.0)
    else:
        glColor3f(1.0, 1.0, 1.0)

    glBegin(GL_QUADS)
    glVertex3f(-3, 0, -MARKING_LENGTH / 2)
    glVertex3f(3, 0, -MARKING_LENGTH / 2)
    glVertex3f(3, 0, MARKING_LENGTH / 2)
    glVertex3f(-3, 0, MARKING_LENGTH / 2)
    glEnd()
    glutSolidCube(1)
    glPopMatrix()

def draw_tree(side, z_pos):
    glPushMatrix()
    
    if side == -1:
        x_pos = tree_positions[0] 
    else: 
        x_pos = tree_positions[1]

    glTranslatef(x_pos, 20, z_pos)
    glColor3f(0.55, 0.27, 0.07)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 80, 10, 4)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.0, 0.6, 0.0)
    glTranslatef(0, 100, 0)
    gluSphere(gluNewQuadric(), 40, 10, 10)
    glTranslatef(20, 15, 20)
    gluSphere(gluNewQuadric(), 25, 8, 8)
    glTranslatef(-40, 10, -10)
    gluSphere(gluNewQuadric(), 30, 8, 8)
    glTranslatef(15, -15, -30)
    gluSphere(gluNewQuadric(), 35, 8, 8)
    glPopMatrix()


def draw_game_objects():
    # Draw diamonds
    for diamond in diamonds:
        if not diamond.collected:
            draw_diamond(diamond.lane, diamond.z_pos)
    
    # Draw obstacles
    for obstacle in obstacles:
        draw_obstacle(obstacle.lane, obstacle.z_pos)
    
    # Draw power-ups
    for powerup in powerups:
        if not powerup.collected:
            draw_powerup(powerup.lane, powerup.z_pos)
    
    # Draw left lane road markings
    for marking in road_markings_left:
        draw_road_marking(-75, marking.z_pos, marking.is_yellow)
    
    # Draw right lane road markings
    for marking in road_markings_right:
        draw_road_marking(75, marking.z_pos, marking.is_yellow)

    # Draw trees
    for tree in trees:
        draw_tree(tree.side, tree.z_pos)


def draw_ground():
    # Draw the ground as a grid
    glBegin(GL_QUADS)
    
    # Main path (middle) - wider road
    glColor3f(0.5, 0.5, 0.5)  # Gray for road
    glVertex3f(-road_width/2, 0, -GRID_LENGTH)
    glVertex3f(road_width/2, 0, -GRID_LENGTH)
    glVertex3f(road_width/2, 0, GRID_LENGTH)
    glVertex3f(-road_width/2, 0, GRID_LENGTH)
    
    # Left footpath/sidewalk
    glColor3f(0.7, 0.7, 0.6)  # Light tan/beige
    glVertex3f(-road_width/2 - 150, 20, -GRID_LENGTH)  
    glVertex3f(-road_width/2, 20, -GRID_LENGTH)
    glVertex3f(-road_width/2, 20, GRID_LENGTH)
    glVertex3f(-road_width/2 - 150, 20, GRID_LENGTH)

    # Right footpath/sidewalk 
    glVertex3f(road_width/2, 20, -GRID_LENGTH)
    glVertex3f(road_width/2 + 150, 20, -GRID_LENGTH)
    glVertex3f(road_width/2 + 150, 20, GRID_LENGTH)
    glVertex3f(road_width/2, 20, GRID_LENGTH)
    
    # Left footpath side wall
    glColor3f(0.6, 0.6, 0.5)  # Slightly darker than top for shadow effect
    glVertex3f(-road_width/2, 0, -GRID_LENGTH)
    glVertex3f(-road_width/2, 20, -GRID_LENGTH)
    glVertex3f(-road_width/2, 20, GRID_LENGTH)
    glVertex3f(-road_width/2, 0, GRID_LENGTH)
    
    # Right footpath side wall (for 3D effect)
    glVertex3f(road_width/2, 0, -GRID_LENGTH)
    glVertex3f(road_width/2, 20, -GRID_LENGTH)
    glVertex3f(road_width/2, 20, GRID_LENGTH)
    glVertex3f(road_width/2, 0, GRID_LENGTH)
    
    glEnd()


def update_player_jump():
    global player_jump_height, jump_in_progress, last_jump_time
    
    if jump_in_progress:
        # Calculate jump height using a parabola
        elapsed_time = time.time() - last_jump_time
        if elapsed_time < 1.0:  
            player_jump_height = 4 * 100 * elapsed_time * (1 - elapsed_time)
        else:
            player_jump_height = 0
            jump_in_progress = False


def update_animation():
    global animation_time, last_animation_update
    
    # Update animation time for running cycle
    current_time = time.time()
    animation_time += (current_time - last_animation_update) * game_speed_factor
    last_animation_update = current_time


def check_collisions():
    global score, lives, game_over
    
    # Get player position
    player_z = 0 
    player_y = 30 + player_jump_height
    player_radius = 25  
    
    for diamond in diamonds:
        if not diamond.collected and abs(diamond.z_pos) < 50:
            if player_lane == diamond.lane:
                if player_y + player_radius > 90 and player_y - player_radius < 150:  
                    diamond.collected = True
                    score += 10
    
    # Check collisions with obstacles
    if not cheat_mode:
        for obstacle in obstacles:
            if abs(obstacle.z_pos) < 50:
                if player_lane == obstacle.lane:
                    if player_jump_height < 50:  # Hit only if not jumping over
                        obstacles.remove(obstacle)
                        lives -= 1
                        if lives <= 0:
                            game_over = True
    
    # Check collisions with power-ups
    for powerup in powerups:
        if not powerup.collected and abs(powerup.z_pos) < 50:
            if player_lane == powerup.lane:
                if player_y + player_radius > 50 and player_y - player_radius < 110: 
                    powerup.collected = True
                    if lives < 5:  
                        lives += 1 


def spawn_objects():
    global last_spawn_time
    
    current_time = time.time()
    if current_time - last_spawn_time > 1.0 / game_speed_factor:  
        last_spawn_time = current_time
        
        # Random lane
        lane = random.randint(0, 2)
        
        if random.random() < 0.6:
            diamonds.append(GameObject(-GRID_LENGTH, lane, 0))
        
        if random.random() < 0.6:
            obstacles.append(GameObject(-GRID_LENGTH, random.randint(0, 2), 1))
        
        if random.random() < 0.2:
            powerups.append(GameObject(-GRID_LENGTH, random.randint(0, 2), 2))


def spawn_trees():
    global tree_spawn_time, trees
    
    current_time = time.time()
    if current_time - tree_spawn_time > 1 / game_speed_factor:
        tree_spawn_time = current_time
        side = -1 if random.random() < 0.5 else 1
        if random.random() < 0.2:
            trees.append(Tree(-GRID_LENGTH, side))

def initialize_road_markings():
    global road_markings_left, road_markings_right
    road_markings_left = []
    road_markings_right = []
    total_marking_length = MARKING_LENGTH + MARKING_GAP
    num_markings = int(GRID_LENGTH * 2 / total_marking_length) + 2
    for i in range(num_markings):
        z_pos = -GRID_LENGTH + i * total_marking_length
        is_yellow = (i % 2 == 0)
        road_markings_left.append(RoadMarking(z_pos, is_yellow))
        road_markings_right.append(RoadMarking(z_pos, is_yellow))

def spawn_road_markings():
    global road_markings_left, road_markings_right
    if road_markings_left and road_markings_right:
        farthest_left_z = min(marking.z_pos for marking in road_markings_left)
        farthest_right_z = min(marking.z_pos for marking in road_markings_right)
        total_marking_length = MARKING_LENGTH + MARKING_GAP
        if farthest_left_z > -GRID_LENGTH + total_marking_length:
            for marking in road_markings_left:
                if marking.z_pos == farthest_left_z:
                    is_yellow = not marking.is_yellow
                    road_markings_left.append(RoadMarking(farthest_left_z - total_marking_length, is_yellow))
                    break
        if farthest_right_z > -GRID_LENGTH + total_marking_length:
            for marking in road_markings_right:
                if marking.z_pos == farthest_right_z:
                    is_yellow = not marking.is_yellow
                    road_markings_right.append(RoadMarking(farthest_right_z - total_marking_length, is_yellow))
                    break

def update_objects():
    global diamonds, obstacles, powerups, road_markings_left, road_markings_right, game_speed
    speed = game_speed * game_speed_factor
    for diamond in diamonds[:]:
        diamond.z_pos += speed
        if diamond.z_pos > 100:
            diamonds.remove(diamond)
    for obstacle in obstacles[:]:
        obstacle.z_pos += speed
        if obstacle.z_pos > 100:
            obstacles.remove(obstacle)
    for powerup in powerups[:]:
        powerup.z_pos += speed
        if powerup.z_pos > 100:
            powerups.remove(powerup)
    for marking in road_markings_left[:]:
        marking.z_pos += 2
        if marking.z_pos > GRID_LENGTH:
            road_markings_left.remove(marking)
    for marking in road_markings_right[:]:
        marking.z_pos += 2
        if marking.z_pos > GRID_LENGTH:
            road_markings_right.remove(marking)
    for tree in trees[:]:
        tree.z_pos += speed
        if tree.z_pos > 100:
            trees.remove(tree)

def auto_collect_diamonds():
    global player_lane, jump_in_progress, last_jump_time
    if cheat_mode:
        nearest_diamond = None
        nearest_distance = float('inf')
        for diamond in diamonds:
            if not diamond.collected and diamond.z_pos < 0:
                distance = abs(diamond.z_pos)
                if distance < nearest_distance:
                    nearest_diamond = diamond
                    nearest_distance = distance
        if nearest_diamond and nearest_distance < 1000:
            target_lane = nearest_diamond.lane
            if player_lane < target_lane:
                player_lane += 1
            elif player_lane > target_lane:
                player_lane -= 1
            if player_lane == target_lane and nearest_distance < 200 and not jump_in_progress:
                jump_in_progress = True
                last_jump_time = time.time()

def keyboardListener(key, x, y):
    global player_lane, jump_in_progress, last_jump_time, cheat_mode, player_character
    global game_speed_factor, game_over, score, lives, diamonds, obstacles, powerups
    global road_markings_left, road_markings_right
    if game_over:
        if key == b'r':
            player_lane = 1
            player_jump_height = 0
            jump_in_progress = False
            score = 0
            lives = 3
            game_over = False
            cheat_mode = False
            game_speed_factor = 1.0
            diamonds = []
            obstacles = []
            powerups = []
            trees = []
            initialize_road_markings()
        return
    if key == b'a':
        if player_lane > 0:
            player_lane -= 1
    if key == b'd':
        if player_lane < 2:
            player_lane += 1
    if key == b' ':
        if not jump_in_progress:
            jump_in_progress = True
            last_jump_time = time.time()
    if key == b'c':
        cheat_mode = not cheat_mode
        if cheat_mode:
            game_speed_factor = 2.0
        else:
            game_speed_factor = 1.0
    if key == b'x':
        player_character = (player_character + 1) % 2
    if key == b'r':
        player_lane = 1
        player_jump_height = 0
        jump_in_progress = False
        score = 0
        lives = 3
        game_over = False
        cheat_mode = False
        game_speed_factor = 1.0
        diamonds = []
        obstacles = []
        powerups = []
        road_markings_left = []
        road_markings_right = []
        trees = []


def specialKeyListener(key, x, y):
    global player_lane
    
    if game_over:
        return
    
    # Move left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        if player_lane > 0:
            player_lane -= 1
    
    # Move right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        if player_lane < 2:
            player_lane += 1


def mouseListener(button, state, x, y):
    global jump_in_progress, last_jump_time
    
    if game_over:
        return
    
    # Left mouse button initiates jump
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not jump_in_progress:
            jump_in_progress = True
            last_jump_time = time.time()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Position the camera to show the player and incoming objects
    x, y, z = camera_pos
    gluLookAt(x, y, z,  # Camera position
              0, 50, -200,  # Look ahead of the player
              0, 1, 0)  # Up vector


def idle():
    if not game_over:
        # Update game state
        update_player_jump()
        update_animation()
        update_objects()
        spawn_objects()
        spawn_road_markings()
        spawn_trees()  # Call the new function
        check_collisions()
        
        # Auto-collect diamonds in cheat mode
        if cheat_mode:
            auto_collect_diamonds()
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw game world
    draw_ground()
    draw_game_objects()
    draw_player()
    
    # Display UI elements
    # Display game title
    draw_text(400, 750, "OBSTACLE RUN", font=GLUT_BITMAP_TIMES_ROMAN_24)
    
    if game_over:
        draw_text(400, 400, "GAME OVER")
        draw_text(350, 350, f"Final Score: {score}")
        draw_text(300, 300, "Press 'R' to restart")
    else:
        # Display game info
        draw_text(10, 770, f"Score: {score}")
        draw_text(10, 740, f"Lives: {lives}")
        if cheat_mode:
            draw_text(10, 710, "CHEAT MODE ACTIVE")
            draw_text(10, 680, "Auto-collecting diamonds")
    
    # Draw controls info
    draw_text(750, 770, "A/D: Move Left/Right")
    draw_text(750, 740, "Space: Jump")
    draw_text(750, 710, "C: Toggle Cheat Mode")
    draw_text(750, 680, "X: Switch Character")
    draw_text(750, 650, f"Character: {'Male' if player_character == 0 else 'Female'}")
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Obstacle Run")
    
    # Initialize road markings before starting the game
    initialize_road_markings()
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()