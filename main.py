# main.py
import pygame
import sys
from settings import COLS, ROWS, SECOND_BOARD, SQUARE_SIZE, WIDTH, HEIGHT, INITIAL_BOARD
from tablero import draw_boards, load_images
from pieces import draw_pieces_on_boards
from game_logic import find_king, is_in_check, is_checkmate, is_valid_move, move_piece_between_boards
from utils import get_square_under_mouse

def move_piece(start, end, source_board, target_board):
    """Move the piece on the board, capture enemy pieces, and teleport to the other board."""
    global current_turn

    sr, sc = start
    er, ec = end
    piece = source_board[sr][sc]

    if not piece:
        print("No piece to move.")
        return False

    # Check if it's the correct turn
    if piece[0] != current_turn:
        print(f"It's not {piece[0]}'s turn!")
        return False

    # Ensure the move is valid on the source board
    if is_valid_move(piece, start, end, source_board):
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
        target_board[er][ec] = piece

        print(f"{piece} teleported to {end} on the target board.")

        # Switch the turn
        current_turn = 'b' if current_turn == 'w' else 'w'
        print(f"Turn switched to: {current_turn}")
        return True
    else:
        print(f"Invalid move for {piece} from {start} to {end}.")
    return False






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

        screen.fill((0, 0, 0))  # Clear the screen

        # Draw the main board
        draw_boards(screen, offset=0)

        # Draw the teleport board with an offset
        draw_boards(screen, offset=WIDTH + 20)

        # Draw pieces
        draw_pieces_on_boards(screen, images, board_main, board_teleport)

        # Highlight selected square
        if selected_square and selected_board == "main":
            sr, sc = selected_square
            pygame.draw.rect(screen, (0, 255, 0), (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        elif selected_square and selected_board == "teleport":
            sr, sc = selected_square
            pygame.draw.rect(screen, (0, 255, 0), 
                             (sc * SQUARE_SIZE + WIDTH + 20, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Display check and checkmate states
        # Highlight check and checkmate states
        king_pos = find_king(board_main, current_turn) or find_king(board_teleport, current_turn)
        if king_pos and is_in_check(board_main, board_teleport, current_turn):
            kr, kc = king_pos
            if king_pos in board_main:
                pygame.draw.rect(screen, (255, 0, 0), (kc * SQUARE_SIZE, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
            else:
                pygame.draw.rect(screen, (255, 0, 0), 
                                (kc * SQUARE_SIZE + WIDTH + 20, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        if king_pos and is_checkmate(board_main, board_teleport, current_turn):
            print(f"Checkmate! {current_turn.upper()} loses.")
            running = False



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

