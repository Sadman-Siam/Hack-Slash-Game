# CSE423 LAB PROJECT (A 3D Hack And Slash GAME)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


camera_pos = (0,500,500)
camera_mode = "third_person"

fovY = 120
GRID_LENGTH = 600

# Character properties
character_pos = [0, 0, 50]  # x, y, z position (starting at center, slightly above ground)
character_size = 30
character_speed = 20

# Player position variables for the draw_player function
player_x = 0
player_y = 0 
player_z = 50
movement_speed = 20.0
# Player rotation and weapon variables
player_rotation = 0  # Player's rotation angle in degrees
current_weapon = "gun"  # Current weapon: "gun" or "sword"

# Bullet system
bullets = []  # List to store active bullets
bullet_speed = 15.0
bullet_size = 5

#Sword
sword_slash = False

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
        draw_sword()
    glPopMatrix()

def draw_sword(sword_angle =90, x=0, y=1, z=0):
    glPushMatrix()
    
    glColor3f(1, 0, 0)  
    glTranslatef(-100, 100, 90)
    glRotatef(sword_angle, x, y, z)
    gluCylinder(gluNewQuadric(), 20, 1, 250, 20, 20)
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

def shoot_bullet():
    global bullets, player_x, player_y, player_z, player_rotation, bullets_fired, max_bullets, game_over, is_dying

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
    global slash_active, slash_timer, sword_swing_active, sword_swing_timer, sword_swing_angle
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_weapon == "gun":
            shoot_bullet()
        elif current_weapon == "sword":
            draw_sword(sword_angle =90, x=0, y=1, z=0)
            draw_sword(sword_angle =45, x=0, y=1, z=0)
            draw_sword(sword_angle =0, x=0, y=1, z=0)

    glutPostRedisplay()


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 1500) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    gluLookAt(x, y, z,  # Camera position
              0, 0, 0,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)


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
        
        if -GRID_LENGTH + 50 < new_x < GRID_LENGTH - 50:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 50 < new_y < GRID_LENGTH - 50:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b's' or key == b'S':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.sin(angle_rad)
        new_y = player_y + movement_speed * math.cos(angle_rad)
        
        if -GRID_LENGTH + 50 < new_x < GRID_LENGTH - 50:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 50 < new_y < GRID_LENGTH - 50:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'a' or key == b'A':
        angle_rad = math.radians(player_rotation)
        new_x = player_x + movement_speed * math.cos(angle_rad)
        new_y = player_y + movement_speed * math.sin(angle_rad)
        
        if -GRID_LENGTH + 50 < new_x < GRID_LENGTH - 50:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 50 < new_y < GRID_LENGTH - 50:
            player_y = new_y
            character_pos[1] = new_y
            
    elif key == b'd' or key == b'D':
        angle_rad = math.radians(player_rotation)
        new_x = player_x - movement_speed * math.cos(angle_rad)
        new_y = player_y - movement_speed * math.sin(angle_rad)
        
        if -GRID_LENGTH + 50 < new_x < GRID_LENGTH - 50:
            player_x = new_x
            character_pos[0] = new_x
        if -GRID_LENGTH + 50 < new_y < GRID_LENGTH - 50:
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
    Idle function that runs continuously:
    - Updates bullets, slash effects, and sword swing animation
    - Triggers screen redraw for real-time updates.
    """
    global slash_active, slash_timer, sword_swing_active, sword_swing_timer
    
    # Update bullets
    update_bullets()
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
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

    # Draw the character
    draw_player()

    # Draw bullets
    draw_all_bullets()


    # Display game info text at a fixed screen position
    draw_text(600, 660, f"Position: ({character_pos[0]:.0f}, {character_pos[1]:.0f})")
    draw_text(600, 640, f"Rotation: {player_rotation:.0f}°")
    draw_text(600, 620, f"Weapon: {current_weapon.upper()}")
    draw_text(600, 600, f"Bullets: {len(bullets)}")
    draw_text(600, 580, f"Controls:")
    draw_text(600, 560, f"W - Move Forward")
    draw_text(600, 540, f"S - Move Backward")
    draw_text(600, 520, f"A - Strafe Left")
    draw_text(600, 500, f"D - Strafe Right")
    draw_text(600, 480, f"Arrow Keys - Rotate")
    draw_text(600, 460, f"Q - Switch Weapon")
    draw_text(600, 440, f"Left Click - Shoot/Slash")
    draw_text(600, 420, f"Right Click - Sword Swing")


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

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
