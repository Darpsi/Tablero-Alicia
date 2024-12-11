# main.py
import pygame
import sys
from settings import COLS, ROWS, SECOND_BOARD, SQUARE_SIZE, WIDTH, HEIGHT, INITIAL_BOARD
from tablero import draw_boards, load_images
from pieces import draw_pieces_on_boards
from game_logic import find_king, is_in_check, is_checkmate, is_valid_move, move_piece_between_boards
from utils import get_square_under_mouse

def move_piece(start, end, source_board, target_board):
    """Move the piece on the board and teleport it to the other board."""
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

    if is_valid_move(piece, start, end, source_board):
        # Simulate the move
        temp_board = [row[:] for row in source_board]
        temp_board[er][ec] = piece
        temp_board[sr][sc] = None

        # Check if the move leaves the king in check
        if is_in_check(temp_board, current_turn):
            print("Move leaves the king in check!")
            return False

        # Apply the move on the source board
        source_board[er][ec] = None
        source_board[sr][sc] = None

        # Teleport the piece to the target board
        target_board[er][ec] = piece
        target_board[sr][sc] = None

        print(f"Moved {piece} to {end} on source board and teleported to the other board.")

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
        king_pos = find_king(board_main, current_turn)
        if king_pos and is_in_check(board_main, current_turn):
            kr, kc = king_pos
            pygame.draw.rect(screen, (255, 0, 0), (kc * SQUARE_SIZE, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        if king_pos and is_checkmate(board_main, current_turn):
            print(f"Checkmate! {current_turn.upper()} loses.")
            running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

