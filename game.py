import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame_menu
from pygame_menu import sound
import sys
import math
import random
import minimax_c4

width = 1280
height = 800

BLACK = 0,0,0
RED = 255,0,0
GREEN = 0,255,0
BLUE = 0,0,255
WHITE = 255, 255, 255

RADIUS = height/20

PLAYER_TO_COLOR = {1: RED, 2: BLUE}
PLAYERS_COLOR = {1: "red", 2: "blue"}
PLAYERS_IMAGE = {1: "resources/images/red.png", 2: "resources/images/blue.png"}

ROWS = 6
COLUMNS = 7
TO_WIN = 4
# depth limits for min minimax
DEPTH_LIMIT = {2: 3, 3: 5}

pygame.font.init()
FONT1 = pygame.font.SysFont("comicsansms", 32)
FONT2 = pygame.font.SysFont("comicsansms", 20)

def get_distance(mouse, piece):
    mx, my = mouse
    px, py = piece
    dx = mx-px
    dy = my-py
    dx2 = dx**2
    dy2 = dy**2
    distance2 = dx2 + dy2
    return math.sqrt(distance2)

def get_row(grid, col, rows):
    for i, row in enumerate(reversed(grid)):
    #if it's over a column, figure out the bottom
    #slot in the grid to put the piece
        if row[col] == 0:
            return rows-i-1
    return None
        
class Piece:
    def __init__(self, screen, player, pos, player_name,radius=height/20):
        self.screen = screen
        self.player = player
        self.pos = pos
        self.color = PLAYER_TO_COLOR[player]
        self.radius = radius
        self.is_grabbed = False
        self.offset = (0,0)
        self.player_name = player_name      
        image = pygame.image.load(PLAYERS_IMAGE[player])
        self.piece_image = pygame.transform.smoothscale(image, (2*RADIUS, 2*RADIUS)) 

    def set_offset(self, mouse):
        mx, my = mouse
        px, py = self.pos
        self.offset = (mx-px, my-py)

    def move(self, mouse_pos):
        mx, my = mouse_pos
        ox, oy = self.offset
        self.pos = (mx-ox, my-oy)

    def is_mouse_over(self, event):
        mouse_position = event.pos
        distance_to_center = get_distance(mouse_position, self.pos)
        return distance_to_center < self.radius

    def draw(self):
        #pygame.draw.circle(self.screen, self.color, self.pos, self.radius)
        posx, posy = self.pos
        self.screen.blit(self.piece_image, (posx-RADIUS, posy-RADIUS))
        if self.player_name != "":
            my_font = FONT2
            player = my_font.render(f"{self.player_name}'s turn", 1, WHITE)
            self.screen.blit(player, (width*0.75, 200))


