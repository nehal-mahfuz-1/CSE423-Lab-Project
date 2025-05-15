
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random  

from OpenGL.GLUT import GLUT_BITMAP_9_BY_15


camera_pos = (0,500,500)
is_third_person = True  
camera_zoom = 1.0  

fovY = 120  
GRID_LEN = 300  
rand_var = 423

player_lives = 3
max_lives = 5
game_won = False  
#falling box variables
falling_boxes = []  
box_spawn_rate = 0.035  # Probability of spawning a new box each frame
box_size = 80  
box_height = 400  
box_fall_speed = 5  
box_collision_active = True 
box_hit_cooldown = 0  

# Enemy variables for the third section
enemy_active = True  
enemy_position = (GRID_LEN - 50, 30, GRID_LEN * 5.2)  
enemy_direction = -1  
enemy_speed = 3  
enemy_size = 25  
enemy_dead = False  
enemy_region_min_x = -GRID_LEN + 50  
enemy_region_max_x = GRID_LEN - 50   
enemy_region_min_z = GRID_LEN * 5.0 
enemy_region_max_z = GRID_LEN * 5.4  

# Bullet variables
bullets = []  
bullet_speed = 15  
bullet_size = 5  
right_arm_extended = False
is_shooting_pose = False  

# Cannon variables for the second section
cannon_positions = [
    (-GRID_LEN, 30, GRID_LEN + 100),    
    (-GRID_LEN, 30, GRID_LEN + 500),   
    (GRID_LEN, 30, GRID_LEN + 300),  
    (GRID_LEN, 30, GRID_LEN + 600)     
]
cannon_rotations = [0, 0, 180, 180]  
cannon_fire_cooldown = [0, 60, 30, 90]  #
cannon_max_cooldown = 120 
cannon_active = True  
cannon_balls = []  
cannon_ball_speed = 20
cannon_hit_cooldown = 0  
cannon_collision_active = True  


# Player state
player_x = 0    
player_y = 0     
player_z = -280   

player_angle = 0          
is_jumping = False
jump_velocity = 0
gravity = -1
jump_strength = 10     
is_falling = False

# Hammer obstacle variables
hammer_angles = [30, 0, -30]  
hammer_rotation_speeds = [5, 5, 5]  
hammer_swing_directions = [1, -1, 1]  
hammer_max_angle = 120  
hammer_min_angle = -120  
# Position hammers in the first portion of the arena - centered in arena width
hammer_positions = [
    (0, 220, -150),   
    (0, 220, 0),    
    (0, 220, 190)    
]
hammer_length = 220  
hammer_head_radius = 30  
hammer_head_length = 100 
hammer_collision_active = True 
hammer_hit_cooldown = 0 
show_blood_effect = False 
blood_effect_timer = 0 

move_speed = 10  # Movement speed per key press

# Rain effect variables
raindrops = [] 
max_raindrops = 100  
rain_speed = 5  

# Shooting cooldown and miss tracking
fire_cooldown = 0 
missed_bullets = 0  
max_missed_bullets = 3  
game_over=False

# Energy orb variables
energy_orbs = []  
max_energy_orbs = 9  
energy_orb_size = 20  


def draw_arena():
    wall_h = 50
    wall_thick = 5
    square_size = 40
    num_rows = 50  
    num_cols = 15
    start_x = -GRID_LEN
    start_z = -GRID_LEN
    for i in range(num_rows):
        for j in range(num_cols):
            x = start_x + j * square_size
            z = start_z + i * square_size
            
            # Split the arena into 3 sections with different colored tiles
            if z < GRID_LEN:
                glColor3f(1.0, 1.0, 1.0) if (i + j) % 2 == 0 else glColor3f(0.3, 0.4, 0.9)
            elif z < GRID_LEN * 3.2:
                glColor3f(1.0, 1.0, 1.0) if (i + j) % 2 == 0 else glColor3f(0.3, 0.8, 0.4)
            else:
                glColor3f(1.0, 1.0, 1.0) if (i + j) % 2 == 0 else glColor3f(0.9, 0.3, 0.3)
            
            glBegin(GL_QUADS)
            glVertex3f(x, 0, z)
            glVertex3f(x + square_size, 0, z)
            glVertex3f(x + square_size, 0, z + square_size)
            glVertex3f(x, 0, z + square_size)
            glEnd()
    
    arena_end_z = start_z + (num_rows * square_size)
    
    # Draw walls - only keep the outer boundaries
    glColor3f(0.4, 0.5, 0.6)  # Wall color
    
    # Back wall (beginning of arena)
    glPushMatrix()
    glTranslatef(0, wall_h / 2, start_z)
    glScalef(GRID_LEN * 2, wall_h, wall_thick)
    glutSolidCube(1)
    glPopMatrix()
    
    # Front wall (end of arena) - now properly aligned with the last row of tiles
    glPushMatrix()
    glTranslatef(0, wall_h / 2, arena_end_z)
    glScalef(GRID_LEN * 2, wall_h, wall_thick)
    glutSolidCube(1)
    glPopMatrix()
    
    # Number of wall segments needed to cover the entire arena length
    wall_segment_length = 100
    num_segments = math.ceil((arena_end_z - start_z) / wall_segment_length)
    
    # Draw side walls (left and right sides for the entire arena)
    for i in range(num_segments):
        z_pos = start_z + (i * wall_segment_length)
        
        # Adjust the last segment to perfectly fit the arena end
        segment_length = min(wall_segment_length, arena_end_z - z_pos)
        
        # Left wall
        glPushMatrix()
        glTranslatef(-GRID_LEN, wall_h / 2, z_pos + segment_length/2)
        glScalef(wall_thick, wall_h, segment_length)
        glutSolidCube(1)
        glPopMatrix()
        
        # Right wall
        glPushMatrix()
        glTranslatef(GRID_LEN, wall_h / 2, z_pos + segment_length/2)
        glScalef(wall_thick, wall_h, segment_length)
        glutSolidCube(1)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, wall_h / 2, GRID_LEN * 3.2)
    glScalef(GRID_LEN * 2, wall_h, wall_thick)
    glColor3f(0.8, 0.2, 0.2)
    glutSolidCube(1)
    glPopMatrix()

