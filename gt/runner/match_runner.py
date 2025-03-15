import dataclasses

import gt


@dataclasses.dataclass
class MatchRunner:
    player1: gt.Strategy
    player2: gt.Strategy
    history: gt.GameHistory = dataclasses.field(default_factory=gt.GameHistory)
    gamelen: int|str = 100

    def get_game_girth(self) -> int:
        return int(self.gamelen)

    def play(self):
        for _ in range(self.get_game_girth()):
            move1 = self.player1.move()
            move2 = self.player2.move()
            self.player1.record_other_player_move(move2)
            self.player2.record_other_player_move(move1)
            self.history.add_moves(move1, move2)
        return self.history
