# game_logic.py
from settings import ROWS, COLS

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

def find_king(board, color):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece == f"{color}k":
                return row, col
    return None 

def is_under_attack(board, position, attacker_color):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == attacker_color:
                if is_valid_move(piece, (row, col), position, board):
                    return True
    return False

def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return False
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

def move_piece_between_boards(start, end, board1, board2):
    sr, sc = start
    er, ec = end
    piece = board1[sr][sc] if board1[sr][sc] else board2[sr][sc]

    if piece:
        # Determine which board to move to
        if board1[sr][sc]:
            source_board, target_board = board1, board2
        else:
            source_board, target_board = board2, board1

        if is_valid_move(piece, start, end, source_board):
            target_board[er][ec] = piece
            source_board[sr][sc] = None
            return True
    return False

