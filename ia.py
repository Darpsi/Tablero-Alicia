import math
from game_logic import is_checkmate, is_valid_move, is_in_check
from heuristic import evaluate_board

def minimax(board_main, board_teleport, depth, is_maximizing, alpha, beta, current_turn):
    """
    Perform the Minimax algorithm with Alpha-Beta Pruning and game logic integration.
    """
    # Base case: checkmate or maximum depth
    if depth == 0 or is_checkmate(board_main, board_teleport, current_turn):
        return evaluate_board(board_main, board_teleport, current_turn)

    moves = generate_all_moves(board_main, board_teleport, current_turn)

    if is_maximizing:
        max_eval = -math.inf
        for move in moves:
            if not validate_move(board_main, board_teleport, move, current_turn):
                continue  # Skip invalid moves
            make_move(board_main, board_teleport, move)
            eval = minimax(board_main, board_teleport, depth - 1, False, alpha, beta, switch_turn(current_turn))
            undo_move(board_main, board_teleport, move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            if not validate_move(board_main, board_teleport, move, current_turn):
                continue  # Skip invalid moves
            make_move(board_main, board_teleport, move)
            eval = minimax(board_main, board_teleport, depth - 1, True, alpha, beta, switch_turn(current_turn))
            undo_move(board_main, board_teleport, move)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def generate_all_moves(board_main, board_teleport, current_turn):
    """
    Generate all possible teleportation moves for the current player.
    """
    moves = []

    # Generate teleportation moves for pieces on the main board
    for r, row in enumerate(board_main):
        for c, piece in enumerate(row):
            if piece and piece[0] == current_turn:
                moves.extend(generate_piece_moves((r, c), piece, board_main, board_teleport))

    # Generate teleportation moves for pieces on the teleport board
    for r, row in enumerate(board_teleport):
        for c, piece in enumerate(row):
            if piece and piece[0] == current_turn:
                moves.extend(generate_piece_moves((r, c), piece, board_teleport, board_main))

    return moves


def generate_piece_moves(position, piece, source_board, target_board):
    """
    Generate all valid teleportation moves for a given piece.
    """
    moves = []
    r, c = position

    def add_move(target_board, sr, sc, er, ec):
        """Add a teleportation move if valid."""
        if 0 <= er < len(target_board) and 0 <= ec < len(target_board[0]):
            if target_board[er][ec] is None:  # Teleport only to empty squares
                moves.append((source_board, target_board, (sr, sc), (er, ec)))

    # Generate teleportation moves to every empty square on the other board
    for er in range(len(target_board)):
        for ec in range(len(target_board[0])):
            add_move(target_board, r, c, er, ec)

    return moves


def validate_move(board_main, board_teleport, move, current_turn):
    """
    Validate a move considering game rules and the king's safety.
    """
    source_board, target_board, start, end = move
    piece = source_board[start[0]][start[1]]

    # Check if the move is valid for the piece
    if not is_valid_move(piece, start, end, source_board):
        return False

    # Simulate the move and check if it leaves the king in check
    make_move(board_main, board_teleport, move)
    in_check = is_in_check(board_main, board_teleport, current_turn)
    undo_move(board_main, board_teleport, move)

    return not in_check


def make_move(board_main, board_teleport, move):
    """
    Apply a move to the board(s).
    """
    source_board, target_board, start, end = move
    piece = source_board[start[0]][start[1]]
    source_board[start[0]][start[1]] = None
    target_board[end[0]][end[1]] = piece


def undo_move(board_main, board_teleport, move):
    """Undo a move to restore the previous state of the boards."""
    source_board, target_board, start, end = move
    sr, sc = start
    er, ec = end

    # Restore the piece on the source board
    piece = target_board[er][ec]
    target_board[er][ec] = None
    source_board[sr][sc] = piece


def switch_turn(current_turn):
    """
    Switch the current player's turn.
    """
    return 'b' if current_turn == 'w' else 'w'



