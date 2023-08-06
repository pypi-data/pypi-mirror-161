from typing import List, Dict

import typer

from .simulator import Simulator
from .custom_exceptions import InvalidMovesException,  TimeoutException, MovesExceededException
from .schema import PlayerMove, Player, GameResult
from .log_writer import LogWriter

app = typer.Typer()


@app.command()
def play_game(
    player1_url: str = typer.Argument(...,
                                      help="The url of the bot for player 1"),
    player2_url: str = typer.Argument(...,
                                      help="The url of the bot for player 2"),
    log_file: str = typer.Argument(default="./logs/local",
                                   help="The path to which log file should be written"),
    verbose: bool = typer.Argument(
        default=False, help="Whether to print out board states and moves when running simulator")
) -> GameResult:
    """
    Judge for the TU game. Enter the endpoints for bots
    let the judge play out the match
    """
    bot_data = [{}, {}]
    player_moves: List[PlayerMove] = []
    game_simulator = Simulator(verbose=verbose)
    try:
        winner = game_simulator.run([player1_url, player2_url],
                                    bot_data=bot_data, player_moves=player_moves)
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, winner=winner)
        log_writer.write()
        result = GameResult.PLAYER1_WINS if winner == Player.BLUE else GameResult.PLAYER2_WINS
        return result
    except (InvalidMovesException, TimeoutException) as ex:
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=ex.message)
        log_writer.write()
        result = GameResult.PLAYER1_WINS if ex.player == Player.RED else GameResult.PLAYER2_WINS
        return result
    except MovesExceededException as ex:
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=ex.message)
        log_writer.write()
        return GameResult.DRAW
    except Exception as ex:  # just in case
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=str(ex))
        log_writer.write()
        return GameResult.DRAW


if __name__ == '__main__':
    app()
