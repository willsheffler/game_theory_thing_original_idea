from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Set, Callable, Optional, Tuple, Any
import random
import math

from gt.tourney import *

def main():
    random.seed(42)  # For reproducible results
    # Run single elimination tournament
    tournament1 = run_tournament_simulation()

    # Run round robin tournament
    # tournament2 = run_round_robin_simulation()

# Tourney system code from previous artifact...
# (Imagine the full code from the previous artifact is here)

# For brevity, I'm continuing with the simulation example

def run_tournament_simulation():
    """Simulate a complete tournament with random results."""
    # Create players
    players = [
        TourneyPlayer(id=f"p{i}", name=f"TourneyPlayer {i}")
        for i in range(1, 9)
    ]

    # Create tournament config for single elimination
    config = TourneyConfig(
        tournament_type=TourneyType.SINGLE_ELIMINATION,
        name="March Madness 2025",
        win_points=3,
        draw_points=1,
        loss_points=0,
        random_seed=42
    )

    # Create tournament
    tournament = Tourney(config=config, players=players)

    print(f"Starting tournament: {config.name}")
    print(f"Tourney type: {config.tournament_type.name}")
    print(f"Number of players: {len(players)}")
    print("-" * 50)

    # Main tournament loop - continue until tournament is completed
    while not tournament.completed:
        print(f"\nRound {tournament.current_round + 1}:")
        print("-" * 30)

        # Get upcoming matches for current round
        current_matches = tournament.get_current_round_matches()

        for match in current_matches:
            # Simulate match result (randomly)
            print(f"Match {match.id}: {match.player1.name} vs {match.player2.name}")

            # Randomly determine winner (80% chance player wins, 20% chance of draw)
            random_val = random.random()
            if random_val < 0.4:  # TourneyPlayer 1 wins
                winner_id = match.player1.id
                is_draw = False
                result_str = f"{match.player1.name} wins!"
            elif random_val < 0.8:  # TourneyPlayer 2 wins
                winner_id = match.player2.id
                is_draw = False
                result_str = f"{match.player2.name} wins!"
            else:  # Draw (if tournament type allows)
                winner_id = None
                is_draw = True
                result_str = "It's a draw!"

                # Single elimination doesn't allow draws, so handle it
                if config.tournament_type in [TourneyType.SINGLE_ELIMINATION,
                                             TourneyType.DOUBLE_ELIMINATION]:
                    # Force a winner
                    winner_id = match.player1.id if random.random() < 0.5 else match.player2.id
                    is_draw = False
                    result_str = f"After overtime, {match.player1.name if winner_id == match.player1.id else match.player2.name} wins!"

            # Record the match result
            tournament.record_match_result(match.id, winner_id, is_draw)
            print(f"Result: {result_str}")

        # Show current standings
        print("\nCurrent Standings:")
        for i, player in enumerate(tournament.rankings):
            print(f"{i+1}. {player.name}: {player.score} points ({player.matches_won}W-{player.matches_lost}L-{player.matches_drawn}D)")

    # Tourney completed
    print("\n" + "=" * 50)
    print(f"Tourney {config.name} completed!")
    print("Final Rankings:")
    for i, player in enumerate(tournament.rankings):
        print(f"{i+1}. {player.name}: {player.score} points ({player.matches_won}W-{player.matches_lost}L-{player.matches_drawn}D)")

    # Announce winner
    if tournament.rankings:
        print(f"\nThe winner is: {tournament.rankings[0].name}!")

    return tournament

# Run the simulation
if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    tournament = run_tournament_simulation()

# Now let's also show a round-robin tournament example
def run_round_robin_simulation():
    """Simulate a round-robin tournament."""
    # Create players
    players = [
        TourneyPlayer(id=f"p{i}", name=f"Team {chr(65+i-1)}")
        for i in range(1, 5)
    ]

    # Create tournament config for round robin
    config = TourneyConfig(
        tournament_type=TourneyType.ROUND_ROBIN,
        name="League Championship 2025",
        win_points=3,  # Standard soccer/football scoring
        draw_points=1,
        loss_points=0,
        random_seed=42
    )

    # Create tournament
    tournament = Tourney(config=config, players=players)

    print(f"\nStarting tournament: {config.name}")
    print(f"Tourney type: {config.tournament_type.name}")
    print(f"Number of teams: {len(players)}")
    print("-" * 50)

    # Print schedule
    print("\nFull Tourney Schedule:")
    for match in tournament.matches:
        print(f"Round {match.round_number + 1}: {match.player1.name} vs {match.player2.name}")

    # Main tournament loop - continue until tournament is completed
    for _ in range(100):
    # while not tournament.completed:
        print(f"\nRound {tournament.current_round + 1}:")
        print("-" * 30)

        # Get upcoming matches for current round
        current_matches = [m for m in tournament.matches if m.round_number == tournament.current_round and not m.completed]

        for match in current_matches:
            # Simulate match result
            print(f"Match: {match.player1.name} vs {match.player2.name}")

            # Simulate scores for a more realistic output
            team1_score = random.randint(0, 3)
            team2_score = random.randint(0, 3)

            if team1_score > team2_score:  # Team 1 wins
                winner_id = match.player1.id
                is_draw = False
                result_str = f"{match.player1.name} {team1_score}-{team2_score} {match.player2.name}"
            elif team2_score > team1_score:  # Team 2 wins
                winner_id = match.player2.id
                is_draw = False
                result_str = f"{match.player1.name} {team1_score}-{team2_score} {match.player2.name}"
            else:  # Draw
                winner_id = None
                is_draw = True
                result_str = f"{match.player1.name} {team1_score}-{team2_score} {match.player2.name} (Draw)"

            # Record the match result
            tournament.record_match_result(match.id, winner_id, is_draw)
            print(f"Result: {result_str}")

        # Show league table after each round
        print("\nLeague Table:")
        print(f"{'Rank':<5}{'Team':<10}{'Pts':<5}{'P':<3}{'W':<3}{'D':<3}{'L':<3}")
        print("-" * 30)
        for i, player in enumerate(tournament.rankings):
            print(f"{i+1:<5}{player.name:<10}{player.score:<5}{player.matches_played:<3}{player.matches_won:<3}{player.matches_drawn:<3}{player.matches_lost:<3}")

    # Tourney completed
    print("\n" + "=" * 50)
    print(f"Tourney {config.name} completed!")
    print("\nFinal League Table:")
    print(f"{'Rank':<5}{'Team':<10}{'Pts':<5}{'P':<3}{'W':<3}{'D':<3}{'L':<3}")
    print("-" * 30)
    for i, player in enumerate(tournament.rankings):
        print(f"{i+1:<5}{player.name:<10}{player.score:<5}{player.matches_played:<3}{player.matches_won:<3}{player.matches_drawn:<3}{player.matches_lost:<3}")

    # Announce winner
    if tournament.rankings:
        print(f"\nThe champion is: {tournament.rankings[0].name}!")

    return tournament

if __name__ == "__main__":
    main()
