from typing import Optional


class InvalidMovesException(Exception):
    def __init__(self, reason: str, player: Optional[int] = None) -> None:
        self.message = f"Invalid Move by Player {player}: {reason}"
        self.player = player
        self.reason = reason
        super().__init__(self.message)


class TimeoutException(Exception):
    def __init__(self, player: int) -> None:
        self.message = f"Timeout: Player {player} Bot took too long to respond"
        self.player = player
        super().__init__(self.message)


class MovesExceededException(Exception):
    def __init__(self) -> None:
        self.message = "Game exceeeded limit for moves without any player winning. Declared as a draw"
        super().__init__(self.message)
