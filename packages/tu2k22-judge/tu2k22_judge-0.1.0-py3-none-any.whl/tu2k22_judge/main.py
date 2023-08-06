from typing import List, Dict

import typer

from simulator import Simulator
from custom_exceptions import InvalidMovesException,  TimeoutException, MovesExceededException
from schema import PlayerMove
from tu2k22_judge.tu2k22_judge.log_writer import LogWriter

app = typer.Typer()


@app.command()
def play_game(
    player1_url: str = typer.Argument(...,
                                      help="The url of the bot for player 1"),
    player2_url: str = typer.Argument(...,
                                      help="The url of the bot for player 2"),
    log_file: str = typer.Argument(...,
                                   help="The path to which log file should be written")
):
    """
    Judge for the TU game. Enter the endpoints for bots
    let the judge play out the match
    """
    bot_data = [{}, {}]
    player_moves: List[PlayerMove] = []
    game_simulator = Simulator()
    try:
        winner = game_simulator.run([player1_url, player2_url],
                                    bot_data=bot_data, player_moves=player_moves)
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, winner=winner)
        log_writer.write()
    except (InvalidMovesException, TimeoutException, MovesExceededException) as ex:
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=ex.message)
        log_writer.write()
    except Exception as ex:  # just in case
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=str(ex))
        log_writer.write()


if __name__ == '__main__':
    app()
