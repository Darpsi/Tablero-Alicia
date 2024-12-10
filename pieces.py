# pieces.py
import pygame
from settings import ROWS, COLS, SQUARE_SIZE, WIDTH

def load_images():
    pieces = ['bp', 'br', 'bn', 'bb', 'bq', 'bk', 
              'wp', 'wr', 'wn', 'wb', 'wq', 'wk']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(
            pygame.image.load(f"{piece}.png"), 
            (SQUARE_SIZE, SQUARE_SIZE)
        )
    return images

def draw_pieces_on_boards(screen, images, board1, board2):
    for i, (board, offset) in enumerate(zip([board1, board2], [0, WIDTH + 20])):
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece:
                    screen.blit(
                        images[piece],
                        (col * SQUARE_SIZE + offset, row * SQUARE_SIZE)
                    )

