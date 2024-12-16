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

def is_under_attack(board1, board2, position, attacker_color):
    for board in (board1, board2):
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece and piece[0] == attacker_color:
                    if is_valid_move(piece, (row, col), position, board):
                        return True
    return False

def is_in_check(board1, board2, color):
    king_pos_main = find_king(board1, color)
    king_pos_teleport = find_king(board2, color)

    if king_pos_main:
        king_pos = king_pos_main
        active_board = board1
    elif king_pos_teleport:
        king_pos = king_pos_teleport
        active_board = board2
    else:
        return False  # No king found (invalid state)

    opponent_color = 'b' if color == 'w' else 'w'

    # Only check for threats on the same board as the king
    for row in range(ROWS):
        for col in range(COLS):
            piece = active_board[row][col]
            if piece and piece[0] == opponent_color:
                if is_valid_move(piece, (row, col), king_pos, active_board):
                    return True

    return False

def get_attack_vector(attacker_row, attacker_col, king_pos, board):
    """
    Returns the attack vector (a list of squares) between the attacking piece and the king.
    This applies only to linear threats (rook, bishop, or queen).
    """
    king_row, king_col = king_pos
    attack_vector = []

    dr = king_row - attacker_row
    dc = king_col - attacker_col

    # Ensure it's a straight line (rook, bishop, or queen)
    if dr == 0 or dc == 0 or abs(dr) == abs(dc):  # Same row, column, or diagonal
        step_r = (dr // abs(dr)) if dr != 0 else 0
        step_c = (dc // abs(dc)) if dc != 0 else 0

        current_row, current_col = attacker_row + step_r, attacker_col + step_c
        while (current_row, current_col) != (king_row, king_col):
            attack_vector.append((current_row, current_col))
            current_row += step_r
            current_col += step_c

    return attack_vector


def can_escape_check(board1, board2, color):
    king_pos_main = find_king(board1, color)
    king_pos_teleport = find_king(board2, color)

    if king_pos_main:
        king_pos = king_pos_main
        active_board = board1  # Board where the king is
        teleport_board = board2  # Opposite board
    elif king_pos_teleport:
        king_pos = king_pos_teleport
        active_board = board2  # Board where the king is
        teleport_board = board1  # Opposite board
    else:
        return False  # No king found (invalid state)

    opponent_color = 'b' if color == 'w' else 'w'

    # Find the attacking piece on the same board as the king
    attacking_piece = None
    for row in range(ROWS):
        for col in range(COLS):
            piece = active_board[row][col]
            if piece and piece[0] == opponent_color:
                if is_valid_move(piece, (row, col), king_pos, active_board):
                    attacking_piece = (row, col)
                    break
        if attacking_piece:
            break

    if not attacking_piece:
        return False  # No attacking piece found, king not in check

    attacker_row, attacker_col = attacking_piece
    attack_vector = get_attack_vector(attacker_row, attacker_col, king_pos, active_board)

    # Check if a piece from the opposite board can teleport to block the attack
    if attack_vector:  # Linear attacks (rook, bishop, queen)
        for row in range(ROWS):
            for col in range(COLS):
                piece = teleport_board[row][col]
                if piece and piece[0] == color:  # Same color as the king
                    for block_pos in attack_vector:
                        if is_valid_move(piece, (row, col), block_pos, teleport_board):
                            # Simulate teleportation to block
                            temp_board = [r[:] for r in active_board]
                            temp_board[block_pos[0]][block_pos[1]] = piece  # Place blocking piece
                            if not is_in_check(temp_board, teleport_board, color):
                                return True  # A teleportation blocking move exists

    return False  # No valid moves to block check found


def is_checkmate(board1, board2, color):
    if not is_in_check(board1, board2, color):
        return False  # King is not in check, so not checkmate

    king_pos_main = find_king(board1, color)
    king_pos_teleport = find_king(board2, color)

    if king_pos_main:
        king_pos = king_pos_main
        active_board = board1
        teleport_board = board2
    elif king_pos_teleport:
        king_pos = king_pos_teleport
        active_board = board2
        teleport_board = board1
    else:
        return False  # No king found

    kr, kc = king_pos

    # Check if the king can move to a safe square
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            nr, nc = kr + dr, kc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if active_board[nr][nc] is None or active_board[nr][nc][0] != color:
                    temp_board = [row[:] for row in active_board]
                    temp_board[kr][kc] = None
                    temp_board[nr][nc] = f"{color}k"
                    if not is_in_check(temp_board, teleport_board, color):
                        return False  # King can escape

    # Check if any piece on the same board can capture the attacker
    for row in range(ROWS):
        for col in range(COLS):
            piece = active_board[row][col]
            if piece and piece[0] == color:  # Same color as the king
                for er in range(ROWS):
                    for ec in range(COLS):
                        if is_valid_move(piece, (row, col), (er, ec), active_board):
                            temp_board = [r[:] for r in active_board]
                            temp_board[row][col] = None
                            temp_board[er][ec] = piece
                            if not is_in_check(temp_board, teleport_board, color):
                                return False  # A piece can capture or block

    # Check if a piece from the opposite board can teleport to block
    if can_escape_check(board1, board2, color):
        return False  # Teleporting piece can block the attack

    return True  # No escape, checkmate




def is_checkmate(board1, board2, color):
    if not is_in_check(board1, board2, color):
        return False  # King is not in check, so not checkmate

    king_pos_main = find_king(board1, color)
    king_pos_teleport = find_king(board2, color)

    if king_pos_main:
        king_pos = king_pos_main
        active_board = board1
        teleport_board = board2
    elif king_pos_teleport:
        king_pos = king_pos_teleport
        active_board = board2
        teleport_board = board1
    else:
        return False  # No king found

    kr, kc = king_pos
    opponent_color = 'b' if color == 'w' else 'w'

    # Check if the king can move to a safe square
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            nr, nc = kr + dr, kc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if active_board[nr][nc] is None or active_board[nr][nc][0] == opponent_color:
                    temp_board = [row[:] for row in active_board]
                    temp_board[kr][kc] = None
                    temp_board[nr][nc] = f"{color}k"
                    if not is_in_check(temp_board, teleport_board, color):
                        return False  # King can escape

    # Check if any piece can block or capture the attacker
    for row in range(ROWS):
        for col in range(COLS):
            piece = active_board[row][col]
            if piece and piece[0] == color:  # Same-color piece
                for er in range(ROWS):
                    for ec in range(COLS):
                        if is_valid_move(piece, (row, col), (er, ec), active_board):
                            temp_board = [r[:] for r in active_board]
                            temp_board[row][col] = None
                            temp_board[er][ec] = piece
                            if not is_in_check(temp_board, teleport_board, color):
                                return False  # A piece can block or capture

    # Check if a piece from the other board can teleport to block or capture
    if can_escape_check(board1, board2, color):
        return False  # Teleporting piece can save the king

    return True  # No escape, checkmate

def move_piece_between_boards(start, end, board1, board2):
    sr, sc = start
    er, ec = end
    piece = board1[sr][sc] if board1[sr][sc] else board2[sr][sc]

    if piece:
        # Determine source and target boards
        if board1[sr][sc]:
            source_board, target_board = board1, board2
        else:
            source_board, target_board = board2, board1

        target_piece = target_board[er][ec]
        if target_piece and target_piece[0] == piece[0]:  # Cannot capture same-color piece
            return False

        if is_valid_move(piece, start, end, source_board):
            target_board[er][ec] = piece
            source_board[sr][sc] = None
            return True
    return False


