from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

active_enemies = []
bosses = []
MAX_ENEMIES = 5

MELEE_CREATURE = 1
RANGED_ATTACKER = 2
FINAL_BOSS = 3

camera_pos = (0,2100,1000)
camera_mode = "third_person"

fovY = 120
GRID_LENGTH = 2000

day_night_cycle = 0

character_pos = [0, 0, 50]
character_size = 30
character_speed = 20

player_x = 0
player_y = 0 
player_z = 50
movement_speed = 20.0
base_movement_speed = 20.0
max_movement_speed = 50.0

player_health = 100
max_health = 200

player_rotation = 0
current_weapon = "gun"

bullets = []
bullet_speed = 15.0
bullet_size = 5

sword_swing_active = False
sword_swing_timer = 0
sword_swing_angle = 90
sword_swing_speed = 8
sword_damage = 60
sword_range = 100

collectibles = []
collectible_size = 25
max_collectibles = 2
spawn_timer = 0
spawn_interval = 300

obstacles = {
    1: [
        {"type": "cube", "x": -400, "y": -400, "z": 50, "size": 100},
        {"type": "cube", "x": 400, "y": 400, "z": 50, "size": 100},
        {"type": "cylinder", "x": -400, "y": 400, "z": 0, "radius": 60, "height": 100},
        {"type": "cylinder", "x": 400, "y": -400, "z": 0, "radius": 60, "height": 100},
    ],
    2: [
        {"type": "cube", "x": 0, "y": 0, "z": 50, "size": 80},
        {"type": "cylinder", "x": -500, "y": -500, "z": 0, "radius": 70, "height": 120},
        {"type": "cylinder", "x": 500, "y": 500, "z": 0, "radius": 70, "height": 120},
    ],
    3: [
        {"type": "cube", "x": 500, "y": 0, "z": 50, "size": 80},
        {"type": "cube", "x": -500, "y": 0, "z": 50, "size": 80},
        {"type": "cube", "x": 0, "y": 500, "z": 50, "size": 80},
        {"type": "cube", "x": 0, "y": -500, "z": 50, "size": 80},
    ]
}

current_level = 1

def draw_obstacles():
    for obstacle in obstacles[current_level]:
        glPushMatrix()
        glTranslatef(obstacle['x'], obstacle['y'], obstacle['z'])
        
        if obstacle['type'] == 'cube':
            glColor3f(0.8, 0.6, 0.4)
            glutSolidCube(obstacle['size'])
        elif obstacle['type'] == 'cylinder':
            glColor3f(0.4, 0.6, 0.8)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), obstacle['radius'], obstacle['radius'], obstacle['height'], 20, 20)
        
        glPopMatrix()

def check_obstacle_collision(new_x, new_y):
    player_radius = 40
    
    for obstacle in obstacles[current_level]:
        obs_x, obs_y = obstacle['x'], obstacle['y']
        
        if obstacle['type'] == 'cube':
            obs_size = obstacle['size']
            dist = math.sqrt((new_x - obs_x)**2 + (new_y - obs_y)**2)
            if dist < (player_radius + obs_size/2):
                return True
        elif obstacle['type'] == 'cylinder':
            obs_radius = obstacle['radius']
            dist = math.sqrt((new_x - obs_x)**2 + (new_y - obs_y)**2)
            if dist < (player_radius + obs_radius):
                return True
    
    return False

def spawn_collectible():
    global collectibles
    
    if len(collectibles) < max_collectibles:
        x = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        y = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        z = collectible_size
        
        cube_type = random.choice(['health', 'speed'])
        
        collectibles.append([x, y, z, cube_type])

def draw_collectible(x, y, z, cube_type):
    glPushMatrix()
    
    glTranslatef(x, y, z)
    
    if cube_type == 'health':
        glColor3f(0, 1, 0)
    elif cube_type == 'speed':
        glColor3f(1, 0, 0)
    
    glutSolidCube(collectible_size)
    
    glPopMatrix()

