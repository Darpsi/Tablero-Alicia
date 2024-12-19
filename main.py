import math
import pygame
import sys
from ia_greed import busqueda_greedy
from ia import generate_piece_moves, minimax, undo_move
from settings import SECOND_BOARD, SQUARE_SIZE, WIDTH, HEIGHT, INITIAL_BOARD
from tablero import draw_boards, load_images
from pieces import draw_pieces_on_boards
from game_logic import find_king, is_in_check, is_valid_move


use_greedy_search = True

def move_piece(start, end, source_board, target_board, check_turn=True):
    """Move the piece on the board, capture enemy pieces, and teleport to the other board."""
    global current_turn

    sr, sc = start
    er, ec = end
    piece = source_board[sr][sc]

    if not piece:
        print("No hay pieza para mover.")
        return False

    if check_turn and piece[0] != current_turn:
        print(f"No es el turno de {piece[0]}!")
        return False

    if is_valid_move(piece, start, end, source_board):
        
        if source_board is target_board:
            print("La pieza no se teletransporta")
            return False

        if target_board[er][ec]:
            print(f"El cuadro {end} no esta vacio!")
            return False
        
        source_board[sr][sc] = None

        temp_source_board = [row[:] for row in source_board]
        temp_target_board = [row[:] for row in target_board]
        temp_target_board[er][ec] = piece

        if is_in_check(temp_source_board, temp_target_board, current_turn):
            print("El rey esta en check!")
            source_board[sr][sc] = piece
            return False

        source_board[er][ec] = None 
        target_board[er][ec] = piece

        current_turn = 'b' if current_turn == 'w' else 'w'
        return True
    else:
        print(f"Movimiento invalido.")
    return False



def ai_move(board_main, board_teleport):
    global current_turn, use_greedy_search

    print("Pensando")
    depth = 2 
    if use_greedy_search:
        print("Usando avara.")
        greedy_result = busqueda_greedy(board_main, board_teleport, 50, 'b')
        if greedy_result:
            best_move, _ = greedy_result 
            if best_move:
                start, end = best_move[2], best_move[3] 
                source_board, target_board = best_move[0], best_move[1]
                if is_valid_move(source_board[start[0]][start[1]], start, end, source_board):
                    move_piece(start, end, source_board, target_board, check_turn=False)
        else:
            print("No encontro movimiento.")

    else:
        print("Usando Minimax...")
        best_move = None
        best_eval = -math.inf

        moves = []
        for r, row in enumerate(board_main):
            for c, piece in enumerate(row):
                if piece and piece[0] == 'b':  
                    possible_moves = generate_piece_moves((r, c), piece, board_main, board_teleport)
                    for move in possible_moves:
                        source_board, target_board, start, end = move
                        if is_valid_move(piece, start, end, source_board): 
                            if target_board[end[0]][end[1]] is None:
                                moves.append(move)

        for r, row in enumerate(board_teleport):
            for c, piece in enumerate(row):
                if piece and piece[0] == 'b': 
                    possible_moves = generate_piece_moves((r, c), piece, board_teleport, board_main)
                    for move in possible_moves:
                        source_board, target_board, start, end = move
                        if is_valid_move(piece, start, end, source_board): 
                            if target_board[end[0]][end[1]] is None:
                                moves.append(move)

        for move in moves:
            source_board, target_board, start, end = move
            if move_piece(start, end, source_board, target_board, check_turn=False):
                eval = minimax(board_main, board_teleport, depth - 1, False, -math.inf, math.inf, 'w')
                undo_move(board_main, board_teleport, move)

                if eval > best_eval:
                    best_eval = eval
                    best_move = move
            

        if best_move:
            source_board, target_board, start, end = best_move
            move_piece(start, end, source_board, target_board, check_turn=False)

    use_greedy_search = not use_greedy_search
    current_turn = 'w' 







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


