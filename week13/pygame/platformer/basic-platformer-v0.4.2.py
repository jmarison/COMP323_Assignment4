"""
BASIC PLATFORMER GAME
A side-scrolling platform game featuring pixel art graphics.
The game includes multiple levels of increasing difficulty,
animated player character, enemies, collectible items, and a leaderboard system.
Features:
- 3 progressively challenging levels with unique platform layouts
- Pixel art graphics with animation support for player and enemies
- Parallax scrolling background for depth effect
- Player state machine with multiple animations (idle, run, jump, fall, etc.)
- Collectible items with different point values
- Enemy AI with animation support
- Secret areas that reward exploration
- Lives system and score tracking
- Leaderboard with persistent storage
- Level transition screens and celebration sequences
- Arrow keys: Move left/right
- Space: Jump
- Escape: Return to menu
- L: View leaderboard (from menu)
- Q: Quit game (from menu)
Game Structure:
- Player class: Handles player movement, physics, animations and collisions
- Enemy class: Manages enemy behavior and animations
- Platform class: Creates solid surfaces for the player to stand on
- BonusItem class: Provides collectible items that increase score
- Goal class: Represents the level completion objective
- SecretArea class: Hidden bonuses that reward exploration
- Level classes: Define level layouts and object placement
- LevelManager: Handles progression between levels
- Background class: Manages parallax scrolling background layers
The game uses a state machine to transition between splash screen, name selection,
intro screen, gameplay, level transitions, and game over screens.
"""
import pygame
import random
import time
import os
import json
import datetime
import math  # For floating animations and background effects

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 800  # Default game window size
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_STRENGTH = -10
MAX_LIVES = 3
TIME_LIMIT = 60  # Time limit in seconds

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basic Platformer Game")
clock = pygame.time.Clock()

# Font for HUD
font = pygame.font.Font(None, 36)

# Simple leaderboard data structure
# Format: {player_name: [{"score": int, "date": str}, ...]}
leaderboard = {}
player_name = ""

# Load background tiles from tilesets
def load_background_tiles():
    """Load background tiles from the tilesets directory"""
    tiles = {}
    # Use absolute path to tilesets directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tileset_folder = os.path.join(current_dir, "tilesets")
    
    if not os.path.exists(tileset_folder):
        print(f"Tilesets folder not found at {tileset_folder}")
        # Try to create the directory if it doesn't exist
        try:
            os.makedirs(tileset_folder)
            print(f"Created tilesets folder at {tileset_folder}")
        except:
            pass
        return tiles
    
    print(f"Loading background tiles from: {tileset_folder}")
    
    # Try to load common background tiles
    background_files = {
        "sky": "sky.png",
        "clouds": "clouds.png",
        "mountains": "mountains.png",
        "trees": "trees.png",
        "grass": "grass.png"
    }
    
    for tile_name, filename in background_files.items():
        file_path = os.path.join(tileset_folder, filename)
        if os.path.exists(file_path):
            try:
                print(f"Loading {file_path}")
                image = pygame.image.load(file_path).convert_alpha()
                # Scale the image to fit the screen height while maintaining aspect ratio
                aspect_ratio = image.get_width() / image.get_height()
                new_height = HEIGHT
                new_width = int(new_height * aspect_ratio)
                image = pygame.transform.scale(image, (new_width, new_height))
                tiles[tile_name] = image
                print(f"Successfully loaded background tile: {tile_name}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Background file not found: {file_path}")
    
    return tiles

# Load tileset sprites for game objects
def load_object_sprites():
    """Load sprites for platforms, enemies, bonus items, and goal"""
    sprites = {
        "platform": None,
        "enemy": [],
        "bonus": [],
        "goal": None
    }
    
    # Use absolute path to tilesets directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tileset_folder = os.path.join(current_dir, "tilesets")
    
    if not os.path.exists(tileset_folder):
        print(f"Tilesets folder not found at {tileset_folder}")
        return sprites
    
    print(f"Loading object sprites from: {tileset_folder}")
    
    # Platform sprites
    try:
        platform_file = os.path.join(tileset_folder, "platform.png")
        if os.path.exists(platform_file):
            print(f"Loading platform sprite: {platform_file}")
            platforms = pygame.image.load(platform_file).convert_alpha()
            sprites["platform"] = platforms
            print("Platform sprite loaded successfully")
        else:
            print(f"Platform sprite not found: {platform_file}")
    except Exception as e:
        print(f"Error loading platform sprites: {e}")
    
    # Enemy sprites
    enemy_types = ["slime.png", "bat.png", "spider.png"]
    for enemy_file in enemy_types:
        try:
            file_path = os.path.join(tileset_folder, enemy_file)
            if os.path.exists(file_path):
                print(f"Loading enemy sprite: {file_path}")
                enemy_img = pygame.image.load(file_path).convert_alpha()
                
                # Check if this is likely to be a spritesheet (width > height)
                if enemy_img.get_width() > enemy_img.get_height() * 1.5:  # Heuristic for detecting spritesheets
                    # Estimate number of frames based on aspect ratio
                    estimated_frames = max(1, round(enemy_img.get_width() / enemy_img.get_height()))
                    
                    # Extract frames
                    frames = []
                    frame_width = enemy_img.get_width() // estimated_frames
                    frame_height = enemy_img.get_height()
                    
                    for i in range(estimated_frames):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        if frame_rect.right <= enemy_img.get_width():
                            frame = enemy_img.subsurface(frame_rect)
                            frames.append(frame)
                    
                    # Add dictionary with info about the enemy type
                    sprites["enemy"].append({
                        "name": enemy_file.split(".")[0],
                        "frames": frames,
                        "is_animated": True
                    })
                    print(f"Loaded {len(frames)} animation frames for {enemy_file}")
                else:
                    # Single frame sprite
                    sprites["enemy"].append({
                        "name": enemy_file.split(".")[0],
                        "frames": [enemy_img],
                        "is_animated": False
                    })
                    print(f"Loaded single frame for {enemy_file}")
            else:
                print(f"Enemy sprite not found: {file_path}")
        except Exception as e:
            print(f"Error loading {enemy_file}: {e}")
    
    # Bonus item sprites
    bonus_types = ["coin.png", "gem.png", "heart.png"]
    for bonus_file in bonus_types:
        try:
            file_path = os.path.join(tileset_folder, bonus_file)
            if os.path.exists(file_path):
                print(f"Loading bonus sprite: {file_path}")
                bonus = pygame.image.load(file_path).convert_alpha()
                sprites["bonus"].append(bonus)
                print(f"Bonus sprite {bonus_file} loaded successfully")
            else:
                print(f"Bonus sprite not found: {file_path}")
        except Exception as e:
            print(f"Error loading {bonus_file}: {e}")
    
    # Goal sprite
    try:
        goal_file = os.path.join(tileset_folder, "key1.png")
        if os.path.exists(goal_file):
            print(f"Loading goal sprite: {goal_file}")
            goal = pygame.image.load(goal_file).convert_alpha()
            sprites["goal"] = goal
            print("Goal sprite loaded successfully")
        else:
            print(f"Goal sprite not found: {goal_file}")
    except Exception as e:
        print(f"Error loading goal sprite: {e}")
    
    return sprites