def draw_all_collectibles():
    for collectible in collectibles:
        x, y, z, cube_type = collectible
        draw_collectible(x, y, z, cube_type)

def update_collectibles():
    global collectibles, spawn_timer
    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_collectible()
        spawn_timer = 0

def check_collectible_collision():
    global collectibles, player_health, movement_speed
    
    player_collision_radius = 60
    
    for i, collectible in enumerate(collectibles):
        x, y, z, cube_type = collectible
        
        dx = player_x - x
        dy = player_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < (player_collision_radius + collectible_size/2):
            if cube_type == 'health':
                health_gain = 25
                player_health = min(player_health + health_gain, max_health)
                print(f"Health collected! +{health_gain} HP (Current: {player_health})")
                
            elif cube_type == 'speed':
                speed_boost = 5.0
                movement_speed = min(movement_speed + speed_boost, max_movement_speed)
                print(f"Speed boost collected! +{speed_boost} speed (Current: {movement_speed:.1f})")
            
            collectibles.pop(i)
            break

def draw_text(x, y, text):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        except:
            pass
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_rotation, 0, 0, 1)
    
    glColor3f(0.5, 1, 0.5)
    glutSolidCube(80)
    
    glTranslatef(0, 0, 80)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 30, 10, 10)
    
    glColor3f(1, .9, .8)
    glTranslatef(50, -30, -70)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)   
    glTranslatef(-100, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)  
    
    glColor3f(0, 0, 1)
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 10, 100)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    glTranslatef(100, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    
    glColor3f(0.5, 0.5, 0.5)
    glRotatef(-90, 1, 0, 0)
    
    if current_weapon == "gun":
        glTranslatef(-110, 70, 80)
        gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    elif current_weapon == "sword":
        current_angle = sword_swing_angle if sword_swing_active else 90
        if sword_swing_active:
            print(f"Drawing sword at angle: {current_angle:.1f}")
        draw_sword(current_angle, 0, 1, 0)
    
    glPopMatrix()

def draw_sword(sword_angle=90, x=0, y=1, z=0):
    glPushMatrix()
    
    glColor3f(1, 0, 0)  
    
    glTranslatef(-100, 100, 90)
    
    glRotatef(sword_angle, x, y, z)
    
    gluCylinder(gluNewQuadric(), 20, 1, 250, 20, 20)
    
    glColor3f(0.4, 0.2, 0.1)
    glTranslatef(0, 0, -30)
    gluCylinder(gluNewQuadric(), 25, 25, 30, 10, 10)
    
    glPopMatrix()

def draw_bullet(x, y, z):
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(x, y, z)
    glutSolidCube(bullet_size)
    glPopMatrix()

def draw_all_bullets():
    for bullet in bullets:
        draw_bullet(bullet[0]-50, bullet[1]-80, bullet[2]-50)

def update_bullets():
    global bullets

    for i, bullet in enumerate(bullets):
        bullet[0] += bullet[3]
        bullet[1] += bullet[4]
        bullet[2] += bullet[5]

def update_sword_swing():
    global sword_swing_active, sword_swing_timer, sword_swing_angle
    
    if sword_swing_active:
        sword_swing_timer += 1
        
        print(f"Swing timer: {sword_swing_timer}, Angle: {sword_swing_angle:.1f}")
        
        swing_duration = 30
        
        if sword_swing_timer <= swing_duration:
            progress = sword_swing_timer / swing_duration
            
            if progress <= 0.5:
                sword_swing_angle = 90 - (135 * (progress * 2))
            else:
                sword_swing_angle = -45 + (135 * ((progress - 0.5) * 2))
        else:
            print("Swing completed!")
            sword_swing_active = False
            sword_swing_timer = 0
            sword_swing_angle = 90

def check_sword_enemy_collision():
    if not sword_swing_active:
        return
    
    angle_rad = math.radians(player_rotation)
    sword_tip_x = player_x + (sword_range * math.sin(angle_rad))
    sword_tip_y = player_y - (sword_range * math.cos(angle_rad))
    
    for enemy in  get_all_enemies():
        if enemy.is_dead:
            continue
            
        dx = sword_tip_x - enemy.x
        dy = sword_tip_y - enemy.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < (enemy.collision_radius + 30):
            enemy_dx = enemy.x - player_x
            enemy_dy = enemy.y - player_y
            enemy_angle = math.degrees(math.atan2(enemy_dx, -enemy_dy))
            
            enemy_angle = enemy_angle % 360
            player_facing = player_rotation % 360
            
            angle_diff = abs(enemy_angle - player_facing)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            if angle_diff <= 45:
                enemy.take_damage(sword_damage)
                print(f"Sword hit! Enemy health: {enemy.current_health}")
                
                knockback_force = 30
                knockback_dx = (enemy.x - player_x) / distance * knockback_force
                knockback_dy = (enemy.y - player_y) / distance * knockback_force
                enemy.x += knockback_dx
                enemy.y += knockback_dy

def simple_sword_collision():
    if not sword_swing_active:
        return
        
    for enemy in get_all_enemies():
        if enemy.is_dead:
            continue
            
        dx = enemy.x - player_x
        dy = enemy.y - player_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= sword_range:
            angle_rad = math.radians(player_rotation)
            forward_x = math.sin(angle_rad)
            forward_y = -math.cos(angle_rad)
            
            dot_product = (dx * forward_x + dy * forward_y) / distance
            
            if dot_product > 0.5:
                enemy.take_damage(sword_damage)
                print(f"Sword hit! Enemy health: {enemy.current_health}")

def shoot_bullet():
    global bullets, player_x, player_y, player_z, player_rotation

    angle_rad = math.radians(player_rotation)
    gun_offset_x = 50 * math.sin(angle_rad)
    gun_offset_y = -30 * math.cos(angle_rad)
    
    gun_x = player_x + gun_offset_x
    gun_y = player_y + gun_offset_y
    gun_z = player_z + 40
    
    bullet_dx = bullet_speed * math.sin(angle_rad)
    bullet_dy = -bullet_speed * math.cos(angle_rad)
    bullet_dz = 0
    
    bullets.append([gun_x, gun_y, gun_z, bullet_dx, bullet_dy, bullet_dz])

def mouseListener(button, state, x, y):
    global sword_swing_active, sword_swing_timer, sword_swing_angle
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_weapon == "gun":
            shoot_bullet()
        elif current_weapon == "sword":
            print("Slash attack!")
    
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if current_weapon == "sword":
            print("Starting sword swing animation!")
            sword_swing_active = True
            sword_swing_timer = 0
            sword_swing_angle = 90
        else:
            print("Right click detected, but weapon is:", current_weapon)

    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def keyboardListener(key, x, y):
    global character_pos, player_x, player_y, player_z, player_rotation, current_weapon
    
    if key == b'w' or key == b'W':
        angle_rad = math.radians(player_rotation)
        new_x = player_x + movement_speed * math.sin(angle_rad)
        new_y = player_y - movement_speed * math.cos(angle_rad)
        
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b's' or key == b'S':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.sin(angle_rad)
        new_y = player_y + movement_speed * math.cos(angle_rad)
        
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'a' or key == b'A':
        angle_rad = math.radians(player_rotation)
        new_x = player_x + movement_speed * math.cos(angle_rad)
        new_y = player_y + movement_speed * math.sin(angle_rad)
        
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'd' or key == b'D':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.cos(angle_rad)
        new_y = player_y - movement_speed * math.sin(angle_rad)
        
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if not check_obstacle_collision(new_x, new_y) and -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'q' or key == b'Q':
        if current_weapon == "gun":
            current_weapon = "sword"
        else:
            current_weapon = "gun"
    
    glutPostRedisplay()


class EnemyCreature:
    def __init__(self, x_coord, y_coord, z_coord, creature_type):
        self.x, self.y, self.z = x_coord, y_coord, z_coord
        self.creature_type = creature_type
        self.current_health = 500 if creature_type == FINAL_BOSS else 100
        self.maximum_health = self.current_health
        self.movement_speed = 1.0 if creature_type == FINAL_BOSS else (2.0 if creature_type == MELEE_CREATURE else 1.5)
        self.is_dead = False
        self.animation_time = 0
        self.initial_x, self.initial_y = x_coord, y_coord
        self.behavior_state = "wandering"
        self.collision_radius = 80 if creature_type == FINAL_BOSS else 40
        
        self.equipped_weapon = "sword"
        self.sword_range = 100 if creature_type == FINAL_BOSS else 80
        self.gun_range = 400 if creature_type == FINAL_BOSS else 300
        self.sword_damage = 60 if creature_type == FINAL_BOSS else 30
        self.gun_damage = 40 if creature_type == FINAL_BOSS else 20
        self.sword_cooldown = 0.5 if creature_type == FINAL_BOSS else 0.8
        self.gun_cooldown = 1.0 if creature_type == FINAL_BOSS else 1.5
        self.last_attack_time = 0
        self.is_swinging = False
        self.swing_duration_timer = 0
        
        if creature_type == FINAL_BOSS:
            self.special_attack_cooldown = 5.0
            self.last_special_attack_time = 0
        
        self.projectiles = []
        self.patrol_direction = random.random() * 6.28
        self.wander_distance = 100
        self.target_position = [0, 0, 50]

    def update(self, delta_time):
        if self.is_dead:
            return
            
        self.animation_time += delta_time
        current_time = time.time()
        
        self.patrol_direction += delta_time * 0.5
        
        self.target_position[0] = player_x
        self.target_position[1] = player_y
        self.target_position[2] = player_z
        
        distance_to_player = self.get_distance(self.target_position)
        
        if distance_to_player <= self.sword_range:
            self.equipped_weapon = "sword"
        elif distance_to_player <= self.gun_range:
            self.equipped_weapon = "gun"
        else:
            self.equipped_weapon = "gun"
        
        if self.is_swinging:
            self.swing_duration_timer += delta_time
            if self.swing_duration_timer > 0.5:
                self.is_swinging = False
                self.swing_duration_timer = 0
        
        self.handle_ai_behavior(delta_time, distance_to_player, current_time)
        self.update_projectiles(delta_time)

    def get_distance(self, target):
        dx = self.x - target[0]
        dy = self.y - target[1]
        return math.sqrt(dx*dx + dy*dy)

    def handle_ai_behavior(self, delta_time, distance_to_player, current_time):
        if self.creature_type == MELEE_CREATURE:
            if distance_to_player < 350:
                self.behavior_state = "hunting"
                if distance_to_player > self.sword_range and self.equipped_weapon == "sword":
                    dx = self.target_position[0] - self.x
                    dy = self.target_position[1] - self.y
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        self.x += (dx/length) * self.movement_speed * delta_time * 60
                        self.y += (dy/length) * self.movement_speed * delta_time * 60
                else:
                    self.behavior_state = "fighting"
                    delay = self.sword_cooldown if self.equipped_weapon == "sword" else self.gun_cooldown
                    if current_time - self.last_attack_time > delay:
                        self.execute_attack()
                        self.last_attack_time = current_time
            else:
                self.behavior_state = "wandering"
                self.wander_around(delta_time)
        
        elif self.creature_type == RANGED_ATTACKER:
            if distance_to_player < 400:
                if distance_to_player <= self.sword_range and self.equipped_weapon == "sword":
                    self.behavior_state = "fighting"
                    if current_time - self.last_attack_time > self.sword_cooldown:
                        self.perform_sword_swing()
                        self.last_attack_time = current_time
                elif distance_to_player <= self.gun_range and self.equipped_weapon == "gun":
                    self.behavior_state = "fighting"
                    if current_time - self.last_attack_time > self.gun_cooldown:
                        self.fire_gun()
                        self.last_attack_time = current_time
                else:
                    self.behavior_state = "positioning"
                    optimal_range = self.gun_range * 0.7
                    if distance_to_player < optimal_range:
                        dx = self.x - self.target_position[0]
                        dy = self.y - self.target_position[1]
                        length = math.sqrt(dx*dx + dy*dy)
                        if length > 0:
                            self.x += (dx/length) * self.movement_speed * delta_time * 40
                            self.y += (dy/length) * self.movement_speed * delta_time * 40
                    else:
                        dx = self.target_position[0] - self.x
                        dy = self.target_position[1] - self.y
                        length = math.sqrt(dx*dx + dy*dy)
                        if length > 0:
                            self.x += (dx/length) * self.movement_speed * delta_time * 40
                            self.y += (dy/length) * self.movement_speed * delta_time * 40
            else:
                self.behavior_state = "wandering"
                self.wander_around(delta_time)
        
        elif self.creature_type == FINAL_BOSS:
            if distance_to_player < 500:
                if distance_to_player > self.sword_range:
                    self.behavior_state = "hunting"
                    dx = self.target_position[0] - self.x
                    dy = self.target_position[1] - self.y
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        self.x += (dx/length) * self.movement_speed * delta_time * 60
                        self.y += (dy/length) * self.movement_speed * delta_time * 60
                
                self.behavior_state = "fighting"
                delay = self.sword_cooldown if self.equipped_weapon == "sword" else self.gun_cooldown
                if current_time - self.last_attack_time > delay:
                    if self.equipped_weapon == "sword":
                        self.perform_sword_swing()
                    else:
                        self.fire_gun()
                    self.last_attack_time = current_time
                
                if current_time - self.last_special_attack_time > self.special_attack_cooldown:
                    self.execute_boss_special_attack()
                    self.last_special_attack_time = current_time

    def wander_around(self, delta_time):
        angle = self.patrol_direction
        target_x = self.initial_x + math.cos(angle) * self.wander_distance
        target_y = self.initial_y + math.sin(angle) * self.wander_distance
        
        dx = target_x - self.x
        dy = target_y - self.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 5:
            self.x += (dx/length) * self.movement_speed * delta_time * 30
            self.y += (dy/length) * self.movement_speed * delta_time * 30

    def execute_attack(self):
        if self.equipped_weapon == "sword":
            self.perform_sword_swing()
        else:
            self.fire_gun()

    def perform_sword_swing(self):
        self.is_swinging = True
        self.swing_duration_timer = 0

    def fire_gun(self):
        dx = self.target_position[0] - self.x
        dy = self.target_position[1] - self.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            velocity_x = dx/length * 250
            velocity_y = dy/length * 250
            projectile = {
                'x': self.x, 'y': self.y, 'z': self.z + 20,
                'vx': velocity_x, 'vy': velocity_y,
                'lifetime': 4.0, 'damage': self.gun_damage,
                'is_special': False
            }
            self.projectiles.append(projectile)

    def execute_boss_special_attack(self):
        if self.creature_type == FINAL_BOSS:
            self.is_swinging = True
            for i in range(0, 360, 20):
                angle = math.radians(i)
                velocity_x = math.cos(angle) * 200
                velocity_y = math.sin(angle) * 200
                projectile = {
                    'x': self.x, 'y': self.y, 'z': self.z + 20,
                    'vx': velocity_x, 'vy': velocity_y,
                    'lifetime': 5.0, 'damage': self.gun_damage,
                    'is_special': True
                }
                self.projectiles.append(projectile)

    def update_projectiles(self, delta_time):
        for projectile in self.projectiles[:]:
            projectile['x'] += projectile['vx'] * delta_time
            projectile['y'] += projectile['vy'] * delta_time
            projectile['lifetime'] -= delta_time
            
            if projectile['lifetime'] <= 0:
                self.projectiles.remove(projectile)

    def take_damage(self, damage_amount):
        self.current_health -= damage_amount
        if self.current_health <= 0:
            self.is_dead = True

    def render_creature(self):
        if self.is_dead:
            return

        current_time = glutGet(GLUT_ELAPSED_TIME) / 500.0
        scale_effect = 1.0 + 0.3 * math.sin(2 * math.pi * current_time)

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        glScalef(scale_effect, scale_effect, scale_effect)
        
        if self.creature_type == MELEE_CREATURE:
            glPushMatrix()
            glColor3f(1, 0, 0)
            glutSolidSphere(35, 20, 20)
            glPopMatrix()
            
            glPushMatrix()
            glColor3f(0, 0, 0)
            glTranslatef(0, 0, 30)
            glutSolidSphere(18, 16, 16)
            glPopMatrix()
            
        elif self.creature_type == RANGED_ATTACKER:
            glPushMatrix()
            glColor3f(0, 0, 1)  # Blue for ranged
            glutSolidSphere(35, 20, 20)
            glPopMatrix()
            
            glPushMatrix()
            glColor3f(0, 0, 0)
            glTranslatef(0, 0, 30)
            glutSolidSphere(18, 16, 16)
            glPopMatrix()
            
        else:  # FINAL_BOSS
            glPushMatrix()
            glColor3f(0.8, 0, 0.8)  # Purple for boss
            glutSolidSphere(35, 20, 20)
            glPopMatrix()
            
            glPushMatrix()
            glColor3f(0, 0, 0)
            glTranslatef(0, 0, 40)
            glutSolidSphere(18, 16, 16)
            glPopMatrix()
        
        self.draw_current_weapon()
        glPopMatrix()
        
        self.draw_health_bar()
        self.draw_projectiles()

    def draw_current_weapon(self):
        if self.equipped_weapon == "sword":
            self.draw_weapon_sword()
        else:
            self.draw_weapon_gun()
    
    def draw_weapon_sword(self):
        glPushMatrix()
        glTranslatef(self.collision_radius * 0.7, 0, 0)
        
        if self.is_swinging:
            swing = math.sin(self.swing_duration_timer * 10) * 50
            glRotatef(swing, 0, 0, 1)
        
        if self.creature_type == MELEE_CREATURE:
            glColor3f(0.9, 0.0, 0.0)
            glPushMatrix()
            glScalef(0.08, 0.9, 0.04)
            glutSolidCube(80)
            glPopMatrix()
            
        elif self.creature_type == FINAL_BOSS:
            glColor3f(0.6, 0.5, 0.2)
            glPushMatrix()
            glScalef(0.12, 1.1, 0.06)
            glutSolidCube(90)
            glPopMatrix()
            
        else:
            glColor3f(0.0, 0.8, 1.0)
            glPushMatrix()
            glScalef(0.05, 0.8, 0.03)
            glutSolidCube(70)
            glPopMatrix()
        
        # Draw handle
        glColor3f(0.15, 0.15, 0.2)
        glPushMatrix()
        glTranslatef(0, -40, 0)
        gluCylinder(gluNewQuadric(), 6, 6, 25, 8, 8)
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_weapon_gun(self):
        glPushMatrix()
        glTranslatef(self.collision_radius * 0.6, 0, 10)
        
        dx = self.target_position[0] - self.x
        dy = self.target_position[1] - self.y
        if dx != 0 or dy != 0:
            angle = math.degrees(math.atan2(dy, dx))
            glRotatef(angle, 0, 0, 1)
        
        if self.creature_type == RANGED_ATTACKER:
            glColor3f(0.1, 0.15, 0.2)
            glPushMatrix()
            glTranslatef(25, 0, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6, 6, 50, 8, 8)
            glPopMatrix()
            
            glColor3f(0.0, 0.6, 1.0)
            glPushMatrix()
            glTranslatef(10, 0, 0)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()
            
        elif self.creature_type == FINAL_BOSS:
            glColor3f(0.3, 0.25, 0.15)
            glPushMatrix()
            glTranslatef(35, 0, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 80, 12, 12)
            glPopMatrix()
            
            glColor3f(0.8, 0.6, 0.2)
            glPushMatrix()
            glTranslatef(60, 0, 0)
            glutSolidSphere(18, 12, 12)
            glPopMatrix()
            
        else:
            glColor3f(0.3, 0.3, 0.35)
            glPushMatrix()
            glTranslatef(20, 0, 0)
            glScalef(0.7, 0.12, 0.12)
            glutSolidCube(35)
            glPopMatrix()
        
        glPopMatrix()

    def draw_health_bar(self):
        if self.is_dead:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z + self.collision_radius + 30)
        
        glRotatef(90 - math.degrees(math.atan2(player_y - self.y, player_x - self.x)), 0, 0, 1)
        
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(-25, -3, 0)
        glVertex3f(25, -3, 0)
        glVertex3f(25, 3, 0)
        glVertex3f(-25, 3, 0)
        glEnd()
        
        health_percentage = self.current_health / self.maximum_health
        if health_percentage > 0.6:
            glColor3f(0.0, 1.0, 0.0)
        elif health_percentage > 0.3:
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 0.0, 0.0)
            
        glBegin(GL_QUADS)
        glVertex3f(-25, -2, 1)
        glVertex3f(-25 + 50 * health_percentage, -2, 1)
        glVertex3f(-25 + 50 * health_percentage, 2, 1)
        glVertex3f(-25, 2, 1)
        glEnd()
        
        glPopMatrix()

    def draw_projectiles(self):
        for projectile in self.projectiles:
            glPushMatrix()
            glTranslatef(projectile['x'], projectile['y'], projectile['z'])
            
            if projectile['is_special']:
                glRotatef(time.time() * 120, 0, 1, 0)
                glColor3f(1.0, 0.8, 0.3)
                glutSolidCube(16)
                glColor3f(0.8, 0.6, 0.2)
                glutWireCube(20)
            elif self.creature_type == RANGED_ATTACKER:
                glColor3f(0.2, 0.8, 1.0)
                glutSolidSphere(8, 10, 10)
                glColor3f(0.0, 0.4, 0.8)
                for i in range(3):
                    glPushMatrix()
                    glTranslatef(-i * 6, 0, 0)
                    glutSolidSphere(6 - i * 2, 6, 6)
                    glPopMatrix()
            elif self.creature_type == MELEE_CREATURE:
                glColor3f(0.8, 0.2, 0.2)
                glutSolidCube(10)
            else:
                glColor3f(0.7, 0.7, 0.4)
                glutSolidSphere(6, 8, 8)
                
            glPopMatrix()

