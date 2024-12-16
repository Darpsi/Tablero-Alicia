# pieces.py
import os
import pygame
from settings import ROWS, COLS, SQUARE_SIZE, WIDTH

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

