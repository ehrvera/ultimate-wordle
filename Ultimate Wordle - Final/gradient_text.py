import pygame
import pygame.freetype

# Initialize pygame
pygame.init()

# Define constants
WINDOW_SIZE = (600, 400)
TEXT = "Gradient Text"
FONT_SIZE = 60
COLOR_START = (255, 0, 0)  # Red
COLOR_END = (0, 0, 255)    # Blue
BACKGROUND_COLOR = (30, 30, 30)

# Create a window
screen = pygame.display.set_mode(WINDOW_SIZE)

# Create a font object
font = pygame.freetype.SysFont(None, FONT_SIZE)

def create_gradient_text(text, font, start_color, end_color, surface_size):
    text_surface, _ = font.render(text, (255, 255, 255))  # Initially render in white
    text_rect = text_surface.get_rect(center=(surface_size[0] // 2, surface_size[1] // 2))

    # Create a surface for the gradient
    gradient_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    width, height = text_surface.get_size()

    # Create the gradient fill
    for y in range(height):
        blend_ratio = y / height
        blended_color = (
            int(start_color[0] * (1 - blend_ratio) + end_color[0] * blend_ratio),
            int(start_color[1] * (1 - blend_ratio) + end_color[1] * blend_ratio),
            int(start_color[2] * (1 - blend_ratio) + end_color[2] * blend_ratio),
        )
        pygame.draw.line(gradient_surface, blended_color, (0, y), (width, y))

    # Apply the gradient to the text surface using the text as a mask
    text_surface.blit(gradient_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)

    return text_surface, text_rect

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill(BACKGROUND_COLOR)

    # Create gradient text and blit it to the screen
    gradient_text, gradient_text_rect = create_gradient_text(TEXT, font, COLOR_START, COLOR_END, WINDOW_SIZE)
    screen.blit(gradient_text, gradient_text_rect)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
