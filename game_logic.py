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
    king_pos = find_king(board1, color) or find_king(board2, color)
    if not king_pos:
        return False
    opponent_color = 'b' if color == 'w' else 'w'
    return is_under_attack(board1, board2, king_pos, opponent_color)


def is_checkmate(board1, board2, color):
    """Check if the king of the given color is in checkmate, considering both boards."""
    king_pos = find_king(board1, color) or find_king(board2, color)
    if not king_pos:
        return False  # The king is not on either board (should not happen in a valid game)

    # If the king is in check, verify if it has any valid escape moves
    if is_in_check(board1, board2, color):
        kr, kc = king_pos
        opponent_color = 'b' if color == 'w' else 'w'

        # Check if the king can move to any adjacent square
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = kr + dr, kc + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    # Check if the square is empty or contains an opponent's piece
                    target_piece1 = board1[nr][nc]
                    target_piece2 = board2[nr][nc]

                    if (target_piece1 is None or target_piece1[0] == opponent_color) and \
                       (target_piece2 is None or target_piece2[0] == opponent_color):
                        # Simulate moving the king to this square on both boards
                        temp_board1 = [row[:] for row in board1]
                        temp_board2 = [row[:] for row in board2]
                        temp_board1[kr][kc] = None
                        temp_board2[kr][kc] = None
                        temp_board1[nr][nc] = f"{color}k"

                        if not is_in_check(temp_board1, temp_board2, color):
                            return False  # The king can escape check

        # If the king cannot move, check if any piece can block the check or capture the attacker
        for row in range(ROWS):
            for col in range(COLS):
                piece = board1[row][col] or board2[row][col]
                if piece and piece[0] == color:  # If it's a piece of the same color
                    for er in range(ROWS):
                        for ec in range(COLS):
                            # Try all possible moves for this piece
                            if is_valid_move(piece, (row, col), (er, ec), board1):
                                temp_board1 = [r[:] for r in board1]
                                temp_board2 = [r[:] for r in board2]
                                temp_board1[row][col] = None
                                temp_board2[row][col] = None
                                temp_board1[er][ec] = piece

                                if not is_in_check(temp_board1, temp_board2, color):
                                    return False  # The piece can block the check or capture the attacker

        # If the king cannot escape and no piece can block the check, it's checkmate
        return True

    return False


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


