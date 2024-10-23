import copy
import sys
import pygame
import random
import numpy as np

WIDTH = 500
HEIGHT = 500

ROWS =3
COLS=3
SQSIZE = WIDTH//COLS

LINE_WIDTH =15
CIRC_WIDTH=15
CROSS_WIDTH=20

RADIUS = SQSIZE//4

OFFSET=50
#colors
BG_COLOR=(79,40,70)
LINE_COLOR=(113,114,113)
CIRC_COLOR=(239,231,200)
CROSS_COLOR=(239,231,220)

# Define Button Colors and Dimensions
BUTTON_COLOR = (100, 200, 150)
BUTTON_HOVER_COLOR = (150, 250, 180)
TEXT_COLOR = (255, 255, 255)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40


# --- PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill(BG_COLOR)


# Button Positions
RESET_BUTTON_RECT = pygame.Rect(WIDTH // 4 - BUTTON_WIDTH // 2, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
MODE_BUTTON_RECT = pygame.Rect(3 * WIDTH // 4 - BUTTON_WIDTH // 2, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)


# --- CLASSES ---
class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.empty_sqrs = self.squares  # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 'User' if User wins
            @return 'AI' if AI wins
        '''

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return 'User' if self.squares[0][col] == 1 else 'AI'

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return 'User' if self.squares[row][0] == 1 else 'AI'

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return 'User' if self.squares[1][1] == 1 else 'AI'

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return 'User' if self.squares[1][1] == 1 else 'AI'

        # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))

        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0


class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    # --- RANDOM ---
    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[idx]  # (row, col)

    # --- MINIMAX ---
    def minimax(self, board, maximizing):
        # terminal case
        case = board.final_state()

        # User wins
        if case == 'User':
            return 1, None  # eval, move

        # AI wins
        if case == 'AI':
            return -1, None

        # draw
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # --- MAIN EVAL ---
    def eval(self, main_board):
        if self.level == 0:
            # random choice
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # minimax algo choice
            eval, move = self.minimax(main_board, False)

        print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')

        return move  # row, col


class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1  # 1 for User, 2 for AI
        self.gamemode = 'ai'  # pvp or ai
        self.running = True
        self.winner = None  # To store winner info
        self.show_lines()

    # --- DRAW METHODS ---
    def show_lines(self):
        # bg
        screen.fill(BG_COLOR)

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

        elif self.player == 2:
            # draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    # --- OTHER METHODS ---
    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'
        print(f"Game mode changed to: {self.gamemode}")

    def isover(self):
        winner = self.board.final_state(show=True)
        if winner != 0:
            self.winner = winner
            return True
        elif self.board.isfull():
            self.winner = 'Draw'
            return True
        return False

    def reset(self):
        # Reset the board, players, and game state to the initial state
        self.board = Board()  # Reset the board
        self.player = 1  # Reset to User's turn
        self.running = True  # Set running state back to True
        self.winner = None  # Reset the winner
        self.show_lines()  # Redraw the lines

        # Optionally print reset message for debugging
        print("Game has been reset!")


def draw_button(rect, text, active=False):
    color = BUTTON_HOVER_COLOR if active else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def main():
    # --- OBJECTS ---
    game = Game()
    board = game.board
    ai = game.ai

    # --- MAINLOOP ---
    while True:

        # pygame events
        mouse_pos = pygame.mouse.get_pos()
        reset_active = RESET_BUTTON_RECT.collidepoint(mouse_pos)
        mode_active = MODE_BUTTON_RECT.collidepoint(mouse_pos)

        for event in pygame.event.get():

            # quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_active:
                    game.reset()
                    board = game.board
                    ai = game.ai

                if mode_active:
                    game.change_gamemode()

                if game.running:
                    pos = event.pos
                    row = pos[1] // SQSIZE
                    col = pos[0] // SQSIZE

                    # User mark square
                    if board.empty_sqr(row, col):
                        game.make_move(row, col)

                        if game.isover():
                            game.running = False

        # AI move (only when gamemode is 'ai' and it's AI's turn)
        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            pygame.display.update()
            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.isover():
                game.running = False

        # Display Winner Message
        if not game.running and game.winner:
            font = pygame.font.Font(None, 60)
            if game.winner == 'Draw':
                message = "It's a Draw!"
            else:
                message = f'{game.winner} Wins!'
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        # Drawing the game
        draw_button(RESET_BUTTON_RECT, "Reset", reset_active)
        draw_button(MODE_BUTTON_RECT, f"Mode: {game.gamemode.upper()}", mode_active)

        pygame.display.update()


main()