class Board:
    def __init__(self, screen,name1,name2):
        self.screen = screen
        self.rows = 6
        self.cols = 7
        self.grid = [[0 for i in range(self.cols)] for j in range(self.rows)]
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.box_size = screen_height / (self.rows + 2)
        self.left_disp_offset = self.box_size * 2
        self.top_disp_offset = self.box_size
        self.computer_mode = False
        self.row_locations = []
        for col_num in range(self.cols+1):
            self.row_locations.append(self.left_disp_offset + (self.box_size * col_num))        
        self.name1 = name1
        self.name2 = name2
        image = pygame.image.load(PLAYERS_IMAGE[1])
        self.token_image1 = pygame.transform.smoothscale(image, (2*RADIUS, 2*RADIUS)) 
        image = pygame.image.load(PLAYERS_IMAGE[2])
        self.token_image2 = pygame.transform.smoothscale(image, (2*RADIUS, 2*RADIUS)) 


    def draw_board(self, winner,start_pos,end_pos, board_full):
        my_font = FONT1
        for row_num in range(self.rows+1):
            row_start = (self.left_disp_offset, self.top_disp_offset + (self.box_size *  row_num))
            row_end = (self.left_disp_offset + (self.box_size * self.cols), self.top_disp_offset + (self.box_size *  row_num))
            pygame.draw.line(self.screen, WHITE, row_start, row_end)
        for col_num in range(self.cols+1):
            col_start = (self.left_disp_offset + (self.box_size * col_num), self.top_disp_offset)
            col_end = (self.left_disp_offset + (self.box_size * col_num), self.top_disp_offset + (self.box_size * self.rows))
            if col_num > 0:
                col_label= my_font.render(str(col_num), 1, WHITE)
                self.screen.blit(col_label, (self.left_disp_offset + (self.box_size * col_num) - self.box_size/2, height-40))
            pygame.draw.line(self.screen, WHITE, col_start, col_end)
        if winner != None:
            if self.computer_mode == True:
                if winner == 2:
                    win_text = "Computer WINS!! Press 'r' to try again"
                else:
                    win_text = "%s BEAT the computer!! Press 'r' to play again" % (self.name1)
            else:
                win_text = "Player %s (%s) WINS!! Press 'r' to play again" % (self.name1, PLAYERS_COLOR[winner])
            my_font = FONT1
            winner_text = my_font.render(win_text, 1, WHITE)
            self.screen.blit(winner_text, (50, 10))
            pygame.draw.line(self.screen, GREEN, start_pos, end_pos,15)
        if board_full:
            win_text = "Tie !! Press 'r' to play again"
            my_font = FONT1
            winner_text = my_font.render(win_text, 1, WHITE)
            self.screen.blit(winner_text, (50, 10))
            pygame.draw.line(self.screen, GREEN, start_pos, end_pos,15)

    # screen coordinates are left to right (invert of grid)
    def get_col_line(self, col_num, row):
        row_num = ROWS - row
        row_start = self.top_disp_offset + (self.box_size *  row_num) #self.row_locations[row]
        row_end = self.top_disp_offset + (self.box_size *  (row_num-TO_WIN))#  self.top_disp_offset + self.box_size * (row+TO_WIN) #self.row_locations[row+TO_WIN]
        col_start = (self.row_locations[col_num+1]-self.row_locations[col_num])/2 + self.row_locations[col_num]
        col_end = col_start
        return (col_start, row_start ), (col_end, row_end)

    def get_row_line(self, row_index, start_col):
        row_num = ROWS - row_index
        row_start = self.top_disp_offset + (self.box_size *  row_num) - self.box_size/2
        row_end = row_start
        col_start =self.row_locations[start_col]
        col_end = self.row_locations[start_col+TO_WIN]
        return (col_start, row_start ), (col_end, row_end)

    def get_pos_slope_line(self, row_index, start_col):
        row_num = ROWS - row_index
        row_start = self.top_disp_offset + (self.box_size *  row_num)
        row_end = self.top_disp_offset + (self.box_size *  (row_num-TO_WIN))
        col_start =self.row_locations[start_col]
        col_end = self.row_locations[start_col+TO_WIN]
        return (col_start, row_start ), (col_end, row_end)

    def get_neg_slope_line(self, row_index, start_col):
        row_num = ROWS - row_index
        row_start = self.top_disp_offset + (self.box_size *  row_num)
        row_end = self.top_disp_offset + (self.box_size *  (row_num+TO_WIN))
        col_start =self.row_locations[start_col]
        col_end = self.row_locations[start_col+TO_WIN]
        return (col_start, row_start ), (col_end, row_end)


    def negwinline(col, row):
        pygame.draw.line(screen, win_color, (row * 100 + 100, col * 100 + 100), (row * 100 - 300, col * 100 + 500), 15)

    def poswinline(col, row):
        pygame.draw.line(screen, win_color, (row * 100, col * 100 + 100), (row * 100 + 400, col * 100 + 500), 15)


    def write_board_instructions(self):
        my_font = FONT2
        a = my_font.render("Instructions:", 1, GREEN)
        b = my_font.render("Move a chip or", 1, WHITE)
        c = my_font.render("select a column", 1, WHITE)
        d = my_font.render("Press 'r' to return", 1, WHITE)
        e = my_font.render("Press 'q' to quit", 1, WHITE)
        self.screen.blit(a, (width*0.75, 10))
        self.screen.blit(b, (width*0.75, 40))
        self.screen.blit(c, (width*0.75, 60))
        self.screen.blit(d, (width*0.75, 80))
        self.screen.blit(e, (width*0.75, 100))

    def add_offset(self, pos):
        x,y = pos
        return (x + self.left_disp_offset, y + self.top_disp_offset)

    def get_col(self, pos):
        x = pos[0]
        for col_num in range(self.cols):
            if x >= self.row_locations[col_num] and x< self.row_locations[col_num+1]:
                return col_num
        return None

    def get_indices(self, pos):
        #get the column that the mouse is over
        col = self.get_col(pos)

        #column is an integer between 0 and self.cols
        if col != None:
            row = get_row(self.grid, col, ROWS)
            if row != None:
                return (col, row)
        return None

    def get_slot_pos_from_indices(self, indices):
        x,y = indices
        board_x_pos = int(self.box_size * (x + 0.5))
        board_y_pos = int(self.box_size * (y + 0.5))
        return self.add_offset((board_x_pos, board_y_pos))

    def draw(self, winner,start_pos,end_pos,board_full):
        if winner == None and not board_full :
            self.write_board_instructions()
        for i, row in enumerate(self.grid):
            for j, col in enumerate(row):
                if col != 0:
                    if col == 1:
                        color = RED
                        image = self.token_image1
                    if col == 2:
                        color = BLUE
                        image = self.token_image2
                    pos = self.get_slot_pos_from_indices((j,i))
                    #pygame.draw.circle(self.screen, color, pos, RADIUS)
                    posx, posy = pos
                    self.screen.blit(image, (posx-RADIUS, posy-RADIUS))
        self.draw_board(winner,start_pos,end_pos,board_full)


