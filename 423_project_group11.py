from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

WIDTH, HEIGHT = 1000, 800

STATE_START = 0
STATE_GAME = 1
game_state = STATE_START
STATE_GAME_OVER = 2
STATE_GAME_WIN = 3
# Cheat Mode
cheat_mode = False

# Camera mode
CAMERA_TPP = 0
CAMERA_FPP = 1
camera_mode = CAMERA_TPP

fovY = 120
camera_angle = 0
camera_distance = 700
camera_height = 450

MIN_ZOOM = 120
MAX_ZOOM = 1200
MIN_HEIGHT = 120
MAX_HEIGHT = 600

shepherd_pos = [0, 0, 60]
shepherd_rotation = 0
shepherd_speed = 2.0
shepherd_rotation_speed = 3.0

# Movement keys state
keys_pressed = {b'w': False, b's': False, b'a': False, b'd': False}

# Shepherd inventory
wood_count = 0
wood_types = {'small': 0, 'medium': 0, 'large': 0}  # 3 wood types
# Stone combat system
stone_count = 20  # Start with 20 stones
stones_on_ground = []  # Stones available to collect
projectiles = []  # Active thrown stones
MAX_STONES_ON_GROUND = 2
STONE_SPAWN_TIMER = 0
STONE_SPAWN_INTERVAL = 600  # 10 seconds at night (60 fps * 10)
STONE_THROW_COOLDOWN = 0
STONE_THROW_COOLDOWN_TIME = 30  # 0.5 seconds between throws
STONE_SPEED = 8.0
STONE_RANGE = 500  # Maximum distance before stone disappears
STONE_COLLECTION_RANGE = 40  # How close to collect
# Whistle system
whistle_active = False
WHISTLE_COOLDOWN = 0
WHISTLE_COOLDOWN_TIME = 180  # 3 seconds between whistles
WHISTLE_RANGE = 400  # Range within which sheep respond to whistle
WHISTLE_DURATION = 1200       # 20 seconds (60 FPS × 20)
whistle_timer = 0
# =============================
# Bonfire System
# =============================
# =============================
# Bonfire System - UPDATED
# =============================
bonfire_level = 0
bonfire_fuel = 0
# NEW: Different fuel durations based on wood type used
bonfire_max_fuel = {
    'small': 600,    # 10 seconds (5 small woods)
    'medium': 1200,  # 20 seconds (7 medium woods)
    'large': 2400    # 40 seconds (10 large woods)
}
bonfire_decay_rate = 1
# NEW: Different ranges based on bonfire type
bonfire_range = {
    'small': 200,   # 30% of clearing radius (~200)
    'medium': 250,
    'large': 300
}
bonfire_wood_requirements = {
    'small': 15,
    'medium': 12,
    'large': 8
}
bonfire_type = None  # Tracks which wood type was used
BONFIRE_POS = [0, 0, 0]

def build_bonfire():
    """Build bonfire - prioritizes large > medium > small"""
    global bonfire_level, bonfire_fuel, wood_types, wood_count, bonfire_type
    
    dx = BONFIRE_POS[0] - shepherd_pos[0]
    dy = BONFIRE_POS[1] - shepherd_pos[1]
    dist = math.sqrt(dx**2 + dy**2)
    
    if dist > 100:
        return False
    
    # Priority 1: Large bonfire (10 large woods)
    if wood_types['large'] >= bonfire_wood_requirements['large']:
        wood_types['large'] -= bonfire_wood_requirements['large']
        wood_count -= bonfire_wood_requirements['large']
        bonfire_level = 3
        bonfire_type = 'large'
        bonfire_fuel = bonfire_max_fuel['large']
        return True
    
    # Priority 2: Medium bonfire (7 medium woods)
    elif wood_types['medium'] >= bonfire_wood_requirements['medium']:
        wood_types['medium'] -= bonfire_wood_requirements['medium']
        wood_count -= bonfire_wood_requirements['medium']
        bonfire_level = 2
        bonfire_type = 'medium'
        bonfire_fuel = bonfire_max_fuel['medium']
        return True
    
    # Priority 3: Small bonfire (5 small woods)
    elif wood_types['small'] >= bonfire_wood_requirements['small']:
        wood_types['small'] -= bonfire_wood_requirements['small']
        wood_count -= bonfire_wood_requirements['small']
        bonfire_level = 1
        bonfire_type = 'small'
        bonfire_fuel = bonfire_max_fuel['small']
        return True
    
    # If bonfire exists, add fuel
    elif bonfire_level > 0 and bonfire_type:
        if wood_types['large'] > 0:
            wood_types['large'] -= 1
            wood_count -= 1
            bonfire_fuel = min(bonfire_fuel + 400, bonfire_max_fuel[bonfire_type])
            return True
        elif wood_types['medium'] > 0:
            wood_types['medium'] -= 1
            wood_count -= 1
            bonfire_fuel = min(bonfire_fuel + 200, bonfire_max_fuel[bonfire_type])
            return True
        elif wood_types['small'] > 0:
            wood_types['small'] -= 1
            wood_count -= 1
            bonfire_fuel = min(bonfire_fuel + 100, bonfire_max_fuel[bonfire_type])
            return True
    
    return False

def update_bonfire():
    """Update bonfire fuel and level"""
    global bonfire_level, bonfire_fuel, bonfire_type
    
    if bonfire_level > 0:
        if not cheat_mode or is_day:
          bonfire_fuel -= bonfire_decay_rate


        if bonfire_fuel <= 0:
            bonfire_level = 0
            bonfire_fuel = 0
            bonfire_type = None
