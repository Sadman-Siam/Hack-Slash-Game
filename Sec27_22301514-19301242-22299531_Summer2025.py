# CSE423 LAB PROJECT (A 3D Hack And Slash GAME)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


camera_pos = (0,500,500)
camera_mode = "third_person"

fovY = 120
GRID_LENGTH = 2000

#Day/Night
day_night_cycle = 0  # 0 to 1, where 0 is day, 1 is night

# Character properties
character_pos = [0, 0, 50]  # x, y, z position (starting at center, slightly above ground)
character_size = 30
character_speed = 20

# Player position variables for the draw_player function
player_x = 0
player_y = 0 
player_z = 50
movement_speed = 20.0
base_movement_speed = 20.0  # Base speed to reset to
max_movement_speed = 50.0   # Maximum speed limit

# Player stats
player_health = 100
max_health = 200

# Player rotation and weapon variables
player_rotation = 0  # Player's rotation angle in degrees
current_weapon = "gun"  # Current weapon: "gun" or "sword"

# Bullet system
bullets = []  # List to store active bullets
bullet_speed = 15.0
bullet_size = 5

# Sword
sword_swing_active = False
sword_swing_timer = 0
sword_swing_angle = 90
sword_swing_speed = 8

# Collectibles system
collectibles = []  # List to store collectible cubes
collectible_size = 25
max_collectibles = 2  # Maximum number of collectibles on map
spawn_timer = 0
spawn_interval = 300  # Frames between spawn attempts (5 seconds)

# Map obstacles for each level
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

# Add level tracking
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
    """Spawn a random collectible on the map"""
    global collectibles
    
    if len(collectibles) < max_collectibles:
        # Choose random position within grid bounds
        x = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        y = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        z = collectible_size  # Place on ground level
        
        # Choose type: 'health' (green) or 'speed' (red)
        cube_type = random.choice(['health', 'speed'])
        
        # Store as [x, y, z, type]
        collectibles.append([x, y, z, cube_type])

def draw_collectible(x, y, z, cube_type):
    """Draw a simple collectible cube"""
    glPushMatrix()
    
    # Position the cube
    glTranslatef(x, y, z)
    
    # Set color based on type
    if cube_type == 'health':
        glColor3f(0, 1, 0)  # Green for health
    elif cube_type == 'speed':
        glColor3f(1, 0, 0)  # Red for speed
    
    # Draw the cube
    glutSolidCube(collectible_size)
    
    glPopMatrix()

def draw_all_collectibles():
    """Draw all collectibles on the map"""
    for collectible in collectibles:
        x, y, z, cube_type, rotation = collectible
        draw_collectible(x, y, z, cube_type, rotation)

def update_collectibles():
    """Update collectible animations and spawning"""
    global collectibles, spawn_timer
    # Handle spawning
    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_collectible()
        spawn_timer = 0

def check_collectible_collision():
    """Check if player collides with any collectibles"""
    global collectibles, player_health, movement_speed
    
    player_collision_radius = 60  # Player collision radius
    
    for i, collectible in enumerate(collectibles):
        x, y, z, cube_type, rotation = collectible
        
        # Calculate distance between player and collectible
        dx = player_x - x
        dy = player_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check collision
        if distance < (player_collision_radius + collectible_size/2):
            # Collision detected!
            if cube_type == 'health':
                # Add health
                health_gain = 25
                player_health = min(player_health + health_gain, max_health)
                print(f"Health collected! +{health_gain} HP (Current: {player_health})")
                
            elif cube_type == 'speed':
                # Increase movement speed
                speed_boost = 5.0
                movement_speed = min(movement_speed + speed_boost, max_movement_speed)
                print(f"Speed boost collected! +{speed_boost} speed (Current: {movement_speed:.1f})")
            
            # Remove the collected cube
            collectibles.pop(i)
            break  # Exit loop to avoid index issues

def draw_text(x, y, text):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        except:
            # Fallback: skip text rendering if font is not available
            pass
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    """Draw player with animated sword"""
    glPushMatrix()
    
    # Apply position and rotation transformations
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_rotation, 0, 0, 1)  # Rotate around Z-axis
    
    # Draw player body (green cube)
    glColor3f(0.5, 1, 0.5)
    glutSolidCube(80)
    
    # Draw player head (black sphere)
    glTranslatef(0, 0, 80)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 30, 10, 10)
    
    # Draw arms (flesh colored cylinders)
    glColor3f(1, .9, .8)
    glTranslatef(50, -30, -70)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)   
    glTranslatef(-100, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)  
    
    # Draw legs (blue cylinders)
    glColor3f(0, 0, 1)
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 10, 100)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    glTranslatef(100, 0, 0)
    gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    
    # Draw weapon based on current selection
    glColor3f(0.5, 0.5, 0.5)
    glRotatef(-90, 1, 0, 0)
    
    if current_weapon == "gun":
        # Draw gun (gray cylinder)
        glTranslatef(-110, 70, 80)
        gluCylinder(gluNewQuadric(), 30, 15, 100, 10, 10)
    elif current_weapon == "sword":
        # Use the animated sword angle if swinging, otherwise use default
        current_angle = sword_swing_angle if sword_swing_active else 90
        # Debug output to verify angle changes
        if sword_swing_active:
            print(f"Drawing sword at angle: {current_angle:.1f}")
        draw_sword(current_angle, 0, 1, 0)
    
    glPopMatrix()

