from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional
import random
import math

class TourneyType(Enum):
    ROUND_ROBIN = auto()
    SINGLE_ELIMINATION = auto()
    DOUBLE_ELIMINATION = auto()
    SWISS = auto()

@dataclass
class TourneyPlayer:
    id: str
    name: str
    score: int = 0
    matches_played: int = 0
    matches_won: int = 0
    matches_lost: int = 0
    matches_drawn: int = 0

    def win_match(self, points: int = 1):
        self.matches_played += 1
        self.matches_won += 1
        self.score += points

    def lose_match(self, points: int = 0):
        self.matches_played += 1
        self.matches_lost += 1
        self.score += points

    def draw_match(self, points: int = 0):
        self.matches_played += 1
        self.matches_drawn += 1
        self.score += points

@dataclass
class Match:
    id: str
    player1: TourneyPlayer
    player2: TourneyPlayer
    winner: Optional[TourneyPlayer] = None
    loser: Optional[TourneyPlayer] = None
    is_draw: bool = False
    completed: bool = False
    round_number: int = 0

    def set_result(self, winner: Optional[TourneyPlayer] = None, is_draw: bool = False):
        self.completed = True

        if is_draw:
            self.is_draw = True
            self.player1.draw_match()
            self.player2.draw_match()
            return

        if winner is not None:
            self.winner = winner
            self.loser = self.player2 if winner == self.player1 else self.player1
            self.winner.win_match()
            self.loser.lose_match()

@dataclass
class TourneyConfig:
    tournament_type: TourneyType
    name: str
    win_points: int = 3
    draw_points: int = 1
    loss_points: int = 0
    random_seed: Optional[int] = None

@dataclass
class Tourney:
    config: TourneyConfig
    players: List[TourneyPlayer]
    matches: List[Match] = field(default_factory=list)
    current_round: int = 0
    completed: bool = False
    rankings: List[TourneyPlayer] = field(default_factory=list)
    _match_id_counter: int = field(default=0, init=False)

    def __post_init__(self):
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
        self.strategy = self._get_tournament_strategy()
        self.strategy.initialize(self)

    def _get_tournament_strategy(self) -> 'TourneyStrategy':
        if self.config.tournament_type == TourneyType.ROUND_ROBIN:
            return RoundRobinStrategy()
        elif self.config.tournament_type == TourneyType.SINGLE_ELIMINATION:
            return SingleEliminationStrategy()
        elif self.config.tournament_type == TourneyType.DOUBLE_ELIMINATION:
            return DoubleEliminationStrategy()
        elif self.config.tournament_type == TourneyType.SWISS:
            return SwissStrategy()
        else:
            raise ValueError(f"Unsupported tournament type: {self.config.tournament_type}")

    def _generate_match_id(self) -> str:
        self._match_id_counter += 1
        return f"match_{self._match_id_counter}"

    def create_match(self, player1: TourneyPlayer, player2: TourneyPlayer, round_number: int) -> Match:
        match_id = self._generate_match_id()
        match = Match(id=match_id, player1=player1, player2=player2, round_number=round_number)
        self.matches.append(match)
        return match

    def record_match_result(self,
                            match_id: str,
                            winner_id: Optional[str] = None,
                            is_draw: bool = False) -> None:
        match = next((m for m in self.matches if m.id == match_id), None)
        if match is None:
            raise ValueError(f"Match with ID {match_id} not found")

        if match.completed:
            raise ValueError(f"Match {match_id} has already been completed")

        if is_draw:
            match.set_result(is_draw=True)
            match.player1.draw_match(self.config.draw_points)
            match.player2.draw_match(self.config.draw_points)
        else:
            winner = None
            if winner_id == match.player1.id:
                winner = match.player1
                match.player1.win_match(self.config.win_points)
                match.player2.lose_match(self.config.loss_points)
            elif winner_id == match.player2.id:
                winner = match.player2
                match.player2.win_match(self.config.win_points)
                match.player1.lose_match(self.config.loss_points)
            else:
                raise ValueError(f"Winner ID {winner_id} does not match either player in the match")

            match.set_result(winner=winner)

        # Check if current round is complete and generate next round if needed
        self.strategy.process_match_result(self, match)

        # Update rankings
        self.update_rankings()

    def update_rankings(self) -> None:
        """Update player rankings based on their scores."""
        self.rankings = sorted(self.players, key=lambda p: (p.score, p.matches_won), reverse=True)

    def get_upcoming_matches(self) -> List[Match]:
        """Get matches that have not been completed yet."""
        return [m for m in self.matches if not m.completed]

    def get_completed_matches(self) -> List[Match]:
        """Get matches that have been completed."""
        return [m for m in self.matches if m.completed]

    def get_current_round_matches(self) -> List[Match]:
        """Get matches in the current round."""
        return [m for m in self.matches if m.round_number == self.current_round]

    def check_round_complete(self) -> bool:
        """Check if all matches in the current round have been completed."""
        current_round_matches = self.get_current_round_matches()
        return all(match.completed for match in current_round_matches)

    def advance_to_next_round(self) -> None:
        """Advance the tournament to the next round."""
        if self.completed:
            raise ValueError("Tourney is already completed")

        if not self.check_round_complete():
            raise ValueError("Current round is not complete")

        self.current_round += 1
        self.strategy.generate_round(self)

    def get_player_by_id(self, player_id: str) -> Optional[TourneyPlayer]:
        """Get a player by their ID."""
        return next((p for p in self.players if p.id == player_id), None)