def spawn_new_enemies():
    global active_enemies, bosses
    active_enemies = []
    bosses = []
    
    for i in range(MAX_ENEMIES):
        x = random.randint(-400, 400)
        y = random.randint(-400, 400)
        
        if i < 2:
            active_enemies.append(EnemyCreature(x, y, 30, MELEE_CREATURE))
        elif i < 4:
            active_enemies.append(EnemyCreature(x, y, 30, RANGED_ATTACKER))
        else:
            bosses.append(EnemyCreature(x, y, 50, FINAL_BOSS))

def update_all_enemies(delta_time):
    global player_health
    
    for creature in active_enemies[:]:  # Use slice to avoid modification during iteration
        if not creature.is_dead:
            creature.update(delta_time)
            distance = math.sqrt((creature.x - player_x)**2 + (creature.y - player_y)**2)
            if distance < creature.collision_radius + 40:
                player_health = max(0, player_health - 1)
        else:
            active_enemies.remove(creature)  # Remove dead enemies
            
    for boss in bosses[:]:  # Use slice to avoid modification during iteration
        if not boss.is_dead:
            boss.update(delta_time)
            distance = math.sqrt((boss.x - player_x)**2 + (boss.y - player_y)**2)
            if distance < boss.collision_radius + 40:
                player_health = max(0, player_health - 2)
        else:
            bosses.remove(boss)  # Remove dead bosses

