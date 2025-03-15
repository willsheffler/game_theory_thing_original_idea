import abc
import random
from dataclasses import dataclass, field

import gt


@dataclass
class Strategy:
    """general stuff for iterated prisoners dilima games"""
    history: gt.GameHistory = field(default_factory=gt.GameHistory)

    def move(self, *a, **kw):
        """returns a move"""
        self._last_move = self.compute_move(*a, **kw)
        return self._last_move

    @abc.abstractmethod
    def compute_move(self):
        raise NotImplementedError

    def record_other_player_move(self, moveid):
        """record the other players move"""
        self.history.add_moves(self._last_move, moveid)

    def last_oppenent_moves(self, n=1):
        """returns the last n moves of the opponent"""
        return ''.join([x.move2 for x in self.history[-n:]])

class TitForTat(Strategy):
    """starts with cooperate and then copies the opponents last move"""
    def compute_move(self):
        if not self.history:
            return 'C'
        if self.history[-1].move2 == 'C':
            return 'C'
        return 'D'

class AlwaysDefect(Strategy):

    def compute_move(self):
        return 'D'

class AlwaysCooperate(Strategy):

    def compute_move(self):
        return 'C'

class Random(Strategy):

    def compute_move(self):
        return random.choice(['C', 'D'])

class TitForTwoTats(Strategy):

    def compute_move(self):
        if not self.history:
            return 'C'
        if len(self.history) < 3:
            return 'C'
        if self.history[-1].move2 == 'D' and self.history[-2].move2 == 'D':
            return 'D'
        return 'C'

class SometimesDefect(Strategy):

    def __init__(self, defect_prob=0.3):
        super().__init__()
        self.defect_prob = defect_prob

    def compute_move(self):
        if not self.history:
            return 'C'
        if random.random() < self.defect_prob:
            return 'D'
        return 'C'

class Grudger(Strategy):

    def compute_move(self):
        if not self.history:
            return 'C'
        if any(x.move2 == 'D' for x in self.history):
            return 'D'
        return 'C'

class Prober(Strategy):

    def compute_move(self):
        if len(self.history) < 5: return 'C'
        if self.last_oppenent_moves(2) == 'DD': return 'D'
        if self.last_oppenent_moves(2) == 'CC': return 'C'
        return random.choice(['C', 'D'])