def draw_bonfire():
    """Draw bonfire with size based on type"""
    glPushMatrix()
    glTranslatef(BONFIRE_POS[0], BONFIRE_POS[1], BONFIRE_POS[2])
    
    # Fire pit base
    if bonfire_level == 0:
        glColor3f(0.4, 0.3, 0.2)
    else:
        glColor3f(0.5, 0.2, 0.1)
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 1)
    for i in range(21):
        angle = i * 2 * math.pi / 20
        glVertex3f(math.cos(angle) * 35, math.sin(angle) * 35, 1)
    glEnd()
    glColor3f(0.5, 0.5, 0.5)
    for i in range(8):
        angle = i * 2 * math.pi / 8
        glPushMatrix()
        glTranslatef(math.cos(angle) * 38, math.sin(angle) * 38, 5)
        glutSolidSphere(5, 8, 8)
        glPopMatrix()
    
    if bonfire_level == 0:
        glPopMatrix()
        return
    # Size multipliers based on bonfire type
    size_mult = {'small': 1.0, 'medium': 1.5, 'large': 2.0}
    mult = size_mult.get(bonfire_type, 1.0)
    
    # Fire base (logs) - more logs for bigger fires
    glColor3f(0.3, 0.15, 0.05)
    log_count = 4 if bonfire_type == 'small' else (6 if bonfire_type == 'medium' else 8)
    for i in range(log_count):
        glPushMatrix()
        glRotatef(i * (360 / log_count), 0, 0, 1)
        glTranslatef(10 * mult, 0, 5)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 3 * mult, 3 * mult, 20 * mult, 6, 2)
        glPopMatrix()
    
    # Fire flames
    fire_height = 30 * mult
    fire_radius = 15 * mult
    
    glColor3f(1.0, 0.3, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    gluCylinder(gluNewQuadric(), fire_radius, 2, fire_height, 8, 4)
    glPopMatrix()
    
    glColor3f(1.0, 0.9, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    gluCylinder(gluNewQuadric(), fire_radius * 0.5, 1, fire_height * 0.7, 6, 3)
    glPopMatrix()
    
    glPopMatrix()
def is_wolf_repelled(wolf_pos):
    """Check if wolf is within bonfire range"""
    if bonfire_level == 0 or not bonfire_type:
        return False
    
    dx = wolf_pos[0] - BONFIRE_POS[0]
    dy = wolf_pos[1] - BONFIRE_POS[1]
    dist = math.sqrt(dx**2 + dy**2)
    
    return dist < bonfire_range[bonfire_type]

# =============================
# Wood Chopping System
# =============================
wood_zones = []
NUM_WOOD_ZONES = 3  # Only 3 wood points
CHOP_RANGE = 60  # Increased detection range
CHOP_COOLDOWN = 60  # 1 second between chops (reduced from 120)

class WoodZone:
    def __init__(self, x, y, wood_type):
        self.pos = [x, y]
        self.wood_type = wood_type
        self.wood_available = True
        self.respawn_timer = 0
        # Different respawn times based on wood type
        respawn_times = {
            'small': 30,    # 0.5 seconds (fast)
            'medium': 90,   # 1.5 seconds (medium)
            'large': 180    # 3 seconds (slow)
        }
        self.respawn_time = respawn_times[wood_type]
        
    def chop(self):
        if self.wood_available:
            self.wood_available = False
            self.respawn_timer = self.respawn_time
            return self.wood_type
        return None
    
    def update(self):
        if not self.wood_available:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.wood_available = True
    
    def draw(self):
        """Draw wood zone with visual differences"""
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        
        # Different colors for different wood types
        if self.wood_available:
            if self.wood_type == 'small':
                glColor3f(0.7, 0.6, 0.5)  # Light brown
            elif self.wood_type == 'medium':
                glColor3f(0.5, 0.4, 0.1)  # Medium brown
            else:  # large
                glColor3f(0.4, 0.24, 0.09)  # Dark brown
        else:
            glColor3f(0.3, 0.3, 0.3)
        
        # Draw circle
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 1)
        for i in range(21):
            angle = i * 2 * math.pi / 20
            glVertex3f(math.cos(angle) * 50, math.sin(angle) * 50, 1)
        glEnd()
        
        # Draw log piles with different sizes
        if self.wood_available:
            pile_size = 5 if self.wood_type == 'small' else (6 if self.wood_type == 'medium' else 7)
            log_radius = 4 if self.wood_type == 'small' else (5 if self.wood_type == 'medium' else 6)
            
            for stack_x in [-20, 0, 20]:
                for i in range(pile_size):
                    glPushMatrix()
                    glTranslatef(stack_x, -15 + i * 7, 5 + i * 6)
                    glRotatef(90, 0, 1, 0)
                    glColor3f(0.5, 0.3, 0.1)
                    gluCylinder(gluNewQuadric(), log_radius, log_radius, 25, 8, 2)
                    glPopMatrix()
        
        glPopMatrix()
# =============================
# Clouds
clouds = []
NUM_CLOUDS = 8
CLOUD_HEIGHT = 450
CLOUD_SPEED = 0.15

# =============================
# Stars (Night Sky)
# =============================
stars = []
NUM_STARS = 120
STAR_HEIGHT = 520


# =============================
# Stone System Classes
# =============================
class StoneOnGround:
    def __init__(self, x, y):
        self.pos = [x, y, 5]  # On ground level
        self.collected = False
    
    def draw(self):
        if not self.collected:
            glPushMatrix()
            glTranslatef(*self.pos)
            glColor3f(0.5, 0.5, 0.5)  # Gray stone
            glutSolidSphere(6, 8, 8)
            glPopMatrix()

class Projectile:
    def __init__(self, x, y, z, direction_x, direction_y):
        self.pos = [x, y, z]
        self.start_pos = [x, y, z]
        self.direction = [direction_x, direction_y, 0]
        self.speed = STONE_SPEED
        self.active = True
        self.distance_traveled = 0

    def update(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed

        dx = self.pos[0] - self.start_pos[0]
        dy = self.pos[1] - self.start_pos[1]
        self.distance_traveled = math.sqrt(dx**2 + dy**2)

        if self.distance_traveled > STONE_RANGE:
            self.active = False
    
    def check_collision(self, wolf):
        dx = self.pos[0] - wolf.pos[0]
        dy = self.pos[1] - wolf.pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        hit_radius = wolf.size * 1.2
        return dist < hit_radius

    def draw(self):
        if self.active:
            glPushMatrix()
            glTranslatef(*self.pos)
            glColor3f(0.4, 0.4, 0.4)
            glutSolidSphere(5, 8, 8)
            glPopMatrix()

def create_wood_zones():
    """Create 3 wood chopping zones"""
    global wood_zones
    wood_zones = []
    
    # Three positions: small (left), medium (right), large (bottom)
    positions = [
        (-280, 280, 'small'),    # NW - small wood
        (280, 280, 'medium'),    # NE - medium wood
        (0, -280, 'large')       # South - large wood
    ]
    
    for x, y, wood_type in positions:
        wood_zones.append(WoodZone(x, y, wood_type))

shepherd_chop_cooldown = 0

def try_chop_wood():
    """Try to chop wood from nearby zone"""
    global wood_count, wood_types, shepherd_chop_cooldown
    
    if shepherd_chop_cooldown > 0:
        return False
    
    # Check if near any wood zone
    for zone in wood_zones:
        dx = zone.pos[0] - shepherd_pos[0]
        dy = zone.pos[1] - shepherd_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < CHOP_RANGE:
            wood_type = zone.chop()
            if wood_type:
                wood_types[wood_type] += 1
                wood_count += 1
                shepherd_chop_cooldown = CHOP_COOLDOWN
                return True
    
    return False

def update_wood_zones():
    """Update all wood zones"""
    for zone in wood_zones:
        zone.update()

def draw_all_wood_zones():
    """Draw all wood zones"""
    for zone in wood_zones:
        zone.draw()

# =============================
# Stone Combat Functions
# =============================
def spawn_stone_on_ground():
    """Spawn a stone at random location in clearing"""
    global stones_on_ground
    
    if len(stones_on_ground) < MAX_STONES_ON_GROUND:
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(100, 500)  # Within clearing
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        stones_on_ground.append(StoneOnGround(x, y))

def update_stone_spawning():
    """Update stone spawn timer at night"""
    global STONE_SPAWN_TIMER
    
    if not is_day:  # Only spawn at night
        STONE_SPAWN_TIMER += 1
        if STONE_SPAWN_TIMER >= STONE_SPAWN_INTERVAL:
            spawn_stone_on_ground()
            STONE_SPAWN_TIMER = 0

def try_collect_stone():
    """Collect stone if shepherd is near"""
    global stone_count, stones_on_ground
    
    collected_any = False
    stones_to_remove = []
    
    for stone in stones_on_ground:
        if not stone.collected:
            dx = stone.pos[0] - shepherd_pos[0]
            dy = stone.pos[1] - shepherd_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < STONE_COLLECTION_RANGE:
                stone.collected = True
                stones_to_remove.append(stone)
                stone_count += 1
                collected_any = True
    
    # Remove collected stones after iteration
    for stone in stones_to_remove:
        if stone in stones_on_ground:
            stones_on_ground.remove(stone)
    
    return collected_any

def throw_stone():
    """Throw a stone in the direction shepherd is facing"""
    global stone_count, projectiles, STONE_THROW_COOLDOWN
    
    if stone_count <= 0 or STONE_THROW_COOLDOWN > 0:
        return False
    
    # Calculate throw direction based on shepherd rotation
    angle_rad = math.radians(shepherd_rotation + 90)
    dir_x = math.cos(angle_rad)
    dir_y = math.sin(angle_rad)
    
    # Normalize direction
    length = math.sqrt(dir_x**2 + dir_y**2)
    if length > 0:
        dir_x /= length
        dir_y /= length
    
    # Create projectile from shepherd's position (slightly elevated)
    proj = Projectile(shepherd_pos[0], shepherd_pos[1], shepherd_pos[2] + 20, dir_x, dir_y)
    projectiles.append(proj)
    
    if not cheat_mode or is_day:
        stone_count -= 1

    STONE_THROW_COOLDOWN = STONE_THROW_COOLDOWN_TIME
    return True

def update_projectiles():
    """Update all projectiles and check collisions"""
    global projectiles, wolves, alpha_wolf
    
    for proj in projectiles[:]:
        if not proj.active:
            projectiles.remove(proj)
            continue
        
        proj.update()
        
        # Check collision with all wolves
        for wolf in wolves[:]:
            if proj.check_collision(wolf):
                wolf.health -= 1
                proj.active = False
                
                # Wolf dies
                if wolf.health <= 0:
                    wolves.remove(wolf)
                    
                    # If alpha dies, make pack retreat
                    if wolf.is_alpha:
                        alpha_wolf = None
                        make_wolves_retreat()
                
                break  # Stone hit, stop checking

def make_wolves_retreat():
    """Make all wolves run away when alpha dies"""
    for wolf in wolves:
        wolf.retreating = True

def draw_all_stones():
    """Draw stones on ground"""
    for stone in stones_on_ground:
        stone.draw()

def draw_all_projectiles():
    """Draw flying stones"""
    for proj in projectiles:
        proj.draw()

# Add large wood generation
def get_large_wood_periodically():
    """Shepherd gets 1 large wood every 30 seconds during day"""
    global wood_types, wood_count
    if is_day and int(game_time) % 1800 == 0 and game_time > DAY_START:  # Every 30 seconds
        wood_types['large'] += 1
        wood_count += 1


# Day-Night Cycle
game_time = 0  # 0 to 1440 
time_speed = 0.3 
is_day = True
day_count = 0
nights_survived = 0
MINUTES_PER_DAY = 1440 
DAY_START = 360 
NIGHT_START = 1080 

# =============================
# Wolf Pack System - UPDATED
# =============================
wolves = []
alpha_wolf = None
NUM_WOLVES = 3  # Regular wolves (not counting alpha)
WOLF_SPEED = 0.6
WOLF_ATTACK_RANGE = 30
WOLF_SEPARATION_DISTANCE = 40  # Minimum distance between wolves
WOLF_HEALTH = 3  # Each wolf needs 3 stone hits to die

class Wolf:
    def __init__(self, x, y, is_alpha=False):
        self.pos = [x, y, 60]
        self.rot = 0
        self.speed = WOLF_SPEED * (1.3 if is_alpha else 1.0)
        self.is_alpha = is_alpha
        self.target_sheep = None
        self.health = 7 if is_alpha else WOLF_HEALTH  # CHANGED: Alpha has 7 health
        self.size = 24 if is_alpha else 18
        self.retreating = False  # ADD THIS LINE
        
    def get_separation_force(self, other_wolves):
        """Calculate separation force to avoid other wolves"""
        sep_force_x = 0
        sep_force_y = 0
        
        for other in other_wolves:
            if other is self:
                continue
            
            dx = self.pos[0] - other.pos[0]
            dy = self.pos[1] - other.pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            # If too close, push away
            if 0 < dist < WOLF_SEPARATION_DISTANCE:
                # Stronger repulsion when closer
                force = (WOLF_SEPARATION_DISTANCE - dist) / WOLF_SEPARATION_DISTANCE
                if dist > 0:
                    sep_force_x += (dx / dist) * force
                    sep_force_y += (dy / dist) * force
        
        return sep_force_x, sep_force_y
    
    def update(self, sheep_list, other_wolves, alpha_target_pos=None):
        """Wolf AI - alpha leads, pack follows"""
        
        if self.retreating:
        # Run away from center
            dx = self.pos[0]
            dy = self.pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.pos[0] += (dx / dist) * self.speed * 3  # Run fast
                self.pos[1] += (dy / dist) * self.speed * 3
                self.rot = math.degrees(math.atan2(dy, dx)) - 90
        
        # Remove wolf if far enough
            if dist > 1500:
                return "RETREAT_COMPLETE"
            return None
    
        if not sheep_list:
            return None
        # Check if repelled by bonfire
        if is_wolf_repelled(self.pos):
            # Run away from bonfire
            dx = self.pos[0] - BONFIRE_POS[0]
            dy = self.pos[1] - BONFIRE_POS[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.pos[0] += (dx / dist) * self.speed * 2  # Run faster
                self.pos[1] += (dy / dist) * self.speed * 2
                self.rot = math.degrees(math.atan2(dy, dx)) - 90
            return None
        
        target_x, target_y = 0, 0
        
        if self.is_alpha:
            # Alpha wolf: Find nearest sheep and move directly to it
            min_dist = float('inf')
            nearest_sheep = None
            for sheep in sheep_list:
                dx = sheep.pos[0] - self.pos[0]
                dy = sheep.pos[1] - self.pos[1]
                dist = math.sqrt(dx**2 + dy**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_sheep = sheep
            
            if nearest_sheep:
                self.target_sheep = nearest_sheep
                target_x = nearest_sheep.pos[0]
                target_y = nearest_sheep.pos[1]
        else:
            # Regular wolf: Follow alpha's target position
            if alpha_target_pos:
                target_x, target_y = alpha_target_pos
            else:
                # Fallback: target nearest sheep
                min_dist = float('inf')
                nearest_sheep = None
                for sheep in sheep_list:
                    dx = sheep.pos[0] - self.pos[0]
                    dy = sheep.pos[1] - self.pos[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_sheep = sheep
                
                if nearest_sheep:
                    target_x = nearest_sheep.pos[0]
                    target_y = nearest_sheep.pos[1]
        
        # Calculate direction to target
        dx = target_x - self.pos[0]
        dy = target_y - self.pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            # Normalize direction
            dir_x = dx / dist
            dir_y = dy / dist
            
            # Get separation force from other wolves
            sep_x, sep_y = self.get_separation_force(other_wolves)
            
            # Combine forces (target direction + separation)
            final_x = dir_x + sep_x * 0.5  # Separation has 50% weight
            final_y = dir_y + sep_y * 0.5
            
            # Normalize final direction
            final_dist = math.sqrt(final_x**2 + final_y**2)
            if final_dist > 0:
                final_x /= final_dist
                final_y /= final_dist
            
            # Move in final direction
            self.pos[0] += final_x * self.speed
            self.pos[1] += final_y * self.speed
            
            # Update rotation to face movement direction
            self.rot = math.degrees(math.atan2(final_y, final_x)) - 90
        
        # Check for collision with sheep
        for sheep in sheep_list:
            dx = sheep.pos[0] - self.pos[0]
            dy = sheep.pos[1] - self.pos[1]
            collision_dist = math.sqrt(dx**2 + dy**2)
            
            if collision_dist < WOLF_ATTACK_RANGE:
                return sheep  # Signal to remove this sheep
        
        return None
    
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.rot, 0, 0, 1)
        
        # Body color based on type
        if self.is_alpha:
            glColor3f(0.5, 0.5, 0.5)  # Gray for alpha
        else:
            glColor3f(0.1, 0.1, 0.1)  # Black for regular wolves
        
        # Body
        glPushMatrix()
        glScalef(1.3, 0.9, 0.8)
        glutSolidSphere(self.size, 12, 12)
        glPopMatrix()
        
        # Head
        head_size = self.size * 0.55
        glPushMatrix()
        if self.is_alpha:
            glColor3f(0.45, 0.45, 0.45)  # Slightly darker gray for head
        else:
            glColor3f(0.05, 0.05, 0.05)  # Very dark for regular wolf head
        glTranslatef(self.size * 1.1, 0, 5)
        glScalef(0.8, 0.7, 0.7)
        glutSolidSphere(head_size, 10, 10)
        glPopMatrix()
        
        # Legs
        leg_height = self.size * 1.4
        leg_radius = self.size * 0.11
        if self.is_alpha:
            glColor3f(0.4, 0.4, 0.4)
        else:
            glColor3f(0.08, 0.08, 0.08)
        
        leg_offset = self.size * 0.44
        for lx in [-leg_offset, leg_offset]:
            for ly in [-leg_offset * 0.75, leg_offset * 0.75]:
                glPushMatrix()
                glTranslatef(lx, ly, -leg_height)
                gluCylinder(gluNewQuadric(), leg_radius, leg_radius * 0.75, leg_height, 6, 4)
                glPopMatrix()
        
        # Red eyes for alpha
        if self.is_alpha:
            glColor3f(1.0, 0.0, 0.0)
            eye_size = self.size * 0.08
            eye_forward = self.size * 1.4
            glPushMatrix()
            glTranslatef(eye_forward, 3, 8)
            glutSolidSphere(eye_size, 6, 6)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(eye_forward, -3, 8)
            glutSolidSphere(eye_size, 6, 6)
            glPopMatrix()
        
        glPopMatrix()

def draw_large_ground():
    glColor3f(0, 0.4, 0.3)  # Dark green
    glBegin(GL_QUADS)
    glVertex3f(-2000, -2000, -2)
    glVertex3f(2000, -2000, -2)
    glVertex3f(2000, 2000, -2)
    glVertex3f(-2000, 2000, -2)
    glEnd()

def spawn_wolves():
    """Spawn wolves at night from far end of forest"""
    global wolves, alpha_wolf
    wolves = []
    alpha_wolf = None
    
    # Spawn wolves at random positions on the outer edge of forest
    # between opening_radius and outer_radius (far edge)
    
    # Spawn alpha wolf first
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(900, 1100)  # Far edge of forest
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    alpha_wolf = Wolf(x, y, is_alpha=True)
    wolves.append(alpha_wolf)
    
    # Spawn regular wolves around alpha (spread around the edge)
    for i in range(NUM_WOLVES):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(900, 1100)  # Far edge
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        wolves.append(Wolf(x, y, is_alpha=False))

def update_wolves():
    """Update all wolves - alpha leads, pack follows"""
    global sheeps, alpha_wolf, wolves
    
    if not wolves:
        return
    
    sheep_to_remove = []
    wolves_to_remove = []
    
    # Get alpha's target position for pack to follow
    alpha_target_pos = None
    if alpha_wolf and alpha_wolf.target_sheep:
        alpha_target_pos = (alpha_wolf.target_sheep.pos[0], alpha_wolf.target_sheep.pos[1])
    
    # Update each wolf
    for wolf in wolves:
        result = wolf.update(sheeps, wolves, alpha_target_pos)
        
        if result == "RETREAT_COMPLETE":
            wolves_to_remove.append(wolf)
        elif result and result not in sheep_to_remove:
            sheep_to_remove.append(result)
    
    # Remove attacked sheep
    for sheep in sheep_to_remove:
        if sheep in sheeps:
            sheeps.remove(sheep)
    
    # Remove retreated wolves
    for wolf in wolves_to_remove:
        if wolf in wolves:
            wolves.remove(wolf)

def draw_all_wolves():
    for wolf in wolves:
        wolf.draw()

# =============================
# Sheep System with AI
# =============================
sheeps = []
NUM_SHEEP = 5

class Sheep:
    def __init__(self, x, y):
        self.pos = [x, y, 60]
        self.rot = random.uniform(0, 360)
        self.target_rot = self.rot
        self.speed = 0.5  # Normal speed
        self.base_speed = 0.5
        self.panic_speed = 1.5  # Faster when panicked
        self.wander_timer = 0
        self.wander_interval = random.randint(60, 180)
        # NEW panic and follow attributes
        self.is_panicked = False
        self.is_following_shepherd = False
        self.panic_direction = random.uniform(0, 360)
    def get_separation_force(self, other_sheep_list):
        """Calculate force to avoid other sheep"""
        sep_x = 0
        sep_y = 0
        SEPARATION_DIST = 40
    
        for other in other_sheep_list:
            if other is self:
                continue
        
            dx = self.pos[0] - other.pos[0]
            dy = self.pos[1] - other.pos[1]
            dist = math.sqrt(dx**2 + dy**2)
        
            if 0 < dist < SEPARATION_DIST:
                force = (SEPARATION_DIST - dist) / SEPARATION_DIST
                sep_x += (dx / dist) * force * 2  # Stronger force
                sep_y += (dy / dist) * force * 2

        return sep_x, sep_y

    def update(self):
        """Update sheep AI - panic, follow, or wander with separation"""
        global whistle_active

        # Check if night and wolves nearby (panic mode)
        if not is_day and len(wolves) > 0:
            self.is_panicked = True
        else:
            self.is_panicked = False

        # Check if following shepherd (whistle or bonfire)
        shepherd_dx = shepherd_pos[0] - self.pos[0]
        shepherd_dy = shepherd_pos[1] - self.pos[1]
        dist_to_shepherd = math.sqrt(shepherd_dx**2 + shepherd_dy**2)

        # Priority 1: Follow shepherd if whistle is active and in range
        if whistle_active and dist_to_shepherd < WHISTLE_RANGE:
            self.is_following_shepherd = True
        # Priority 2: Stay near bonfire if it exists
        elif bonfire_level > 0 and bonfire_type:
            bonfire_dx = BONFIRE_POS[0] - self.pos[0]
            bonfire_dy = BONFIRE_POS[1] - self.pos[1]
            dist_to_bonfire = math.sqrt(bonfire_dx**2 + bonfire_dy**2)
            # Stay within bonfire safe zone
            if dist_to_bonfire < bonfire_range[bonfire_type] * 0.7:
                self.is_following_shepherd = False
                # Calm wandering near bonfire
                self.is_panicked = False
            else:
                # Move toward bonfire if outside safe zone
                self.is_following_shepherd = False
                angle_to_bonfire = math.degrees(math.atan2(bonfire_dy, bonfire_dx))
                self.target_rot = angle_to_bonfire
        else:
            self.is_following_shepherd = False

    # ========== NEW: Calculate separation force from other sheep ==========
        separation_x = 0
        separation_y = 0
        SHEEP_SEPARATION_DISTANCE = 40  # Minimum distance between sheep
    
        for other_sheep in sheeps:
            if other_sheep is self:
                continue
        
            dx = self.pos[0] - other_sheep.pos[0]
            dy = self.pos[1] - other_sheep.pos[1]
            dist = math.sqrt(dx**2 + dy**2)
        
            # If too close, push away
            if 0 < dist < SHEEP_SEPARATION_DISTANCE:
                force = (SHEEP_SEPARATION_DISTANCE - dist) / SHEEP_SEPARATION_DISTANCE
                separation_x += (dx / dist) * force
                separation_y += (dy / dist) * force

        # Behavior 1: Following shepherd
        if self.is_following_shepherd:
            # Move toward shepherd but maintain distance
            if dist_to_shepherd > 50:  # Don't get too close
                angle_to_shepherd = math.degrees(math.atan2(shepherd_dy, shepherd_dx))
                self.target_rot = angle_to_shepherd
                self.speed = self.base_speed * 1.2
            else:
                # Stay near shepherd, slow wandering
                self.speed = self.base_speed * 0.5

        # Behavior 2: Panicked (night with wolves)
        elif self.is_panicked:
            # Run away from nearest wolf
            nearest_wolf_dist = float('inf')
            nearest_wolf_dx = 0
            nearest_wolf_dy = 0

            for wolf in wolves:
                dx = self.pos[0] - wolf.pos[0]
                dy = self.pos[1] - wolf.pos[1]
                dist = math.sqrt(dx**2 + dy**2)
                if dist < nearest_wolf_dist:
                    nearest_wolf_dist = dist
                    nearest_wolf_dx = dx
                    nearest_wolf_dy = dy

            # If wolf is close, run away
            if nearest_wolf_dist < 300:
                angle_away = math.degrees(math.atan2(nearest_wolf_dy, nearest_wolf_dx))
                self.target_rot = angle_away
                self.speed = self.panic_speed
            else:
                # Scatter randomly when no immediate threat
                self.wander_timer += 1
                if self.wander_timer >= 30:
                    self.panic_direction = random.uniform(0, 360)
                    self.wander_timer = 0
                self.target_rot = self.panic_direction
                self.speed = self.panic_speed * 0.7

        # Behavior 3: Normal wandering (day or safe)
        else:
            self.speed = self.base_speed
            self.wander_timer += 1

            if self.wander_timer >= self.wander_interval:
                self.target_rot = random.uniform(0, 360)
                self.wander_timer = 0
                self.wander_interval = random.randint(60, 180)

        # ========== Apply separation force to target rotation ==========
        # Combine target direction with separation
        if separation_x != 0 or separation_y != 0:
            # Calculate separation angle
            separation_angle = math.degrees(math.atan2(separation_y, separation_x))
        
            # Blend target rotation with separation (50% weight for separation)
            angle_diff = separation_angle - self.target_rot
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
        
            # Add separation influence (stronger when following shepherd)
            separation_weight = 0.7 if self.is_following_shepherd else 0.3
            self.target_rot += angle_diff * separation_weight

        # Smooth rotation toward target
        angle_diff = self.target_rot - self.rot
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        rotation_speed = 0.15 if self.is_panicked else 0.1
        self.rot += angle_diff * rotation_speed

        # Move forward in current direction
        rad = math.radians(self.rot)
        new_x = self.pos[0] + math.cos(rad) * self.speed
        new_y = self.pos[1] + math.sin(rad) * self.speed

        # Boundary check - stay in clearing
        dist = math.sqrt(new_x**2 + new_y**2)
        if dist < 600:  # Within grass clearing
            self.pos[0] = new_x
            self.pos[1] = new_y
        else:
            # Turn back toward center when hitting boundary
            angle_to_center = math.degrees(math.atan2(-self.pos[1], -self.pos[0]))
            self.target_rot = angle_to_center + random.uniform(-45, 45)
    
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.rot, 0, 0, 1)

        # Body - color changes when panicked
        if self.is_panicked:
            glColor3f(0.95, 0.85, 0.75)  # Slightly yellowish when scared
        else:
            glColor3f(0.95, 0.95, 0.95)  # Normal white
        glutSolidSphere(18, 16, 16)

    # Head
        glPushMatrix()
        if self.is_panicked:
            glColor3f(0.8, 0.7, 0.6)
        else:
            glColor3f(0.8, 0.8, 0.8)
        glTranslatef(22, 0, 6)
        glutSolidSphere(9, 12, 12)
        glPopMatrix()
    # Legs
        leg_height = 28
        for lx in [-8, 8]:
            for ly in [-6, 6]:
                glPushMatrix()
                glColor3f(0.3, 0.3, 0.3)
                glTranslatef(lx, ly, -leg_height)
                gluCylinder(gluNewQuadric(), 2.5, 2.0, leg_height, 8, 4)
                glPopMatrix()
    
        # Panic indicator (exclamation mark above head)
        if self.is_panicked:
            glColor3f(1.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(0, 0, 35)
            glutSolidSphere(2, 8, 8)
            glPopMatrix()

        glPopMatrix()

def create_sheep():
    global sheeps
    sheeps = []
    for i in range(NUM_SHEEP):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(80, 150)
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        sheeps.append(Sheep(x, y))

def update_sheep():
    for sheep in sheeps:
        sheep.update()

def use_whistle():
    global whistle_active, whistle_timer, WHISTLE_COOLDOWN
    
    if WHISTLE_COOLDOWN > 0:
        return False
    
    whistle_active = True
    whistle_timer = WHISTLE_DURATION   # START EFFECT TIMER
    WHISTLE_COOLDOWN = WHISTLE_COOLDOWN_TIME
    return True


def update_whistle():
    global WHISTLE_COOLDOWN, whistle_active, whistle_timer
    
    if WHISTLE_COOLDOWN > 0:
        WHISTLE_COOLDOWN -= 1

    if whistle_active:
        whistle_timer -= 1
        if whistle_timer <= 0:
            whistle_active = False   # ⬅️ STOP FOLLOWING


def draw_all_sheeps():
    for s in sheeps:
        s.draw()

# =============================
# Day-Night Cycle System
# =============================
def update_time():
    """Update game time and day-night cycle"""
    global game_time, is_day, day_count, wolves, alpha_wolf, stone_count
    
    game_time += time_speed
    
    # New day cycle
    if game_time >= MINUTES_PER_DAY:
        game_time = 0
        day_count += 1
        stone_count += 10  # ADD THIS: Give 10 stones every new day
    
    # Check day or night
    old_is_day = is_day
    is_day = DAY_START <= game_time < NIGHT_START
    
    # Night falls - spawn wolves
    if old_is_day and not is_day:
        spawn_wolves()
    
    # Day breaks - remove wolves and extinguish bonfire
    elif not old_is_day and is_day:
        wolves = []
        alpha_wolf = None

        global nights_survived
        nights_survived += 1


        # 🔥 Extinguish bonfire at sunrise
        global bonfire_level, bonfire_fuel, bonfire_type
        bonfire_level = 0
        bonfire_fuel = 0
        bonfire_type = None

        

def get_sky_color():
    if is_day:
        return (0.53, 0.81, 0.92)   # Bright blue day
    else:
        return (0.01, 0.01, 0.05)   # MUCH darker night sky

def get_fog_density():
    """Get fog density - increases at night"""
    if is_day:
        return 0.0
    else:
        # Fog at night
        return 0.0008

def apply_fog():
    """Apply fog effect for night atmosphere (no glDisable used)"""
    if not is_day:
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogfv(GL_FOG_COLOR, [0.05, 0.05, 0.15, 1.0])
        glFogf(GL_FOG_DENSITY, 0.0008)
        glHint(GL_FOG_HINT, GL_NICEST)


def get_time_string():
    """Convert game time to readable format"""
    hours = int(game_time // 60)
    minutes = int(game_time % 60)
    period = "AM" if hours < 12 else "PM"
    display_hour = hours if hours <= 12 else hours - 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour:02d}:{minutes:02d} {period}"

# =============================
# Environment
# =============================
opening_radius = 650
outer_radius = 1200
num_trees = 250
trees = []

def generate_trees():
    global trees
    trees = []
    for _ in range(num_trees):
        a = random.uniform(0, 2*math.pi)
        d = random.uniform(opening_radius+40, outer_radius-40)
        trees.append((d*math.cos(a), d*math.sin(a)))

generate_trees()

def draw_ground():
    glColor3f(0.2, 0.7, 0.2)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(50):
        a = i*2*math.pi/49
        glVertex3f(opening_radius*math.cos(a),
                   opening_radius*math.sin(a), 0)
    glEnd()

def draw_tree(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.4, 0.2, 0.1)
    gluCylinder(gluNewQuadric(), 6, 6, 60, 8, 2)
    glTranslatef(0, 0, 60)
    glColor3f(0, 0.6, 0)
    glutSolidSphere(25, 10, 10)
    glPopMatrix()

def draw_forest():
    draw_ground()
    for t in trees:
        draw_tree(*t)

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = CLOUD_HEIGHT
        self.size = random.randint(25, 40)

    def update(self):
        self.x += CLOUD_SPEED
        if self.x > 1400:
            self.x = -1400

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1.0, 1.0, 1.0)

        # Main cloud body
        glutSolidSphere(self.size, 12, 12)

        # Side puffs
        glPushMatrix()
        glTranslatef(self.size * 0.8, 0, 0)
        glutSolidSphere(self.size * 0.7, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-self.size * 0.8, 0, 0)
        glutSolidSphere(self.size * 0.7, 10, 10)
        glPopMatrix()

        glPopMatrix()

def create_stars():
    global stars
    stars = []
    for _ in range(NUM_STARS):
        x = random.uniform(-1400, 1400)
        y = random.uniform(-1400, 1400)
        z = random.uniform(STAR_HEIGHT, STAR_HEIGHT + 150)
        stars.append((x, y, z))
def draw_stars():
    glColor3f(1.0, 1.0, 1.0)  # White stars
    for (x, y, z) in stars:
        glPushMatrix()
        glTranslatef(x, y, z)
        glutSolidSphere(2.5, 6, 6)
        glPopMatrix()

# =============================
# Shepherd with Movement
# =============================
def update_shepherd():
    """Update shepherd position based on key presses"""
    global shepherd_pos, shepherd_rotation, shepherd_chop_cooldown
    
    # Update chop cooldown
    if shepherd_chop_cooldown > 0:
        shepherd_chop_cooldown -= 1
    
    # Rotation
    if keys_pressed[b'a']:
        shepherd_rotation += shepherd_rotation_speed
    if keys_pressed[b'd']:
        shepherd_rotation -= shepherd_rotation_speed
    
    # Forward/Backward movement
    move_forward = 0
    if keys_pressed[b'w']:
        move_forward = 1
    if keys_pressed[b's']:
        move_forward = -1
    
    # Move in the direction the shepherd is facing
    if move_forward != 0:
        rad = math.radians(shepherd_rotation + 90)  # +90 because model faces "up" by default
        move_x = math.cos(rad) * shepherd_speed * move_forward
        move_y = math.sin(rad) * shepherd_speed * move_forward
        
        # Update position
        new_x = shepherd_pos[0] + move_x
        new_y = shepherd_pos[1] + move_y
        
        # Boundary check - stay in clearing
        dist = math.sqrt(new_x**2 + new_y**2)
        if dist < 620:  # Stay within grass area
            shepherd_pos[0] = new_x
            shepherd_pos[1] = new_y

def draw_shepherd():
    # Do not draw shepherd in first-person view
    if camera_mode == CAMERA_FPP:
        return

    # -------- GAME OVER: Shepherd lies on ground --------
    if game_state == STATE_GAME_OVER:
        glPushMatrix()
        glTranslatef(shepherd_pos[0], shepherd_pos[1], 10)
        glRotatef(90, 1, 0, 0)  # Lie flat on ground
        glScalef(30, 12, 8)
        glColor3f(0.4, 0.25, 0.15)
        glutSolidCube(1)
        glPopMatrix()
        return

    # -------- NORMAL (ALIVE) SHEPHERD --------
    glPushMatrix()
    glTranslatef(*shepherd_pos)
    glRotatef(shepherd_rotation, 0, 0, 1)
    glScalef(0.8, 0.8, 0.8)

    # Body
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2)
    glTranslatef(0, 0, 20)
    glScalef(20, 30, 45)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(0, 0, 60)
    gluSphere(gluNewQuadric(), 12, 16, 16)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(-18, 0, 40)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 28, 12, 6)
    glPopMatrix()

    # Right arm + weapon
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(18, 0, 40)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 28, 12, 6)

    glTranslatef(0, 0, 28)

    if is_day:
        # Axe
        glColor3f(0.4, 0.2, 0.1)
        gluCylinder(gluNewQuadric(), 2, 2, 35, 8, 2)

        glPushMatrix()
        glTranslatef(0, 0, 30)
        glColor3f(0.6, 0.6, 0.7)
        glScalef(3, 12, 8)
        glutSolidCube(1)
        glPopMatrix()
    else:
        # Sword
        glColor3f(0.3, 0.15, 0.05)
        gluCylinder(gluNewQuadric(), 2, 2, 12, 8, 2)

        glPushMatrix()
        glTranslatef(0, 0, 12)
        glColor3f(0.8, 0.7, 0.0)
        glScalef(10, 2, 2)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0, 14)
        glColor3f(0.8, 0.8, 0.9)
        glScalef(1.5, 5, 30)
        glutSolidCube(1)
        glPopMatrix()

    glPopMatrix()

    # Legs
    for lx in [-6, 6]:
        glPushMatrix()
        glColor3f(0.3, 0.2, 0.1)
        glTranslatef(lx, 0, 5)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 2, 40, 12, 6)
        glPopMatrix()

    glPopMatrix()