def spawn_energy_orbs():
    global energy_orbs

    energy_orbs.clear()

    # Spawn orbs for section 1
    for _ in range(3):
        x = random.randint(-GRID_LEN + 20, GRID_LEN - 20)
        z = random.randint(-GRID_LEN + 20, GRID_LEN - 20)
        energy_orbs.append({"position": (x, 10, z), "collected": False})

    # Spawn orbs for section 2
    for _ in range(3):
        x = random.randint(-GRID_LEN + 20, GRID_LEN - 20)
        z = random.randint(GRID_LEN + 20, GRID_LEN * 3 - 20)
        energy_orbs.append({"position": (x, 10, z), "collected": False})

    # Spawn orbs for section 3
    for _ in range(3):
        x = random.randint(-GRID_LEN + 20, GRID_LEN - 20)
        z = random.randint(GRID_LEN * 3.2 + 20, GRID_LEN * 5 - 20)
        energy_orbs.append({"position": (x, 10, z), "collected": False})

def draw_energy_orbs():
    for orb in energy_orbs:
        if orb["collected"]:
            continue 
        x, y, z = orb["position"]

        glPushMatrix()
        glTranslatef(x, y, z)  
        glColor3f(0, 1, 1)  
        glScalef(5, 10, 5)  
        glutSolidCube(2.5) 
        glPopMatrix()

def check_energy_orb_collision():
    global energy_orbs, player_lives, max_lives

    for orb in energy_orbs:
        if orb["collected"]:
            continue 

        x, y, z = orb["position"]
        dx = player_x - x
        dy = player_y - y
        dz = player_z - z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance < energy_orb_size:
            # Player collects the orb
            orb["collected"] = True
            if player_lives < max_lives:
                player_lives += 1
                print(f"Energy orb collected! Lives: {player_lives}/{max_lives}")
            
            # Relocate the orb to a new random position
            orb["position"] = (
                random.randint(-GRID_LEN + 20, GRID_LEN - 20),
                10,
                random.randint(-GRID_LEN + 20, GRID_LEN * 5 - 20)
            )
            orb["collected"] = False 

def spawn_raindrops():
    global raindrops
    if player_z < GRID_LEN * 3.2:
        return

    while len(raindrops) < max_raindrops:
        x = random.uniform(-GRID_LEN, GRID_LEN)
        z = random.uniform(GRID_LEN * 3.2, GRID_LEN * 5.5)
        y = random.uniform(300, 500)
        raindrops.append({"position": (x, y, z)})

def update_raindrops():
    global raindrops

    for drop in raindrops[:]:
        x, y, z = drop["position"]
        y -= rain_speed 

        if y <= 0:
            raindrops.remove(drop)
        else:
            drop["position"] = (x, y, z)

def draw_raindrops():
    glColor3f(0.5, 0.5, 1.0)
    for drop in raindrops:
        x, y, z = drop["position"]

        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(1, 5, 1)
        glutSolidCube(1)
        glPopMatrix()

