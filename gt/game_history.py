from dataclasses import dataclass, field


@dataclass
class HistoryEntry:
    move1: str
    move2: str

    def __iter__(self):
        yield self.move1
        yield self.move2

@dataclass
class GameHistory:
    history: list[HistoryEntry] = field(default_factory=list)

    def add_moves(self, move1: str, move2: str):
        self.history.append(HistoryEntry(move1, move2))

    def __getitem__(self, i):
        return self.history[i]

    def __bool__(self):
        return bool(self.history)

    def __str__(self):
        return 'P1: ' + ''.join([f'{x.move1}' for x in self.history]) + '\nP2: ' + ''.join([f'{x.move2}' for x in self.history])

    def __len__(self):
        return len(self.history)
