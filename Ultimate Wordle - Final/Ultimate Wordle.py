import pygame
import ctypes, os
from ctypes import wintypes
from sys import argv
user32 = ctypes.windll.user32
import re, time

from wordle_algorithm import *

# Initialize Pygame
pygame.init()
pygame.display.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

DEBUG_OPTIONS = False

WINDOW_SIZE = (1600, 1000)
TITLE_BAR_HEIGHT = 40
SCROLL_SPEED = 20

# Colors
COLOR_INACTIVE = pygame.Color(48, 48, 48)
COLOR_ACTIVE = pygame.Color(80, 80, 80)
BACKUP_BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (100, 100, 100)

# scroll bar
SCROLL_BAR_COLOR = (100, 100, 100) 
SCROLL_BAR_HOVER_COLOR = (120, 120, 120) 
SCROLL_BAR_ACTIVE_COLOR = (150, 150, 150)

ROBOTO_CON_BLACK = pygame.font.Font('assets/fonts/RobotoCondensed-black.ttf', 140)
ROBOTO_MED = pygame.font.Font('assets/fonts/Roboto-medium.ttf', 26)
ROBOTO_REG = pygame.font.Font('assets/fonts/Roboto-medium.ttf', 20)

# keyboard
KEY_WIDTH = 65
KEY_HEIGHT = 80
KEY_MARGIN = 5
PADDING = 20
NUM_KEYS_PER_ROW = 10
NUM_ROWS = 3
KEYBOARD_WIDTH = (KEY_WIDTH + KEY_MARGIN) * NUM_KEYS_PER_ROW - KEY_MARGIN + PADDING * 2
KEYBOARD_HEIGHT = (KEY_HEIGHT + KEY_MARGIN) * NUM_ROWS - KEY_MARGIN + PADDING * 2
KEYBOARD_X = (1600 - KEYBOARD_WIDTH) // 2
KEYBOARD_Y = 710

TOGGLE_BUTTON_RECT = pygame.Rect(100, 900, 100, 50)
UPDATE_BUTTON_RECT = pygame.Rect(250, 900, 100, 50)

# Key colors and hover effect
KEY_COLORS = {
    "default": (166, 166, 166),
    "dark_grey": (80, 80, 80),
    "yellow": (200, 200, 20),
    "green": (83, 141, 78)
}
KEYBOARD_BG_COLOR = (20, 20, 20)
KEYBOARD_BORDER_COLOR = (34, 34, 34)
HOVER_COLOR = (145, 145, 145)

# detection for keys (ignored)
IGNORED_KEYS = [
    pygame.K_LSUPER, pygame.K_RSUPER,  # Windows/Super/Meta keys
    pygame.K_LMETA, pygame.K_RMETA,    # Command/Meta keys for Mac
    pygame.K_CAPSLOCK,
    pygame.K_TAB,
    #pygame.K_ESCAPE,
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_PRINT, pygame.K_SYSREQ,   # Print Screen/SysRq
    pygame.K_INSERT,
    pygame.K_DELETE,
    pygame.K_HOME, pygame.K_END,       # Home and End keys
    pygame.K_PAGEUP, pygame.K_PAGEDOWN,
    pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4,  # Function keys
    pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8,
    pygame.K_F9, pygame.K_F10, pygame.K_F11, pygame.K_F12,
    pygame.K_NUMLOCK, pygame.K_SCROLLOCK,
    pygame.K_PAUSE,
]

# Set the display mode with resizable and no frame flags
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE | pygame.NOFRAME, 32)
pygame.display.set_caption("ULTIMATE WORDLE")

window_icon = pygame.image.load('assets\graphics\window_icon.png')
pygame.display.set_icon(window_icon)

# Clock to manage frame rate
clock = pygame.time.Clock()

def setup_word_lists():
    GAME_moderatedWord_dict = {}
    GAME_completeWord_dict = {}

    for mode in ['moderated', 'complete']:
        for length in range(4, 6):  #4-5 
            wordImport_file = open(f'assets/{length}_wordList_{mode}.txt', "r" )
            wordImport_word = wordImport_file.read()
            
            if mode == 'moderated':
                GAME_moderatedWord_dict[length] = re.findall(r'\b\w+\b', wordImport_word)
            if mode == 'complete':
                GAME_completeWord_dict[length] = re.findall(r'\b\w+\b', wordImport_word)
            #setattr(self, f"_{length}_wordList_{mode}", re.findall(r'\b\w+\b', wordImport_word))
            wordImport_file.close()

    return GAME_moderatedWord_dict, GAME_completeWord_dict

# Function to set window position (Windows OS specific)
def set_window_position(x, y):
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001)

def background_reference():
    img = pygame.image.load('assets/refernece planning photo.jpg')
    image_width, image_height = 1820, 1200

    if image_height > user32.GetSystemMetrics(1) * 0.8:  # Adjust to screen size
        image_width = image_width * (user32.GetSystemMetrics(1)) / image_height
        image_height = user32.GetSystemMetrics(1) * 0.9

    img = pygame.transform.scale(img, (int(image_width), int(image_height)))
    imgrect = img.get_rect(x=-30, y=20)
    return img, imgrect  # Return image and its rectangle