# =============================
# Camera
# =============================
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WIDTH / HEIGHT, 1, 4000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == CAMERA_TPP:
        # Third-person orbit camera (EXISTING)
        cx = camera_distance * math.cos(math.radians(camera_angle))
        cy = camera_distance * math.sin(math.radians(camera_angle))
        gluLookAt(
            cx, cy, camera_height,
            0, 0, 0,
            0, 0, 1
        )

    else:
        # First-person camera (NEW)
        eye_x = shepherd_pos[0]
        eye_y = shepherd_pos[1]
        eye_z = shepherd_pos[2] + 20  # eye height

        rad = math.radians(shepherd_rotation + 90)
        look_x = eye_x + math.cos(rad)
        look_y = eye_y + math.sin(rad)
        look_z = eye_z

        gluLookAt(
            eye_x, eye_y, eye_z,
            look_x, look_y, look_z,
            0, 0, 1
        )


# =============================
# HUD
# =============================
def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1, 1, 1)
    
    # Game info
    draw_text(10, 770, f"Sheep: {len(sheeps)}")
    draw_text(10, 750, f"Day: {day_count + 1}")
    draw_text(10, 730, f"Time: {get_time_string()}")
    if whistle_active:
        draw_text(10, 475, f"Whistle Active: {whistle_timer//60}s")

    # Wood inventory
    draw_text(10, 700, f"Wood: {wood_count}")
    draw_text(10, 680, f"  Small: {wood_types['small']}")
    draw_text(10, 660, f"  Medium: {wood_types['medium']}")
    draw_text(10, 640, f"  Large: {wood_types['large']}")
    
    # ADD STONE COUNT HERE
    glColor3f(0.7, 0.7, 0.7)
    draw_text(10, 610, f"Stones: {stone_count}")
    if cheat_mode:
        glColor3f(1.0, 0.0, 0.0)
        draw_text(800, 770, "CHEAT MODE ON")

    # Bonfire status (MOVE DOWN)
    if bonfire_level > 0 and bonfire_type:
        fire_names = {'small': "Small", 'medium': "Medium", 'large': "Large"}
        glColor3f(1.0, 0.7, 0.0)
        draw_text(10, 580, f"Fire: {fire_names[bonfire_type]}")
        draw_text(10, 560, f"Fuel: {int(bonfire_fuel / 60)}s")
        draw_text(10, 540, f"Range: {bonfire_range[bonfire_type]}")
    else:
        glColor3f(0.5, 0.5, 0.5)
        draw_text(10, 580, "Fire: None")
        draw_text(10, 560, "Need: 15 small / 12 med / 8 large")
    
    # After the bonfire status section, add:
    # Whistle status
    if WHISTLE_COOLDOWN > 0:
        glColor3f(0.8, 0.8, 0.8)
        draw_text(10, 510, f"Whistle: {int(WHISTLE_COOLDOWN / 60)}s")
    else:
        glColor3f(0.6, 1.0, 0.6)
        draw_text(10, 510, "Whistle: Ready!")
        # If whistle is active
    if whistle_active:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(10, 490, ">>> SHEEP FOLLOWING <<<")
    # Day/Night indicator (MOVE DOWN)
    glColor3f(1, 1, 1)
    if is_day:
        glColor3f(1.0, 1.0, 0.3)
        draw_text(10, 530, "DAY - Chop Wood!")
    else:
        glColor3f(1.0, 0.3, 0.3)
        draw_text(10, 530, "NIGHT - Survive!")
        glColor3f(1, 1, 1)
        draw_text(10, 510, f"Wolves: {len(wolves)}")
        
        # ADD ALPHA WOLF HEALTH BAR HERE
        if alpha_wolf and not alpha_wolf.retreating:
            glColor3f(1.0, 0.0, 0.0)
            draw_text(10, 420, "=== ALPHA WOLF ===")
            draw_text(10, 400, f"Health: {alpha_wolf.health}/7")
            
            # Health bar
            bar_x = 10
            bar_y = 440
            bar_width = 140
            bar_height = 15
            
            # Background (empty bar)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_QUADS)
            glVertex2f(bar_x, bar_y)
            glVertex2f(bar_x + bar_width, bar_y)
            glVertex2f(bar_x + bar_width, bar_y + bar_height)
            glVertex2f(bar_x, bar_y + bar_height)
            glEnd()
            
            # Foreground (health remaining)
            health_width = (alpha_wolf.health / 7.0) * bar_width
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_QUADS)
            glVertex2f(bar_x, bar_y)
            glVertex2f(bar_x + health_width, bar_y)
            glVertex2f(bar_x + health_width, bar_y + bar_height)
            glVertex2f(bar_x, bar_y + bar_height)
            glEnd()
    # Stone count section (around line 880)
        glColor3f(0.7, 0.7, 0.7)
        draw_text(10, 610, f"Stones: {stone_count}")

    # ADD THIS: Show stones on ground at night
        if not is_day:
            glColor3f(0.6, 0.6, 0.6)
            draw_text(10, 600, f"  On Ground: {len(stones_on_ground)}")
    # Controls (MOVE DOWN)
    
    glColor3f(1, 1, 1)
    draw_text(10, 170, "Right Click - Toggle First/Third Person View")
    draw_text(10, 150, "W/S - Move Forward/Back")
    draw_text(10, 130, "A/D - Rotate Left/Right")
    draw_text(10, 110, "SPACE - Chop Wood (Day)")
    draw_text(10, 90, "E - Throw Stone (Night)")
    draw_text(10, 70, "V - Whistle (Call Sheep)")  # ADD THIS
    draw_text(10, 50, "F - Build/Add to Fire (at center)")
    draw_text(10, 30, "3 wood zones: NW, NE, South!")
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(font, ord(c))

