from email import message
from typing import Any, List, Tuple
import json
import logging

import requests
from requests import Timeout
from colorama import Fore, Back, Style

from schema import Piece, Move, Player, InvalidMovesMessage, BotResponse, PlayerMove
from custom_exceptions import InvalidMovesException, TimeoutException, MovesExceededException
from constants import MAX_MOVES_ALLOWED

logging.basicConfig()


class Simulator:
    def __init__(self, move_timeout: int = 4, verbose: bool = True) -> None:
        pieces = ['B', 'b', '_', 'r', 'R']
        self.board = [[pieces[i] for _ in range(5)] for i in range(5)]
        self.RED_PIECES = [Piece.RED_BOMBER, Piece.RED_STINGER]
        self.BLUE_PIECES = [Piece.BLUE_BOMBER, Piece.BLUE_STINGER]
        self.move_timeout = move_timeout
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        if not verbose:
            self.logger.setLevel(level=logging.WARNING)
        self.verbose = verbose

    def print_board(self):
        if self.verbose:
            print(Fore.BLACK + Style.BRIGHT + "  0 1 2 3 4")
            for index, row in enumerate(self.board):
                print(Fore.BLACK + Style.BRIGHT + str(index) + " ")
                for cell in row:
                    if cell in self.RED_PIECES:
                        print(Fore.RED + cell + " ")
                    elif cell in self.BLUE_PIECES:
                        print(Fore.BLUE + cell + " ")
                    else:
                        print(Fore.WHITE + cell + " ")
                print()

    @staticmethod
    def validate_direction(move: Move, player: Player):
        """
        Check if player is moving in correct vertical direction, blue should move down the board, red should move up
        """
        sign = 2*player - 1
        absolute_direction = move.dst.y - move.src.y
        if absolute_direction*sign < 0:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_DIRECTION, player=player)

    def validate_endpoints(self, move: Move, player: Player):
        if self.board[move.dst.x][move.dst.y] != Piece.EMPTY_SPACE:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_DESTINATION, player=player)
        if (
            player == player.BLUE and self.board[move.src.x][move.src.y] not in self.BLUE_PIECES
        ) or (
            player == player.RED and self.board[move.src.x][move.src.y] not in self.RED_PIECES
        ):
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_SOURCE, player=player)

    def validate_elimination_move(self, move: Move, player: Player):
        if move.src.x == move.dst.y == 0 or move.src.x == move.src.y == 4:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.HOME_ROW_ELIMINATION_FORBIDDEN, player=player)
        eliminated_x_coord = int((move.src.x + move.dst.x) / 2)
        eliminated_y_coord = int((move.src.y + move.dst.y) / 2)
        eliminated_piece = self.board[eliminated_x_coord][eliminated_y_coord]

        if (
            player.RED and eliminated_piece in self.BLUE_PIECES
        ) or (
            player.BLUE and eliminated_piece in self.RED_PIECES
        ):
            return
        else:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_ELIMINATION_TARGET, player=player)

    def validate_stinger_move(self, move: Move, player: Player):
        if abs(move.src.x - move.dst.x) == abs(move.src.y - move.dst.y) == 1:
            # simply diagonal move (direction in y axis has already been validated)
            return
        elif (
            # horizontal elimination
            abs(move.src.x - move.dst.x) == 2 and move.src.y == move.dst.y
        ) or (
            # vertical elimination
            abs(move.src.y - move.dst.y) == 2 and move.src.x == move.dst.y
        ):
            self.validate_elimination_move(move, player)
        else:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_STINGER_MOVE, player=player)

    def validate_bomber_move(self, move: Move, player: Player):
        if abs(move.src.y - move.dst.y) <= 1 and abs(move.src.x - move.dst.x) <= 1 and move.src != move.dst:
            return  # single move in any direction
        elif (
            # horizontal elimination
            abs(move.src.x - move.dst.x) == 2 and move.src.y == move.dst.y
        ) or (
            # vertical elimination
            abs(move.src.y - move.dst.y) == 2 and move.src.x == move.dst.y
        ):
            self.validate_elimination_move(move, player)
        else:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_BOMBER_MOVE, player=player)

    def validate_move(self, move: Move, player: Player):
        self.validate_direction(move, player)
        self.validate_endpoints(move, player)
        piece = self.board[move.src.x][move.src.y]
        if piece in [Piece.BLUE_STINGER, Piece.RED_STINGER]:
            self.validate_stinger_move(move, player)
        else:
            self.validate_bomber_move(move, player)

    def make_move(self, move: Move, player: Player):
        self.board[move.dst.x][move.dst.y] = self.board[move.src.x][move.src.y]
        self.board[move.src.x][move.src.y] = Piece.EMPTY_SPACE
        if abs(move.src.x - move.dst.x) == 2 or abs(move.src.y - move.dst.y) == 2:
            eliminated_x_coord = int((move.src.x + move.dst.x) / 2)
            eliminated_y_coord = int((move.src.y + move.dst.y) / 2)
            self.board[eliminated_x_coord][eliminated_y_coord] = Piece.EMPTY_SPACE

    def check_if_game_over(self) -> Tuple[bool, Player | None]:
        if Piece.RED_BOMBER in self.board[0]:
            return True, Player.RED
        elif Piece.BLUE_BOMBER in self.board[0]:
            return True, Player.BLUE
        return False, None

    def run(self, bot_urls: List[str], bot_data: List[Any], player_moves: List[PlayerMove]):
        player = Player.BLUE
        print("STARTING GAME")
        self.print_board()
        while len(player_moves) < MAX_MOVES_ALLOWED:
            bot_input = {
                "board": self.board,
                "data": bot_data[player],
                "player": player
            }
            response = requests.post(
                bot_urls[player], json=bot_input, timeout=self.move_timeout)
            try:
                bot_response = BotResponse.validate(
                    json.loads(response.content))
                bot_data[player] = bot_response.data
                self.validate_move(bot_response.move, player=player)
                self.logger.info(f"Move by Player: {player}")
                self.logger.info(bot_response.move)
                self.make_move(bot_response.move, player=player)
                self.print_board()
                game_over, winner = self.check_if_game_over()
                if game_over:
                    self.logger.info(f"Player {player} wins")
                    return winner
                player_moves.append(PlayerMove(
                    move=bot_response.move, player=player))
                player ^= player  # infers type of player as int
                # functions expect call of type Player Enum
                player = Player(player)
            except InvalidMovesException as imex:
                self.logger.error(
                    f"Invalid response received from player: {player}. Message: ", imex.message)
                raise InvalidMovesException(
                    reason=imex.reason, player=player)  # append player info
            except Timeout as t:
                self.logger.error(
                    f"Request to player: {player} times out")
                raise TimeoutException(player=player)
        raise MovesExceededException()
