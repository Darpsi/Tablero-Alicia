from queue import PriorityQueue
from heuristic import evaluate_board

def es_valido(fila, colum, mapa):
    n, m = len(mapa), len(mapa[0])
    return 0 <= fila < n and 0 <= colum < m

def busqueda_greedy(board_main, board_teleport, maximo_iteraciones, current_turn):
    """
    Greedy Search to evaluate and determine the best chess move.
    """
    iteraciones = 0
    best_move = None
    best_heuristic = float('-inf')

    while iteraciones < maximo_iteraciones:
        moves = generate_all_moves(board_main, board_teleport, current_turn)
        iteraciones += 1

        for move in moves:
            make_move(board_main, board_teleport, move)
            heuristic_value = evaluate_board(board_main, board_teleport, current_turn)
            undo_move(board_main, board_teleport, move)

            if heuristic_value > best_heuristic:
                best_heuristic = heuristic_value
                best_move = move

        if best_move:
            make_move(board_main, board_teleport, best_move)
            return best_move, best_heuristic

    return None

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

    def add_move(target_board, sr, sc, er, ec):
        """Add a move if valid."""
        if 0 <= er < len(board_main) and 0 <= ec < len(board_main[0]):
            target_piece = target_board[er][ec]
            if not target_piece or target_piece[0] != color:
                moves.append((board_main, target_board, (sr, sc), (er, ec)))

    # Add teleportation moves
    for er in range(len(board_teleport)):
        for ec in range(len(board_teleport[0])):
            if board_teleport[er][ec] is None:  # Teleport to empty squares
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

    # Restore the piece on the source board
    piece = target_board[er][ec]
    target_board[er][ec] = None
    source_board[sr][sc] = piece