# =============================
# Startup Screen
# =============================
def draw_startup_screen():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ✅ Dark text color for better visibility
    glColor3f(0.1, 0.1, 0.1)

    draw_centered_text(520, "SHEPHERD AND THE SHEEP", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_centered_text(470, "Press ENTER to Start", GLUT_BITMAP_HELVETICA_18)

    draw_centered_text(420, "W / S  - Move Forward / Backward", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(400, "A / D  - Rotate Left / Right", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(380, "Arrow Keys - Rotate / Zoom Camera (TPP)", GLUT_BITMAP_HELVETICA_12)

    draw_centered_text(360, "Right Mouse Click - Toggle First Person / Third Person", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(340, "C - Toggle Cheat Mode (Night Only)", GLUT_BITMAP_HELVETICA_12)

    draw_centered_text(320, "SPACE - Chop Wood (Day)", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(300, "E - Throw Stone (Night)", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(280, "V - Whistle (Call Sheep)", GLUT_BITMAP_HELVETICA_12)
    draw_centered_text(260, "F - Build / Add to Fire (Center)", GLUT_BITMAP_HELVETICA_12)

    draw_centered_text(220, "Protect your sheep and survive 3 nights!", GLUT_BITMAP_HELVETICA_12)

def draw_game_over_screen():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.8, 0.1, 0.1)
    draw_centered_text(450, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.1, 0.1, 0.1)
    draw_centered_text(410, "All sheep have been lost")
    draw_centered_text(370, "Press ENTER to restart")


def draw_game_win_screen():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.1, 0.6, 0.1)
    draw_centered_text(450, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.1, 0.1, 0.1)
    draw_centered_text(410, "You protected your sheep for 3 nights")
    draw_centered_text(370, "Press ENTER to restart")
def draw_game_win_overlay(is_win):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # ----- DARK BACKGROUND BOX -----
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    box_w, box_h = 600, 240
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2

    glColor4f(0.0, 0.0, 0.0, 0.75)
    glBegin(GL_QUADS)
    glVertex2f(box_x, box_y)
    glVertex2f(box_x + box_w, box_y)
    glVertex2f(box_x + box_w, box_y + box_h)
    glVertex2f(box_x, box_y + box_h)
    glEnd()
    glClear(GL_DEPTH_BUFFER_BIT)

    # ----- RESET MODELVIEW FOR TEXT -----
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ----- TITLE -----
    if is_win:
        glColor3f(0.2, 1.0, 0.2)
        draw_centered_text(box_y + 170, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24)

        glColor3f(1.0, 1.0, 1.0)
        draw_centered_text(box_y + 130, "You have successfully protected the sheep")
        draw_centered_text(box_y + 105, "for 3 consecutive nights")
    else:
        glColor3f(1.0, 0.2, 0.2)
        draw_centered_text(box_y + 170, "YOU LOST!!!", GLUT_BITMAP_TIMES_ROMAN_24)

        glColor3f(1.0, 1.0, 1.0)
        draw_centered_text(box_y + 130, "You failed to protect your sheep.")


    draw_centered_text(box_y + 70, "Press R to restart the game")

    # ----- RESTORE MATRICES -----
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def draw_centered_text(y, text, font=GLUT_BITMAP_HELVETICA_18):
    x = WIDTH//2 - len(text)*4
    glRasterPos3f(x, y, 0)  # <-- KEY FIX (use 3D raster pos)
    for c in text:
        glutBitmapCharacter(font, ord(c))


# =============================
# Input
# =============================
def mouse(button, state, x, y):
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == CAMERA_TPP:
            camera_mode = CAMERA_FPP
        else:
            camera_mode = CAMERA_TPP

def keyboard(key, x, y):
    global game_state, shepherd_pos, game_time, day_count, shepherd_rotation, sheeps, alpha_wolf
    global wolves, wood_count, wood_types
    global bonfire_level, bonfire_fuel, bonfire_type
    global stone_count
    global cheat_mode
    global whistle_active
    if key == b'\r':
        if game_state == STATE_START:
            game_state = STATE_GAME

        # Core reset
            shepherd_pos = [0, 0, 60]
            shepherd_rotation = 0

            game_time = DAY_START
            day_count = 0

            wolves = []
            alpha_wolf = None
            sheeps = []
            create_sheep()

            wood_count = 0
            wood_types = {'small': 0, 'medium': 0, 'large': 0}
            create_wood_zones()
            clouds.clear()
            for i in range(NUM_CLOUDS):
                x = random.uniform(-1200, 1200)
                y = random.uniform(-800, 800)
                clouds.append(Cloud(x, y))
            create_stars()

            bonfire_level = 0
            bonfire_fuel = 0
            bonfire_type = None

            stone_count = 20
            stones_on_ground.clear()
            projectiles.clear()
            whistle_active = False
            cheat_mode = False

    
    # Chop wood
    if key == b' ':
        if game_state == STATE_GAME and is_day:
            try_chop_wood()
    
    # Throw stone
    if key == b'e' or key == b'E':
        if game_state == STATE_GAME and not is_day:
            throw_stone()
    
    # Build/fuel bonfire
    if key == b'f' or key == b'F':
        if game_state == STATE_GAME:
            build_bonfire()
    
    # NEW: Use whistle
    if key == b'v' or key == b'V':
        if game_state == STATE_GAME:
            use_whistle()
    if key == b'r' or key == b'R':
        if game_state in [STATE_GAME_OVER, STATE_GAME_WIN]:
            game_state = STATE_START

    if key == b'c' or key == b'C':
        if game_state == STATE_GAME and not is_day:
            cheat_mode = not cheat_mode

    # Movement keys
    if key in keys_pressed:
        keys_pressed[key] = True

def keyboard_up(key, x, y):
    """Handle key release"""
    if key in keys_pressed:
        keys_pressed[key] = False

def special(key, x, y):
    global camera_angle, camera_distance, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5
    if key == GLUT_KEY_RIGHT:
        camera_angle += 5
    if key == GLUT_KEY_UP:
        camera_distance = max(MIN_ZOOM, camera_distance - 40)
        camera_height = max(MIN_HEIGHT, camera_height - 30)
    if key == GLUT_KEY_DOWN:
        camera_distance = min(MAX_ZOOM, camera_distance + 40)
        camera_height = min(MAX_HEIGHT, camera_height + 30)

# =============================
# Game Loop
# =============================
def update():
    """Main game update loop"""
    global game_state, STONE_THROW_COOLDOWN

    if game_state == STATE_GAME:
        # ---- NORMAL GAME UPDATE FIRST ----
        update_time()
        if is_day:
            for cloud in clouds:
                cloud.update()
        update_shepherd()
        update_sheep()
        update_wood_zones()
        update_bonfire()
        update_whistle()
        get_large_wood_periodically()

        update_stone_spawning()
        try_collect_stone()
        update_projectiles()

        if STONE_THROW_COOLDOWN > 0:
            STONE_THROW_COOLDOWN -= 1

        if not is_day:
            update_wolves()

        # ---- NOW CHECK GAME OVER / WIN ----
        if len(sheeps) == 0:
            game_state = STATE_GAME_OVER
            glutPostRedisplay()
            return

        if nights_survived >= 3 and len(sheeps) > 0:
            game_state = STATE_GAME_WIN
            glutPostRedisplay()
            return

    glutPostRedisplay()


def display():
    # Set sky color
    if game_state == STATE_GAME:
        sky = get_sky_color()
        glClearColor(sky[0], sky[1], sky[2], 1.0)
    else:
        glClearColor(0.53, 0.81, 0.92, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ---- STATE SWITCH ----
    if game_state == STATE_START:
        draw_startup_screen()

    elif game_state == STATE_GAME:
        apply_fog()
        setup_camera()
        if not is_day:
            draw_stars()
        draw_large_ground()
        draw_forest()
        if is_day:
            for cloud in clouds:
                cloud.draw()
        draw_all_wood_zones()
        draw_all_stones()
        draw_bonfire()
        draw_shepherd()
        draw_all_sheeps()
        draw_all_projectiles()
        if not is_day:
            draw_all_wolves()
        draw_hud()

    elif game_state == STATE_GAME_OVER:
        apply_fog()
        setup_camera()
        draw_forest()
        draw_all_wood_zones()
        draw_bonfire()
        draw_shepherd()   # ← shepherd lies down
        draw_all_sheeps()
        draw_all_projectiles()
        draw_hud()

        draw_game_win_overlay(False)



    elif game_state == STATE_GAME_WIN:
        
        apply_fog()
        setup_camera()
        draw_forest()
        draw_all_wood_zones()
        draw_all_stones()
        draw_bonfire()
        draw_shepherd()
        draw_all_sheeps()
        draw_all_projectiles()
        if not is_day:
            draw_all_wolves()
        draw_hud()

        draw_game_win_overlay(True)


    glutSwapBuffers()

# =============================
# Main
# =============================
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Shepherd and The Sheep")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.53, 0.81, 0.92, 1.0)  # Sky blue

    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)  # Handle key release
    glutSpecialFunc(special)
    glutMouseFunc(mouse)
    glutMainLoop()

if __name__ == "__main__":
    main()