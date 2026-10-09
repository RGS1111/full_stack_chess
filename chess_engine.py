import numpy as np
import itertools
import math

class board:
    def __init__(self):
        self.board_array = np.zeros((8,8), dtype=int)
        #flipped_array = np.flip(board_array) (not needed since i have the negative number logic
        #for opposing player)
        count_p1 = 0
        for row in range(0,2):
            for column in range (0,8):
                count_p1 = count_p1 + 1
                self.board_array[row, column] = count_p1
        count_p2 = 0
        for row in range(6,8):
            for column in range (0,8):
                count_p2 = count_p2 - 1
                self.board_array[row, column] = count_p2
    def game_view(self):
        translate_to_letters = { 1 : "R",
                                 2 : "k",
                                 3 : "B",
                                 4 : "Q",
                                 5 : "K",
                                 6 : "B",
                                 7 : "k",
                                 8 : "R",
                                 -9 : "R",
                                 -10 : "k",
                                 -11 : "B",
                                 -12 : "Q",
                                 -13 : "K",
                                 -14 : "B",
                                 -15 : "k",
                                 -16 : "R"}
        letter_board_array = np.zeros((9,9), dtype=object)
        letter_board_array[0, 0] = " "
        for label in range(1, 9):
            # turned to string so that labels align with the board
            # for column 
            letter_board_array[0, label] = f"\033[1m{label - 1}\033[0m"
            # for row
            letter_board_array[label, 0] = f"\033[1m{label - 1}\033[0m"

        for row in range(8):
            for column in range(8):
                board_pos = (row, column)
                # shift down right, so that it fits the labels for row and columns 
                letter_pos = (row + 1, column + 1)

                piece_id = self.board_array[board_pos]

                # checks if piece_id is pawn, returns 1 if pawn else 0
                is_pawn = 1 if (piece_id >= 9 
                                and piece_id <= 16) \
                                or (piece_id >= -8 and 
                                    piece_id <= -1) else 0
                if is_pawn == 1:
                    letter_board_array[letter_pos] = "P"
                elif piece_id != 0:
                    piece_letter = translate_to_letters[piece_id]
                    letter_board_array[letter_pos] = piece_letter
                else:
                    letter_board_array[letter_pos] = "0"
                    
        # loop through each row and print it as a clean space separated line by forcing numpy out of debug mode
        for row in letter_board_array:
            print("   ".join(str(cell) for cell in row))


    def sign_check(self, piece_id):
            # sign of piece_id compared to biggefr or smaller than 0 returning true or false aka 1 or 0 
            # and then if bigger than 0, then the same piece_id is NOT smaller than 0, so 0 
            # therefore 1 - 0 = +1 or if opposite example 0 - 1 = -1, thus determining sign
            return (int(piece_id > 0) - int(piece_id < 0))
    
    # returns the piece id, for checking of piece
    def get_piece_id(self, start):
        return self.board_array[start]

    def can_capture(self, start, end):
        start_id = self.board_array[start]
        end_id = self.board_array[end]

        if end_id == 0:
            return True
        # returns true if the start piece is a different sign to the end piece 
        # aka + and - means black and white 
        return (self.sign_check(start_id) != self.sign_check(end_id))

    def path_clear(self, start, end):
        # NOT TO BE USED FOR KNIGHT AS IT JUMPS OVER PIECES, so no path to check clearing for

        ########## flipped x and y in start and end, so that coordinates dispalyed are normal, 
        # NOT INDICATIVE of how the system views x and y internally
        (x1, y1) = start
        (x2, y2) = end
        dx = x2 - x1
        dy = y2 - y1
        # Allows us to trace the direction of the move 
        stepx = 1 if dx > 0 else -1 if dx < 0 else 0 
        stepy = 1 if dy > 0 else -1 if dy < 0 else 0
        
        # current starts 1 off forward as we know there is nothing blocking us in 
        # the initial standing position
        current = (x1, y1)
        # print(current)
        # print("Previous Position:",start[::-1], self.board_array[current])
        # print("New Position:",end[::-1], self.board_array[current])
        ################################# x and y in visual is flipped
        while current != end:
            current = (
                current[0] + stepx,
                current[1] + stepy
            )
            # makes sure that the end coordinate is never decided, 
            # so that can_capture decides the capture logic
            if current == end:
                break
            if self.board_array[current] != 0:
                return False
        return True

    def is_empty(self, end):
        return self.board_array[end] == 0
    # checks to see if coordinates are within board range
    def within_board(self, generated_pos):
        within_x_axis = (generated_pos[1] >= 0) and (generated_pos[1] <= 7)
        within_y_axis = (generated_pos[0] >= 0) and (generated_pos[0] <= 7)
        return within_y_axis and within_x_axis
    
    def is_enemy(self, current_piece_id, end):
        # board coordinates needed
        target_id = self.board_array[end]
        if target_id == 0:
            return False
        return (current_piece_id > 0) != (target_id > 0)

    def is_pawn(self, end):
        piece_id = self.board_array[end]
        return (piece_id >= -8 and piece_id <= 9)

    def undo_move(self, board_start, board_end, captured_piece):
        self.board_array[board_start] = self.board_array[board_end]
        self.board_array[board_end] = captured_piece

    def move_piece(self, start, end):
        self.board_array[end] = self.board_array[start]
        self.board_array[start] = 0
        #self.game_view()
    # # to decide 1 or 2 step move for 1st move on pawn
    # def increment_pawn(self, start):
    #     pawn_id = self.board_array[start]


