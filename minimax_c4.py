import pprint
import pdb
import random

ROWS = 6
COLUMNS = 7
to_win = 4

MAX = 2
MIN = 1

MINIMAX_POINTS = {2: 1, 1: -1}

BLANK_BOARD = [[0 for i in range(COLUMNS)] for j in range(ROWS)]

if COLUMNS == 3:
    ORDER = [1, 0, 2]
elif COLUMNS == 5:
    ORDER = [2, 1, 3, 0, 4]
elif COLUMNS == 7:
    ORDER = [3, 2, 4, 1, 5, 0, 6]


def get_row(grid, col, rows):
    for i, row in enumerate(reversed(grid)):
    #if it's over a column, figure out the bottom
    #slot in the grid to put the piece
        if row[col] == 0:
            return rows-i-1
    return None

def get_winner(connected_squares):
    if len(set(connected_squares)) == 1:
        member = connected_squares.pop()
        return member

def is_row_win(grid, to_win):
    for row in reversed(grid):
        for start in range(COLUMNS - to_win + 1):
            if row[start] != 0:
                connected_squares = [row[start+i] for i in range(to_win)]
                winner = get_winner(connected_squares)
                if winner:
                    return winner

def is_col_win(grid, to_win):
    for col_num in range(COLUMNS):
        col = [row[col_num] for row in reversed(grid)]
        for start in range(ROWS - to_win + 1):
            if col[start] != 0:
                connected_squares = [col[start+i] for i in range(to_win)]
                winner = get_winner(connected_squares)
                if winner:
                    return winner

def generate_legal_diagonals(grid, to_win):
    diags = []
    #top left -> bottom right
    for row_num in range(ROWS - to_win + 1):
        for col_num in range (COLUMNS - to_win + 1):
            connected_squares = [grid[row_num+i][col_num+i] for i in range(to_win)]
            if 0 not in connected_squares:
                diags.append(connected_squares)
    #bottom left -> top right
    for row_num in range(to_win - 1, ROWS):
        for col_num in range (COLUMNS - to_win + 1):
            connected_squares = [grid[row_num-i][col_num+i] for i in range(to_win)]
            if 0 not in connected_squares:
                diags.append(connected_squares)
    return diags

def is_diag_win(grid, to_win):
    for diag in generate_legal_diagonals(grid, to_win):
        winner = get_winner(diag)
        if winner:
            return winner

def determine_winner(grid, to_win):
    return is_row_win(grid, to_win) or is_col_win(grid, to_win) or is_diag_win(grid, to_win)


def make_move(b, player):
    boards = []
    for i in ORDER:
        new_b = [row[:] for row in b] #copy board
        row = get_row(b, i, ROWS)
        if row != None:
            new_b[get_row(b, i, ROWS)][i] = player
            boards.append([new_b[:],i] )
    return boards

def no_more_moves(board):
    #if there are no 0's in the top row, there are no more moves
    return not(0 in board[0])

def get_max_or_min(possible_moves, player):
    if player == MAX:
        return max(possible_moves)
    else: #player is MIN
        return min(possible_moves)

def reverse_board(grid):
    reversed_grid = []
    for row in grid:
        reversed_grid.append([col for col in reversed(row)])
    return reversed_grid

def detect_win(boards, to_win):
    for board, col in boards:
        if determine_winner(board, to_win):
            return (True, board, col)
    return (False, board, col)

def memoize_board(b, recur_result, col, memoized_board):
    memoized_board[str(b)] = (recur_result, col)
    rev_b = reverse_board(b)
    memoized_board[str(rev_b)] = (recur_result, COLUMNS - col - 1)
    return memoized_board

def recur_add_player_depth(board, player, max_depth, to_win=4, memoized_board = {}, boards=[], col=0, depth=1):
    #pp.pprint(board)
    #pdb.set_trace()
    if (str(board) in memoized_board) and memoized_board[str(board)][0] != 0:
        #print "**the board was memoized already, will result in", memoized_board[str(board)]
        return memoized_board[str(board)]

    winner = determine_winner(board, to_win)
    if winner:
        #print "** %s is winner!" % (winner)
        return (MINIMAX_POINTS[player], col)
    elif no_more_moves(board):
        return (0, col)
    elif depth == max_depth:
        return (-2, col)
    else:
        boards = make_move(board, player)
        possible_moves = []
        pos_win, b, win_col = detect_win(boards, to_win)

        if pos_win:
            #print "possible win", win_col
            col = win_col
            recur_result = MINIMAX_POINTS[player]
            memoized_board = memoize_board(b, recur_result, col, memoized_board)
            return (recur_result, col)
        elif (depth + 1) == max_depth:
            col = 3
            recur_result = 0
            memoized_board = memoize_board(b, recur_result, col, memoized_board)
            return (recur_result, col)

        else:
            for b, col in boards:
                if player == MAX:
                    next_player = MIN
                else:
                    next_player = MAX
                recur_result, _ = recur_add_player_depth(b, next_player, max_depth, to_win, memoized_board, boards, col, depth+1)
                if recur_result == -2:
                    recur_result = 0
                else:
                    #if depth < 6:
                        #print "memoizing %s, %s for player %s" % (str(recur_result), str(col), str(player))
                    memoized_board = memoize_board(b, recur_result, col, memoized_board)
                possible_moves.append((recur_result, col))
                if MINIMAX_POINTS[player] == recur_result:
                    #print "**PRUNED"
                    return (recur_result, col)
    return get_max_or_min(possible_moves, player)
