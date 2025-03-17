import names
import random
import abc
from dataclasses import dataclass, field

import gt

@dataclass(frozen=True)
class Tourney:
    players: list
    matchmaker: 'i'

    def __post_init__(self):
        self.matchmaker.set_tourney(self)

    def run(self):
        while match := self.matchmaker.next_match():
            match.play()

@dataclass
class MatchMaker:
    tourney: Tourney = None
    gamelen: int | tuple[int, int] = 100

    def get_gamelen(self):
        if isinstance(self.gamelen, int): return self.gamelen
        return random.randint(*self.gamelen)

    @abc.abstractmethod
    def next_match(self) -> gt.MatchRunner:
        pass

@dataclass
class Player:
    strategy: gt.Strategy
    name: str = field(default_factory=names.get_first_name)

    def __post_init__(self):
        if self.name is None:
            self.name = self.strategy.__class__.__name__

    def move(self):
        return self.strategy.move()

    def record_other_player_move(self, move):
        self.strategy.record_other_player_move(move)

    def __hash__(self):
        return hash(self.name)

@dataclass
class AllPairs(MatchMaker):
    playself: bool = True
    num_matches: int = 1
    playcount: dict[(Player, Player), int] = field(default_factory=dict)

    def set_tourney(self, tourney):
        self.tourney = tourney
        for i, p in enumerate(self.tourney.players):
            for q in self.tourney.players[:i + self.playself]:
                self. playcount[(p, q)] = 0

    def next_match(self) -> gt.MatchRunner:
        for players, nmatches in self.playcount.items():
            if nmatches < self.num_matches:
                self.playcount[players] += 1
                return gt.MatchRunner(*players, gamelen=self.get_gamelen())
        return None
