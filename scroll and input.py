import pygame as pg
import ctypes
from ctypes import wintypes

# Initialize Pygame
pg.init()

WINDOW_SIZE = (1200, 800)
TITLE_BAR_HEIGHT = 30
SCROLL_SPEED = 10
max_scroll_height = 1000  # Scrollable area height

# Colors
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (100, 100, 100)

# Set the display mode with resizable and no frame flags
screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.NOFRAME, 32)
pg.display.set_caption("Resizable Window with Input Boxes and Movable Bar")

# Clock to manage frame rate
clock = pg.time.Clock()

# Variables to keep track of window movement
moving = False
initial_pos = (0, 0)
window_pos = (0, 0)

# Variables for scrolling
scroll_y = 0

# Function to set window position (Windows OS specific)
def set_window_position(x, y):
    hwnd = pg.display.get_wm_info()["window"]
    ctypes.windll.user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001)

# Get initial window position
hwnd = pg.display.get_wm_info()["window"]
rect = wintypes.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
window_pos = (rect.left, rect.top)

# Input box class
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = INPUT_FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN:
                self.text = ''
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalnum():
                self.text += event.unicode.upper()
            self.txt_surface = INPUT_FONT.render(self.text, True, self.color)

    def draw(self, surface):
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pg.draw.rect(surface, self.color, self.rect, 2)

# Create gradient surface for background
def create_gradient_surface(width, height, top_color, bottom_color):
    surface = pg.Surface((width, height))
    for i in range(height):
        color = [
            top_color[j] + (bottom_color[j] - top_color[j]) * i // height
            for j in range(3)
        ]
        pg.draw.line(surface, color, (0, i), (width, i))
    return surface

# Draw input boxes on a surface
def draw_input_boxes(surface, input_boxes):
    for box in input_boxes:
        box.draw(surface)

# Add buttons to increase/decrease number of input boxes
def draw_buttons(surface, increase_button, decrease_button):
    pg.draw.rect(surface, BUTTON_COLOR, increase_button)
    pg.draw.rect(surface, BUTTON_COLOR, decrease_button)
    surface.blit(INPUT_FONT.render("+", True, (255, 255, 255)), (increase_button.x + 10, increase_button.y))
    surface.blit(INPUT_FONT.render("-", True, (255, 255, 255)), (decrease_button.x + 10, decrease_button.y))

# Main function
def main():
    global INPUT_FONT
    INPUT_FONT = pg.font.Font(None, 32)

    global window_pos, moving, scroll_y

    input_boxes = [InputBox(100 + i * 150, 150 + TITLE_BAR_HEIGHT, 140, 32) for i in range(3)]

    # Buttons for input boxes
    increase_button = pg.Rect(50, 10, 30, 30)
    decrease_button = pg.Rect(100, 10, 30, 30)

    # Scrollable surface
    scroll_surface = pg.Surface((WINDOW_SIZE[0], max_scroll_height))
    gradient_surface = create_gradient_surface(WINDOW_SIZE[0], max_scroll_height, (50, 50, 50), (0, 0, 0))
    scroll_surface.blit(gradient_surface, (0, 0))

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # Handle input box events
            for box in input_boxes:
                box.handle_event(event)

            # Handle window movement
            if event.type == pg.MOUSEBUTTONDOWN and event.pos[1] <= TITLE_BAR_HEIGHT:
                moving = True
                mouse_x, mouse_y = event.pos
                initial_pos = (mouse_x, mouse_y)

            elif event.type == pg.MOUSEBUTTONUP:
                moving = False

            elif event.type == pg.MOUSEMOTION and moving:
                mouse_x, mouse_y = event.pos
                dx = mouse_x - initial_pos[0]
                dy = mouse_y - initial_pos[1]
                new_x = window_pos[0] + dx
                new_y = window_pos[1] + dy
                set_window_position(new_x, new_y)
                window_pos = (new_x, new_y)

            # Handle button clicks for adding/removing input boxes
            if event.type == pg.MOUSEBUTTONDOWN:
                if increase_button.collidepoint(event.pos) and len(input_boxes) < 6:
                    input_boxes.append(InputBox(100 + len(input_boxes) * 150, 150 + TITLE_BAR_HEIGHT, 140, 32))
                if decrease_button.collidepoint(event.pos) and len(input_boxes) > 3:
                    input_boxes.pop()

            # Handle scrolling
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    scroll_y = min(scroll_y + SCROLL_SPEED, 0)
                elif event.button == 5:  # Scroll down
                    scroll_y = max(scroll_y - SCROLL_SPEED, -max_scroll_height + WINDOW_SIZE[1])

        # Drawing
        screen.fill(BG_COLOR)

        # Draw scrollable content first
        scroll_surface.fill((0, 0, 0))  # Clear the scroll surface
        scroll_surface.blit(gradient_surface, (0, 0))
        draw_input_boxes(scroll_surface, input_boxes)  # Draw input boxes on the scroll surface
        screen.blit(scroll_surface, (0, scroll_y + TITLE_BAR_HEIGHT))  # Scrollable area

        # Draw the fixed top bar and buttons
        pg.draw.rect(screen, (50, 50, 50), (0, 0, WINDOW_SIZE[0], TITLE_BAR_HEIGHT))  # Movable bar
        draw_buttons(screen, increase_button, decrease_button)  # Draw the buttons

        pg.display.flip()
        clock.tick(60)

    pg.quit()

main()