def draw_player():

    toe_width, toe_height = 10, 5
    leg_radius, leg_height = 5, 20
    body_width, body_height = 25, 30
    arm_radius, arm_length = 4, 18
    head_radius = 8

    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_angle, 0, 1, 0)
    
    #Feet
    for dx in [-8, 8]:
        glPushMatrix()
        glTranslatef(dx, 0, 0)
        glScalef(toe_width, toe_height, toe_width)
        glColor3f(0.4, 0.4, 0.4) 
        glutSolidCube(1)
        glPopMatrix()

    #Legs
    for dx in [-8, 8]:
        glPushMatrix()
        glTranslatef(dx, 0, toe_height)
        glColor3f(0.2, 0.2, 1.0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), leg_radius, leg_radius, leg_height, 10, 10)
        glPopMatrix()

    #Body
    glPushMatrix()
    body_base_y = leg_height + toe_height
    glTranslatef(0, body_base_y + body_height/2, 0)
    glScalef(body_width, body_height, body_width)
    glColor3f(0.9, 0.4, 0.2)
    glutSolidCube(1)
    glPopMatrix()
    # Left arm is always down
    glPushMatrix()
    x_offset = -1 * (body_width / 2 + arm_radius + 1)  # Left side
    arm_base_y = body_base_y + body_height/2 - 3
    glTranslatef(x_offset, arm_base_y, 0)
    glColor3f(0.2, 1.0, 0.2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), arm_radius, arm_radius, arm_length, 10, 10)

    # Hand (sphere at end of arm)
    glTranslatef(0, 0, arm_length - 20)
    glColor3f(1.0, 0.8, 0.6)
    glutSolidSphere(arm_radius + 1, 10, 10)
    glPopMatrix()
    
    # Right arm is either down or extended forward for shooting in section 3
    glPushMatrix()
    x_offset = 1 * (body_width / 2 + arm_radius + 1)  # Right side
    arm_base_y = body_base_y + body_height/2 - 3  # Middle of body height
    glTranslatef(x_offset, arm_base_y, 0)
    glColor3f(0.2, 1.0, 0.2)
    
    if is_shooting_pose:
        # Extended forward for shooting
        glRotatef(0, 1, 0, 0)  # Horizontal, pointing forward
        gluCylinder(gluNewQuadric(), arm_radius, arm_radius, arm_length, 10, 10)
        
        # Hand at end of extended arm
        glTranslatef(0, 0, arm_length)
        glColor3f(1.0, 0.8, 0.6)
        glutSolidSphere(arm_radius + 1, 10, 10)
    else:
        # Normal hanging arm
        glRotatef(-90, 1, 0, 0)  # Point down along Y axis
        gluCylinder(gluNewQuadric(), arm_radius, arm_radius, arm_length, 10, 10)
        
        # Hand (sphere at end of arm)
        glTranslatef(0, 0, arm_length - 20)
        glColor3f(1.0, 0.8, 0.6)
        glutSolidSphere(arm_radius + 1, 10, 10)
    glPopMatrix()

    #Head
    glPushMatrix()
    head_base_y = body_base_y + body_height + head_radius + 1
    glTranslatef(0, head_base_y, 0)
    glColor3f(1.0, 0.8, 0.6)
    glutSolidSphere(head_radius, 10, 10)

    #Eyes
    eye_radius = 1.5  
    eye_spacing = 4  
    eye_forward = 4 

    for side in [-1, 1]:  # Left and right eyes
        glPushMatrix()
        glTranslatef(side * eye_spacing, 5, eye_forward)
        glColor3f(0, 0, 0)
        glutSolidSphere(eye_radius, 10, 10)
        glPopMatrix()

    glPopMatrix()
    
    glColor3f(0.7, 0, 0.1)  # Red Bull red
    glPushMatrix()
    glTranslatef(15, arm_base_y - 5, 10) 
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 10, 12, 12)
    glColor3f(0.8, 0.8, 0.8)
    glTranslatef(0, 0, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_hammer(position, angle):
    x, y, z = position
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    
    # Draw hammer handle
    glColor3f(0.6, 0.3, 0.1)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, hammer_length, 10, 10)
    glPopMatrix()
    
    # Draw hammer head
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0, -hammer_length, 0) 
    glutSolidSphere(hammer_head_radius, 15, 15)
    glPopMatrix()
    
    glPopMatrix()

def draw_hammers():
    for i in range(3):
        draw_hammer(hammer_positions[i], hammer_angles[i])

def update_hammers():
    global hammer_angles, hammer_swing_directions
    
    for i in range(3):
        hammer_angles[i] += hammer_rotation_speeds[i] * hammer_swing_directions[i]
        if hammer_angles[i] >= hammer_max_angle:
            hammer_angles[i] = hammer_max_angle
            hammer_swing_directions[i] = -1
        elif hammer_angles[i] <= hammer_min_angle:
            hammer_angles[i] = hammer_min_angle
            hammer_swing_directions[i] = 1

def check_hammer_collision():
    global player_lives, show_blood_effect, blood_effect_timer, hammer_hit_cooldown, game_over
    
    if not hammer_collision_active or hammer_hit_cooldown > 0:
        return
    
    for i in range(3):
        x, y, z = hammer_positions[i]
        angle_rad = math.radians(hammer_angles[i])
        
        # Compute rotated hammer head position
        head_x = x + hammer_length * math.sin(angle_rad)
        head_y = y - hammer_length * math.cos(angle_rad)
        head_z = z
        
        dx = player_x - head_x
        dy = player_y - head_y
        dz = player_z - head_z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        collision_threshold = hammer_head_radius + 10 # Player collision radius approx.
        
        if distance < collision_threshold:
            player_lives -= 1
            show_blood_effect = True
            blood_effect_timer = 30
            hammer_hit_cooldown = 60
            
            print(f"Hit by hammer {i+1}! Lives remaining: {player_lives}")
            respawn()
            
            # If lives reach 0, reset everything to default
            if player_lives <= 0:
                game_over=0
                print("GAME OVER! Out of lives. Starting over with full health.")
            break


def draw_blood_effect():
    if not show_blood_effect:
        return
    
    glPushMatrix()
    glTranslatef(player_x, player_y + 30, player_z)
    
    glColor3f(1.0, 0.0, 0.0)
    quadric= gluNewQuadric()
    gluSphere(quadric,15, 8, 8) 
    
    for i in range(8):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(5, 20)
        size = random.uniform(3, 8)
        
        x_offset = dist * math.cos(angle)
        z_offset = dist * math.sin(angle)
        
        glPushMatrix()
        glTranslatef(x_offset, random.uniform(20, 40), z_offset)
        quadric= gluNewQuadric()
        gluSphere(quadric,size, 6, 6) 
        glPopMatrix()
    glPopMatrix()

