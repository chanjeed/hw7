#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import logging
import random
import webapp2
w=[1,0.75,2,6,-3,20]
score_board=[[w[5],w[4],w[3],w[3],w[3],w[3],w[4],w[5]],
			[w[4],w[4],w[2],w[2],w[2],w[2],w[4],w[4]],
			[w[3],w[2],w[3],w[1],w[1],w[3],w[2],w[3]],
			[w[3],w[2],w[1],w[1],w[1],w[1],w[2],w[3]],
			[w[3],w[2],w[1],w[1],w[1],w[1],w[2],w[3]],
			[w[3],w[2],w[3],w[1],w[1],w[3],w[2],w[3]],
			[w[4],w[4],w[2],w[2],w[2],w[2],w[4],w[4]],
			[w[5],w[4],w[3],w[3],w[3],w[3],w[4],w[5]]]

# Reads json description of the board and provides simple interface.
class Game:
	# Takes json or a board directly.
	def __init__(self, body=None, board=None):
		score=0
		if body:
         		game = json.loads(body)
         		self._board = game["board"]
         	else:
         		self._board = board

	#Evaluate score for Player1 to win the game
	def Find_score(self):
		
		score=0
		for i in range(8):
			for j in range(8):
				if self._board['Pieces'][i][j]==1:
					score+=score_board[i][j];
				if self._board['Pieces'][i][j]==2:
					score-=score_board[i][j];
		# Extra score for adjacent corner
		if self._board['Pieces'][0][0]==1 and (self._board['Pieces'][0][7]==1 or self._board['Pieces'][7][0]==1):
			score+=2
		if self._board['Pieces'][0][7]==1 and (self._board['Pieces'][0][0]==1 or self._board['Pieces'][7][0]==1):
			score+=2
		if self._board['Pieces'][7][0]==1 and (self._board['Pieces'][0][0]==1 or self._board['Pieces'][7][7]==1):
			score+=2
		if self._board['Pieces'][7][7]==1 and (self._board['Pieces'][0][7]==1 or self._board['Pieces'][7][0]==1):
			score+=2
		if self._board['Pieces'][0][0]==1 and (self._board['Pieces'][0][7]==1 or self._board['Pieces'][7][0]==2):
			score-=2
		if self._board['Pieces'][0][7]==1 and (self._board['Pieces'][0][0]==1 or self._board['Pieces'][7][0]==2):
			score-=2
		if self._board['Pieces'][7][0]==1 and (self._board['Pieces'][0][0]==1 or self._board['Pieces'][7][7]==2):
			score-=2
		if self._board['Pieces'][7][7]==1 and (self._board['Pieces'][0][7]==1 or self._board['Pieces'][7][0]==2):
			score-=2
		#Extra score for next valid moves
		valid_moves=self.ValidMoves()
		if self.Next()==1:
			score+=w[0]*len(valid_moves)
		else:
			score-=w[0]*len(valid_moves)
		return score
	# Returns piece on the board.
	# 0 for no pieces, 1 for player 1, 2 for player 2.
	# None for coordinate out of scope.
	def Pos(self, x, y):
		return Pos(self._board["Pieces"], x, y)

	# Returns who plays next.
	def Next(self):
		return self._board["Next"]

	# Returns the array of valid moves for next player.
	# Each move is a dict
	#   "Where": [x,y]
	#   "As": player number
	def ValidMoves(self):
                moves = []
                for y in xrange(1,9):
                        for x in xrange(1,9):
                                move = {"Where": [x,y],
                                        "As": self.Next()}
                                if self.NextBoardPosition(move):
                                        moves.append(move)
                return moves

	# Helper function of NextBoardPosition.  It looks towards
	# (delta_x, delta_y) direction for one of our own pieces and
	# flips pieces in between if the move is valid. Returns True
	# if pieces are captured in this direction, False otherwise.
	def __UpdateBoardDirection(self, new_board, x, y, delta_x, delta_y):
		player = self.Next()
		opponent = 3 - player
		look_x = x + delta_x
		look_y = y + delta_y
		flip_list = []
		while Pos(new_board, look_x, look_y) == opponent:
			flip_list.append([look_x, look_y])
			look_x += delta_x
			look_y += delta_y
		if Pos(new_board, look_x, look_y) == player and len(flip_list) > 0:
                        # there's a continuous line of our opponents
                        # pieces between our own pieces at
                        # [look_x,look_y] and the newly placed one at
                        # [x,y], making it a legal move.
			SetPos(new_board, x, y, player)
			for flip_move in flip_list:
				flip_x = flip_move[0]
				flip_y = flip_move[1]
				SetPos(new_board, flip_x, flip_y, player)
                        return True
                return False

	# Takes a move dict and return the new Game state after that move.
	# Returns None if the move itself is invalid.
	def NextBoardPosition(self, move):
		x = move["Where"][0]
		y = move["Where"][1]
                if self.Pos(x, y) != 0:
                        # x,y is already occupied.
                        return None
		new_board = copy.deepcopy(self._board)
                pieces = new_board["Pieces"]

		if not (self.__UpdateBoardDirection(pieces, x, y, 1, 0)
                        | self.__UpdateBoardDirection(pieces, x, y, 0, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, 0)
		        | self.__UpdateBoardDirection(pieces, x, y, 0, -1)
		        | self.__UpdateBoardDirection(pieces, x, y, 1, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, 1, -1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, -1)):
                        # Nothing was captured. Move is invalid.
                        return None
                
                # Something was captured. Move is valid.
                new_board["Next"] = 3 - self.Next()
		return Game(board=new_board)

	def choose_bestmove_recursive(self,valid_moves,depth):
		

		if depth==1:
    			score=self.Find_score()
			return score

		
		next_player=self.Next()
		if next_player==1:
			best_score=-9999
		elif next_player==2:
			best_score=9999
		
		if len(valid_moves)!=0:
    			for current_move in valid_moves:
    				new_board=self.NextBoardPosition(current_move)
    				new_valid_moves=new_board.ValidMoves()
    				score=new_board.choose_bestmove_recursive(new_valid_moves,depth-1)
    				if next_player==1:
    					if score>best_score:
    						best_score=score
    					
    				else:
    					if score<best_score:
    						best_score=score
    		else:
    			new_board=self
    			new_board._board['Next']=3-new_board._board['Next']
    			new_valid_moves=new_board.ValidMoves()
    			return new_board.choose_bestmove_recursive(new_valid_moves,depth-1)


    		return best_score

    	def choose_bestmove(self,valid_moves,depth):
    		next_player=self.Next()
 		if next_player==1:
			best_score=-9999
		elif next_player==2:
			best_score=9999
		best_move=None   		
    		for move in valid_moves:
    			new_board=self.NextBoardPosition(move)
    			new_valid_moves=new_board.ValidMoves()
    			score=new_board.choose_bestmove_recursive(new_valid_moves,depth-1)
    			if next_player==1:
    				if score>best_score:
    					best_score=score
    					best_move=move
    			else:
    				if score<best_score:
    					best_score=score
    					best_move=move
    		return best_move

	def alphabeta_recursive(self,valid_moves,depth,alpha,beta):
		

		if depth==1:
    			score=self.Find_score()
			return score

		
		next_player=self.Next()
	
		if len(valid_moves)!=0:
			if next_player==1:
    				for current_move in valid_moves:
    					new_board=self.NextBoardPosition(current_move)
    					new_valid_moves=new_board.ValidMoves()
    				
    					alpha=max(alpha,new_board.alphabeta_recursive(new_valid_moves,depth-1,alpha,beta))
    			
    					if alpha>=beta:
    						break #prune
   				return alpha
    					
    			elif next_player==2:
    				for current_move in valid_moves:
    					new_board=self.NextBoardPosition(current_move)
    					new_valid_moves=new_board.ValidMoves()
    					
    					beta=min(beta,new_board.alphabeta_recursive(new_valid_moves,depth-1,alpha,beta))
    					
    					if alpha>=beta:
    						break #prune
    				return beta
    		else:
    			new_board=self
    			new_board._board['Next']=3-new_board._board['Next']
    			new_valid_moves=new_board.ValidMoves()
    			if next_player==1:
    				return max(alpha,new_board.alphabeta_recursive(new_valid_moves,depth-1,alpha,beta))
    			elif next_player==2:
    				return min(beta,new_board.alphabeta_recursive(new_valid_moves,depth-1,alpha,beta))


    	def alphabeta(self,valid_moves,depth,alpha,beta):
    		next_player=self.Next()
 		if next_player==1:
			best_score=-99999
		elif next_player==2:
			best_score=99999
		best_move=None   		
    		for move in valid_moves:
    			new_board=self.NextBoardPosition(move)
    			new_valid_moves=new_board.ValidMoves()
    			score=new_board.alphabeta_recursive(new_valid_moves,depth-1,alpha,beta)
    			if next_player==1:
    				if score>best_score:
    					best_score=score
    					best_move=move
    			else:
    				if score<best_score:
    					best_score=score
    					best_move=move
    		return best_move

