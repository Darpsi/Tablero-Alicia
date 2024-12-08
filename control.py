import pygame
import sys

# Import the display and piece-drawing logic from the existing file
from tablero import draw_board, load_images

# Constants
WIDTH, HEIGHT = 400, 400
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Initial board setup
board = [
    ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
]

# Helper functions
def get_square_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    col = mouse_pos[0] // SQUARE_SIZE
    row = mouse_pos[1] // SQUARE_SIZE
    return row, col

def is_valid_move(piece, start, end, board):
    """Validate moves based on piece type (basic rules)."""
    sr, sc = start
    er, ec = end

    if 0 <= er < ROWS and 0 <= ec < COLS:
        # Can't capture pieces of the same color
        if board[er][ec] and board[er][ec][0] == piece[0]:
            return False
        return True
    return False

def move_piece(start, end, board):
    """Move the piece on the board if the move is valid."""
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]

    if is_valid_move(piece, start, end, board):
        board[er][ec] = piece
        board[sr][sc] = None
        return True
    return False

# Draw pieces using the current board state
def draw_pieces(screen, images, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    images = load_images()
    selected_square = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse()

                if selected_square:
                    # Try to move the piece
                    if move_piece(selected_square, (row, col), board):
                        print(f"Moved to {row, col}")
                    selected_square = None  # Deselect after move
                elif board[row][col]:
                    # Select the piece
                    selected_square = (row, col)
                    print(f"Selected {board[row][col]} at {row, col}")

        # Drawing
        draw_board(screen)
        draw_pieces(screen, images, board)

        # Highlight selected square
        if selected_square:
            sr, sc = selected_square
            pygame.draw.rect(screen, (0, 255, 0), (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