def render_all_enemies():
    for creature in active_enemies:
        if not creature.is_dead:
            creature.render_creature()
    for boss in bosses:
        if not boss.is_dead:
            boss.render_creature()

def get_all_enemies():
    return active_enemies + bosses

def deal_damage_at_location(x, y, damage_amount, splash_effect_radius=50):
    for creature in active_enemies + bosses:
        if creature.is_dead:
            continue
        distance = math.sqrt((creature.x - x)**2 + (creature.y - y)**2)
        if distance <= splash_effect_radius:
            creature.take_damage(damage_amount)

# Add enemy collision detection for bullets
def check_bullet_enemy_collision():
    """Check if bullets hit enemies and deal damage"""
    global bullets
    
    for bullet_index, bullet in enumerate(bullets[:]):
        bullet_x, bullet_y, bullet_z = bullet[0], bullet[1], bullet[2]
        
        for enemy in get_all_enemies():
            if enemy.is_dead:
                continue
                
            # Calculate distance between bullet and enemy
            dx = bullet_x - enemy.x
            dy = bullet_y - enemy.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check collision
            if distance < (enemy.collision_radius + bullet_size):
                # Hit detected!
                enemy.take_damage(30)  # Deal 30 damage
                bullets.remove(bullet)  # Remove the bullet
                print(f"Enemy hit! Health: {enemy.current_health}")
                break  # Exit inner loop since bullet is removed

