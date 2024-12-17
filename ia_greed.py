import math
from queue import PriorityQueue
from game_logic import is_valid_move
from heuristic import evaluate_board


def busqueda_greedy(board_main, board_teleport, max_moves, current_turn):
    """
    Greedy search algorithm for the AI.
    Evaluates all valid moves and selects the one with the highest heuristic value.
    """

    best_move = None
    best_score = -math.inf if current_turn == 'b' else math.inf  

   
    moves = []
    for r, row in enumerate(board_main):
        for c, piece in enumerate(row):
            if piece and piece[0] == current_turn:
                possible_moves = generate_piece_moves((r, c), piece, board_main, board_teleport)
                for move in possible_moves:
                    source_board, target_board, start, end = move
                    if is_valid_move(piece, start, end, source_board): 
                        moves.append(move)

  
    for move in moves:
        source_board, target_board, start, end = move

       
        piece = source_board[start[0]][start[1]]
        make_move(board_main, board_teleport, move)

        
        score = evaluate_board(board_main, board_teleport, current_turn)

        
        undo_move(board_main, board_teleport, move)

        if (current_turn == 'b' and score > best_score) or (current_turn == 'w' and score < best_score):
            best_score = score
            best_move = move

    return (best_move, best_score) if best_move else None


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


