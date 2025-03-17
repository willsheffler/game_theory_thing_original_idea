from icecream import ic
import gt

def main():
    test_tourney_simple()

def test_tourney_simple():

    matchmaker = gt.AllPairs()
    players = [
        gt.Player(gt.Cooperator()),
        gt.Player(gt.Defector()),
        gt.Player(gt.TitForTat()),
        gt.Player(gt.Random()),
    ]
    print([p.name for p in players])
    print(matchmaker)
    tourney = gt.Tourney(players, matchmaker)
    tourney.run()
    

if __name__ == '__main__':
    main()