class pieces:
    def __init__(self):
        # contains all the pieces metadata for all 32 significant pieces
        self.piece = {
        1 : rook(),
        2 : knight(),
        3 : bishop(),
        4 : queen(),
        5 : king(),
        6 : bishop(),
        7 : knight(),
        8 : rook(),
        9 : pawn(),
        10 : pawn(),
        11 : pawn(),
        12 : pawn(),
        13 : pawn(),
        14 : pawn(),
        15 : pawn(),
        16 : pawn(),
        -1 : pawn(),
        -2 : pawn(),
        -3 : pawn(),
        -4 : pawn(),
        -5 : pawn(),
        -6 : pawn(),
        -7 : pawn(),
        -8 : pawn(),
        -9 : rook(),
        -10 : knight(),
        -11 : bishop(),
        -12 : queen(),
        -13 : king(),
        -14 : bishop(),
        -15 : knight(),
        -16 : rook()
        }

    def pawn_promotion(self, id, promotion):
        self.piece[id] = promotion
        #print(f"promoted to {promotion}")

##############################################################################################################
# for all chess peices the move made by the player can be determined by subtracting 
# the end position and start position giving a constant change/pattern for each piece
class pawn:
    # hardest and most feature rich func, with all the things a pawn can do
    # - pawn can either move 1 step forward at start or 2 squares forward 
    # - en passant - pawn that has moved forward 2 squares can be 
    #   captured by opposing pawn (by moving straight 1 square next to pawn 
    #   which has moved 2 squares) 
    # - pawn promotion when pawn reaches end of oppsite side board - TODO
        
    def is_valid_move(self, start, end, board, board_start, board_end, en_passant_target):
        #self.board = board()
        # user presentable x,y start and end 
        (x1, y1) = start 
        (x2, y2) = end 
        #print("start and end: ", start, end)
        dx = x2 - x1
        dy = y2 - y1
        piece_id = board.get_piece_id(board_start)
        target_id = board.get_piece_id(board_end)
        # pawns initially located at y = 1 and y = 6
        direction = 1 if piece_id > 0 else -1
        pawn_start_row = 1 if piece_id > 0 else 6

        # normal forward 
        if dx == 0 and dy == direction and board.is_empty(board_end):
            return True
        # double step 
        if (dx == 0 and dy == 2 * direction and y1 == pawn_start_row and board.is_empty(board_end) and board.is_empty((y1 + direction, x1))):
            return True 
        # diagonal capture only 
        if (abs(dx) == 1 and dy == direction and board.is_enemy(piece_id, board_end)):
            return True
        # en-passant capture 
        if abs(dx) == 1 and dy == direction and end == en_passant_target:
            return True 
            
