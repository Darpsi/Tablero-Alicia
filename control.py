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
        return False

    sr, sc = start
    er, ec = end
    delta_row = er - sr
    delta_col = ec - sc

    if not (0 <= er < ROWS and 0 <= ec < COLS):
        return False  # Out of bounds

    target_piece = board[er][ec]
    if target_piece and target_piece[0] == piece[0]:
        return False  # Can't capture a piece of the same color

    piece_type = piece[1]

    if piece_type == 'k':  # King
        if max(abs(delta_row), abs(delta_col)) == 1:
            return True

    elif piece_type == 'q':  # Queen
        if abs(delta_row) == abs(delta_col) or delta_row == 0 or delta_col == 0:
            return path_clear(start, end, board)

    elif piece_type == 'r':  # Rook
        if delta_row == 0 or delta_col == 0:
            return path_clear(start, end, board)

    elif piece_type == 'b':  # Bishop
        if abs(delta_row) == abs(delta_col):
            return path_clear(start, end, board)

    elif piece_type == 'n':  # Knight
        if (abs(delta_row), abs(delta_col)) in [(2, 1), (1, 2)]:
            return True

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

    return False  # Invalid move for this piece type


def find_king(board, color):
    """Find the position of the king for the given color."""
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece == f"{color}k":
                return row, col
    return None  # El rey no se encuentra (esto no debería suceder en un juego válido)

def is_under_attack(board, position, attacker_color):
    """Check if the given position is under attack by any piece of the attacker color."""
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == attacker_color:
                if is_valid_move(piece, (row, col), position, board):
                    return True
    return False

def is_in_check(board, color):
    """Check if the king of the given color is in check."""
    king_pos = find_king(board, color)
    if not king_pos:
        return False  # Esto solo ocurre si no hay rey en el tablero, lo cual no es normal
    opponent_color = 'b' if color == 'w' else 'w'
    return is_under_attack(board, king_pos, opponent_color)

def is_checkmate(board, color):
    """Check if the current player's king is in checkmate."""
    king_pos = find_king(board, color)
    if not king_pos:
        return False  # El rey no se encuentra en el tablero (lo cual no debería ocurrir)
    
    # Si el rey está en jaque, verificar si tiene alguna salida
    if is_in_check(board, color):
        kr, kc = king_pos
        opponent_color = 'b' if color == 'w' else 'w'
        
        # Verificar si alguna casilla alrededor del rey puede ser movida sin poner al rey en jaque
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = kr + dr, kc + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    # Verificar si la casilla está vacía o si contiene una pieza del color enemigo
                    target_piece = board[nr][nc]
                    if target_piece is None or target_piece[0] == opponent_color:
                        # Probar mover el rey a esa casilla
                        temp_board = [row[:] for row in board]
                        temp_board[kr][kc] = None
                        temp_board[nr][nc] = f"{color}k"
                        
                        if not is_in_check(temp_board, color):
                            return False  # El rey puede moverse y salir del jaque

        # Si no puede moverse, verificar si alguna pieza puede bloquear el jaque o capturar la pieza atacante
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece and piece[0] == color:  # Si es una pieza del color del rey
                    if is_valid_move(piece, (row, col), king_pos, board):  # Si puede mover y bloquear
                        temp_board = [row[:] for row in board]
                        temp_board[kr][kc] = None
                        temp_board[row][col] = None  # Remover pieza bloqueadora
                        temp_board[kr][kc] = f"{color}k"  # Colocar el rey de nuevo

                        if not is_in_check(temp_board, color):
                            return False  # Si se puede bloquear el jaque, no es jaque mate

        # Si no puede escapar ni bloquear el jaque, es jaque mate
        return True
    return False


# Add a variable to track the current turn
current_turn = 'w'  # White starts the game

def move_piece(start, end, board):
    """Move the piece on the board if the move is valid and doesn't leave the king in check."""
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

    if is_valid_move(piece, start, end, board):
        # Simulate the move
        temp_board = [row[:] for row in board]  # Create a copy of the board
        temp_board[er][ec] = piece
        temp_board[sr][sc] = None

        # Check if the move leaves the king in check
        if is_in_check(temp_board, current_turn):
            print("Move leaves the king in check!")
            return False

        # Apply the move
        board[er][ec] = piece
        board[sr][sc] = None

        # Switch the turn
        current_turn = 'b' if current_turn == 'w' else 'w'
        print(f"Moved {piece} to {end}")
        print(f"Turn switched to: {current_turn}")
        return True
    else:
        print(f"Invalid move for {piece} from {start} to {end}.")
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

        # Highlight the king if it's in check
        king_pos = find_king(board, current_turn)
        if king_pos and is_in_check(board, current_turn):
            kr, kc = king_pos
            pygame.draw.rect(screen, (255, 0, 0), (kc * SQUARE_SIZE, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Check for checkmate
        if king_pos and is_checkmate(board, current_turn):
            print(f"Checkmate! {current_turn.upper()} loses.")
            running = False  # End the game

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
