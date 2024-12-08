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
        images[piece] = pygame.image.load(f"{piece}.png")
        images[piece] = pygame.transform.scale(images[piece], (SQUARE_SIZE, SQUARE_SIZE))
    return images

# Draw the chessboard
def draw_board(screen):
    colors = [WHITE, BROWN]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Place the pieces on the board
def draw_pieces(screen, images):
    initial_positions = [
        ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
        ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
    ]

    for row in range(ROWS):
        for col in range(COLS):
            piece = initial_positions[row][col]
            if piece:
                screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

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

        draw_board(screen)
        draw_pieces(screen, images)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