# Returns piece on the board.
# 0 for no pieces, 1 for player 1, 2 for player 2.
# None for coordinate out of scope.
#
# Pos and SetPos takes care of converting coordinate from 1-indexed to
# 0-indexed that is actually used in the underlying arrays.
def Pos(board, x, y):
	if 1 <= x and x <= 8 and 1 <= y and y <= 8:
		return board[y-1][x-1]
	return None

# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):
	if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0,1,2]:
		return False
	board[y-1][x-1] = piece

# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):
	s = ""
	for row in board:
		for piece in row:
			s += str(piece)
		s += nl
	return s

def PrettyMove(move):
	m = move["Where"]
	return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])

class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.
    def get(self):
        if not self.request.get('json'):
          self.response.write("""
<body><form method=get>
Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
<p/><input type=submit>
</form>
</body>
""")
          return
        else:
          g = Game(self.request.get('json'))
          self.pickMove(g)

    def post(self):
    	# Reads JSON representation of the board and store as the object.
    	g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)



    def pickMove(self, g):
    	# Gets all valid moves.
    	valid_moves = g.ValidMoves()
    	if len(valid_moves) == 0:
    		# Passes if no valid moves.
    		self.response.write("PASS")
    	else:
    		# Chooses a valid move randomly if available.
         # TO STEP STUDENTS:
         # You'll probably want to change how this works, to do something
         # more clever than just picking a random move.
         best_move = g.alphabeta(valid_moves,3,-99999,99999)
         self.response.write(PrettyMove(best_move))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