def draw_enemy():
    if enemy_dead:
        return
    
    x, y, z = enemy_position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Enemy body
    glColor3f(0.9, 0.1, 0.1)
    glPushMatrix()
    glScalef(enemy_size, enemy_size, enemy_size)
    glutSolidCube(1)
    glPopMatrix()
    
    # Enemy eyes
    glColor3f(0.0, 0.0, 0.0)
    for eye_x in [-5, 5]:
        glPushMatrix()
        glTranslatef(eye_x, 7, enemy_size/2)
        quadric= gluNewQuadric()
        gluSphere(quadric,3, 8, 8) 
        glPopMatrix()
    
    # Enemy mouth
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, -5, enemy_size/2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 2, 10, 2)
    glPopMatrix()

    glPopMatrix()


def draw_enemy_region():
    glColor3f(0.7, 0.2, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(enemy_region_min_x, 1, enemy_region_min_z)
    glVertex3f(enemy_region_max_x, 1, enemy_region_min_z)
    glVertex3f(enemy_region_max_x, 1, enemy_region_max_z)
    glVertex3f(enemy_region_min_x, 1, enemy_region_max_z)
    glEnd()


def update_enemy():
    global enemy_position, enemy_direction
    if enemy_dead or not enemy_active:
        return
    x, y, z = enemy_position
    # Move enemy left/right
    x += enemy_direction * enemy_speed
    # Reverse direction if enemy reaches boundary
    if x <= enemy_region_min_x:
        x = enemy_region_min_x
        enemy_direction = 1  # Change to right
    elif x >= enemy_region_max_x:
        x = enemy_region_max_x
        enemy_direction = -1  # Change to left
    enemy_position = (x, y, z)

def draw_bullet(position):
    x, y, z = position
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(1.0, 0.8, 0.0)
    quadric= gluNewQuadric()
    gluSphere(quadric,bullet_size, 8, 8) 
    glPopMatrix()

def draw_bullets():
    for bullet in bullets:
        draw_bullet(bullet["position"])

def update_bullets():
    global bullets, enemy_dead, missed_bullets, player_lives
    i = 0
    while i < len(bullets):
        bullet = bullets[i]
        x, y, z = bullet["position"]
        dx, dy, dz = bullet["direction"]
        # Move bullet
        new_x = x + dx * bullet_speed
        new_y = y + dy * bullet_speed
        new_z = z + dz * bullet_speed
        # Update position
        bullet["position"] = (new_x, new_y, new_z)
        # Increment age
        bullet["age"] += 1
        # Check for collision with enemy if enemy is active
        if not enemy_dead and enemy_active:
            ex, ey, ez = enemy_position
            distance = math.sqrt((new_x - ex)**2 + (new_y - ey)**2 + (new_z - ez)**2)
            
            if distance < enemy_size + bullet_size:
                # Enemy is hit!
                enemy_dead = True
                print("Enemy killed! Go to the purple region to win the game.")
                # Remove the bullet
                bullets.pop(i)
                continue
        
        # Remove bullets that are too old or out of boundary
        if (bullet["age"] > 200 or 
            abs(new_x) > GRID_LEN + 100 or 
            new_y < 0 or new_y > 500 or 
            abs(new_z) > GRID_LEN * 6):
            if not bullet["hit"]:
                missed_bullets += 1
                print(f"Missed bullet: {missed_bullets}/{max_missed_bullets}")
                if missed_bullets == max_missed_bullets:
                    player_lives -= 1
                    missed_bullets = 0  # Reset missed bullets after losing a life
                    print(f"Missed bullets exceeded! Lives remaining: {player_lives}")
                    respawn()
            bullets.pop(i)  # Remove bullet if too old or out of bounds
        else:
            i += 1

def check_win_condition():
    global game_won
    if not enemy_dead or game_won:
        return
    # Check if player is in the enemy region
    in_x_range = enemy_region_min_x <= player_x <= enemy_region_max_x
    in_z_range = enemy_region_min_z <= player_z <= enemy_region_max_z

    if in_x_range and in_z_range:
        game_won = True
        print("Congratulations! You've won the game!")
        print("Press 'r' to restart the game.")

def fire_bullet():
    global fire_cooldown, missed_bullets
    #player's right hand position
    right_arm_x = player_x + 15
    right_arm_y = player_y + 40
    right_arm_z = player_z

    if fire_cooldown > 0:
        print("Cannot fire yet! Cooldown active.")
        return
    rad = math.radians(player_angle)

    # Calculate bullet direction
    dx = math.sin(rad)
    dz = math.cos(rad)
    
    # Create a new bullet
    bullets.append({
        "position": (right_arm_x, right_arm_y, right_arm_z),
        "direction": (dx, 0, dz),
        "age": 0,
        "hit": False
    })
    fire_cooldown = 50
    print("Bullet fired!")

def draw_falling_box(position):
    x, y, z = position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    r = random.uniform(0.5, 0.7)
    g = random.uniform(0.0, 0.2)
    b = random.uniform(0.0, 0.2)
    glColor3f(r, g, b)

    glScalef(box_size, box_size, box_size)
    glutSolidCube(1)
    
    glPopMatrix()


def draw_falling_boxes():

    for box in falling_boxes:
        draw_falling_box(box["position"])


def spawn_falling_boxes():
    if player_z < GRID_LEN * 3.2 or player_z > GRID_LEN * 5.5:
        return  
    if random.random() < box_spawn_rate:
        x = random.randint(int(-GRID_LEN + 80), int(GRID_LEN - 80))
        z = random.randint(int(GRID_LEN * 3.3), int(GRID_LEN * 5.5 - 80))

        falling_boxes.append({
            "position": (x, box_height, z),
            "age": 0
        })

        
def update_falling_boxes():

    global player_lives, show_blood_effect, blood_effect_timer, box_hit_cooldown, game_over
    
    if box_hit_cooldown > 0:
        box_hit_cooldown -= 1
    i = 0
    while i < len(falling_boxes):
        box = falling_boxes[i]
        x, y, z = box["position"]
        
        new_y = y - box_fall_speed
        box["position"] = (x, new_y, z)
        box["age"] += 1
        
        if box_collision_active and box_hit_cooldown <= 0:
           
            player_head_y = player_y + 30  
            dist_to_player_feet = math.sqrt((x - player_x)**2 + (new_y - player_y)**2 + (z - player_z)**2)
            dist_to_player_head = math.sqrt((x - player_x)**2 + (new_y - player_head_y)**2 + (z - player_z)**2)
            dist_to_player = min(dist_to_player_feet, dist_to_player_head)
            
            if dist_to_player < box_size + 15: 
               
                player_lives -= 1
                show_blood_effect = True
                blood_effect_timer = 30
                box_hit_cooldown = 60
                
                falling_boxes.pop(i)
                print(f"Hit by falling box! Lives remaining: {player_lives}")
                
                respawn()
                
                if player_lives <= 0:
                    game_over=True  
                    print("GAME OVER! Out of lives. Starting over with full health.")
                
                continue 
       
        if new_y <= 0 or box["age"] > 500:
            falling_boxes.pop(i)
        else:
            i += 1

def draw_cannon(position, rotation, is_ready_to_fire=False):
    x, y, z = position
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)  
    
    glColor3f(0.3, 0.3, 0.3)  
    glPushMatrix()
    glScalef(15, 15, 15) 
    glutSolidCube(1)
    glPopMatrix()
    
    if is_ready_to_fire:
        glColor3f(0.8, 0.2, 0.2)  
    else:
        glColor3f(0.5, 0.5, 0.5)  
    glPushMatrix()
    glTranslatef(0, 0, 10) 
    glRotatef(90, 0, 1, 0) 
    gluCylinder(gluNewQuadric(), 5, 5, 25, 12, 12)  
    glPopMatrix()
    glPopMatrix()

