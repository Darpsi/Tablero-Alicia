def evaluate_board(board_main, board_teleport, current_turn):
    score = 0
    for board in [board_main, board_teleport]:
        for row in board:
            for piece in row:
                if piece:
                    piece_value = get_piece_value(piece)
                    score += piece_value if piece[0] == current_turn else -piece_value
    return score

def get_piece_value(piece):
    values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 1000}
    return values.get(piece[1], 0)
