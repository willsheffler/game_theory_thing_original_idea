import gt

def main():
    run_tourney()

def run_tourney():
    players = [gt.TourneyPlayer(id=f"p{i}", name=f"gt.TourneyPlayer {i}") for i in range(1, 3)]
    config = gt.TourneyConfig(tournament_type=gt.TourneyType.ROUND_ROBIN,
                              name="Example Tourney",
                              win_points=3,
                              draw_points=1,
                              loss_points=0,
                              random_seed=42)
    tourney = gt.Tourney(config=config, players=players)
    print(tourney)

def run_single_match():
    scorer = gt.GameScorer()
    player1 = gt.SometimesDefect(0.3)
    player2 = gt.Prober()
    match = gt.MatchRunner(player1, player2)
    result = match.play()
    print(result)
    score = scorer.score_game(result)
    print(score)

if __name__ == '__main__':
    main()