def draw_cannon_ball(position):
   
    x, y, z = position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(0.0, 0.0, 0.0)  
    quadric= gluNewQuadric()
    gluSphere(quadric,8, 12, 12)   
    glPopMatrix()


def draw_cannons_and_balls():
   
    for i in range(len(cannon_positions)):
        draw_cannon(cannon_positions[i], cannon_rotations[i])
    
    for ball in cannon_balls:
        draw_cannon_ball(ball["position"])


def update_cannons_and_balls():
    
    global cannon_fire_cooldown, cannon_balls, player_lives, player_x, player_y, player_z, game_over
    global show_blood_effect, blood_effect_timer, cannon_hit_cooldown
    
    if player_z < GRID_LEN or player_z > GRID_LEN * 3.2:
        return
    
    if cannon_active:
        for i in range(len(cannon_positions)):
            if cannon_fire_cooldown[i] > 0:
                cannon_fire_cooldown[i] -= 1
            
            if cannon_fire_cooldown[i] <= 0:
                cannon_fire_cooldown[i] = cannon_max_cooldown  
                
                x, y, z = cannon_positions[i]
                dx = player_x - x
                dz = player_z - z
                
                dist = math.sqrt(dx*dx + dz*dz)
                if dist > 0:  
                    dx /= dist
                    dz /= dist
                
                cannon_balls.append({
                    "position": (x, y, z),
                    "direction": (dx, dz),
                    "age": 0
                })
    
    i = 0
    while i < len(cannon_balls):
        ball = cannon_balls[i]
        
        x, y, z = ball["position"]
        dx, dz = ball["direction"]
        
        new_x = x + dx * cannon_ball_speed
        new_z = z + dz * cannon_ball_speed
        
        ball["position"] = (new_x, y, new_z)

        ball["age"] += 1
          
        if cannon_collision_active and cannon_hit_cooldown <= 0:
            player_head_y = player_y + 30 
            dist_to_player_feet = math.sqrt((new_x - player_x)**2 + (y - player_y)**2 + (new_z - player_z)**2)
            dist_to_player_head = math.sqrt((new_x - player_x)**2 + (y - player_head_y)**2 + (new_z - player_z)**2)
            dist_to_player = min(dist_to_player_feet, dist_to_player_head)
            
            if dist_to_player < 50: 
                print(f"Distance to player: {dist_to_player:.1f}, Ball at: ({new_x:.1f}, {y:.1f}, {new_z:.1f}), Player at: ({player_x:.1f}, {player_y:.1f}, {player_z:.1f})")
            
            if dist_to_player < 30:                
                player_lives -= 1
                show_blood_effect = True
                blood_effect_timer = 30
                cannon_hit_cooldown = 60
                
                cannon_balls.pop(i)
                
                print(f"Hit by cannon ball! Lives remaining: {player_lives}")
                
                respawn()
                
                if player_lives <= 0:
                    game_over=True 
                    print("GAME OVER! Out of lives. Starting over with full health.")
                
                continue  
        
        if ball["age"] > 300 or abs(new_x) > GRID_LEN + 20 or abs(new_z) > GRID_LEN * 5:
            cannon_balls.pop(i)
        else:
            i += 1