class ScrollBar:
    def __init__(self, window_height, content_height):
        self.window_height = window_height
        self.content_height = content_height
        self.scroll_y = 0
        self.dragging = False
        self.bar_rect = pygame.Rect(WINDOW_SIZE[0] - 20, TITLE_BAR_HEIGHT, 15, self.calculate_bar_height())
        self.color = SCROLL_BAR_COLOR  # default colour

    def calculate_bar_height(self):
        # Bar height based on the ratio of window height to content height
        ratio = self.window_height / self.content_height
        return max(50, self.window_height * ratio)  # Ensure a minimum height

    def update_bar_position(self):
        # Calculate slider bar position based on scroll position
        scroll_ratio = -self.scroll_y / (self.content_height - self.window_height)
        self.bar_rect.y = TITLE_BAR_HEIGHT + int(scroll_ratio * (self.window_height - self.bar_rect.height))
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # if mouse is hovered 
        if self.bar_rect.collidepoint(mouse_pos):
            self.color = SCROLL_BAR_HOVER_COLOR
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.dragging = True
                self.mouse_y_offset = event.pos[1] - self.bar_rect.y
            if event.type == pygame.MOUSEBUTTONUP:
                self.color = SCROLL_BAR_HOVER_COLOR
                self.dragging = False
        else:
            self.color = SCROLL_BAR_COLOR

        if self.dragging:
            self.color = SCROLL_BAR_ACTIVE_COLOR

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.mouse_y_offset
            # Constrain the slider within the window height
            self.bar_rect.y = max(TITLE_BAR_HEIGHT, min(new_y, self.window_height - self.bar_rect.height))
            # Calculate the new scroll position based on slider position
            scroll_ratio = (self.bar_rect.y - TITLE_BAR_HEIGHT) / (self.window_height - self.bar_rect.height)
            self.scroll_y = -scroll_ratio * (self.content_height - self.window_height)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.bar_rect, border_radius = 7)
    
    def update_scroll(self, scroll_delta):
        # Update scroll position with mouse wheel and update the slider bar
        self.scroll_y = max(min(self.scroll_y + scroll_delta, 0), -(self.content_height - 500))
        self.update_bar_position()


class NotificationOverlay:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.notification_text = None
        self.notification_start_time = None
        self.notification_rect = None
        self.notification_duration = 1.6
        self.padding = 20  # Padding around the text
        self.bg_color = (55, 55, 55)  # Background color
        self.outline_color = (67, 67, 67)  # Outline stroke color
        self.progress_bar_height = 8  # Height of the progress bar
        self.progress_bar_color = (100, 100, 100)

    def show_notification(self, text, notification_duration=5):
        print('processed notifcation')
        self.notification_duration = notification_duration
        # Reset notification timer
        self.notification_text = text
        self.notification_start_time = time.time()

        # Calculate size of the notification box based on the text
        text_surface = self.font.render(text, True, (200, 200, 200))
        text_rect = text_surface.get_rect()

        # Create a notification box with padding and rounded corners
        box_width = text_rect.width + self.padding * 3
        box_height = text_rect.height + self.padding * 2

        # Center the notification box on the screen
        self.notification_rect = pygame.Rect(
            (WINDOW_SIZE[0] - box_width) // 2,
            TITLE_BAR_HEIGHT + 14,
            box_width,
            box_height
        )

    def draw_notification(self):
        if self.notification_text:
            current_time = time.time()
            elapsed_time = current_time - self.notification_start_time

            # Check if the notification is still active (4 seconds)
            if elapsed_time <= self.notification_duration:                
                # Draw rounded rectangle for the notification background
                pygame.draw.rect(self.screen, self.bg_color, self.notification_rect, border_radius=8)
                
                # Draw the outline stroke around the notification
                pygame.draw.rect(self.screen, self.outline_color, self.notification_rect, 3, border_radius=8)

                # Render the text and center it inside the notification box
                text_surface = self.font.render(self.notification_text, True, (210, 210, 210))
                text_rect = text_surface.get_rect(center=self.notification_rect.center)
                self.screen.blit(text_surface, text_rect)
                progress_bar_width = int(self.notification_rect.width * (1 - elapsed_time / self.notification_duration))

                # Draw the progress bar
                progress_bar_rect = pygame.Rect(
                    self.notification_rect.x,
                    self.notification_rect.bottom - self.progress_bar_height,
                    progress_bar_width,
                    self.progress_bar_height
                )
                pygame.draw.rect(self.screen, self.progress_bar_color, progress_bar_rect, border_radius=3)

            else:
                # Reset if time exceeds 4 seconds
                self.notification_text = None
                self.notification_start_time = None