class bishop:
    def is_valid_move(self, start, end, board = None, board_start = None, board_end = None, en_passant_target = None):
        (x1, y1) = start
        (x2, y2) = end 
        return(abs((x2-x1)) == abs((y2-y1)))
    #2 pieces per side/manipulate both with one class
    #pass
class knight:
    #2 pieces per side/manipulate both with one class
    ####### this piece doesn't need to have 'check_path', as knight JUMPS in L shape, 
    # skipping the pieces in between
    def is_valid_move(self, start, end, board = None, board_start = None, board_end = None, en_passant_target = None):
        (x1, y1) = start
        (x2, y2) = end 
        #print("start and end: ", start, end)
        dx = x2 - x1
        dy = y2 - y1
        # the general direction that the piece moves in 
        return((abs(dx) == 2) and (abs(dy) == 1)
               or ((abs(dy) == 2) and (abs(dx) == 1)))

class rook:
    def is_valid_move(self, start, end, board = None, board_start = None, board_end = None, en_passant_target = None):
        (x1, y1) = start
        (x2, y2) = end
        dx = x2 - x1
        dy = y2 - y1
        # Allows us to trace the direction of the move 
        stepx = 1 if dx > 0 else -1 if dx < 0 else 0 
        stepy = 1 if dy > 0 else -1 if dy < 0 else 0
        return((abs(stepx) == 1 and stepy == 0) or (stepx == 0 and abs(stepy) == 1))

class king:
    #1 piece per side/manipulate both with one class
    def is_valid_move(self, start, end, board = None, board_start = None, board_end = None, en_passant_target = None):
        (x1, y1) = start
        (x2, y2) = end 
        dx = x2 - x1
        dy = y2 - y1
        return(((abs(dx) == 1 and dy == 0)) 
               or ((dx == 0 and abs(dy) == 1)) 
               or (abs(dx) == 1 and abs(dy) == 1))
class queen:
    #1 piece per side/manipulate both with one class
    # queen can make moves from both the bishop and the rook, 
    # aka (linear and diagonal)
    def is_valid_move(self, start, end, board = None, board_start = None, board_end = None, en_passant_target = None):
            (x1, y1) = start
            (x2, y2) = end
            dx = x2 - x1
            dy = y2 - y1
            # Allows us to trace the direction of the move 
            stepx = 1 if dx > 0 else -1 if dx < 0 else 0 
            stepy = 1 if dy > 0 else -1 if dy < 0 else 0
            # rook and bishop conditions combined 
            return((abs((x2-x1)) == abs((y2-y1))) 
                   or (abs(stepx) == 1 and stepy == 0) 
                   or (stepx == 0 and abs(stepy) == 1)) 

class player:
    def __init__(self, colour):
        # balck is +1 and white is -1
        self.colour = colour
        self.captured_pieces = []  

