import math
from game_logic import is_checkmate
from heuristic import evaluate_board


def minimax(board_main, board_teleport, depth, is_maximizing, alpha, beta, current_turn):
    """
    Perform the Minimax algorithm with Alpha-Beta Pruning and game logic integration.
    """
    if depth == 0 or is_checkmate(board_main, board_teleport, current_turn):
        return evaluate_board(board_main, board_teleport, current_turn)

    moves = generate_all_moves(board_main, board_teleport, current_turn)

    if is_maximizing:
        max_eval = -math.inf
        for move in moves:
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
    Generate all possible moves for the current player, including teleportation logic.
    """
    moves = []
    for board in [board_main, board_teleport]:
        for r, row in enumerate(board):
            for c, piece in enumerate(row):
                if piece and piece[0] == current_turn:
                    moves.extend(generate_piece_moves((r, c), piece, board_main, board_teleport))
    return moves


def generate_piece_moves(position, piece, board_main, board_teleport):
    """
    Generate all valid moves for a given piece, including teleportation.
    """
    moves = []
    r, c = position
    color = piece[0]
    piece_type = piece[1]

    def add_move(target_board, sr, sc, er, ec):
        """Add a move if valid."""
        if 0 <= er < len(board_main) and 0 <= ec < len(board_main[0]):
            target_piece = target_board[er][ec]
            if not target_piece or target_piece[0] != color:
                moves.append((board_main, target_board, (sr, sc), (er, ec)))



    for er in range(len(board_teleport)):
        for ec in range(len(board_teleport[0])):
            if board_teleport[er][ec] is None:  
                add_move(board_teleport, r, c, er, ec)

    return moves



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

    piece = target_board[er][ec]
    target_board[er][ec] = None
    source_board[sr][sc] = piece


def switch_turn(current_turn):
    """
    Switch the current player's turn.
    """
    return 'b' if current_turn == 'w' else 'w'


