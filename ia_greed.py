import math
from queue import PriorityQueue
from game_logic import is_valid_move, is_in_check, can_escape_check, find_king, move_piece_between_boards
from heuristic import evaluate_board


def busqueda_greedy(board_main, board_teleport, max_moves, current_turn):
    """
    Greedy search algorithm for the AI.
    Evaluates all valid moves and selects the one with the highest heuristic value.
    """

    best_move = None
    best_score = -math.inf if current_turn == 'b' else math.inf  # Maximize for black, minimize for white

    # Generate all possible moves for both boards
    all_moves = generate_all_moves(board_main, board_teleport, current_turn)

    for move in all_moves:
        source_board, target_board, start, end = move
        piece = source_board[start[0]][start[1]]

        # Validate the move using game logic
        if not is_valid_move(piece, start, end, source_board):
            continue

        # Simulate the move
        make_move(board_main, board_teleport, move)

        # Check if the move leaves the king in check
        if is_in_check(board_main, board_teleport, current_turn):
            undo_move(board_main, board_teleport, move)
            continue

        # Evaluate the board state
        score = evaluate_board(board_main, board_teleport, current_turn)

        # Undo the move to restore the original state
        undo_move(board_main, board_teleport, move)

        # Update the best move based on the evaluation
        if (current_turn == 'b' and score > best_score) or (current_turn == 'w' and score < best_score):
            best_score = score
            best_move = move

    return (best_move, best_score) if best_move else None


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