class letterSelection:
    def __init__(self, previousValue):
        self.previousValue = previousValue
        self.default_status = True
        self.current_slider_y = None  # To store the slider button's y position
        self.letter_length = 5
        self.sliderValue_update = False

    def display_guide(self):
        
        gameplay_guide_txt = f"Guess the {self.letter_length} letter word"

        text_surface = pygame.Surface((WINDOW_SIZE[0], 50), pygame.SRCALPHA)  # 50 is the height of the text area
        text_surface.fill((0, 0, 0, 0))  # Fully transparent fill
        
        # Render the text
        display_text = ROBOTO_MED.render(gameplay_guide_txt, True, '#5C5C5C')
        
        # Calculate text position (in this case, we place it at a fixed y position)
        text_rect = display_text.get_rect(topleft=(58, 925))

        # Blit the text onto the transparent surface
        text_surface.blit(display_text, text_rect)


        pygame.display.update(screen.blit(display_text, (58, 925)))
        
    def sliderBar_rectangle(self):
        pygame.draw.rect(screen, "#151515", (-20, 228, 170, 590), 0, 14)
        pygame.draw.rect(screen, "#1E1E1E", (-20, 228, 170, 590), 2, 14)

    def sliderBar_slider(self, sx, sy, width, height, action,  # complete slider bar positions (pyRect attr)
                         buttonColor, buttonBorderThickness, buttonWidth,                                 # slider button customizations
                         sliderBarColor, sliderBarBorderThickness, sliderBarWidth,                        # background line customizations
                         sliderStepColor, sliderStepBorderThickness, sliderStepWidth, sliderStepHeight,   # toggle drag step customizations
                         maxValue, is_init=False, startValue=0, sliderBar_locked = False):  # slider attributes
        self.sliderValue_update = False
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Always update the visuals every frame
        # Draw the vertical slider bar
        pygame.draw.rect(screen, sliderBarColor, (sx + width // 2 - sliderBarWidth // 2, sy, sliderBarWidth, height - sliderStepWidth // 2))
        if sliderBarBorderThickness != 0:
            pygame.draw.rect(screen, sliderBarColor, (sx + width // 2 - sliderBarWidth // 2, sy, sliderBarWidth, height - sliderStepWidth), sliderBarBorderThickness)

        # Draw the vertical slider steps as circles
        step = (height - buttonWidth) / (maxValue - 1)
        for i in range(maxValue):
            stepY = sy + i * step
            pygame.draw.circle(screen, sliderStepColor, (sx + width // 2, int(stepY)), sliderStepWidth // 2)
            if sliderStepBorderThickness != 0:
                pygame.draw.circle(screen, (65, 65, 65), (sx + width // 2, int(stepY)), sliderStepWidth // 2, sliderStepBorderThickness)

        # Initialize the slider button position at startup
        if is_init and self.current_slider_y is None:
            self.current_slider_y = sy + startValue * step

        # Redraw the slider button every frame at the current stored position
        pygame.draw.circle(screen, buttonColor, (sx + buttonWidth + (buttonWidth// 7.5), int(self.current_slider_y)), buttonWidth)
        if buttonBorderThickness != 0:
            pygame.draw.rect(screen, (0, 0, 0), (sx, self.current_slider_y, width, buttonWidth), buttonBorderThickness)

        pygame.display.update(pygame.Rect(sx - 20, sy - sliderStepWidth // 2 - 20, width + 50, height + sliderStepWidth + 50))

        self.display_guide()

        # Handle slider movement interaction
        if sx - 60 <= mouse[0] <= sx + width + 60 and sy - 150 <= mouse[1] <= sy + height + 150:
            if click[0] == 1:
                if sliderBar_locked:
                    return True
                
                self.default_status = False
                mouseY = mouse[1] - 5
                # Snap to steps
                if mouseY < sy:
                    mouseY = sy
                elif mouseY > sy + height - buttonWidth:
                    mouseY = sy + height - buttonWidth
                else:
                    mouseY = round((mouseY - sy) / step) * step + sy

                # Update the current slider button y position
                self.current_slider_y = mouseY

                # Calculate the new slider value
                self.sliderValue = (mouseY - sy) / ((height - buttonWidth) / (maxValue - 1))
                if self.sliderValue != self.previousValue:
                    if action == "int-slider":
                        self.letter_length = int(self.sliderValue + 3)
                        self.sliderValue_update = True

                    self.previousValue = self.sliderValue

# Input box class
class InputBox:

    def __init__(self, x, y, w, h, text='', background_color='grey'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE  # Outline color
        self.text_color = (255, 255, 255)  # Text color (set to white initially)
        self.text = text
        self.background_color = self.get_color(background_color)  # Set initial background color
        self.max_font_size = 110  # Set the maximum zoomed-in size (bigger size for animation)
        self.current_font_size = 30  # Starting font size
        self.zoom_in_speed = 30  # Speed of the zooming animation
        self.zooming_in = False  # Flag to start/stop zooming effect
        self.txt_surface = pygame.font.Font('assets/fonts/RobotoCondensed-black.ttf', self.current_font_size).render(self.text, True, self.text_color)
        self.active = False
        self.locked = False

    def get_color(self, color_name):
        # Helper function to convert color names to actual RGB values
        colors = {
            'yellow': (229, 201, 56),
            'green': (90, 143, 57),
            'grey': (40, 40, 40),
            'input_nonwithin': (70, 70, 70)
        }
        return colors.get(color_name.lower(), (128, 128, 128))  # Default to grey

    def update_background_color(self, color_name):
        # Dynamically update background color
        self.background_color = self.get_color(color_name)

    def handle_event(self, event, scroll_offset_y, game, row, current_box_index, keyboard_rect):  #Handle events, including keyboard and mouse events.
        if self.locked:
            return  # Ignore input if the box is locked

        # Adjust rect for scrolling and title bar offset
        adjusted_rect = self.rect.move(0, scroll_offset_y + TITLE_BAR_HEIGHT)

        # Mouse click event to toggle active state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            adjusted_mouse_pos = (event.pos[0], event.pos[1] - scroll_offset_y)

            if keyboard_rect.collidepoint(event.pos):
                return

            if adjusted_rect.collidepoint(adjusted_mouse_pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        # Handle keyboard events when active
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key not in IGNORED_KEYS:
                #if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT]:
                    #return
                current_time = pygame.time.get_ticks()
                # Ensure input cooldown has passed
                if current_time - game.last_input_time > game.input_cooldown:
                    if event.key == pygame.K_RETURN:
                        if len(self.text) >= 1 and current_box_index+1 == len(row):
                            num_text_full = 0
                            current_row_text = ''
                            for i in range(len(row)):
                                if len(row[i].text) == 1:
                                    current_row_text += row[i].text
                                    num_text_full += 1
                                if num_text_full == len(row):
                                    game.handle_word_check(current_row_text)
                                    print('complete text', current_row_text)


                        #print(self.text)  # Do something with the text (e.g., print or process)
                        #self.text = ''


                    elif event.key == pygame.K_BACKSPACE:
                        self.text = ''  # Clear text if not empty
                        self.current_font_size = 30  # Reset font size for animation
                        game.move_to_previous_box(row, current_box_index)  # Move focus to the previous box

                    if event.unicode.isalpha() or event.unicode.isdigit() or event.unicode in "-*$#@!~`<>":
                        if len(self.text) == 0:  # Ensure only one character per box
                            self.text = event.unicode.upper()  # Convert input to uppercase
                            self.zooming_in = True  # Start zooming effect
                            game.move_to_next_box(row, current_box_index)  # Move focus to the next box
                            game.last_input_time = current_time  # Update input time for cooldown

                        elif len(self.text) >= 1 and current_box_index + 1 < len(row):
                            if len(row[current_box_index+1].text) < 1:
                                row[current_box_index + 1].text = event.unicode.upper()
                                row[current_box_index + 1].zooming_in = True
                                game.move_to_next_box(row, current_box_index)  # Move focus to the next box
                                game.last_input_time = current_time  
                            
                        # Render the text again with updated font size
                    self.txt_surface = pygame.font.Font('assets/fonts/RobotoCondensed-black.ttf', self.current_font_size).render(self.text, True, self.text_color)

    def draw(self, screen, scroll_offset_y):
        # Move the rect vertically according to the scroll offset
        adjusted_rect = self.rect.move(0, scroll_offset_y + TITLE_BAR_HEIGHT)

        # Zoom-in animation: increase font size if zooming is active
        if self.zooming_in and self.current_font_size < self.max_font_size:
            self.current_font_size += self.zoom_in_speed  # Gradually increase font size
            if self.current_font_size >= self.max_font_size:
                self.current_font_size = self.max_font_size  # Cap the font size
                self.zooming_in = False  # Stop zooming once it reaches max size

        # Render the text with the current font size
        current_font = pygame.font.Font('assets/fonts/RobotoCondensed-black.ttf', self.current_font_size)
        self.txt_surface = current_font.render(self.text, True, self.text_color)

        # Calculate position to center the text inside the box
        text_rect = self.txt_surface.get_rect(center=adjusted_rect.center)

        # Draw the rounded background color
        pygame.draw.rect(screen, self.background_color, adjusted_rect, border_radius=7)  # Fill with rounded background

        # Draw the text
        screen.blit(self.txt_surface, text_rect)

        # Draw the rounded outline of the input box with a different color when active
        pygame.draw.rect(screen, self.color, adjusted_rect, 4, border_radius=7)

class Key:
    def __init__(self, letter, x, y, width, height):
        self.letter = letter
        self.rect = pygame.Rect(x, y, width, height)
        self.color = KEY_COLORS["default"]
        self.is_hovered = False

    def draw(self, screen):
        # Hover effect for default-colored keys
        color_to_draw = self.color
        if self.is_hovered and self.color == KEY_COLORS["default"]:
            color_to_draw = HOVER_COLOR

        # Draw key background with rounded corners
        #pygame.draw.rect(screen, (150, 150, 150), self.rect, border_radius=8)  # Light border color
        inner_rect = self.rect.inflate(-5, -5)
        pygame.draw.rect(screen, color_to_draw, inner_rect, border_radius=8)  # Key's actual color

        # Render the letter in the middle of the key
        font = pygame.font.SysFont(None, 40)
        text_surface = font.render(self.letter, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update_color(self, new_color):
        if new_color in KEY_COLORS:
            self.color = KEY_COLORS[new_color]

    def handle_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        

class Keyboard:
    def __init__(self):
        self.keys = {}  # Initialize as an empty dictionary
        self.is_visible = True
        
        # Initialize current states
        self.current_correct = set()
        self.current_within = set()
        self.current_nonwithin = set()

        self.create_keys()

    def update_key_colors(self, correct, within, nonwithin):
        print("Updating key colors...")
        if correct is not None:
            print(f"Correct: {correct}")
            self._update_correct({k.upper(): v for k, v in correct.items()})
        if within is not None:
            print(f"Within: {within}")
            self._update_within({k.upper(): v for k, v in within.items()})
        if nonwithin is not None:
            print(f"Nonwithin: {nonwithin}")
            self._update_nonwithin({k.upper(): v for k, v in nonwithin.items()})

    def _update_correct(self, correct):
        # Update keys with correct color (priority 1: green)
        for letter, _ in correct.items():
            if letter in self.keys:
                if letter not in self.current_correct:
                    self.keys[letter].update_color("green")
                    self.current_correct.add(letter)
                    # Remove from within and nonwithin if present
                    if letter in self.current_within:
                        self.current_within.remove(letter)
                    if letter in self.current_nonwithin:
                        self.current_nonwithin.remove(letter)

    def _update_within(self, within):
        # Update keys with within color (priority 2: yellow)
        for letter, _ in within.items():
            if letter in self.keys:
                if letter not in self.current_correct and letter not in self.current_within:
                    self.keys[letter].update_color("yellow")
                    self.current_within.add(letter)
                    # Remove from nonwithin if present
                    if letter in self.current_nonwithin:
                        self.current_nonwithin.remove(letter)

    def _update_nonwithin(self, nonwithin):
        # Update keys with nonwithin color (priority 3: dark grey)
        for letter, _ in nonwithin.items():
            if letter in self.keys:
                if letter not in self.current_correct and letter not in self.current_within and letter not in self.current_nonwithin:
                    self.keys[letter].update_color("dark_grey")
                    self.current_nonwithin.add(letter)

    def create_keys(self):
        alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"
        x_start = KEYBOARD_X + PADDING
        y_start = KEYBOARD_Y + PADDING
        x, y = x_start, y_start

        row_lengths = [10, 9, 7]  # Number of keys in each row
        row_start_letters = [0, 10, 19]  # Starting index of letters for each row

        for row in range(NUM_ROWS):
            keys_in_row = row_lengths[row]
            letter_index = row_start_letters[row]

            total_row_width = (keys_in_row * KEY_WIDTH) + ((keys_in_row - 1) * KEY_MARGIN)
            x = (KEYBOARD_WIDTH - total_row_width) // 2 + KEYBOARD_X  # Center the row horizontally

            for i in range(keys_in_row):
                if letter_index < len(alphabet):
                    letter = alphabet[letter_index]
                    key = Key(letter, x, y, KEY_WIDTH, KEY_HEIGHT)
                    self.keys[letter] = key
                    x += KEY_WIDTH + KEY_MARGIN
                    letter_index += 1

            y += KEY_HEIGHT + KEY_MARGIN

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def draw(self, screen):
        if self.is_visible:
            pygame.draw.rect(screen, KEYBOARD_BG_COLOR, (KEYBOARD_X, KEYBOARD_Y, KEYBOARD_WIDTH, KEYBOARD_HEIGHT), border_radius=12)
            pygame.draw.rect(screen, KEYBOARD_BORDER_COLOR, (KEYBOARD_X, KEYBOARD_Y, KEYBOARD_WIDTH, KEYBOARD_HEIGHT), 5, border_radius=12)

            for key in self.keys.values():
                key.draw(screen)

    def handle_click(self, mouse_pos):
        for key in self.keys.values():
            if key.rect.collidepoint(mouse_pos):
                return key.letter
        return None

    def handle_hover(self):
        for key in self.keys.values():
            key.handle_hover()





# Create gradient surface for background
def create_gradient_surface(width, height, top_color, bottom_color):
    surface = pygame.Surface((width, height))
    for i in range(height):
        color = [
            top_color[j] + (bottom_color[j] - top_color[j]) * i // height
            for j in range(3)
        ]
        pygame.draw.line(surface, color, (0, i), (width, i))
    return surface

# Add buttons to increase/decrease number of input boxes
def draw_buttons(surface, increase_button, decrease_button, next_row_button):
    pygame.draw.rect(surface, BUTTON_COLOR, increase_button)
    pygame.draw.rect(surface, BUTTON_COLOR, decrease_button)
    pygame.draw.rect(surface, BUTTON_COLOR, next_row_button)
    surface.blit(ROBOTO_REG.render("+", True, (255, 255, 255)), (increase_button.x + 10, increase_button.y))
    surface.blit(ROBOTO_REG.render("-", True, (255, 255, 255)), (decrease_button.x + 10, decrease_button.y))
    surface.blit(ROBOTO_REG.render("row", True, (255, 255, 255)), (next_row_button.x + 10, next_row_button.y))

class UltimateWordle:
    def __init__(self):
        self.initial_pos = (0, 0)
        self.moving = False
        hwnd = pygame.display.get_wm_info()["window"]
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
        self.window_pos = (rect.left, rect.top)

        self.letter_length = 5  # Set initial number of input boxes
        self.letter_selection_mgn = letterSelection(-1)

        self.starting_input_box_y = 180

        self.input_cooldown = 70  # Cooldown time (ms)
        self.last_input_time = 0   # Track the last time an input was accepted

        self.rows_of_input_boxes = []
        self.input_box_height = 145
        self.spacing_between_rows = 10  # Vertical space between each row of input boxes
        self.top_margin = 180
        self.bottom_margin = 500

        self.correct_comparedWord = None
        self.notification = NotificationOverlay(screen, ROBOTO_MED, 800, 600)

        self.content_height = 0
        self.scroll_bar = ScrollBar(WINDOW_SIZE[1], self.content_height + self.bottom_margin)

        # keyboard
        self.keyboard = Keyboard()

        self.current_typable_row = 0
        
    def centered_letter_input_boxes(self, screen_width, num_boxes, box_width, box_height, y_pos):
        input_boxes = []
        # Calculate total width occupied by input boxes and the starting x position to center them
        total_width = num_boxes * box_width + (num_boxes - 1) * self.spacing_between_rows
        start_x = (screen_width - total_width) // 2  # Center the input boxes horizontally

        # Create the input boxes and position them
        for i in range(num_boxes):
            x_pos = start_x + i * (box_width + self.spacing_between_rows)
            input_boxes.append(InputBox(x_pos, y_pos, box_width, box_height))

        return input_boxes
    
    def calculate_scroll_height(self):
        #Calculate the total height occupied by all input box rows including spacing.
        num_rows = len(self.rows_of_input_boxes)
        new_content_height = (num_rows * self.input_box_height)
        return new_content_height

    def update_content_height_and_scrollbar(self):
        """Update the scrollable content height and adjust the scrollbar without resetting scroll."""
        new_content_height = self.calculate_scroll_height()
        if hasattr(self, 'scroll_bar'):
            # Calculate the previous scroll ratio before updating the content height
            previous_scroll_ratio = -self.scroll_bar.scroll_y / (self.scroll_bar.content_height - WINDOW_SIZE[1])
            self.content_height = new_content_height
            self.scroll_bar.content_height = self.content_height + self.bottom_margin
            self.scroll_bar.bar_rect.height = self.scroll_bar.calculate_bar_height()

            # Maintain the scroll position based on the previous ratio
            self.scroll_bar.scroll_y = -previous_scroll_ratio * (self.scroll_bar.content_height - WINDOW_SIZE[1])
            self.scroll_bar.update_bar_position()
        else:
            self.content_height = new_content_height
            self.scroll_bar = ScrollBar(self.content_height + self.bottom_margin)

        self.scroll_surface = pygame.Surface((WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1])))
        self.gradient_surface = create_gradient_surface(WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1]), (22, 22, 22), (7, 7, 7))

    
    def lock_all_rows_except(self, rows_of_input_boxes, row_index):
        """Locks all rows except the one at row_index."""
        for i, row in enumerate(rows_of_input_boxes):
            locked = i != row_index
            for box in row:
                box.active = False  # Deactivate all boxes initially
                box.color = COLOR_INACTIVE
                box.locked = locked

    def auto_focus_first_box(self, row):
        """Auto-focus the first box of the specified row."""
        for box in row:
            box.active = False  # Deactivate all boxes initially
            box.color = COLOR_INACTIVE

        row[0].active = True  # Activate the first box
        row[0].color = COLOR_ACTIVE 

    def move_to_next_box(self, row, current_box_index): #Move focus to the next box after current_box_index, if it exists. 
        if current_box_index + 1 < len(row):
            row[current_box_index].active = False
            row[current_box_index].color = COLOR_INACTIVE
            row[current_box_index + 1].active = True
            row[current_box_index + 1].color = COLOR_ACTIVE 

    def move_to_previous_box(self, row, current_box_index): #Move focus to the previous box before current_box_index, if it exists.
        if current_box_index - 1 >= 0:
            row[current_box_index].active = False
            row[current_box_index].color = COLOR_INACTIVE
            row[current_box_index - 1].active = True
            row[current_box_index - 1].color = COLOR_ACTIVE

    def update_active_box_with_key(self, key_pressed):
        for row in self.rows_of_input_boxes:
            for box in row:
                if box.active:  # Find the active input box
                    if len(box.text) == 0:  # Ensure only one character per box
                        box.text = key_pressed.upper()  # Convert to uppercase
                        box.zooming_in = True  # Start zooming effect
                        self.move_to_next_box(row, row.index(box))  # Move focus to the next box
                        return  # Exit after updating the active box
                    
    def handle_word_check(self, user_input_guess):
        input_is_valid = False
        if self.correct_comparedWord == None:
            for key, value in GAME_MODERATEDWORD_DICT.items():
                if key == self.letter_length:
                    random_index = random.randint(0, len([item for item in value if item]) - 1)
                    print('correct word @' , random_index, value[random_index])
                    self.correct_comparedWord = value[random_index]

        if type(user_input_guess) == str:
            user_input_guess = user_input_guess.lower()
            for key, value in GAME_COMPLETEWORD_DICT.items():
                if key == self.letter_length:
                    if user_input_guess in [item for item in value if item]:
                        input_is_valid = True

        if not input_is_valid:
            self.notification.show_notification("Please enter a valid word! ", 2)
        else:
            self.wordle_algorithm = wordleAlgorithm(self.correct_comparedWord)
            word_to_algorithm_analysis = self.wordle_algorithm.analyse(user_input_guess)
            self.keyboard.update_key_colors(correct=word_to_algorithm_analysis[0], within=word_to_algorithm_analysis[1], nonwithin=word_to_algorithm_analysis[2])
            
            for index in range(self.letter_length):
                if word_to_algorithm_analysis[3][index] == '-w-':
                    self.rows_of_input_boxes[self.current_typable_row][index].update_background_color('yellow')
                if word_to_algorithm_analysis[3][index] == '-c-':
                    self.rows_of_input_boxes[self.current_typable_row][index].update_background_color('green')
                if word_to_algorithm_analysis[3][index] == '-n-':
                    self.rows_of_input_boxes[self.current_typable_row][index].update_background_color('input_nonwithin')


            if not word_to_algorithm_analysis[4]:
                self.current_typable_row += 1
                if self.current_typable_row == len(self.rows_of_input_boxes) -1:
                    # We're about to make the last row typable, so generate a new row
                    new_y_pos = self.rows_of_input_boxes[-1][0].rect.y + self.input_box_height
                    self.rows_of_input_boxes.append(self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, new_y_pos))

                    self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)
                    self.auto_focus_first_box(self.rows_of_input_boxes[self.current_typable_row])

                    self.update_content_height_and_scrollbar()
                    self.scroll_surface = pygame.Surface((WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1])))
                    self.gradient_surface = create_gradient_surface(WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1]), (22, 22, 22), (7, 7, 7))

                else:
                    self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)
                    self.auto_focus_first_box(self.rows_of_input_boxes[self.current_typable_row])  # Lock the current row and unlock the next row
            if word_to_algorithm_analysis[4] == True:
                if self.current_typable_row == 0:
                    self.notification.show_notification(f"You guessed it in {self.current_typable_row+1} attempt?!! What? Press 'new game' to play again (:", 7)
                if self.current_typable_row < 3:
                    self.notification.show_notification(f"You guessed it in {self.current_typable_row+1} attempts!  Press 'new game' to play again (:", 7)
                else:
                    self.notification.show_notification(f"You guessed it! Press 'new game' to play again & beat your current {self.current_typable_row+1} attempts...", 12)



    def game_menu(self, started_new_game):
        if started_new_game:
            self.notification.show_notification("Started a new game! ", 2)

        background_visible = False # for debugging
        sliderBar_firstLoop = True # initialsing slider bar setup

        # Initially create a list of input boxes aligned horizontally
        self.rows_of_input_boxes = [self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, self.starting_input_box_y + i * self.input_box_height) for i in range(5)]
        self.lock_all_rows_except(self.rows_of_input_boxes, 0) # Lock all rows except the first one
        self.update_content_height_and_scrollbar()

        increase_button = pygame.Rect(50, 10, 30, 30)
        decrease_button = pygame.Rect(100, 10, 30, 30)
        next_row_button = pygame.Rect(150, 10, 30, 30)

        round_button_radius = 44
        new_game_icon = pygame.image.load('assets\graphics\\resignFlag_icon.png')
        new_game_icon = pygame.transform.scale(new_game_icon, (50, 50))
        new_game_icon.set_alpha(225 * 0.80)

        keyboard_icon = pygame.image.load('assets\graphics\\keyboard_icon.png')
        keyboard_icon = pygame.transform.scale(keyboard_icon, (50, 50))
        keyboard_icon.set_alpha(225 * 0.80)


        new_game_button = pygame.Rect(WINDOW_SIZE[0] - 130, WINDOW_SIZE[1] - 230, round_button_radius * 2, round_button_radius * 2)
        keyboard_button = pygame.Rect(WINDOW_SIZE[0] - 130, WINDOW_SIZE[1] - 125, round_button_radius * 2, round_button_radius * 2)


        self.current_typable_row = 0  # Keep track of which row is currently typable
        self.auto_focus_first_box(self.rows_of_input_boxes[self.current_typable_row])  # Auto-focus the first box of the first row

        # Create the scrollable surface
        self.scroll_surface = pygame.Surface((WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1])))
        self.gradient_surface = create_gradient_surface(WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1]), (22, 22, 22), (7, 7, 7))


        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos
            current_time = pygame.time.get_ticks()
            if self.current_typable_row >= 1:
                sliderBar_locked = True
            else:
                sliderBar_locked = False


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle input box events for each row with correct scroll offset
                for row in self.rows_of_input_boxes:
                    for i, box in enumerate(row):
                        box.handle_event(event, self.scroll_bar.scroll_y, self, row, i,pygame.draw.rect(screen, KEYBOARD_BG_COLOR, (KEYBOARD_X, KEYBOARD_Y, KEYBOARD_WIDTH, KEYBOARD_HEIGHT), border_radius=12))

                if event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] <= TITLE_BAR_HEIGHT:
                    self.moving = True
                    mouse_x, mouse_y = event.pos
                    self.initial_pos = (mouse_x, mouse_y)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.moving = False

                elif event.type == pygame.MOUSEMOTION and self.moving:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - self.initial_pos[0]
                    dy = mouse_y - self.initial_pos[1]
                    new_x = self.window_pos[0] + dx
                    new_y = self.window_pos[1] + dy
                    set_window_position(new_x, new_y)
                    self.window_pos = (new_x, new_y)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        background_visible = not background_visible

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if DEBUG_OPTIONS:
                        if TOGGLE_BUTTON_RECT.collidepoint(event.pos):
                            #self.keyboard.update_key_colors(correct={'x': 1, 'e': 1}, within={'l': 4, 'e':2}, nonwithin={'y': 2, 'a': 5, 'z': 6})
                            self.keyboard.toggle_visibility()

                        # Update keyboard colors when clicking the update button
                        if UPDATE_BUTTON_RECT.collidepoint(event.pos):
                            self.keyboard.update_key_colors(correct={'a': 1, 'b': 3}, within={'c': 2, 'd': 4}, nonwithin={'e': 1, 'f': 5})

                        if increase_button.collidepoint(event.pos) and len(self.rows_of_input_boxes[-1]) < 7:
                            self.letter_length = len(self.rows_of_input_boxes[-1]) + 1
                            # Increase the number of boxes in the current row
                            self.rows_of_input_boxes = [self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, self.starting_input_box_y + i * self.input_box_height) for i in range(len(self.rows_of_input_boxes))]
                            self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)

                        if decrease_button.collidepoint(event.pos) and len(self.rows_of_input_boxes[-1]) > 3:
                            self.letter_length = len(self.rows_of_input_boxes[-1]) - 1
                            # Decrease the number of boxes in the current row
                            self.rows_of_input_boxes = [self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, self.starting_input_box_y + i * self.input_box_height) for i in range(len(self.rows_of_input_boxes))]
                            self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)

                        if next_row_button.collidepoint(event.pos):
                            # lock all rows except the next
                            self.current_typable_row += 1 # auto focus the 1st box of next row

                            if self.current_typable_row == len(self.rows_of_input_boxes):
                                # We're about to make the last row typable, so generate a new row
                                new_y_pos = self.rows_of_input_boxes[-1][0].rect.y + self.input_box_height
                                self.rows_of_input_boxes.append(self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, new_y_pos))

                                self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row-1)
                                self.auto_focus_first_box(self.rows_of_input_boxes[self.current_typable_row-1])

                                self.update_content_height_and_scrollbar()
                                self.scroll_surface = pygame.Surface((WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1])))
                                self.gradient_surface = create_gradient_surface(WINDOW_SIZE[0], max(self.content_height + self.bottom_margin, WINDOW_SIZE[1]), (22, 22, 22), (7, 7, 7))

                            else:
                                self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)
                                self.auto_focus_first_box(self.rows_of_input_boxes[self.current_typable_row])  # Lock the current row and unlock the next row
                    
                    if keyboard_button.collidepoint(event.pos):
                        self.keyboard.toggle_visibility()

                    if new_game_button.collidepoint(event.pos):
                        return True

                    if self.keyboard.is_visible:
                        key_pressed = self.keyboard.handle_click(event.pos)
                        if key_pressed:
                            self.update_active_box_with_key(key_pressed)

                    if event.button == 4:
                        self.scroll_bar.scroll_y = min(self.scroll_bar.scroll_y + SCROLL_SPEED, 0)
                        self.scroll_bar.update_scroll(SCROLL_SPEED)
                    elif event.button == 5:
                        self.scroll_bar.scroll_y = max(self.scroll_bar.scroll_y - SCROLL_SPEED, -(self.content_height - self.bottom_margin - 20))
                        self.scroll_bar.update_scroll(-SCROLL_SPEED)

                self.scroll_bar.handle_event(event)  # Get pressed 'event' within the scroll function
                self.keyboard.handle_hover()

            if self.letter_selection_mgn.sliderValue_update:
                self.letter_length = self.letter_selection_mgn.letter_length
                self.rows_of_input_boxes = [self.centered_letter_input_boxes(WINDOW_SIZE[0], self.letter_length, 120, 120, self.starting_input_box_y + i * self.input_box_height) for i in range(len(self.rows_of_input_boxes))]
                self.lock_all_rows_except(self.rows_of_input_boxes, self.current_typable_row)



            """"""
            # Clear the scroll surface by re-blitting the gradient or filling with a color
            self.scroll_surface.fill((0, 0, 0))  # Clear with black background
            self.scroll_surface.blit(self.gradient_surface, (0, 0))  # Re-blit the gradient background

            # Draw input boxes on the scroll surface
            for row in self.rows_of_input_boxes:
                for box in row:
                    box.draw(self.scroll_surface, self.scroll_bar.scroll_y)

            # Draw the scrolling surface
            screen.fill(BACKUP_BG_COLOR)
            screen.blit(self.scroll_surface, (0, self.scroll_bar.scroll_y))  # Scroll content from (0, 0)

            self.scroll_bar.draw(screen)

            if False:  # update scroll for content height changes 
                self.content_height = new_content_height
                self.scroll_bar = ScrollBar(WINDOW_SIZE[1], self.content_height)

            if background_visible:
                background_img, background_rect = background_reference()
                screen.blit(background_img, background_rect)

            """ SNAPPING SLIDER BAR """
            self.letter_selection_mgn.sliderBar_rectangle()

            if sliderBar_firstLoop:
                if self.letter_selection_mgn.sliderBar_slider(50, 330, 50, 400, "int-slider", 
                                (144, 144, 144), 0, 23,
                                (51, 51, 51), 0, 10,
                                (58, 58, 58), 2, 33, 3, 
                                5, is_init=True, startValue=2, sliderBar_locked=sliderBar_locked) == True:
                    self.notification.show_notification(f"Already in a game.. Press 'new game' button to change word length! ", 6)

                sliderBar_firstLoop = False
            
            # Handle slider interaction
            if self.letter_selection_mgn.sliderBar_slider(50, 330, 50, 400, "int-slider", 
                            (144, 144, 144), 0, 23,
                            (51, 51, 51), 0, 10,
                            (58, 58, 58), 2, 33, 3, 
                            5, is_init=False, startValue=2, sliderBar_locked=sliderBar_locked) ==  True:
                self.notification.show_notification(f"Already in a game.. Press 'new game' button to change word length! ", 6)
            

            ''' TOP MOST OVERLAY '''

            self.keyboard.draw(screen)
            self.notification.draw_notification()

            # Draw title bar last so it overlays the scrollable content
            pygame.draw.rect(screen, (40, 40, 40), (0, 0, WINDOW_SIZE[0], TITLE_BAR_HEIGHT))  # Title bar
            screen.blit(ROBOTO_REG.render(f"Ultimate Wordle ({self.letter_length}-letter words)", True, (161, 160, 160)), (20, TITLE_BAR_HEIGHT // 2 - 10))

            #new game button
            #pygame.draw.rect(screen, BUTTON_COLOR, new_game_button)
            new_game_button_center = (new_game_button.x + round_button_radius, new_game_button.y + round_button_radius)
            pygame.draw.circle(screen, (48, 48, 48), new_game_button_center, round_button_radius)
            pygame.draw.circle(screen, (40, 40, 40), new_game_button_center, round_button_radius - 5)
            icon_x = new_game_button.x + (new_game_button.width - new_game_icon.get_width()) // 2  # Blit the reset icon in the center of the button
            icon_y = new_game_button.y + (new_game_button.height - new_game_icon.get_height()) // 2
            screen.blit(new_game_icon, (icon_x, icon_y))


            keyboard_button_center = (keyboard_button.x + round_button_radius, keyboard_button.y + round_button_radius)
            pygame.draw.circle(screen, (48, 48, 48), keyboard_button_center, round_button_radius)
            pygame.draw.circle(screen, (40, 40, 40), keyboard_button_center, round_button_radius - 5)
            icon_x = keyboard_button.x + (keyboard_button.width - keyboard_icon.get_width()) // 2
            icon_y = keyboard_button.y + (keyboard_button.height - keyboard_icon.get_height()) // 2
            screen.blit(keyboard_icon, (icon_x, icon_y))


            if DEBUG_OPTIONS:
                draw_buttons(screen, increase_button, decrease_button, next_row_button)  # Buttons
                pygame.draw.rect(screen, (100, 100, 255), (100, 900, 100, 50))
                pygame.draw.rect(screen, (100, 100, 255), UPDATE_BUTTON_RECT)
        
            pygame.display.flip()
            #pygame.display.update()
            clock.tick(40)
        pygame.quit()
        
# Run the window
GAME_MODERATEDWORD_DICT, GAME_COMPLETEWORD_DICT = setup_word_lists()

def operations():
    started_new_game = False
    while True:
        if UltimateWordle().game_menu(started_new_game):
            started_new_game = True

operations()