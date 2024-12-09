import pygame
import sys

# Import the display and piece-drawing logic from the existing file
from tablero import draw_board, load_images

# Add a variable to track the current turn
current_turn = 'w'  # White starts the game

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

def path_clear(start, end, board):
    """Check if the path between start and end is clear."""
    sr, sc = start
    er, ec = end

    delta_row = er - sr
    delta_col = ec - sc

    step_row = 0 if delta_row == 0 else delta_row // abs(delta_row)
    step_col = 0 if delta_col == 0 else delta_col // abs(delta_col)

    current_row, current_col = sr + step_row, sc + step_col
    while (current_row, current_col) != (er, ec):
        if board[current_row][current_col]:
            return False
        current_row += step_row
        current_col += step_col

    return True


def is_valid_move(piece, start, end, board):
    """Validate moves based on piece type."""
    if not piece:  # No piece at the start square
        print("No piece at start square.")
        return False

    sr, sc = start
    er, ec = end
    delta_row = er - sr
    delta_col = ec - sc

    if not (0 <= er < ROWS and 0 <= ec < COLS):
        print(f"Move out of bounds: start={start}, end={end}")
        return False  # Out of bounds

    target_piece = board[er][ec]
    if target_piece and target_piece[0] == piece[0]:
        print("Cannot capture a piece of the same color.")
        return False  # Can't capture a piece of the same color

    piece_type = piece[1]

    if piece_type == 'k':  # King
        if max(abs(delta_row), abs(delta_col)) == 1:
            return True
        print("Invalid King move.")
        return False

    elif piece_type == 'q':  # Queen
        if abs(delta_row) == abs(delta_col) or delta_row == 0 or delta_col == 0:
            return path_clear(start, end, board)
        print("Invalid Queen move.")
        return False

    elif piece_type == 'r':  # Rook
        if delta_row == 0 or delta_col == 0:
            return path_clear(start, end, board)
        print("Invalid Rook move.")
        return False

    elif piece_type == 'b':  # Bishop
        if abs(delta_row) == abs(delta_col):
            return path_clear(start, end, board)
        print("Invalid Bishop move.")
        return False

    elif piece_type == 'n':  # Knight
        if (abs(delta_row), abs(delta_col)) in [(2, 1), (1, 2)]:
            return True
        print("Invalid Knight move.")
        return False

    elif piece_type == 'p':  # Pawn
        direction = -1 if piece[0] == 'w' else 1  # White moves up, Black moves down

        # Forward movement
        if delta_col == 0:
            if delta_row == direction and not target_piece:  # Single step
                return True
            if delta_row == 2 * direction and sr in (1, 6) and not target_piece:
                intermediate_row = sr + direction
                if not board[intermediate_row][sc]:  # Check the intermediate square
                    return True

        # Capturing diagonally
        if abs(delta_col) == 1 and delta_row == direction:
            if target_piece:  # Capturing an opponent's piece
                return True

        print("Invalid Pawn move.")
        return False

    print(f"Invalid move for piece type: {piece_type}")
    return False  # Invalid move for this piece type



# Add a variable to track the current turn
current_turn = 'w'  # White starts the game

def move_piece(start, end, board):
    """Move the piece on the board if the move is valid."""
    global current_turn
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]

    if not piece:
        print("No piece to move.")
        return False

    # Check if it's the correct turn
    if piece[0] != current_turn:
        print(f"It's not {piece[0]}'s turn!")
        return False

    print(f"Attempting to move {piece} from {start} to {end}")
    if is_valid_move(piece, start, end, board):
        board[er][ec] = piece
        board[sr][sc] = None
        print(f"Moved {piece} to {end}")

        # Switch the turn
        current_turn = 'b' if current_turn == 'w' else 'w'
        print(f"Turn switched to: {current_turn}")
        return True
    else:
        print("Move invalid.")
    return False

def display_turn(screen, font, current_turn):
    """Display the current turn on the screen."""
    turn_text = f"Turno de {'Blancas' if current_turn == 'w' else 'Negras'}"
    text_surface = font.render(turn_text, True, (0, 0, 0))
    screen.blit(text_surface, (10, HEIGHT + 10))  # Posición del mensaje debajo del tablero


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
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))  # Añadir espacio para el mensaje
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Fuente para el texto del turno

    images = load_images()
    selected_square = None
    running = True

    global current_turn

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse()

                # Validar que el clic esté dentro de los límites del tablero
                if 0 <= row < ROWS and 0 <= col < COLS:
                    if selected_square:
                        # Attempt to move the piece
                        if move_piece(selected_square, (row, col), board):
                            print(f"Moved {board[row][col]} to {row, col}")
                        selected_square = None  # Deselect after move
                    elif board[row][col]:
                        # Check if the piece matches the current turn
                        if board[row][col][0] == current_turn:
                            selected_square = (row, col)
                            print(f"Selected {board[row][col]} at {row, col}")
                        else:
                            print(f"Es el turno de {'Blancas' if current_turn == 'w' else 'Negras'}")
                else:
                    print("Clic fuera del tablero.")  # Mensaje para depuración

        # Drawing
        draw_board(screen)
        draw_pieces(screen, images, board)

        # Highlight selected square
        if selected_square:
            sr, sc = selected_square
            pygame.draw.rect(screen, (0, 255, 0), (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Highlight pieces that can move
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece and piece[0] == current_turn:
                    pygame.draw.rect(screen, (0, 255, 255), 
                                     (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)

        # Display the turn
        display_turn(screen, font, current_turn)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()