class game:
    # logic to control and manage all classses here, below all other classes and things needed \
    # dictionary to have letter/number position identity instead of coordinates
    # dictionary or such to identify what piece each number is, from 1-16 (same for -1 to -16)
    def __init__(self):
        self.playing = True
        self.board = board()
        self.pieces = pieces()
        self.en_passant_target = (None) # store target tuple or none
        #######################################################################
        self.black = player(1)
        self.white = player(-1)
        # black goes 1st by deafult 
        self.current_player = self.black
        self.kings_moved = {1 : 0, -1 : 0}
        self.rooks_moved = {1 : 0, -9 : 0,
                        8 : 0, -16 : 0}
        # coordinates in y, x format 
        self.king_position = {1 : (0, 4),
                            -1 : (7, 4)}
        #("Current Player: Black (Top)")
    def sign_check(self, piece_id):
        # sign of piece_id compared to biggefr or smaller than 0 returning true or false aka 1 or 0 
        # and then if bigger than 0, then the same piece_id is NOT smaller than 0, so 0 
        # therefore 1 - 0 = +1 or if opposite example 0 - 1 = -1, thus determining sign
        #print(int(piece_id > 0), int(piece_id < 0))
        return (int(piece_id > 0) - int(piece_id < 0))

    def switch_player(self):
        # switch player after successful move 
        if self.current_player == self.black:
            self.current_player = self.white
            #print("\n")
            #print("\nCurrent Player: WHITE (Bottom)")
        else:
            self.current_player = self.black
            #print("\nCurrent Player: BLACK (Top)\n")


    def king_in_check(self, king_position):
        # logic for king in check RETURN TRUE IF king_in_check
        # check diagonal(4) and orthogonal(4) + knight jump (8)
        # knight jump check can be calculated using a dictionary of 8 positions displaced from king
        y1, x1 = king_position
        # 8 DIRECTIONS FOR KNIGHT 
        numbers = [1, 2, -1, -2]
        pairs = itertools.permutations(numbers, 2)
        filtered_pairs = [knight_pos for knight_pos in pairs if abs(knight_pos[0]) != abs(knight_pos[1])] 
        king_id = self.board.get_piece_id(king_position)
        for knight_pos in filtered_pairs:
            # for board coordinates
            dy, dx = knight_pos
            generated_pos = (y1 + dy, x1 + dx)

            if self.board.within_board(generated_pos):
                gen_piece_id = self.board.get_piece_id(generated_pos)

                if gen_piece_id != 0:
                    gen_chess_piece = self.pieces.piece[gen_piece_id]

                    if (isinstance(gen_chess_piece, knight)
                            and self.board.is_enemy(king_id, generated_pos)):
                        return True
                        
        # DIAGONAL CHECK FOR BISHOP,QUEEN, PAWN
        # list of all possible diagonal movements
        diagonal_step = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        # for loop to check all 4 directions till board end. 
        for dy, dx in diagonal_step:
            y, x = y1 + dy, x1 + dx
            while self.board.within_board((y, x)):
                diagonal_pos = (y, x)
                piece_id = self.board.get_piece_id(diagonal_pos)

                if piece_id != 0:
                    diag_piece = self.pieces.piece[piece_id]

                    if self.board.is_enemy(king_id, diagonal_pos):

                        if isinstance(diag_piece, bishop) or isinstance(diag_piece, queen):
                            return True 
                    # break here as there is no other end condition
                    break
                # increment y and x by the diagonal_step
                y += dy
                x += dx
                        
        # ORTHOGONAL CHECK FOR ROOK, QUEEN, PAWN
        orthogonal_step = [(1, 0), (0, 1), (0, -1), (-1, 0)]
        for dy, dx in orthogonal_step:
            y, x = dy + y1, dx + x1

            while self.board.within_board((y, x)):
                orthogonal_pos = (y, x)
                piece_id = self.board.get_piece_id(orthogonal_pos)

                if piece_id != 0:
                    orthogonal_piece = self.pieces.piece[piece_id]

                    if self.board.is_enemy(king_id, orthogonal_pos):

                        if isinstance(orthogonal_piece, rook) or isinstance(orthogonal_piece, queen):
                            return True
                    break

                y += dy
                x += dx

        # PAWN CHECK - FOR INDIVIDUAL ONE STEP PAWNS NEAR KING 
        pawn_direction = 1 if king_id < 0 else -1
        # checks for individual diagonal pawns around king leading too check
        pawn_positions = [(y1 + pawn_direction, x1 - 1), (y1 + pawn_direction, x1 + 1)]

        for pawn_pos in pawn_positions:
            if self.board.within_board(pawn_pos):
                piece_id = self.board.get_piece_id(pawn_pos)

                if piece_id != 0:
                    piece_name = self.pieces.piece[piece_id]

                    if (isinstance(piece_name, pawn)
                            and self.board.is_enemy(king_id, pawn_pos)):
                        return True
                # KING CHECK
        king_step = [
            (1, 0), (-1, 0),
            (0, 1), (0, -1),
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]

        # if enemy attacking is opposing teams king 
        for dy, dx in king_step:
            king_pos = (y1 + dy, x1 + dx)

            if self.board.within_board(king_pos):
                piece_id = self.board.get_piece_id(king_pos)

                if piece_id != 0:
                    piece = self.pieces.piece[piece_id]

                    if (isinstance(piece, king)
                        and self.board.is_enemy(king_id, king_pos)):
                        return True

        return False
        # if this is reached then king is just not in check

    def has_legal_move(self, colour, king_position):
    # checks whether the player has at least ONE legal move
    # Returns:
    # - True  means a legal move exists
    # - False means no legal moves exist

        for row in range(8):
            for column in range(8):

                board_start = (row, column)
                piece_id = self.board.get_piece_id(board_start)

                # empty square
                if piece_id == 0:
                    continue

                # only look at pieces belonging to this player
                if (piece_id > 0) != (colour > 0):
                    continue

                chess_piece = self.pieces.piece[piece_id]

                # try every possible destination
                for end_row in range(8):
                    for end_column in range(8):

                        board_end = (end_row, end_column)

                        if board_start == board_end:
                            continue

                        # convert board coordinates (y,x)
                        # into user coordinates (x,y)
                        start = (column, row)
                        end = (end_column, end_row)

                        # Check piece movement rules
                        if not chess_piece.is_valid_move(start, end, self.board, board_start, board_end, self.en_passant_target):
                            continue

                        # knights jump over pieces
                        if isinstance(chess_piece, knight):
                            path_is_clear = True
                        else:
                            path_is_clear = self.board.path_clear(board_start, board_end)

                        if not path_is_clear:
                            continue

                        # Normal capture / empty square
                        legal_capture = self.board.can_capture(board_start, board_end)

                        # Special case: en passant
                        en_passant = (isinstance(chess_piece, pawn) 
                            and end == self.en_passant_target
                            and self.board.is_empty(board_end))

                        if not legal_capture and not en_passant:
                            continue

                        # Save current board
                        saved_board = self.board.board_array.copy()

                        self.board.board_array[board_end] = piece_id
                        self.board.board_array[board_start] = 0

                        # en-passant removes the pawn behind the target square
                        if en_passant:
                            captured_pawn_pos = (board_start[0], board_end[1])
                            self.board.board_array[captured_pawn_pos] = 0

                        # determine where this players king would be
                        if isinstance(chess_piece, king):
                            test_king_position = board_end
                        else:
                            test_king_position = king_position

                        # if the king is NOT in check after this move, then we found an escape
                        still_in_check = self.king_in_check(test_king_position)

                        # restore board
                        self.board.board_array = saved_board

                        if not still_in_check:
                            return True

        # if every possible move was tested and all left the king in check
        return False


    def checkmate(self, colour, king_position):
        # returns true if the player is in checkmate

        # Checkmate requires the king to currently be in check
        if not self.king_in_check(king_position):
            return False

        # If there is at least one legal escape, it isn't checkmate
        if self.has_legal_move(colour, king_position):
            return False

        return True

    def force_castle(self, board_start, board_end, rook_board_start, rook_board_end):
        # function to force rook to move for castling logic TODO 
        # moves the king by 2 pieces entere by user
        self.board.move_piece(board_start, board_end)
        # moves the closest rook next to the king 
        self.board.move_piece(rook_board_start, rook_board_end)


    def castling_condition(self, start, end, board_start, board_end, kings_moved, rooks_moved, king_id):
        # king must not have moved before
        king_side = 1 if king_id > 0 else -1

        if kings_moved[king_side] != 0:
            #print("Invalid Castling: King has already moved")
            return False

        # four legal castling moves in GAME coordinates
        # rook positions are given in BOARD coordinates
        castling_moves = {
            ((4, 7), (2, 7)): ((7, 0), (7, 3)),  # White queenside
            ((4, 7), (6, 7)): ((7, 7), (7, 5)),  # White kingside
            ((4, 0), (2, 0)): ((0, 0), (0, 3)),  # Black queenside
            ((4, 0), (6, 0)): ((0, 7), (0, 5))   # Black kingside
        }

        move = (start, end)

        if move not in castling_moves:
            #print("Invalid Castling")
            return False

        rook_board_start, rook_board_end = castling_moves[move]

        # Check that the correct rook exists
        rook_id = self.board.get_piece_id(rook_board_start)

        if rook_id not in rooks_moved:
            #print("Invalid Castling: No valid rook")
            return False

        # Make sure the piece actually is a rook
        if not isinstance(self.pieces.piece[rook_id], rook):
            #("Invalid Castling: Piece is not a rook")
            return False 

        # Rook must not have moved before
        if rooks_moved[rook_id] != 0:
            #print("Invalid Castling: Rook has already moved")
            return False

        # Every square between king and rook must be empty
        if not self.board.path_clear(board_start, rook_board_start):
            #print("Invalid Castling: Path is blocked")
            return False

        # If all conditions above passed, perform castling
        self.force_castle(board_start, board_end, rook_board_start, rook_board_end)
        # - returns TRUE for KING, so king_in_check can track the king pos for check 
        #   using kings end coordinates
        return True  
    def make_move(self, start, end, promotion_choice = None):

        if self.playing == False:
            return {"valid" : False,
                    "reason" : "Game Over"}
        # self.board.game_view()
        # below the tuple stores everything as string
        x1, y1 = start
        x2, y2 = end 

        # on board row and column as x and y is flipped, so y in x and x in y position 
        board_start = (y1, x1)
        board_end = (y2, x2)
        board_piece_start = self.board.get_piece_id(board_start)
        board_piece_end = self.board.get_piece_id(board_end)
        # for en-passant logic dy
        dx = x2 - x1
        dy = y2 - y1

        if self.board.get_piece_id(board_start) == 0: # fixes the 0 id bug, as not in ß
            return {"valid" : False,
                    "reason" : "No piece at starting square"}
        # retrives the id for the starting/playing piece
        piece_id = self.board.get_piece_id(board_start)

        # check the selected piece belongs to current_player
        if piece_id > 0:
            piece_colour = 1
        else:
            piece_colour = -1
        if piece_colour != self.current_player.colour:
            #print("\n That is not your piece.\n")
            return {"valid" : False,
                    "reason" : "This is not your piece"}
            
        # chess_piece holds the class for the id's piece type (eg. rook, queen ect...)
        chess_piece = self.pieces.piece[piece_id]
        # if start == end then move invalid
        if start == end:
            #print("\nInvalid Move\n")
            return {"valid" : False,
                    "reason" : "Start cannot be same as end"}
        # is_valid_move function used to check the move conforms to its piece id 
        # - 'start' and 'end' given to chess piece class as its the correct x,y format for user 
        #   and 'boardstart' and 'boardend' given to the internal board mechanics
        if chess_piece.is_valid_move(start, end, self.board, board_start, board_end, self.en_passant_target): 
            # - self.board instead of self.board(), as the '()' represents calling 
            #   a function, in which the piece that recieves the board function 
            #   will not be able to access the function, due to it being in the 
            #   game() class, so just pass a REFRENCE instead, aka 'self.board' 
            #   which points to the board in memory stored in game class.

            if isinstance(chess_piece, knight): # knight != path check as it jumps over 
                path_is_clear = True
            else:
                path_is_clear = self.board.path_clear(board_start, board_end)

            if not path_is_clear:
                return{"valid" : False,
                       "reason" : "Path is not clear"}
            if not self.board.can_capture(board_start, board_end):
                return {"valid" : False,
                        "reason" : "Cannot capture your own piece"}

            # PAWN PROMOTION
            if isinstance(chess_piece, pawn) and y2 in (0 , 7):
                # - I can use 'or' here, since a pawn cannot travel backwards, thus any pawn at 
                #   vertical ends y == 0 or y == 7 would be eligible for a pawn promotion
                if promotion_choice is None:
                    return {"valid" : True,
                            "promotion_required" : True}
                
                promotion = {1 : rook(),
                            2 : knight(),
                            3 : bishop(),
                            4 : queen()} 
                
                # quick validation 
                if promotion_choice not in promotion:
                    return {"valid" : False,
                            "reason" : "Invalid promotion choice"}

                self.pieces.pawn_promotion(piece_id, promotion[promotion_choice])
            
            # EN-PASSANT MOVE and Capture

            en_passant = (isinstance(chess_piece, pawn) and 
                            end == self.en_passant_target and 
                            self.board.is_empty(board_end))
            # initialize captured piece to 0 each time (as a precaution)
            captured_piece = 0
            if en_passant:
                # in y, x form, starting y and ending x is the captured piece for en passant
                captured_pawn_pos = (board_start[0], board_end[1])
                # if en-passant, then piece captured is captured_pawn_pos
                captured_piece = self.board.get_piece_id(captured_pawn_pos)
                self.board.board_array[captured_pawn_pos] = 0

            else:
                # if not en passant capture is normal board_end
                captured_piece = self.board.get_piece_id(board_end)

            # ##################################################################################################################################################
            self.board.move_piece(board_start, board_end)#
            # ##################################################################################################################################################

            # CHECK KINGS SAFETY
            if isinstance(chess_piece, king):
                test_king_position = board_end
            else:
                test_king_position = self.king_position[piece_id // abs(piece_id)]

            if self.king_in_check(test_king_position):
                self.board.undo_move(board_start, board_end, captured_piece)

                return {"valid" : False,
                        "reason" : "Invalid move, king would be in check"}
                    
            # CAPTURED PIECE RECORDED
            # stores en-passant capture (where ending piece pos is target of en-passant) 
            # or normal piece board_end capture (where the ending piece pos is captured)
            if captured_piece != 0:
                # stores the captured piece into white or black holding 
                self.current_player.captured_pieces.append(captured_piece)

            # KINGS STATE
            # determines the kings eligibility for castling (must not have moved)
            if isinstance(chess_piece, king):
                # piece_id must be the king's id, then piece_id / abs(piece_id will give +1 or -1, as black or white)
                team = piece_id // abs(piece_id) 
                self.kings_moved[team] += 1
                # - updates current king position for king_in_check function needing king 
                #   coordinates at all times 
                self.king_position[team] = board_end

            # ROOK STATE
            # determines the rooks eligibility for castling (must not have moved)
            if isinstance(chess_piece, rook):
                self.rooks_moved[piece_id] += 1

            # PAWN STATE / EN-PASSANT
            # - Check if the moved piece was a double step pawn for en-passant count 
            #   as en-passant only occurs on the turn after the double pawn moves forward
            if isinstance(chess_piece, pawn) and abs(dy) == 2:
                # Target square is the skipped square in user coordinates (x, y)
                skipped_y = (y1 + y2) // 2
                self.en_passant_target = (x1, skipped_y)
            else:
                # Clear en passant if any other move is made
                    self.en_passant_target = None

            # CHECKMATE LOGIC
            # check whether the opposing player is now in checkmate
            if self.current_player == self.black:
                opponent_colour = -1
            else:
                opponent_colour = 1
            
            opponent_king_position = self.king_position[opponent_colour]

            # function below checks if the move current player 
            # - has done causes the other player to be trapped
            # - if so then current player HAS WON
            if self.checkmate(opponent_colour, opponent_king_position):
                self.playing = False
                # board sent back at end due to checkmate as list for json to contain send 
                return {"valid" : True,
                        "board" : self.board.board_array.tolist(),
                        "playing" : self.playing,
                        "checkmate" : True,
                        "current_player" : self.current_player.colour}
            
            # PLAYER SWITCH
            # switch player after successful move 
            self.switch_player()

            # CORRECT/WORKING MOVE 
            # after checks and special conditions
            return {"valid" : True,
                    "board" : self.board.board_array.tolist(),
                    "playing" : self.playing,
                    "checkmate" : False,
                    "current_player" : self.current_player.colour}
    
        # if king piece move is not valid, and is castling, execute castling_condition func 
        elif isinstance(chess_piece, king) and abs(dx) == 2 and dy == 0:
            # TODO #################### - KING CASTLING LOGIC HERE
            castle_condition = self.castling_condition(start, end, board_start, board_end, self.kings_moved, self.rooks_moved, piece_id)

            if not castle_condition:
                return {"valid" : False,
                        "reason" : "Invalid Castling"}
            if castle_condition:
                # - if castle condition is approved, then kings end coordinates is updated 
                #   for king_in_check. ELSE king_position is updated
                team = piece_id // abs(piece_id)
                self.king_position[team] = board_end
                self.switch_player()

                return {"valid" : True,
                    "board" : self.board.board_array.tolist(),
                    "playing" : self.playing,
                    "checkmate" : False,
                    "current_player" : self.current_player.colour}

        # INVALID / WRONG MOVE
        else:
            return {"valid" : False,
                    "reason" : "Invalid Move"}


## TODO
## - ensure that file is rid of all print statements and contains only return statements with json text