def reset_cannon_section():
    
    global cannon_balls, cannon_fire_cooldown
    
    cannon_balls.clear()

    cannon_fire_cooldown = [0, 60, 30, 90]
    
    print("Leaving section 2 - Cannons reset and balls removed.")


def draw_text(x, y, text, color=(.31,.36,94), font=GLUT_BITMAP_9_BY_15):
    glColor3f(*color) 
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800) 
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def is_outside_hallway(x, y):
   
    hallway_width = 300
    half_width = hallway_width / 2
    start_x = -500
    end_x = start_x + 1500 
    
    return x < start_x or x > end_x or y < -half_width or y > half_width

def respawn():
    
    global player_x, player_y, player_z, is_falling, player_angle, missed_bullets
    
    missed_bullets=0

    if player_lives <= 0:
        player_x = 0        
        player_y = 0         
        player_z = -280      
        player_angle = 0    
        idle.previous_section = 1  
   
    elif GRID_LEN * 3.2 <= player_z < GRID_LEN * 5.5:
        player_x = 0        
        player_y = 0        
        player_z = GRID_LEN * 3.2 + 20  
        idle.previous_section = 3  
   
    elif GRID_LEN <= player_z < GRID_LEN * 3.2:
        player_x = 0       
        player_y = 0        
        player_z = GRID_LEN + 20  
        idle.previous_section = 2 
    
    else:
        player_x = 0        
        player_y = 0         
        player_z = -280     
        idle.previous_section = 1  
    
    is_falling = False

def reset_game():
    global player_x, player_y, player_z, player_angle
    global player_lives, game_won, enemy_dead, enemy_position, enemy_direction
    global bullets, falling_boxes, cannon_balls
    global hammer_angles, hammer_swing_directions
    global cannon_fire_cooldown, is_jumping, jump_velocity, is_falling
    global show_blood_effect, blood_effect_timer, hammer_hit_cooldown
    global cannon_hit_cooldown, box_hit_cooldown, is_shooting_pose
    global bar_angles 
    global camera_zoom, is_third_person, game_over
    global missed_bullets, max_missed_bullets
    global energy_orbs
   
    player_x = 0         
    player_y = 0         
    player_z = -280     
    player_angle = 0    
    is_jumping = False
    jump_velocity = 0
    is_falling = False

    idle.previous_section = 1 
    player_lives = max_lives
    game_won = False
    game_over = False
    enemy_dead = False
    enemy_position = (GRID_LEN - 50, 30, GRID_LEN * 5.2)
    enemy_direction = -1
    
    bullets.clear()
    falling_boxes.clear()
    cannon_balls.clear()
    
    hammer_angles = [30, 0, -30]  
    hammer_swing_directions = [1, -1, 1]  
    
    bar_angles = [0, 45, 90]  
    
    cannon_fire_cooldown = [0, 60, 30, 90]  
    
    show_blood_effect = False
    blood_effect_timer = 0
    hammer_hit_cooldown = 0
    cannon_hit_cooldown = 0
    box_hit_cooldown = 0
    missed_bullets = 0
    max_missed_bullets = 3
    
    is_shooting_pose = False
    spawn_energy_orbs()
    print("Game completely reset to initial state!")