def draw_sword(sword_angle=90, x=0, y=1, z=0):
    """Draw sword with proper positioning and rotation"""
    glPushMatrix()
    
    # Sword color (red)
    glColor3f(1, 0, 0)  
    
    # Position the sword relative to the player's hand
    glTranslatef(-100, 100, 90)
    
    # Apply the rotation - this is the key part that makes it swing
    glRotatef(sword_angle, x, y, z)
    
    # Draw the sword as a tapered cylinder (blade)
    gluCylinder(gluNewQuadric(), 20, 1, 250, 20, 20)
    
    # Optional: Draw sword handle
    glColor3f(0.4, 0.2, 0.1)  # Brown handle
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
    """Update sword swing animation with debug output"""
    global sword_swing_active, sword_swing_timer, sword_swing_angle
    
    if sword_swing_active:
        sword_swing_timer += 1
        
        # Debug output to see if function is being called
        print(f"Swing timer: {sword_swing_timer}, Angle: {sword_swing_angle:.1f}")
        
        # Swing duration (frames)
        swing_duration = 30  # Made it a bit longer to see the motion better
        
        if sword_swing_timer <= swing_duration:
            # Calculate swing progress (0 to 1)
            progress = sword_swing_timer / swing_duration
            
            # Create a smooth swing motion - swinging around Y-axis
            # From 90° (vertical) to -45° (diagonal down) and back
            if progress <= 0.5:
                # First half: swing down from 90° to -45°
                sword_swing_angle = 90 - (135 * (progress * 2))
            else:
                # Second half: swing back up from -45° to 90°
                sword_swing_angle = -45 + (135 * ((progress - 0.5) * 2))
        else:
            # End the swing
            print("Swing completed!")
            sword_swing_active = False
            sword_swing_timer = 0
            sword_swing_angle = 90  # Reset to default position

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
    """Handle mouse clicks for shooting and slashing"""
    global sword_swing_active, sword_swing_timer, sword_swing_angle
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_weapon == "gun":
            shoot_bullet()
        elif current_weapon == "sword":
            # Simple slash attack
            print("Slash attack!")
    
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if current_weapon == "sword":
            # Start sword swing animation
            print("Starting sword swing animation!")
            sword_swing_active = True
            sword_swing_timer = 0
            sword_swing_angle = 90
        else:
            print("Right click detected, but weapon is:", current_weapon)

    glutPostRedisplay()


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 5000) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Third-person camera that follows the player
    camera_distance = 300
    camera_height = 150
    
    # Calculate camera position based on player rotation
    angle_rad = math.radians(player_rotation)
    cam_x = player_x - camera_distance * math.cos(angle_rad)
    cam_y = player_y - camera_distance * math.sin(angle_rad)
    cam_z = player_z + camera_height
    
    # Look at the player
    gluLookAt(cam_x, cam_y, cam_z,
              player_x, player_y, player_z + 50,
              0, 0, 1)


def keyboardListener(key, x, y):
    """
    Handle keyboard input for character movement, rotation, and weapon switching.
    WASD keys control character movement relative to player's facing direction.
    Q key switches weapons.
    """
    global character_pos, player_x, player_y, player_z, player_rotation, current_weapon
    
    if key == b'w' or key == b'W':
        angle_rad = math.radians(player_rotation)
        new_x = player_x + movement_speed * math.sin(angle_rad)
        new_y = player_y - movement_speed * math.cos(angle_rad)
        
        if -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b's' or key == b'S':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.sin(angle_rad)
        new_y = player_y + movement_speed * math.cos(angle_rad)
        
        if -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'a' or key == b'A':
        angle_rad = math.radians(player_rotation)
        new_x = player_x + movement_speed * math.cos(angle_rad)
        new_y = player_y + movement_speed * math.sin(angle_rad)
        
        if -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'd' or key == b'D':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.cos(angle_rad)
        new_y = player_y - movement_speed * math.sin(angle_rad)
        
        if -GRID_LENGTH + 100 < new_x < GRID_LENGTH - 100:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 100 < new_y < GRID_LENGTH - 100:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'q' or key == b'Q':  # Switch weapon
        if current_weapon == "gun":
            current_weapon = "sword"
        else:
            current_weapon = "gun"
    
    glutPostRedisplay()  # Redraw the scene


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


def idle():
    """
    Idle function that runs continuously
    """
    # Update day/night cycle
    day_night_cycle = (day_night_cycle + 0.0005) % 1.0

    # Update bullets
    update_bullets()
    
    # Update sword swing animation
    update_sword_swing()
    
    # Update collectibles
    update_collectibles()
    
    # Check for collectible collisions
    check_collectible_collision()
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
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

    # Display game info text at a fixed screen position
    draw_text(600, 660, f"Position: ({character_pos[0]:.0f}, {character_pos[1]:.0f})")
    draw_text(600, 640, f"Rotation: {player_rotation:.0f}°")
    draw_text(600, 620, f"Weapon: {current_weapon.upper()}")
    draw_text(600, 600, f"Health: {player_health}/{max_health}")
    draw_text(600, 580, f"Speed: {movement_speed:.1f}")
    draw_text(600, 560, f"Collectibles: {len(collectibles)}")
    draw_text(600, 540, f"Controls:")
    draw_text(600, 520, f"W - Move Forward")
    draw_text(600, 500, f"S - Move Backward")
    draw_text(600, 480, f"A - Strafe Left")
    draw_text(600, 460, f"D - Strafe Right")
    draw_text(600, 440, f"Arrow Keys - Rotate")
    draw_text(600, 420, f"Q - Switch Weapon")
    draw_text(600, 400, f"Left Click - Shoot/Slash")
    draw_text(600, 380, f"Right Click - Sword Swing")

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

    # Initialize some collectibles
    for _ in range(3):
        spawn_collectible()

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()









# Srizon enemy part updated