class Background:
    def __init__(self):
        self.tiles = load_background_tiles()
        
        # Define parallax factors for each layer (lower = slower movement)
        self.parallax_factors = {
            "sky": 0.0,         # Stationary
            "clouds": 0.1,      # Very slow
            "mountains": 0.2,   # Slow
            "trees": 0.4,       # Medium
            "grass": 0.8        # Fast, but not as fast as foreground
        }
    
    def render(self, screen, camera_x):
        """Render the background with parallax scrolling effect"""
        # Render in order from back to front
        layers = ["sky", "clouds", "mountains", "trees", "grass"]
        
        # First fill with black in case not all layers are available
        screen.fill((0, 0, 0))
        
        for layer in layers:
            if layer in self.tiles:
                # Calculate parallax offset
                parallax_offset = camera_x * self.parallax_factors[layer]
                
                # Get the image width and calculate how many times to tile it
                tile_image = self.tiles[layer]
                tile_width = tile_image.get_width()
                
                # Calculate repeats needed to cover screen, plus one extra for smooth scrolling
                repeats = (WIDTH // tile_width) + 2
                
                # Calculate the starting position (where to begin rendering)
                start_x = -(int(parallax_offset) % tile_width)
                
                # Draw the layer multiple times to fill the screen
                for i in range(repeats):
                    screen.blit(tile_image, (start_x + i * tile_width, 0))

# Player sprite handling
def load_player_sprites():
    """Load and prepare player sprite animations from sprite sheets"""
    
    sprites = {
        "idle": [],
        "run": [],
        "jump": [],
        "fall": [],
        "climb": [],
        "dash": [],
        "death": [],
        "hit": [],
        "wallslide": []
    }
    
    # Define scale factor for player sprites
    PLAYER_SCALE = 3
    
    sprite_folder = os.path.join(os.path.dirname(__file__), "sprites")
    if not os.path.exists(sprite_folder):
        os.makedirs(sprite_folder)
        print(f"Created sprites folder at {sprite_folder}")
        print("Please add player sprites to this folder")
        
        # Return default colored rectangle as fallback
        default = pygame.Surface((32 * PLAYER_SCALE, 32 * PLAYER_SCALE))
        default.fill(GREEN)
        for key in sprites:
            sprites[key] = [default]
        return sprites
    
    # Frame count mapping - estimate based on typical sprite sheets
    frame_counts = {
        "idle": 6,
        "run": 8,
        "jump": 2,
        "fall": 2,
        "climb": 6,
        "dash": 4,
        "death": 8,
        "hit": 4,
        "wallslide": 2
    }
    
    # Try to load sprite sheets
    try:
        sprite_files = {
            "idle": "Idle.png",
            "run": "Run.png",
            "jump": "Jump.png",
            "fall": "Fall.png",
            "climb": "Climb.png",
            "dash": "Dash.png",
            "death": "Death.png",
            "hit": "Hit.png",
            "wallslide": "Wallslide.png"
        }
        
        # Load each sprite sheet
        for action, filename in sprite_files.items():
            file_path = os.path.join(sprite_folder, filename)
            
            if os.path.exists(file_path):
                try:
                    # Load the sprite sheet
                    sheet = pygame.image.load(file_path).convert_alpha()
                    sheet_width = sheet.get_width()
                    sheet_height = sheet.get_height()
                    
                    # Try to detect the number of frames automatically from the image width
                    # This works better than hardcoding if the sprite sheets have different numbers of frames
                    # We'll detect based on aspect ratio - most frames are roughly square
                    estimated_frames = max(1, round(sheet_width / sheet_height))
                    
                    # If our estimate seems off, use the predefined counts
                    frames = estimated_frames if 1 <= estimated_frames <= 16 else frame_counts.get(action, 6)
                        
                    frame_width = sheet_width // frames
                    frame_height = sheet_height
                    
                    # Calculate scaled dimensions
                    scaled_width = frame_width * PLAYER_SCALE
                    scaled_height = frame_height * PLAYER_SCALE
                    
                    # Extract each frame from the sheet and scale it
                    for i in range(frames):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        # Make sure we don't exceed the sheet dimensions
                        if frame_rect.right <= sheet_width:
                            frame = sheet.subsurface(frame_rect)
                            
                            # Scale the frame to be larger
                            frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
                            sprites[action].append(frame)
                    
                    print(f"Loaded {len(sprites[action])} frames for {action} animation at size {scaled_width}x{scaled_height}")
                    
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Sprite file not found: {file_path}")
        
        # Check if we loaded any sprites
        has_sprites = any(len(frames) > 0 for frames in sprites.values())
        
        if not has_sprites:
            print("No sprite images found. Using colored rectangles instead.")
            default = pygame.Surface((32 * PLAYER_SCALE, 32 * PLAYER_SCALE))
            default.fill(GREEN)
            for key in sprites:
                sprites[key] = [default]
    
    except Exception as e:
        print(f"Error loading sprites: {e}")
        default = pygame.Surface((32 * PLAYER_SCALE, 32 * PLAYER_SCALE))
        default.fill(GREEN)
        for key in sprites:
            sprites[key] = [default]
    
    return sprites

def load_leaderboard():
    global leaderboard
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
    else:
        leaderboard = {}

def save_leaderboard():
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)