def keyboardListener(key, x, y):
    global player_x, player_z, player_angle
    global is_jumping, jump_velocity
    global is_falling
    global camera_zoom
    global game_over, game_won

    if is_falling:
        return
    rad = math.radians(player_angle)
    movement_x = 0
    movement_z = 0
    player_speed=6
    speed_multiplier = 2 if is_jumping else 1.0
    
    if key == b'q': 
        player_angle += 5
    elif key == b'e': 
        player_angle -= 5
    elif key == b'w':  
        movement_x = player_speed * math.sin(rad)*speed_multiplier
        movement_z = player_speed * math.cos(rad)*speed_multiplier
    elif key == b's':  
        movement_x = -player_speed * math.sin(rad)*speed_multiplier
        movement_z = -player_speed * math.cos(rad)*speed_multiplier
    elif key == b'a':  
        movement_x = player_speed * math.cos(rad)
        movement_z = -player_speed * math.sin(rad)
    elif key == b'd':  
        movement_x = -player_speed * math.cos(rad)
        movement_z = player_speed * math.sin(rad)
    elif key == b' ':  
        if not is_jumping and player_y == 0:
            is_jumping = True
            jump_velocity = jump_strength
    elif key == b'm':  
        if not is_third_person:
            camera_zoom = min(camera_zoom + 0.1, 5.0)  
            print(f"Zoom level: {camera_zoom:.1f}x")
    elif key == b'n':  
        if not is_third_person:
            camera_zoom = max(camera_zoom - 0.1, 0.5)  
            print(f"Zoom level: {camera_zoom:.1f}x")
    elif (key == b'r' and game_over) or (key==b'r' and game_won):  
        game_over = False
        game_won = False
        reset_game()
    new_x = player_x + movement_x
    new_z = player_z + movement_z
    
    if abs(new_x) > GRID_LEN - 10:
        return
 
    arena_start_z = -GRID_LEN + 10
    square_size = 40
    num_rows = 50
    arena_end_z = -GRID_LEN + (num_rows * square_size) - 10
        
    if new_z < arena_start_z:
        return
    elif new_z > arena_end_z:
        return
         
    section1_start_z = -GRID_LEN
    section1_end_z = GRID_LEN
    barrier_start_z = section1_start_z + 100
    barrier_end_z = section1_end_z - 50
    barrier_width = 150
    
    if new_z >= barrier_start_z and new_z <= barrier_end_z:
        safe_width = (GRID_LEN * 2) - (barrier_width * 2)
        if new_x <= -GRID_LEN + barrier_width + 10 or new_x >= GRID_LEN - barrier_width - 10:
            return
        
    wall_z = GRID_LEN * 3.2
    wall_h = 50
    if not is_jumping and new_z >= wall_z - 5 and new_z <= wall_z + 5 and player_y < wall_h:
        return        
    player_x = new_x
    player_z = new_z

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos

    if key == GLUT_KEY_UP:
        z += 10
    if key == GLUT_KEY_DOWN:
        z -= 10
    if key == GLUT_KEY_LEFT:
        x -= 10 
    if key == GLUT_KEY_RIGHT:
        x += 10 
    camera_pos = (x, y, z)


def mouseListener(button, state, x, y):
    global is_third_person, camera_zoom

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        is_third_person = not is_third_person
        print(f"Camera mode: {'Third Person' if is_third_person else 'Default'}")
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and is_shooting_pose:
        fire_bullet()
        print("Bullet fired!")

def setupCamera():
    
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()  
  
    if not is_third_person:
        adjusted_fov = fovY / camera_zoom  
    else:
        adjusted_fov = fovY  
    
    gluPerspective(adjusted_fov, 1000/800, 1, 2000)
    glMatrixMode(GL_MODELVIEW)  
    glLoadIdentity() 
    if is_third_person:
        rad = math.radians(player_angle)
        
        camera_distance = 70
        camera_height = 90
        cam_x = player_x - camera_distance * math.sin(rad)
        cam_y = player_y + camera_height
        cam_z = player_z - camera_distance * math.cos(rad)
        
        target_x = player_x + 30 * math.sin(rad)
        target_y = player_y + 20 
        target_z = player_z + 30 * math.cos(rad)
        
        # Set up camera view
        gluLookAt(cam_x, cam_y, cam_z,      
                  target_x, target_y, target_z,  
                  0, 1, 0)                
    else:
        x, y, z = camera_pos
        # Position the camera and set its orientation
        gluLookAt(x, y, z,     
                  0, 0, 0,      
                  0, 1, 0)     
def idle():
    global player_lives, game_over, game_won
    global player_x, player_y, player_z, jump_velocity, is_jumping, is_falling
    global player_lives, hammer_hit_cooldown, cannon_hit_cooldown, box_hit_cooldown, show_blood_effect, blood_effect_timer
    global is_shooting_pose, fire_cooldown
    global previous_section

    if player_lives <= 0:
        game_over = True 
        glutPostRedisplay()  
        return
    if game_won or game_over:
        glutPostRedisplay()
        return 
    # Track when player moves between sections
    current_section = 0
    if player_z < GRID_LEN:
        current_section = 1  
    elif player_z < GRID_LEN * 3.2:
        current_section = 2 
    else:
        current_section = 3  

    if fire_cooldown > 0:
        fire_cooldown -= 1
    check_energy_orb_collision()

    if player_z < GRID_LEN * 3.2:  
        glClearColor(0.9, 0.9, 0.9, 1.0) 
    elif GRID_LEN * 3.2 <= player_z <= GRID_LEN * 3.5:  
       
        transition_progress = (player_z - GRID_LEN * 3.2) / (GRID_LEN * 0.3)
        r = 0.9 * (1 - transition_progress)
        g = 0.9 * (1 - transition_progress)
        b = 0.9 * (1 - transition_progress)
        glClearColor(r, g, b, 1.0)
    else:  
        glClearColor(0.0, 0.0, 0.0, 1.0)  

    if hasattr(idle, 'previous_section') and idle.previous_section == 2 and current_section != 2:
        reset_cannon_section()
    
    idle.previous_section = current_section

    if is_jumping:
        player_y += jump_velocity
        jump_velocity += gravity
        if player_y <= 0:
            player_y = 0
            is_jumping = False
    
    # Check if player has fallen off the floor
    if player_y < -200:
        player_lives -= 1
        respawn()
        print(f"Fell off the floor! Lives remaining: {player_lives}")
        if player_lives <= 0:
            player_lives = max_lives  
            print("GAME OVER! Out of lives. Starting over with full health.")

    update_hammers()
    check_hammer_collision()
    
    if hammer_hit_cooldown > 0:
        hammer_hit_cooldown -= 1
    
    if cannon_hit_cooldown > 0:
        cannon_hit_cooldown -= 1
    
    spawn_falling_boxes()
    update_falling_boxes()
    spawn_raindrops()
    update_raindrops()

    if box_hit_cooldown > 0:
        box_hit_cooldown -= 1

    if blood_effect_timer > 0:
        blood_effect_timer -= 1
    else:
        show_blood_effect = False

    update_cannons_and_balls()
    
    if player_z >= GRID_LEN * 3.2:
        is_shooting_pose = True 
    else:
        is_shooting_pose = False  
    update_enemy()
    update_bullets()
    check_win_condition()
    glutPostRedisplay()

