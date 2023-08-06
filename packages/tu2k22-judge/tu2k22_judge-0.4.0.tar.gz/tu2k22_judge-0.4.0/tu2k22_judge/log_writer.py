from typing import List, Optional
from .schema import PlayerMove, Player


class LogWriter:
    def __init__(self, path: str, player_moves: List[PlayerMove], winner: Optional[Player] = None, error_message: Optional[str] = None) -> None:
        self.path = path
        self.player_moves = player_moves
        self.winner = winner
        self.error_message = error_message

    def format_moves(self) -> List[str]:
        formatted_moves: List[str] = []
        for player_move in self.player_moves:
            move = player_move.move
            formatted_move = f'M, {player_move.player}, {move.src.x} {move.src.y} {move.dst.x} {move.dst.y}'
            formatted_moves.append(formatted_move)
        return formatted_moves

    def write(self):
        formatted_moves = self.format_moves()
        with open(self.path, "w+") as log_file:
            log_file.writelines(formatted_moves)
            if self.winner is not None:
                log_file.write(f"W, Player {self.winner} wins")
            elif self.error_message is not None:
                log_file.write(f"E, {self.error_message}")
