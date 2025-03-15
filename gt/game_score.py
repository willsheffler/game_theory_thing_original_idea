class GameScorer:

    def score_game(self, moves):
        p1_score = 0
        p2_score = 0

        score = dict(
            CC=(3, 3),
            CD=(0, 5),
            DC=(5, 0),
            DD=(1, 1),
        )
        for move1, move2 in moves:
                p1_score, p2_score = p1_score + score[move1 + move2][0], p2_score + score[move1 + move2][1]
        return (p1_score, p2_score)