def specialKeyListener(key, x, y):
    """
    Handle special keys (arrow keys) for player rotation.
    """
    global player_rotation
    
    if key == GLUT_KEY_LEFT:  # Rotate left
        player_rotation += 10
    elif key == GLUT_KEY_RIGHT:  # Rotate right
        player_rotation -= 10
    
    # Keep rotation within 0-360 degrees
    player_rotation = player_rotation % 360
    
    glutPostRedisplay()  # Redraw the scene

# Add frame timing
last_time = time.time()

def idle():
    """
    Idle function that runs continuously
    """
    global day_night_cycle, last_time
    
    # Calculate delta time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    
    # Update day/night cycle
    day_night_cycle = (day_night_cycle + 0.0005) % 1.0

    # Update bullets
    update_bullets()
    
    # Check bullet-enemy collisions
    check_bullet_enemy_collision()
    
    # Update sword swing animation
    update_sword_swing()
    check_sword_enemy_collision()
    
    # Update collectibles
    update_collectibles()
    
    # Check for collectible collisions
    check_collectible_collision()
    
    # Update enemies
    update_all_enemies(delta_time)
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Clear color and depth buffers
    day_color = 0.5 + 0.3 * math.sin(day_night_cycle * 2 * math.pi)
    glClearColor(day_color * 0.2, day_color * 0.2, day_color * 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw a random points
    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    # Draw the grid (game floor)
    glBegin(GL_QUADS)
    
    glColor3f(1, 1, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)

    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(0, -GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(GRID_LENGTH, 0, 0)

    glColor3f(0.7, 0.5, 0.95)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -GRID_LENGTH, 0)

    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glEnd()

    # Draw the obstacles
    draw_obstacles()

    # Draw the character
    draw_player()

    # Draw bullets
    draw_all_bullets()

    # Draw collectibles
    draw_all_collectibles()

    # Draw enemies
    render_all_enemies()

    # Display game info text at a fixed screen position
    draw_text(600, 620, f"Weapon: {current_weapon}")
    draw_text(600, 600, f"Health: {player_health}/{max_health}")
    draw_text(600, 580, f"Speed: {movement_speed:.1f}")

    # Enemy info
    draw_text(50, 200, f"Enemies: {len(active_enemies)}")
    draw_text(50, 180, f"Bosses: {len(bosses)}")

    # Collectible legend
    draw_text(50, 100, f"Collectibles:")
    draw_text(50, 80, f"Green Cube = +25 Health")
    draw_text(50, 60, f"Red Cube = +5 Speed")

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)  # Register special key listener for arrow keys
    glutMouseFunc(mouseListener)  # Register mouse listener for shooting/slashing
    glutIdleFunc(idle)  # Register the idle function to update bullets and effects

    # Enable OpenGL features
    glEnable(GL_DEPTH_TEST)
    
    # Initialize some collectibles
    for _ in range(3):
        spawn_collectible()
    
    # Spawn initial enemies
    spawn_new_enemies()

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()

