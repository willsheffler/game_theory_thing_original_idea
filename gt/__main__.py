import gt


def main():
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
