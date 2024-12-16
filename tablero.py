import os
import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400  # Half of the original size
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

# Load images of chess pieces
def load_images():
    pieces = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 
              'bp', 'br', 'bn', 'bb', 'bq', 'bk']
    images = {}
    for piece in pieces:
        # Correct path construction
        image_path = os.path.join("png", f"{piece}.png")  
        
        if not os.path.exists(image_path):  # Check if the file exists
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load and scale the image
        images[piece] = pygame.image.load(image_path)
        images[piece] = pygame.transform.scale(images[piece], (SQUARE_SIZE, SQUARE_SIZE))
    return images


# Draw the chessboard
def draw_boards(screen, offset=0):
    colors = [WHITE, BROWN]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(
                screen,
                color,
                (col * SQUARE_SIZE + offset, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            )




def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chessboard")
    images = load_images()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_boards(screen)
        pygame.display.flip()
        clock.tick(60)
        