def showScreen():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  
    if game_over:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_text(400, 400, "GAME OVER", (1.0, 0.0, 0.0), GLUT_BITMAP_TIMES_ROMAN_24)  
        draw_text(400, 370, "You lost. Please Press R to restart.", (1.0, 1.0, 1.0), GLUT_BITMAP_HELVETICA_18)  
        glutSwapBuffers()
        return
    if game_won:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_text(400, 400, "CONGRATULATIONS! YOU WON!", (0.0, 1.0, 0.0), GLUT_BITMAP_TIMES_ROMAN_24) 
        draw_text(400, 370, "Press 'r' to play again", (1.0, 1.0, 1.0), GLUT_BITMAP_HELVETICA_18)  
        glutSwapBuffers()
        return

    setupCamera() 
    draw_arena()
    draw_section1_barriers()
    draw_hammers()
    draw_cannons_and_balls()
    draw_falling_boxes()
    draw_enemy_region()
    draw_enemy()
    draw_bullets()
    draw_energy_orbs()
    draw_player()
    
    if show_blood_effect:
        draw_blood_effect()

    # Display game info text at fixed screen positions
    draw_text(10, 770, f"Red Bull Obstacle Challenge")
    draw_text(10, 740, f"Lives: {player_lives}/{max_lives}")

    if game_over:
        draw_text(400, 400, "GAME OVER", (1.0, 0.0, 0.0), GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(400, 370, "You lost. Please Press R to restart.", (1.0, 1.0, 1.0), GLUT_BITMAP_HELVETICA_18)  # Smaller white text

    if game_won:
        draw_text(400, 400, "YOU WIN!", (0.0, 1.0, 0.0), GLUT_BITMAP_TIMES_ROMAN_24) 
        draw_text(400, 370, "Press 'r' to restart from the beginning", (1.0, 1.0, 1.0), GLUT_BITMAP_HELVETICA_18)  # Smaller white text

    elif GRID_LEN <= player_z < GRID_LEN * 3.2:
        draw_text(10, 680, "DANGER! Cannons firing from walls - DODGE the balls!")

    elif player_z >= GRID_LEN * 3.2:
        draw_raindrops()
        draw_text(10, 680, "DANGER! Falling boxes ahead - AVOID them!")
        draw_text(10, 650, "Find and shoot the enemy at the far end of this section!")
        if enemy_dead:
            draw_text(10, 620, "Enemy defeated! Enter the purple region at the end to win!")
    
    # Show controls info
    draw_text(700, 770, "Controls:")
    draw_text(700, 740, "W/S - Move Forward/Back")
    draw_text(700, 710, "A/D - Strafe Left/Right")
    draw_text(700, 680, "Q/E - Rotate Left/Right")
    draw_text(700, 650, "Space - Jump")
    draw_text(700, 620, "Left Click - Fire (in section 3)")
    draw_text(700, 560, "R - Reset Game (return to start)")
    
    glutSwapBuffers()

def draw_section1_barriers():
    barrier_height = 60  
    barrier_width = 150 
    barrier_thickness = 40 
    section1_start_z = -GRID_LEN
    section1_end_z = GRID_LEN
    barrier_start_z = section1_start_z + 100
    actual_barrier_length = section1_end_z - barrier_start_z - 50  

    num_blocks = 5
    block_length = actual_barrier_length / num_blocks
    
    for i in range(num_blocks):
        glPushMatrix()
        glColor3f(0.7, 0.3, 0.3) 
        z_pos = barrier_start_z + (i * block_length) + (block_length/2)
        glTranslatef(-GRID_LEN + barrier_width/2, barrier_height/2, z_pos)
        glScalef(barrier_width, barrier_height, block_length - 10)  
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glColor3f(0.7, 0.3, 0.3)  
        glTranslatef(GRID_LEN - barrier_width/2, barrier_height/2, z_pos)
        glScalef(barrier_width, barrier_height, block_length - 10) 
        glutSolidCube(1)
        glPopMatrix()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) 
    glutInitWindowSize(1000, 800)  
    glutInitWindowPosition(0, 0) 
    wind = glutCreateWindow(b"Red Bull Obstacle Challenge")  
    spawn_energy_orbs()
    idle.previous_section = 1 
    
    glutDisplayFunc(showScreen)  
    glutKeyboardFunc(keyboardListener)  
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  

    glutMainLoop()

if __name__ == "__main__":
    main()