class ConnectFour(object):

    def __init__(
            self,
            name1: str = "",
            name2: str = "",
            difficulty: int = 1,
            num_players: int = 1,
    ):
        # Create the maze
        self.name1 = name1
        self.name2 = name2
        self.difficulty = difficulty
        self.num_players = num_players


    def get_random_spot(self,grid):
        slot = random.randint(0,6)
        row = get_row(grid, slot, ROWS)
        return slot, row

    def get_winner(self,connected_squares):
        if len(set(connected_squares)) == 1:
            member = connected_squares.pop()
            return member

    def is_board_full(self,board):
        grid = board.grid
        row_index=0
        for row in grid:
            for col in range(COLUMNS):
                if row[col] == 0:
                    return False
            row_index = row_index+1
        return True

    def is_row_win(self,board):
        grid = board.grid
        row_index=0
        for row in reversed(grid):
            for start in range(COLUMNS - TO_WIN + 1):
                if row[start] != 0:
                    connected_squares = [row[start+i] for i in range(TO_WIN)]
                    winner = self.get_winner(connected_squares)
                    if winner:
                        start_pos,end_pos = board.get_row_line(row_index, start)
                        return winner,start_pos,end_pos
            row_index = row_index+1
        return None,(0,0),(0,0)

    def is_col_win(self,board):
        grid = board.grid
        for col_num in range(COLUMNS):
            col = [row[col_num] for row in reversed(grid)]
            for start in range(ROWS - TO_WIN + 1):
                if col[start] != 0:
                    connected_squares = [col[start+i] for i in range(TO_WIN)]
                    winner = self.get_winner(connected_squares)
                    if winner:
                        start_pos,end_pos = board.get_col_line(col_num, start)
                        return winner,start_pos,end_pos
        return None,(0,0),(0,0)
 
    def is_neg_slope_win(self,board):
        grid = board.grid
        diags = []
        #top left -> bottom right
        for row_num in range(ROWS - TO_WIN + 1):
            for col_num in range (COLUMNS - TO_WIN + 1):
                connected_squares = [grid[row_num+i][col_num+i] for i in range(TO_WIN)]
                if 0 not in connected_squares:
                    winner = self.get_winner(connected_squares)
                    if winner:
                        start_pos,end_pos = board.get_neg_slope_line( ROWS - row_num,col_num,)
                        return winner,start_pos,end_pos
        return None,(0,0),(0,0)

    def is_pos_slope_win(self,board):
        grid = board.grid
        diags = []
        #bottom left -> top right
        for row_num in range(TO_WIN - 1, ROWS):
            for col_num in range (COLUMNS - TO_WIN + 1):
                connected_squares = [grid[row_num-i][col_num+i] for i in range(TO_WIN)]
                if 0 not in connected_squares:   
                    winner = self.get_winner(connected_squares)
                    if winner:
                        start_pos,end_pos = board.get_pos_slope_line(ROWS - row_num -1,col_num)
                        return winner,start_pos,end_pos
        return None,(0,0),(0,0)

    def determine_winner(self,board):
        if self.is_board_full(board):
            return None,(0,0),(0,0), True
        winner,start_pos,end_pos = self.is_row_win(board)
        if winner:
            return winner,start_pos, end_pos, False
        winner,start_pos,end_pos = self.is_col_win(board)
        if winner:
            return winner,start_pos, end_pos, False
        winner,start_pos,end_pos = self.is_pos_slope_win(board)
        if winner:
            return winner,start_pos, end_pos, False
        winner,start_pos,end_pos = self.is_neg_slope_win(board)
        if winner:
            return winner,start_pos, end_pos, False
        return None,(0,0),(0,0), False

    def game_loop(self,screen, clock, mode, main_menu, level=None):
        b = Board(screen, self.name1,self.name2)
        red_piece = Piece(screen, 1, (int(width*0.75), height/2),self.name1)
        piece = red_piece

        added_to_grid = False
        winner = None
        start_pos = (0,0)
        end_pos = (0,0)
        board_is_full = False

        while True:
            if mode != "reset":
                screen.fill(BLACK)
                b.draw(winner,start_pos,end_pos,board_is_full)
                if piece:
                    piece.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_x or event.key == pygame.K_q)):
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu.enable()
                        return
                if event.type == pygame.KEYDOWN or mode == "reset":
                    if event.key == pygame.K_r or mode == "reset":
                    #player wants to reset game
                        main_menu.enable()
                        return

                # Pass events to main_menu
                if main_menu.is_enabled():
                    main_menu.update(events)
 

                if piece:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                    #if mouse is over the piece, set piece as grabbed
                    #and record the offset as the distance from mouse to center
                        mouse_pos = pygame.mouse.get_pos()
                        piece.is_grabbed = piece.is_mouse_over(event)
                        if piece.is_grabbed:
                            piece.set_offset(event.pos)


                    if event.type == pygame.MOUSEMOTION and piece.is_grabbed:
                    #if you move while the piece is grabbed, move the piece
                    #with you.
                        if piece.is_grabbed:
                            piece.move(event.pos)

                    if event.type == pygame.MOUSEBUTTONUP:
                    #if you unclick piece over the board, get "indices" of board
                    #position to put piece
                        if piece.is_grabbed:
                            indices = b.get_indices(piece.pos)
                            if indices:
                                slot_pos = b.get_slot_pos_from_indices(indices)

                                x,y = indices
                                b.grid[y][x] = piece.player
                                added_to_grid = True


                    if event.type == pygame.KEYDOWN:
                        #see if a slot was selected by user (key 1-7)
                        slot = event.key - 49#if you press 1-7 event.key = 49-55
                        if slot <= 6:
                            row = get_row(b.grid, slot, ROWS)
                            if row != None:
                                b.grid[row][slot] = piece.player
                                added_to_grid = True

          
            if self.num_players == 1: # Player Vs Computer
                b.computer_mode = True
                level = self.difficulty
                if piece != None and piece.player == 2:
                    if level == 1: # "easy"
                        slot, row = self.get_random_spot(b.grid)
                    if level == 2 or level == 3:  # "medium" or "hard"
                        _, slot = minimax_c4.recur_add_player_depth(b.grid, 2, DEPTH_LIMIT[level], 4, {})
                        row = get_row(b.grid, slot, ROWS)
                    if row != None:
                        b.grid[row][slot] = piece.player
                        added_to_grid = True

            if added_to_grid:
                #alternate player 1 and 2
                next_player = (piece.player)%2 + 1

                added_to_grid = False

                winner,start_pos, end_pos, board_is_full = self.determine_winner(b)
                if winner or board_is_full:
                    piece = None
                    mode = None
                else:
                    if next_player ==1:
                        player_name = self.name1
                    else:
                        player_name = self.name2
                    piece = Piece(screen, next_player, (int(width*0.75), height/2),player_name)

            pygame.display.flip()
            clock.tick(100)


    def button(gameDisplay,msg,x,y,w,h,ic,ac,action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
            if click[0] == 1 and action != None:
                action()         
        else:
            pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
        smallText = pygame.font.SysFont("comicsansms",20)
        textSurf, textRect = text_objects(msg, smallText)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        gameDisplay.blit(textSurf, textRect)
        


    def text_objects(text, font):
        textSurface = font.render(text, True, BLACK)
        return textSurface, textSurface.get_rect()
     

def main():
    app = ConnectFour( "name1", "name2", 1, 1)
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    app.game_loop(screen, clock, "play")
    return app


if __name__ == '__main__':
    main()