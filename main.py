import math
import pygame
import sys
from ia import generate_piece_moves, make_move, minimax, undo_move
from settings import COLS, ROWS, SECOND_BOARD, SQUARE_SIZE, WIDTH, HEIGHT, INITIAL_BOARD
from tablero import draw_boards, load_images
from pieces import draw_pieces_on_boards
from game_logic import find_king, is_in_check, is_checkmate, is_valid_move, move_piece_between_boards
from utils import get_square_under_mouse


def move_piece(start, end, source_board, target_board, check_turn=True):
    """Move the piece on the board, capture enemy pieces, and teleport to the other board."""
    global current_turn

    sr, sc = start
    er, ec = end
    piece = source_board[sr][sc]

    if not piece:
        print("No piece to move.")
        return False

    # Check if it's the correct turn (can be bypassed for AI)
    if check_turn and piece[0] != current_turn:
        print(f"It's not {piece[0]}'s turn!")
        return False

    # Ensure the move is valid on the source board
    if is_valid_move(piece, start, end, source_board):
        # Ensure the move is to the other board
        if source_board is target_board:
            print("Pieces must teleport to the other board.")
            return False

        # Check if the target square on the target board is empty
        if target_board[er][ec]:
            print(f"Cannot teleport {piece} to {end}: destination square on the target board is not empty.")
            return False

        # Temporarily remove the piece from the source board
        source_board[sr][sc] = None

        # Simulate the move and check both boards for checks
        temp_source_board = [row[:] for row in source_board]
        temp_target_board = [row[:] for row in target_board]
        temp_target_board[er][ec] = piece

        # Ensure the king is not in check on either board
        if is_in_check(temp_source_board, temp_target_board, current_turn):
            print("Move leaves the king in check!")
            # Restore the piece if the move is invalid
            source_board[sr][sc] = piece
            return False

        # Perform the move: update source and target boards
        source_board[sr][sc] = None
        source_board[er][ec] = None
        target_board[er][ec] = piece

        print(f"{piece} teleported to {end} on the target board.")

        # Switch the turn
        current_turn = 'b' if current_turn == 'w' else 'w'
        print(f"Turn switched to: {current_turn}")
        return True
    else:
        print(f"Invalid move for {piece} from {start} to {end}.")
    return False



def ai_move(board_main, board_teleport):
    """Calculate and execute the AI's move using the minimax algorithm."""
    global current_turn
    print("AI is thinking...")

    depth = 2  # Adjust depth for difficulty level
    best_move = None
    best_eval = -math.inf

    # Generate all possible moves for the AI (black)
    moves = []
    for r, row in enumerate(board_main):
        for c, piece in enumerate(row):
            if piece and piece[0] == 'b':  # AI is playing black
                moves.extend(
                    generate_piece_moves((r, c), piece, board_main, board_teleport)
                )

    for move in moves:
        source_board, target_board, start, end = move

        # Simulate the move using `move_piece`
        if move_piece(start, end, source_board, target_board, check_turn=False):
            # Evaluate the move using minimax
            eval = minimax(board_main, board_teleport, depth - 1, False, -math.inf, math.inf, 'w')
            undo_move(board_main, board_teleport, move)  # Undo move for evaluation

            if eval > best_eval:
                best_eval = eval
                best_move = move

    # Execute the best move
    if best_move:
        source_board, target_board, start, end = best_move
        if move_piece(start, end, source_board, target_board, check_turn=False):
            print(f"AI moved: {source_board[start[0]][start[1]]} from {start} to {end}")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * 2 + 50, HEIGHT + 50))
    pygame.display.set_caption("Alicia's Chess Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    images = load_images()
    selected_square = None
    selected_board = None
    running = True

    global current_turn
    current_turn = 'w'

    # Two boards: main and teleport
    board_main = [row[:] for row in INITIAL_BOARD]
    board_teleport = [row[:] for row in SECOND_BOARD]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_turn == 'w':  # Only allow interaction during the player's turn
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    if mouse_x < WIDTH:  # Main board
                        row, col = mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE
                        clicked_board = board_main
                        board_type = "main"
                    elif mouse_x > WIDTH + 20:  # Teleport board
                        row, col = mouse_y // SQUARE_SIZE, (mouse_x - WIDTH - 20) // SQUARE_SIZE
                        clicked_board = board_teleport
                        board_type = "teleport"
                    else:
                        continue  # Click was not on a board

                    if selected_square and selected_board:
                        source_board = board_main if selected_board == "main" else board_teleport
                        target_board = board_teleport if selected_board == "main" else board_main

                        if move_piece(selected_square, (row, col), source_board, target_board):
                            selected_square, selected_board = None, None
                        else:
                            selected_square, selected_board = None, None

                    elif clicked_board[row][col]:  # Select a piece
                        if clicked_board[row][col][0] == current_turn:
                            selected_square = (row, col)
                            selected_board = board_type
                            print(f"Selected {clicked_board[row][col]} at {row, col} on {board_type} board")
                        else:
                            print(f"Es el turno de {'Blancas' if current_turn == 'w' else 'Negras'}")

        if current_turn == 'b':  # AI's turn
            ai_move(board_main, board_teleport)
            current_turn = 'w'  # Switch turn back to the player

        screen.fill((0, 0, 0))  # Clear the screen

        # Draw the main board
        draw_boards(screen, offset=0)

        # Draw the teleport board with an offset
        draw_boards(screen, offset=WIDTH + 20)

        # Draw pieces
        draw_pieces_on_boards(screen, images, board_main, board_teleport)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