class TourneyStrategy:
    """Base class for tournament strategies."""

    def initialize(self, tournament: Tourney) -> None:
        """Initialize the tournament with first round matches."""
        pass

    def generate_round(self, tournament: Tourney) -> None:
        """Generate matches for the next round."""
        pass

    def process_match_result(self, tournament: Tourney, match: Match) -> None:
        """Process a match result and determine if tournament should advance."""
        if tournament.check_round_complete():
            if self.is_tournament_complete(tournament):
                tournament.completed = True
            else:
                # Auto-advance to next round
                tournament.current_round += 1
                self.generate_round(tournament)

    def is_tournament_complete(self, tournament: Tourney) -> bool:
        """Determine if the tournament is complete."""
        return False

class RoundRobinStrategy(TourneyStrategy):
    """Round robin tournament where each player plays against every other player once."""

    def initialize(self, tournament: Tourney) -> None:
        # Generate all matches in advance
        players = tournament.players.copy()
        round_num = 1

        # If odd number of players, each round one player gets a bye
        if len(players) % 2 == 1:
            players.append(None)  # Add a dummy player for pairing

        n = len(players)
        for _ in range(n - 1):
            # Generate matches for this round
            for i in range(n // 2):
                player1 = players[i]
                player2 = players[n - 1 - i]

                # Skip if one player is the dummy player (None)
                if player1 is not None and player2 is not None:
                    tournament.create_match(player1, player2, round_num)

            round_num += 1

            # Rotate players for next round (first player stays fixed)
            players.insert(1, players.pop())

    def is_tournament_complete(self, tournament: Tourney) -> bool:
        # Tourney is complete when all matches are completed
        return all(match.completed for match in tournament.matches)

    def generate_round(self, tournament: Tourney) -> None:
        # All matches are generated during initialization
        pass

class SingleEliminationStrategy(TourneyStrategy):
    """Single elimination tournament where losers are eliminated."""

    def initialize(self, tournament: Tourney) -> None:
        players = tournament.players.copy()
        random.shuffle(players)

        # Calculate number of byes needed to make total participants a power of 2
        total_slots = 2**math.ceil(math.log2(len(players)))
        byes = total_slots - len(players)

        # First round matches
        round_players = []

        # Assign byes to random players
        bye_indices = random.sample(range(len(players)), min(byes, len(players)))

        for i, player in enumerate(players):
            if i in bye_indices:
                # This player gets a bye to the next round
                round_players.append(player)
            else:
                # This player plays in the first round
                if players:
                    opponent = players.pop()
                    match = tournament.create_match(player, opponent, tournament.current_round)
                    # Winner will advance to next round

    def generate_round(self, tournament: Tourney) -> None:
        # Get winners from previous round
        previous_round = tournament.current_round - 1
        winners = [
            match.winner for match in tournament.matches
            if match.round_number == previous_round and match.completed
        ]

        # Pair winners for next round
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                tournament.create_match(winners[i], winners[i + 1], tournament.current_round)

    def is_tournament_complete(self, tournament: Tourney) -> bool:
        # Count remaining players (not eliminated)
        remaining = sum(1 for match in tournament.matches if match.round_number == tournament.current_round)
        return remaining <= 1

class DoubleEliminationStrategy(TourneyStrategy):
    """Double elimination tournament where players are eliminated after two losses."""

    def initialize(self, tournament: Tourney) -> None:
        # Similar to single elimination but with winners and losers brackets
        players = tournament.players.copy()
        random.shuffle(players)

        # For simplicity, we'll require power of 2 number of players
        while not self._is_power_of_two(len(players)):
            # Add byes as needed
            players.append(None)

        # Create first round matches in winners bracket
        for i in range(0, len(players), 2):
            if players[i] is not None and players[i + 1] is not None:
                tournament.create_match(players[i], players[i + 1], tournament.current_round)

        # Tourney data will track winners bracket and losers bracket
        tournament.winners_bracket = []  # Players still in winners bracket
        tournament.losers_bracket = []  # Players in losers bracket
        tournament.eliminated = []  # Players eliminated (lost twice)

    def _is_power_of_two(self, n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    def process_match_result(self, tournament: Tourney, match: Match) -> None:
        # Update brackets based on match result
        if match.winner is not None and match.loser is not None:
            # Add winner to winners bracket if not already there
            if match.winner not in tournament.winners_bracket:
                tournament.winners_bracket.append(match.winner)

            # Move loser to losers bracket if from winners bracket
            if match.loser in tournament.winners_bracket:
                tournament.winners_bracket.remove(match.loser)
                tournament.losers_bracket.append(match.loser)
            # Eliminate player if already in losers bracket
            elif match.loser in tournament.losers_bracket:
                tournament.losers_bracket.remove(match.loser)
                tournament.eliminated.append(match.loser)

        super().process_match_result(tournament, match)

    def generate_round(self, tournament: Tourney) -> None:
        # Logic for generating matches in both winners and losers brackets
        # This is simplified - real implementation would be more complex
        # to properly handle double elimination bracket structure

        # Generate winners bracket matches
        winners = tournament.winners_bracket.copy()
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                tournament.create_match(winners[i], winners[i + 1], tournament.current_round)

        # Generate losers bracket matches
        losers = tournament.losers_bracket.copy()
        for i in range(0, len(losers), 2):
            if i + 1 < len(losers):
                tournament.create_match(losers[i], losers[i + 1], tournament.current_round)

    def is_tournament_complete(self, tournament: Tourney) -> bool:
        # Tourney is complete when only one player remains
        return len(tournament.winners_bracket) + len(tournament.losers_bracket) <= 1

class SwissStrategy(TourneyStrategy):
    """Swiss tournament where players are paired against others with similar records."""

    def initialize(self, tournament: Tourney) -> None:
        players = tournament.players.copy()
        random.shuffle(players)

        # First round: random pairings
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                tournament.create_match(players[i], players[i + 1], tournament.current_round)

    def generate_round(self, tournament: Tourney) -> None:
        # Swiss pairing: group players by score and pair within groups
        players_by_score = {}
        for player in tournament.players:
            score = player.score
            if score not in players_by_score:
                players_by_score[score] = []
            players_by_score[score].append(player)

        # Get unique scores and sort them descending
        scores = sorted(players_by_score.keys(), reverse=True)

        # Track players who have been paired
        paired_players = set()

        # Pair players within same score group first
        for score in scores:
            players = players_by_score[score].copy()
            random.shuffle(players)  # Randomize order within same score group

            while len(players) >= 2:
                player1 = players.pop(0)

                # Find opponent who hasn't played against player1 yet
                opponent_idx = -1
                for i, player2 in enumerate(players):
                    if not self._have_played(tournament, player1, player2):
                        opponent_idx = i
                        break

                if opponent_idx >= 0:
                    player2 = players.pop(opponent_idx)
                    tournament.create_match(player1, player2, tournament.current_round)
                    paired_players.add(player1)
                    paired_players.add(player2)
                else:
                    # Couldn't find an opponent in same score group, will try later
                    break

        # Pair remaining players across score groups
        remaining_players = [p for p in tournament.players if p not in paired_players]
        remaining_players.sort(key=lambda p: p.score, reverse=True)

        while len(remaining_players) >= 2:
            player1 = remaining_players.pop(0)

            # Find first player who hasn't played against player1
            opponent_idx = -1
            for i, player2 in enumerate(remaining_players):
                if not self._have_played(tournament, player1, player2):
                    opponent_idx = i
                    break

            if opponent_idx >= 0:
                player2 = remaining_players.pop(opponent_idx)
                tournament.create_match(player1, player2, tournament.current_round)
            else:
                # Everyone has played everyone - rematch with closest score
                player2 = remaining_players.pop(0)
                tournament.create_match(player1, player2, tournament.current_round)

    def _have_played(self, tournament: Tourney, player1: TourneyPlayer, player2: TourneyPlayer) -> bool:
        """Check if two players have already played against each other."""
        for match in tournament.matches:
            if ((match.player1 == player1 and match.player2 == player2)
                    or (match.player1 == player2 and match.player2 == player1)):
                return True
        return False

    def is_tournament_complete(self, tournament: Tourney) -> bool:
        # Swiss typically runs for a predetermined number of rounds
        # For this example, we'll say 5 rounds or when all possible matches have been played
        max_rounds = 5
        all_played = True

        # Check if all possible player combinations have had a match
        for i, player1 in enumerate(tournament.players):
            for player2 in tournament.players[i + 1:]:
                if not self._have_played(tournament, player1, player2):
                    all_played = False
                    break

        return tournament.current_round >= max_rounds or all_played