def draw_hud(screen, score, lives, elapsed_time, level_num=1):
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    time_text = font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
    level_text = font.render(f"Level: {level_num}", True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(time_text, (10, 90))
    screen.blit(level_text, (10, 130))

def show_leaderboard_screen():
    global screen, player_name
    leaderboard_font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    screen.fill((0, 0, 0))

    # Get global top scores across all players
    all_scores = []
    for name, scores in leaderboard.items():
        for score_entry in scores:
            all_scores.append((name, score_entry["score"], score_entry["date"]))
    all_scores.sort(key=lambda x: x[1], reverse=True)
    global_top_five = all_scores[:5]
    
    # Get current player's top scores
    player_scores = []
    if player_name in leaderboard:
        for score_entry in leaderboard[player_name]:
            player_scores.append((player_name, score_entry["score"], score_entry["date"]))
        player_scores.sort(key=lambda x: x[1], reverse=True)
    player_top_five = player_scores[:5]
    
    # Draw title
    title_surface = title_font.render("LEADERBOARD", True, WHITE)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))
    
    # Draw global top scores
    global_title = title_font.render("Global Top 5", True, YELLOW)
    screen.blit(global_title, (WIDTH // 4 - global_title.get_width() // 2, 120))
    
    for i, (name, score_val, date_str) in enumerate(global_top_five):
        score_text = f"{i+1}. {name}: {score_val}"
        text_surface = leaderboard_font.render(score_text, True, WHITE)
        date_surface = leaderboard_font.render(f"Date: {date_str}", True, LIGHT_GRAY)
        screen.blit(text_surface, (WIDTH // 4 - text_surface.get_width() // 2, 180 + i * 60))
        screen.blit(date_surface, (WIDTH // 4 - date_surface.get_width() // 2, 210 + i * 60))
    
    # Draw player's top scores
    if player_name:
        player_title = title_font.render(f"{player_name}'s Top 5", True, GREEN)
        screen.blit(player_title, (WIDTH * 3 // 4 - player_title.get_width() // 2, 120))
        
        for i, (name, score_val, date_str) in enumerate(player_top_five):
            score_text = f"{i+1}. Score: {score_val}"
            text_surface = leaderboard_font.render(score_text, True, WHITE)
            date_surface = leaderboard_font.render(f"Date: {date_str}", True, LIGHT_GRAY)
            screen.blit(text_surface, (WIDTH * 3 // 4 - text_surface.get_width() // 2, 180 + i * 60))
            screen.blit(date_surface, (WIDTH * 3 // 4 - date_surface.get_width() // 2, 210 + i * 60))
    
    # Draw navigation instructions
    instructions_surface = leaderboard_font.render("Press B to return", True, WHITE)
    screen.blit(instructions_surface, (WIDTH // 2 - instructions_surface.get_width() // 2, HEIGHT - 100))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    waiting = False  # Return to previous screen

def show_name_selection_screen():
    """
    Display the player name selection screen and handle user input.
    This function allows the player to either select an existing player name from the leaderboard
    or create a new player name. The function controls the UI rendering and all user interactions
    until a player name is selected or the game is exited.
    The screen displays:
    - Title
    - List of existing player names from the leaderboard
    - Option to enter a new player name
    - Instructions for navigation and control
    Controls:
    - UP/DOWN arrows: Navigate through existing names and the "new player" option
    - ENTER: Select highlighted option or confirm new name entry
    - L: View leaderboard
    - Q: Quit game
    During new name entry:
    - Alphanumeric characters, space, hyphen, and underscore are allowed
    - BACKSPACE: Delete the last character
    - ENTER: Confirm the new name
    Returns:
        None: The function sets the global variable 'player_name' with the selected or created name
    """
    global player_name, leaderboard
    load_leaderboard()
    
    existing_names = list(leaderboard.keys())
    selected_index = -1  # -1 means "enter new name"
    
    selection_font = pygame.font.Font(None, 48)
    info_font = pygame.font.Font(None, 36)
    
    typing_new_name = False
    temp_name = ""
    
    while True:
        screen.fill((0, 0, 0))
        
        # Draw title
        title_text = selection_font.render("Select Player Name", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Draw existing names
        if existing_names:
            names_title = info_font.render("Existing players (use UP/DOWN to select):", True, YELLOW)
            screen.blit(names_title, (WIDTH // 2 - names_title.get_width() // 2, 120))
            
            for i, name in enumerate(existing_names):
                if i == selected_index:
                    color = GREEN
                else:
                    color = LIGHT_GRAY
                name_text = info_font.render(name, True, color)
                screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 170 + i * 40))
        
        # Draw "new player" option
        new_player_text = info_font.render("Enter new player name", True, 
                                          GREEN if selected_index == -1 else LIGHT_GRAY)
        screen.blit(new_player_text, (WIDTH // 2 - new_player_text.get_width() // 2, 
                                     170 + len(existing_names) * 40 + 20))
        
        # If typing a new name
        if typing_new_name:
            pygame.draw.rect(screen, DARK_GRAY, (WIDTH // 4, HEIGHT // 2, WIDTH // 2, 100))
            name_prompt = info_font.render("Enter name: " + temp_name, True, WHITE)
            screen.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, HEIGHT // 2 + 20))
            enter_text = info_font.render("Press ENTER when done", True, LIGHT_GRAY)
            screen.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT // 2 + 60))
        
        # Draw instructions
        instructions = [
            "ENTER: Select highlighted option",
            "UP/DOWN: Navigate options",
            "L: View leaderboard",
            "Q: Quit game"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = info_font.render(instruction, True, WHITE)
            screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, HEIGHT - 150 + i * 30))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            elif event.type == pygame.KEYDOWN:
                if typing_new_name:
                    if event.key == pygame.K_RETURN:
                        if temp_name:
                            player_name = temp_name
                            return  # Exit with the new name
                    elif event.key == pygame.K_BACKSPACE:
                        temp_name = temp_name[:-1]
                    else:
                        # Accept alphanumeric and some special characters
                        if event.unicode.isalnum() or event.unicode in " -_":
                            temp_name += event.unicode
                else:
                    if event.key == pygame.K_UP:
                        if selected_index > -1:
                            selected_index -= 1
                        elif selected_index == -1 and existing_names:
                            # Wrap around to the bottom of the list
                            selected_index = len(existing_names) - 1
                            
                    elif event.key == pygame.K_DOWN:
                        if selected_index < len(existing_names) - 1:
                            selected_index += 1
                        else:
                            selected_index = -1  # Go to "new player" option
                            
                    elif event.key == pygame.K_RETURN:
                        if selected_index == -1:
                            # Start typing a new name
                            typing_new_name = True
                            temp_name = ""
                        else:
                            # Select existing name
                            player_name = existing_names[selected_index]
                            return  # Exit with selected name
                            
                    elif event.key == pygame.K_l:
                        # Show leaderboard screen
                        show_leaderboard_screen()
                        
                    elif event.key == pygame.K_q:
                        # Quit game
                        pygame.quit()
                        exit()

def show_intro_screen():
    global player_name
    
    # First select/enter player name
    show_name_selection_screen()
    
    intro_font = pygame.font.Font(None, 48)
    intro_text = [
        "Welcome to the Basic Platformer Game!",
        "Use the arrow keys to move the player and the space bar to jump.",
        "Avoid enemies and collect bonus items to increase your score.",
        "Reach the blue goal object to complete the level.",
        f"You have {MAX_LIVES} lives and {TIME_LIMIT} seconds to complete the level."
    ]

    # Show welcome screen with name confirmation
    screen.fill((0, 0, 0))
    
    # Show player name at top
    name_surface = intro_font.render(f"Player: {player_name}", True, GREEN)
    screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, 50))
    
    # Show game instructions
    for i, line in enumerate(intro_text):
        text_surface = intro_font.render(line, True, WHITE)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 120 + i * 50))
    
    # Show options
    options_text = "Press ENTER to start game, L for leaderboard, or Q to quit"
    options_surface = intro_font.render(options_text, True, YELLOW)
    screen.blit(options_surface, (WIDTH // 2 - options_surface.get_width() // 2, HEIGHT - 100))
    
    pygame.display.flip()

    # Wait for player input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Start the game
                elif event.key == pygame.K_l:
                    show_leaderboard_screen()
                    # Redraw the intro screen after returning
                    screen.fill((0, 0, 0))
                    screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, 50))
                    for i, line in enumerate(intro_text):
                        text_surface = intro_font.render(line, True, WHITE)
                        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 120 + i * 50))
                    screen.blit(options_surface, (WIDTH // 2 - options_surface.get_width() // 2, HEIGHT - 100))
                    pygame.display.flip()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()

def show_game_over_screen(won, reason="", score=0, lives=0):
    global player_name, leaderboard
    
    # Save score with date if player won
    if won:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if player_name not in leaderboard:
            leaderboard[player_name] = []
        
        # Add score with date
        leaderboard[player_name].append({"score": score, "date": today})
        save_leaderboard()

    game_over_font = pygame.font.Font(None, 48)
    if won:
        game_over_text = f"Congratulations! You won!\nScore: {score}\nLives remaining: {lives}"
    else:
        if reason == "time_up":
            game_over_text = "Game Over! Time's up!"
        elif reason == "lives_lost":
            game_over_text = "Game Over! No lives left."
        else:
            game_over_text = "Game Over! You lost the game."
        game_over_text += f"\nScore: {score}"
    instructions_text = "Press R to restart, L for leaderboard, or Q to quit."

    screen.fill((0, 0, 0))
    for i, line in enumerate(game_over_text.split('\n')):
        text_surface = game_over_font.render(line, True, WHITE)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 100 + i * 50))
    instructions_surface = game_over_font.render(instructions_text, True, WHITE)
    screen.blit(instructions_surface, (WIDTH // 2 - instructions_surface.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_r:
                    waiting = False
                    return "start_screen"  # Return to start screen instead of directly restarting
                elif event.key == pygame.K_l:
                    show_leaderboard_screen()
                    # Redraw game over screen after returning
                    screen.fill((0, 0, 0))
                    for i, line in enumerate(game_over_text.split('\n')):
                        text_surface = game_over_font.render(line, True, WHITE)
                        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 100 + i * 50))
                    screen.blit(instructions_surface, (WIDTH // 2 - instructions_surface.get_width() // 2, HEIGHT // 2 + 50))
                    pygame.display.flip()
    
    return "start_screen"  # Default to returning to start screen

def show_splash_screen():
    """Display a splash screen when the game first starts"""
    # Set up the splash screen
    splash_font_large = pygame.font.Font(None, 86)
    splash_font_small = pygame.font.Font(None, 36)
    
    # Fill screen with a dark background
    screen.fill((0, 0, 0))
    
    # Draw game title
    title_text = splash_font_large.render("PLATFORM ADVENTURE", True, GREEN)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    
    # Draw subtitle
    subtitle_text = splash_font_small.render("A Pixel Art Platformer Game", True, WHITE)
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2))
    
    # Draw copyright notice
    year = datetime.datetime.now().year
    copyright_text = splash_font_small.render(f"© {year} NJH Game Studio", True, LIGHT_GRAY)
    screen.blit(copyright_text, (WIDTH // 2 - copyright_text.get_width() // 2, HEIGHT - 100))
    
    # Draw "Press any key" message with animation effect
    pygame.display.flip()
    
    # Display for 3 seconds, then wait for key press
    start_time = time.time()
    key_prompt_visible = True
    key_prompt_timer = 0
    waiting = True
    
    while waiting:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # After 3 seconds, show "press any key" message
        if elapsed >= 3.0:
            # Flash the "press any key" message every 0.5 seconds
            key_prompt_timer += 1/30  # assuming 30 FPS updates
            if key_prompt_timer >= 0.5:
                key_prompt_timer = 0
                key_prompt_visible = not key_prompt_visible
            
            # Draw or hide the prompt based on animation state
            screen.fill((0, 0, 0), (0, HEIGHT - 50, WIDTH, 50))  # Clear the prompt area
            if key_prompt_visible:
                prompt_text = splash_font_small.render("Press Any Key to Start", True, YELLOW)
                screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT - 50))
            pygame.display.update(pygame.Rect(0, HEIGHT - 50, WIDTH, 50))
            
            # Check for key events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        else:
            # Before 3 seconds, just check for quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        
        clock.tick(30)  # Lower framerate during splash screen

class Player(pygame.sprite.Sprite):
    """
    A player character for a platform game using Pygame.
    This class manages the player's appearance, animations, movement, physics, 
    and interactions with other game elements like platforms, enemies, and bonus items.
    Attributes:
        sprites (dict): Dictionary containing sprite animations for different states.
        current_state (str): Current animation state ("idle", "run", "jump", etc.).
        animation_frame (int): Index of the current animation frame.
        animation_speed (dict): Animation frame rates for different states.
        last_update_time (float): Timestamp of the last animation update.
        facing_right (bool): Whether the character is facing right.
        image (Surface): Current sprite image.
        rect (Rect): Rectangle defining player position and size.
        vel_x (float): Horizontal velocity.
        vel_y (float): Vertical velocity.
        on_ground (bool): Whether the player is on a platform.
        on_wall (bool): Whether the player is touching a wall.
        is_dashing (bool): Whether the player is dashing.
        is_hit (bool): Whether the player was recently hit.
        camera_x (int): Camera offset for side-scrolling.
        alive (bool): Whether the player is alive.
        score (int): Player's current score.
        lives (int): Number of lives remaining.
        death_animation_timer (float): Timer for death animation sequence.
        death_animation_duration (float): Duration of death animation in seconds.
        mask (Mask): Pixel-perfect collision mask.
    """
    def __init__(self):
        super().__init__()
        self.sprites = load_player_sprites()
        
        # Animation variables - UPDATED
        self.current_state = "idle"
        self.animation_frame = 0
        self.animation_speed = {
            "idle": 0.1,   # Slower for idle animations (more frames)
            "run": 0.07,   # Faster for running (smoother movement)
            "jump": 0.1,
            "fall": 0.1,
            "climb": 0.15,
            "dash": 0.05,  # Very fast for dash
            "death": 0.15, # Slower for dramatic effect
            "hit": 0.08,
            "wallslide": 0.1
        }
        self.last_update_time = time.time()
        self.facing_right = True
        
        # Get dimensions from the first sprite
        first_sprite = self.sprites["idle"][0] if self.sprites["idle"] else pygame.Surface((32, 50))
        sprite_width = first_sprite.get_width()
        sprite_height = first_sprite.get_height()
        
        # Initialize with the first frame of the idle animation
        self.image = self.sprites["idle"][0] if self.sprites["idle"] else first_sprite
        self.rect = self.image.get_rect(midbottom=(100, HEIGHT - 50))
        
        # Physics and game state
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.on_wall = False
        self.is_dashing = False
        self.is_hit = False
        self.camera_x = 0
        self.alive = True
        self.score = 0
        self.lives = MAX_LIVES
        self.death_animation_timer = 0
        self.death_animation_duration = 2.0  # seconds to show death animation
        
        # Create a mask for pixel-perfect collision detection (optional)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, platforms, enemies, bonus_items, all_sprites):
        if not self.alive:
            self.current_state = "death"
            # Check if we're still in death animation
            if self.death_animation_timer < self.death_animation_duration:
                self.death_animation_timer += 1/60  # assuming 60 FPS
                # Continue updating animation frames during death
                self.update_animation()
                return False  # Game not done yet
            else:
                return True  # Death animation finished, game over
        
        # Store previous state for animation transitions
        previous_state = self.current_state
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        moving = False
        self.vel_x = 0
        
        if keys[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.vel_x = -PLAYER_SPEED
                self.rect.x += self.vel_x
                self.camera_x += self.vel_x
                moving = True
                self.facing_right = False
                
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.rect.x += self.vel_x
            self.camera_x += self.vel_x
            moving = True
            self.facing_right = True

        # Jump logic
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Platform collision
        self.on_ground = False
        self.on_wall = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Check if colliding from above (landing on platform)
                if self.vel_y > 0 and self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # Check for wall collision
                elif not self.on_ground and (
                    (self.vel_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left) or
                    (self.vel_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right)
                ):
                    self.on_wall = True

        # Enemy collision
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.vel_y > 0 and self.rect.bottom > enemy.rect.top and self.rect.top < enemy.rect.top:  # Player lands on enemy
                    enemies.remove(enemy)
                    all_sprites.remove(enemy)
                    self.vel_y = JUMP_STRENGTH
                    self.score += enemy.points
                    self.on_ground = True
                    # Spawn a new enemy further along
                    new_enemy = Enemy(self.rect.x + 800, HEIGHT - 50)
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)
                else:
                    self.is_hit = True
                    self.lose_life()

        # Bonus item collection
        for bonus_item in bonus_items:
            if self.rect.colliderect(bonus_item.rect):
                self.score += bonus_item.points
                bonus_items.remove(bonus_item)
                all_sprites.remove(bonus_item)
        
        # Update player animation state
        if not self.alive:
            self.current_state = "death"
        elif self.is_hit:
            self.current_state = "hit"
            # Reset hit state after animation completes
            if previous_state == "hit" and self.animation_frame >= len(self.sprites["hit"]) - 1:
                self.is_hit = False
        elif self.is_dashing:
            self.current_state = "dash"
        elif self.on_wall and not self.on_ground:
            self.current_state = "wallslide"
        elif not self.on_ground:
            if self.vel_y < 0:
                self.current_state = "jump"
            else:
                self.current_state = "fall"
        else:
            if moving:
                self.current_state = "run"  # Use run instead of walk for your sprite set
            else:
                self.current_state = "idle"
        
        # Only reset animation counter if state changed
        if previous_state != self.current_state:
            self.animation_frame = 0
            self.last_update_time = time.time()
        
        # UPDATED animation timing system using actual elapsed time
        self.update_animation()
        return False  # Normal update, game continues
        
    def update_animation(self):
        # Extract animation code to a separate method
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        
        # Get the appropriate animation speed for current state
        speed = self.animation_speed.get(self.current_state, 0.1)
        
        if elapsed > speed:
            frames_to_advance = int(elapsed / speed)
            frames_in_state = len(self.sprites[self.current_state])
            
            if frames_in_state > 0:
                self.animation_frame = (self.animation_frame + frames_to_advance) % frames_in_state
                self.last_update_time = current_time  # Reset timer
        
        # Update sprite image
        if self.sprites[self.current_state] and len(self.sprites[self.current_state]) > 0:
            frame_index = min(self.animation_frame, len(self.sprites[self.current_state]) - 1)
            self.image = self.sprites[self.current_state][frame_index]
            
            # Flip image if facing left
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            
            # Update mask for pixel-perfect collision
            self.mask = pygame.mask.from_surface(self.image)

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.alive = False
            self.death_animation_timer = 0  # Start death animation
            print("Game Over! No lives left.")
        else:
            print(f"Lives left: {self.lives}")
            self.rect.midbottom = (100, HEIGHT - 50)  # Reset position
            self.camera_x = 0
            self.vel_y = 0

    def update_death_animation(self):
        """Update only the death animation when in dying state"""
        self.current_state = "death"
        
        if self.death_animation_timer < self.death_animation_duration:
            self.death_animation_timer += 1/60  # assuming 60 FPS
            self.update_animation()
            return False  # Not done with death animation
        else:
            return True  # Death animation finished

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        
        # Try to load platform sprite
        object_sprites = load_object_sprites()
        platform_sprite = object_sprites["platform"]
        
        if platform_sprite:
            # Create a surface and tile the platform sprite to fill the width
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # If platform_sprite is smaller than our platform, tile it
            sprite_width = platform_sprite.get_width()
            repeats = max(1, width // sprite_width)
            
            for i in range(repeats):
                # Scale height if needed
                scaled_sprite = pygame.transform.scale(
                    platform_sprite, 
                    (sprite_width, height)
                )
                self.image.blit(scaled_sprite, (i * sprite_width, 0))
        else:
            # Fallback to colored rectangle
            self.image = pygame.Surface((width, height))
            self.image.fill(WHITE)
        
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1  # Seconds per frame
        self.last_update_time = time.time()
        self.is_animated = False
        
        # Try to load enemy sprites
        object_sprites = load_object_sprites()
        enemy_sprites = object_sprites["enemy"]
        
        self.shape = random.choice(['square', 'circle', 'triangle'])
        self.points = 0  # Will be set based on enemy type
        self.frames = None  # Will store animation frames
        
        if enemy_sprites and len(enemy_sprites) > 0:
            # Choose a random enemy sprite if available
            sprite_idx = random.randint(0, len(enemy_sprites) - 1)
            self.enemy_type = sprite_idx
            
            # Get sprite data
            sprite_data = enemy_sprites[sprite_idx]
            self.frames = sprite_data["frames"]
            self.is_animated = sprite_data["is_animated"]
            
            # Set points based on enemy type (harder enemies worth more)
            if "bat" in sprite_data["name"]:
                self.points = 15  # Bats are harder
                self.animation_speed = 0.08  # Faster animation for bats
            elif "spider" in sprite_data["name"]:
                self.points = 25  # Spiders are hardest
                self.animation_speed = 0.12  # Slower animation for spiders
            else:  # slime or other
                self.points = 5
                self.animation_speed = 0.15  # Slowest animation for slimes
            
            # Get first frame to start with
            if self.frames and len(self.frames) > 0:
                first_frame = self.frames[0]
                # Scale to appropriate size
                self.original_image = pygame.transform.scale(first_frame, (50, 50))
                self.image = self.original_image
            else:
                self._create_default_enemy()
        else:
            self._create_default_enemy()
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = random.choice([-1, 1])
    
    def _create_default_enemy(self):
        """Create a default enemy if sprites aren't available"""
        if self.shape == 'square':
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            self.points = 5
        elif self.shape == 'circle':
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 15)
            self.points = 15
        elif self.shape == 'triangle':
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, PURPLE, [(15, 0), (30, 30), (0, 30)])
            self.points = 25
    
    def update_animation(self):
        """Update the enemy's animation frame based on elapsed time"""
        # Only proceed if we have animation frames
        if not self.is_animated or not self.frames or len(self.frames) <= 1:
            return
            
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        
        if elapsed > self.animation_speed:
            # Calculate frames to advance (usually 1)
            frames_to_advance = int(elapsed / self.animation_speed)
            self.animation_frame = (self.animation_frame + frames_to_advance) % len(self.frames)
            self.last_update_time = current_time
            
            # Get the new frame and scale it
            new_frame = self.frames[self.animation_frame]
            self.original_image = pygame.transform.scale(new_frame, (50, 50))
            
            # Update image, accounting for direction
            if self.direction < 0:
                self.image = pygame.transform.flip(self.original_image, True, False)
            else:
                self.image = self.original_image
    
    def update(self):
        self.rect.x += self.direction * 2
        
        # If enemy goes out of extended area, remove and respawn
        if self.rect.left < 0 or self.rect.right > 3000:
            self.kill()
            new_x = random.randint(0, 3000)
            new_enemy = Enemy(new_x, HEIGHT - 50)
            # We can't access level directly, so we'll let the main game loop handle respawning
            # This enemy will be removed but no new one is added here
            return
        
        # Update animation
        self.update_animation()
        
        # If not animating or need to flip sprite based on direction
        if not self.is_animated and self.original_image is not None:
            if self.direction < 0:
                self.image = pygame.transform.flip(self.original_image, True, False)
            else:
                self.image = self.original_image

class BonusItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Try to load bonus sprites
        object_sprites = load_object_sprites()
        bonus_sprites = object_sprites["bonus"]
        
        self.type = random.choice(['coin', 'gem', 'heart'])
        self.points = 0  # Will be set based on item type
        
        if bonus_sprites and len(bonus_sprites) > 0:
            # Choose sprite based on type
            sprite_index = 0  # Default to first sprite
            if self.type == 'coin' and len(bonus_sprites) > 0:
                sprite_index = 0
                self.points = 10
            elif self.type == 'gem' and len(bonus_sprites) > 1:
                sprite_index = 1
                self.points = 20
            elif self.type == 'heart' and len(bonus_sprites) > 2:
                sprite_index = 2
                self.points = 30
            
            # Make sure the index is valid
            if sprite_index < len(bonus_sprites):
                # Scale to appropriate size
                self.image = pygame.transform.scale(bonus_sprites[sprite_index], (30, 30))
            else:
                self._create_default_bonus()
        else:
            self._create_default_bonus()
                
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Add animation for floating effect
        self.float_offset = 0
        self.float_speed = 0.05
        self.original_y = y
    
    def _create_default_bonus(self):
        """Create a default bonus item if sprites aren't available"""
        if self.type == 'coin':
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (10, 10), 10)
            self.points = 10
        elif self.type == 'gem':
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, PINK, [(10, 0), (20, 10), (10, 20), (0, 10)])
            self.points = 20
        else:  # heart
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, RED, [(10, 5), (15, 0), (20, 5), (20, 10), (10, 20), (0, 10), (0, 5), (5, 0)])
            self.points = 30

    def update(self):
        # Make item float up and down slightly
        self.float_offset += self.float_speed
        self.rect.y = self.original_y + int(math.sin(self.float_offset) * 5)

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Try to load goal sprite
        object_sprites = load_object_sprites()
        goal_sprite = object_sprites["goal"]
        
        if goal_sprite:
            # Use the sprite for the goal
            self.image = goal_sprite
            # Scale to appropriate size
            self.image = pygame.transform.scale(self.image, (60, 80))
        else:
            # Fallback to colored rectangle
            self.image = pygame.Surface((40, 60))
            self.image.fill(BLUE)
            
        self.rect = self.image.get_rect(topleft=(x, y))

class SecretArea:
    def __init__(self, x, y, width, height, reward=100):
        """
        Create a secret area that rewards the player when discovered.
        
        Args:
            x, y: The position of the secret area
            width, height: The dimensions of the secret area
            reward: Points awarded when discovered (default: 100)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.discovered = False
        self.reward = reward
        self.discovery_time = 0
        
        # Create a subtle visual marker for debug/visualization
        self.visual = pygame.Surface((width, height), pygame.SRCALPHA)
        self.visual.fill((255, 255, 0, 30))  # Semi-transparent yellow
        
    def check_player_entry(self, player):
        """Check if the player has entered this secret area and award points if not already discovered"""
        if not self.discovered and self.rect.colliderect(player.rect):
            self.discovered = True
            player.score += self.reward
            self.discovery_time = time.time()
            return True
        return False
        
    def draw(self, screen, camera_x):
        """Draw the secret area (only visible after discovery for a few seconds)"""
        if self.discovered:
            # Show visual for 5 seconds after discovery
            if time.time() - self.discovery_time < 5:
                # Calculate pulsating alpha for fade effect
                alpha = int(128 + 127 * math.sin((time.time() - self.discovery_time) * 4))
                self.visual.fill((255, 255, 0, alpha))
                screen.blit(self.visual, (self.rect.x - camera_x, self.rect.y))

class Level:
    def __init__(self):
        # Create background
        self.background = Background()
        
        # Default empty containers - to be filled by subclasses
        self.platforms = []
        self.enemies = pygame.sprite.Group()
        self.bonus_items = pygame.sprite.Group()
        self.goal = None
        self.secret_areas = []  # Added secret areas to the level

    def get_all_sprites(self):
        return pygame.sprite.Group(self.platforms + list(self.enemies) + list(self.bonus_items) + [self.goal])

class Level1(Level):
    def __init__(self):
        super().__init__()
        
        # Level 1 platforms - relatively easy layout
        self.platforms = [
            Platform(0, HEIGHT - 20, 3000, 20),  # Ground platform
            Platform(300, HEIGHT - 100, 150, 20),
            Platform(600, HEIGHT - 150, 100, 20),
            Platform(900, HEIGHT - 200, 150, 20),
            Platform(1200, HEIGHT - 250, 100, 20),
            Platform(1500, HEIGHT - 300, 200, 20),
            Platform(1800, HEIGHT - 350, 150, 20),
            Platform(2100, HEIGHT - 400, 100, 20),
            Platform(2400, HEIGHT - 450, 200, 20),
            Platform(2700, HEIGHT - 500, 150, 20)
        ]
        
        # Level 1 enemies - fewer and simpler
        self.enemies = pygame.sprite.Group([
            Enemy(500, HEIGHT - 50),
            Enemy(1000, HEIGHT - 50),
            Enemy(1400, HEIGHT - 250),
            Enemy(2000, HEIGHT - 350),
            Enemy(2500, HEIGHT - 450)
        ])
        
        # Level 1 bonus items
        self.bonus_items = pygame.sprite.Group([
            BonusItem(400, HEIGHT - 150),
            BonusItem(800, HEIGHT - 270),
            BonusItem(1300, HEIGHT - 300),
            BonusItem(1700, HEIGHT - 400),
            BonusItem(2150, HEIGHT - 450),
            BonusItem(2600, HEIGHT - 550),
            BonusItem(2900, HEIGHT - 160)
        ])
        
        # Level 1 goal
        self.goal = Goal(2900, HEIGHT - 100)
        
        # Add secret areas to Level 1
        self.secret_areas = [
            SecretArea(350, HEIGHT - 350, 100, 250, 200),    # Hidden at start of level
            SecretArea(1250, HEIGHT - 300, 100, 100, 300),   # Hidden under platform
            SecretArea(2800, HEIGHT - 200, 150, 200, 500)    # Hidden near end of level
        ]

class Level2(Level):
    def __init__(self):
        super().__init__()
        
        # Level 2 platforms - more complex layout with vertical challenges
        self.platforms = [
            Platform(0, HEIGHT - 20, 3500, 20),  # Ground platform (longer)
            
            # First section - stair pattern
            Platform(300, HEIGHT - 120, 100, 20),
            Platform(500, HEIGHT - 220, 100, 20),
            Platform(700, HEIGHT - 320, 100, 20),
            Platform(900, HEIGHT - 420, 400, 20),  # Upper platform
            
            # Middle section - gap jumping
            Platform(1500, HEIGHT - 350, 100, 20),
            Platform(1700, HEIGHT - 300, 80, 20),
            Platform(1900, HEIGHT - 250, 60, 20),
            Platform(2100, HEIGHT - 300, 80, 20),
            Platform(2300, HEIGHT - 350, 100, 20),
            
            # Final section - downward path
            Platform(2600, HEIGHT - 200, 200, 20),
            Platform(2900, HEIGHT - 300, 100, 20),
            Platform(3100, HEIGHT - 400, 80, 20),
            Platform(3300, HEIGHT - 200, 150, 20)  # Platform near goal
        ]
        
        # Level 2 enemies - more and tougher enemies
        self.enemies = pygame.sprite.Group([
            Enemy(500, HEIGHT - 150),
            Enemy(700, HEIGHT - 350),
            Enemy(900, HEIGHT - 450),
            Enemy(1200, HEIGHT - 450),
            Enemy(1500, HEIGHT - 380),
            Enemy(1900, HEIGHT - 280),
            Enemy(2300, HEIGHT - 380),
            Enemy(2600, HEIGHT - 230),
            Enemy(3300, HEIGHT - 230)
        ])
        
        # Level 2 bonus items - more valuable items
        self.bonus_items = pygame.sprite.Group([
            BonusItem(300, HEIGHT - 170),  # Coin at first step
            BonusItem(700, HEIGHT - 370),  # Coin at third step
            BonusItem(1050, HEIGHT - 470), # Gem at top platform
            BonusItem(1700, HEIGHT - 350), # Gem at middle platform
            BonusItem(2100, HEIGHT - 350), # Heart at middle platform
            BonusItem(2600, HEIGHT - 250), # Coin at final section
            BonusItem(3100, HEIGHT - 450), # Heart near goal (difficult to get)
            BonusItem(3350, HEIGHT - 250)  # Gem near goal
        ])
        
        # Level 2 goal - positioned at end of level
        self.goal = Goal(3400, HEIGHT - 100)
        
        # Add secret areas to Level 2 - more valuable ones
        self.secret_areas = [
            SecretArea(400, HEIGHT - 400, 150, 280, 400),    # Hidden vertical shaft
            SecretArea(1600, HEIGHT - 200, 120, 180, 600),   # Hidden in middle gap
            SecretArea(3000, HEIGHT - 150, 100, 150, 800)    # Under final platform
        ]

class Level3(Level):
    def __init__(self):
        super().__init__()
        
        # Level 3 - most challenging with complex platform arrangements
        self.platforms = [
            Platform(0, HEIGHT - 20, 4000, 20),  # Ground platform (even longer)
            
            # Beginning section - tall vertical challenge
            Platform(300, HEIGHT - 150, 80, 20),
            Platform(450, HEIGHT - 280, 60, 20),
            Platform(600, HEIGHT - 410, 50, 20),
            Platform(750, HEIGHT - 540, 100, 20),  # Top of first challenge
            
            # Middle section - precision jumps with small platforms
            Platform(950, HEIGHT - 480, 40, 20),   # Small platform
            Platform(1100, HEIGHT - 420, 35, 20),  # Even smaller
            Platform(1250, HEIGHT - 480, 30, 20),  # Smallest
            Platform(1400, HEIGHT - 400, 200, 20), # Relief platform
            
            # Zigzag descent section
            Platform(1700, HEIGHT - 350, 100, 20),
            Platform(1900, HEIGHT - 250, 100, 20),
            Platform(2100, HEIGHT - 350, 100, 20),
            Platform(2300, HEIGHT - 250, 100, 20),
            Platform(2500, HEIGHT - 350, 100, 20),
            
            # Final gauntlet - difficult jumps
            Platform(2800, HEIGHT - 300, 70, 20),
            Platform(3000, HEIGHT - 400, 60, 20),
            Platform(3200, HEIGHT - 500, 50, 20),
            Platform(3400, HEIGHT - 400, 50, 20),
            Platform(3600, HEIGHT - 300, 50, 20),
            Platform(3800, HEIGHT - 200, 150, 20)  # Final platform before goal
        ]
        
        # Level 3 enemies - many challenging enemies
        self.enemies = pygame.sprite.Group([
            Enemy(450, HEIGHT - 310),
            Enemy(750, HEIGHT - 570),
            Enemy(1400, HEIGHT - 430),
            Enemy(1700, HEIGHT - 380),
            Enemy(1900, HEIGHT - 280),
            Enemy(2100, HEIGHT - 380),
            Enemy(2300, HEIGHT - 280),
            Enemy(2500, HEIGHT - 380),
            Enemy(3000, HEIGHT - 430),
            Enemy(3400, HEIGHT - 430),
            Enemy(3800, HEIGHT - 230)
        ])
        
        # Level 3 bonus items - strategically placed for risk/reward
        self.bonus_items = pygame.sprite.Group([
            BonusItem(300, HEIGHT - 200),   # Easy coin
            BonusItem(600, HEIGHT - 460),   # Mid-height gem
            BonusItem(750, HEIGHT - 590),   # High-value heart at top
            BonusItem(1100, HEIGHT - 470),  # Risky coin on small platform
            BonusItem(1400, HEIGHT - 450),  # Relief platform bonus
            BonusItem(2100, HEIGHT - 400),  # Mid-zigzag gem
            BonusItem(2500, HEIGHT - 400),  # End-zigzag heart
            BonusItem(3200, HEIGHT - 550),  # Very high gem (difficult)
            BonusItem(3800, HEIGHT - 250),  # Final platform gem
            BonusItem(3900, HEIGHT - 250)   # Final platform heart
        ])
        
        # Level 3 goal
        self.goal = Goal(3900, HEIGHT - 100)
        
        # Add secret areas to Level 3 - most valuable ones
        self.secret_areas = [
            SecretArea(500, HEIGHT - 600, 100, 300, 600),    # Hidden high area
            SecretArea(2000, HEIGHT - 400, 200, 150, 800),   # Hidden in zigzag section
            SecretArea(3500, HEIGHT - 600, 150, 300, 1000),  # Hidden above final challenge
            SecretArea(3850, HEIGHT - 300, 100, 280, 1500)   # Secret near goal (super bonus)
        ]

class LevelManager:
    def __init__(self):
        self.current_level_num = 1
        self.levels = {
            1: Level1(),
            2: Level2(),
            3: Level3()
        }
    
    def get_current_level(self):
        return self.levels[self.current_level_num]
    
    def get_current_level_num(self):
        return self.current_level_num
    
    def next_level(self):
        self.current_level_num += 1
        if self.current_level_num > len(self.levels):
            return False  # No more levels
        return True
    
    def reset(self):
        self.current_level_num = 1

def show_level_transition_screen(current_level, next_level, score):
    """Display a transition screen between levels"""
    transition_font = pygame.font.Font(None, 48)
    
    screen.fill((0, 0, 0))
    
    # Show level completion message
    complete_text = transition_font.render(f"Level {current_level} Complete!", True, GREEN)
    screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 3))
    
    # Show score
    score_text = transition_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    
    # Show next level message
    next_text = transition_font.render(f"Preparing Level {next_level}...", True, YELLOW)
    screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT * 2 // 3))
    
    # Show continue prompt
    prompt_text = font.render("Press ENTER to continue", True, LIGHT_GRAY)
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT - 100))
    
    pygame.display.flip()
    
    # Wait for enter key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

def main():
    global screen, start_time
    
    # Initialize level manager
    level_manager = LevelManager()
    current_level_num = level_manager.get_current_level_num()
    level = level_manager.get_current_level()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    player = Player()
    all_sprites = level.get_all_sprites()
    all_sprites.add(player)

    start_time = time.time()
    running = True
    game_over_reason = ""
    paused_time = 0  # Track paused time
    is_dying = False  # New flag to track dying state
    
    # Celebration state variables
    celebrating = False
    celebration_start_time = 0
    CELEBRATION_DURATION = 5.0  # seconds to celebrate at goal
    celebration_jump_timer = 0  # Timer for automatic celebration jumps
    
    # Secret area discovery tracking
    discovered_secret = False
    discovery_message = ""
    discovery_time = 0
    
    while running:
        screen.fill((0, 0, 0))
        
        # Render the background with parallax scrolling
        level.background.render(screen, player.camera_x)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return "start_screen"
            elif event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.w, event.h
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

        # Calculate elapsed time, but don't increment while dying
        if is_dying:
            elapsed_time = paused_time
        else:
            elapsed_time = time.time() - start_time
            
        if elapsed_time > TIME_LIMIT and not is_dying and not celebrating:
            print("Time's up! Game Over.")
            game_over_reason = "time_up"
            running = False
        
        # Check if celebration period is over
        if celebrating:
            celebration_elapsed = time.time() - celebration_start_time
            if celebration_elapsed >= CELEBRATION_DURATION:
                # Instead of going to game over, check for next level
                if level_manager.get_current_level_num() < len(level_manager.levels):
                    # Show transition screen
                    show_level_transition_screen(
                        current_level_num,
                        current_level_num + 1,
                        player.score
                    )
                    
                    # Move to next level
                    level_manager.next_level()
                    current_level_num = level_manager.get_current_level_num()
                    level = level_manager.get_current_level()
                    
                    # Reset player position but keep score
                    player.rect.midbottom = (100, HEIGHT - 50)
                    player.camera_x = 0
                    player.vel_y = 0
                    player.on_ground = True
                    
                    # Reset celebration state
                    celebrating = False
                    
                    # Update sprites
                    all_sprites = level.get_all_sprites()
                    all_sprites.add(player)
                    
                    # Reset timer
                    start_time = time.time()
                    
                    # Continue the game loop
                    continue
                else:
                    # No more levels, player wins the game
                    running = False
                    return show_game_over_screen(True, "completed_all_levels", player.score, player.lives)
            
            # Automatic jumping during celebration
            if player.on_ground:
                celebration_jump_timer += 1
                # Make the player jump automatically every 30 frames (about half a second)
                if celebration_jump_timer >= 30:
                    player.vel_y = JUMP_STRENGTH
                    player.on_ground = False
                    celebration_jump_timer = 0  # Reset timer
            
            # Apply gravity and handle vertical movement only
            player.vel_y += GRAVITY
            player.rect.y += player.vel_y
            
            # Check ground and platform collisions for jumping
            player.on_ground = False
            for platform in level.platforms:
                if player.rect.colliderect(platform.rect) and player.vel_y > 0:
                    player.rect.bottom = platform.rect.top
                    player.vel_y = 0
                    player.on_ground = True
            
            # Update animation state for celebration jumps
            if not player.on_ground:
                if player.vel_y < 0:
                    player.current_state = "jump"
                else:
                    player.current_state = "fall"
            else:
                # When on ground, use idle animation 
                player.current_state = "idle"
            
            player.update_animation()
        elif not is_dying:
            # Normal gameplay update
            if not player.alive:
                # Player just died, enter dying state
                is_dying = True
                paused_time = elapsed_time  # Store the time when death happened
                
            # Update player, platforms, enemies, etc. during normal gameplay
            player.update(level.platforms, level.enemies, level.bonus_items, all_sprites)
            
            # Only update enemies in normal gameplay
            removed_enemies = []
            for enemy in level.enemies:
                enemy.update()
                # Check if enemy was removed (went off-screen)
                if enemy not in level.enemies:
                    removed_enemies.append(enemy)
            
            # Respawn new enemies for any that were removed
            for _ in removed_enemies:
                new_x = random.randint(0, 3000)
                new_enemy = Enemy(new_x, HEIGHT - 50)
                level.enemies.add(new_enemy)
                all_sprites.add(new_enemy)
                
            # Check if the player has reached the goal
            if player.rect.colliderect(level.goal.rect):
                print("Goal reached! Starting celebration period!")
                celebrating = True
                celebration_start_time = time.time()
                
                # Remove the goal object from the game
                all_sprites.remove(level.goal)
                
                # Create a safe platform for the player to stand on where the goal was
                celebration_platform = Platform(
                    level.goal.rect.x - 20,  # Slightly wider than the goal
                    level.goal.rect.bottom,  # Place at the bottom of where the goal was
                    100,  # Make the platform wider for celebration
                    20    # Standard platform height
                )
                level.platforms.append(celebration_platform)
                all_sprites.add(celebration_platform)
                
                # Position the player on top of where goal was
                player.rect.midbottom = (level.goal.rect.midtop[0], level.goal.rect.top)
                player.vel_y = 0
                player.on_ground = True

            # If player falls below screen or goes past goal's right side
            if player.rect.left > level.goal.rect.right or player.rect.bottom > HEIGHT:
                player.lose_life()
                # If player just died, enter dying state
                if not player.alive:
                    is_dying = True
                    paused_time = elapsed_time
        else:
            # Dying state - only update player death animation
            game_over_from_death = player.update_death_animation()
            if game_over_from_death:
                game_over_reason = "lives_lost"
                running = False

        # Check for secret areas during normal gameplay
        if not is_dying and not celebrating:
            for secret_area in level.secret_areas:
                if secret_area.check_player_entry(player):
                    discovered_secret = True
                    discovery_message = f"Secret Area Found! +{secret_area.reward} points!"
                    discovery_time = time.time()
        
        # Render everything
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - player.camera_x, sprite.rect.y))
        
        # Render secret areas (will only be visible after discovery)
        for secret_area in level.secret_areas:
            secret_area.draw(screen, player.camera_x)
        
        # Display HUD with current level number
        draw_hud(screen, player.score, player.lives, elapsed_time, current_level_num)
        
        # Display secret area discovery message if needed
        if discovered_secret and time.time() - discovery_time < 3:  # Show for 3 seconds
            discovery_text = font.render(discovery_message, True, YELLOW)
            screen.blit(discovery_text, (WIDTH // 2 - discovery_text.get_width() // 2, 150))
        else:
            discovered_secret = False
            
        # Display celebration message if celebrating
        if celebrating:
            celebration_text = font.render("Level Complete!", True, YELLOW)
            screen.blit(celebration_text, (WIDTH // 2 - celebration_text.get_width() // 2, 200))
            
            # Add additional congratulatory text
            bonus_text = font.render(f"Bonus: +{player.score // 10}", True, GREEN)
            screen.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, 250))

        pygame.display.flip()
        clock.tick(60)
    
    # If we get here, the game is over
    if game_over_reason:
        return show_game_over_screen(False, game_over_reason, player.score, player.lives)
    
    return "start_screen"

def game_loop():
    """Main game loop manager that handles different game states"""
    global player_name

    current_state = "splash_screen"
    
    while True:
        if current_state == "splash_screen":
            show_splash_screen()
            current_state = "start_screen"
        elif current_state == "start_screen":
            show_intro_screen()
            current_state = "main_game"
        elif current_state == "main_game":
            current_state = main()
        else:
            # Unknown state, default to start screen
            current_state = "start_screen"

# Start the game loop
game_loop()
