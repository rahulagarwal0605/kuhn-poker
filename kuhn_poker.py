import numpy as np

class Node:
    def __init__(self, name):
        self.name = name
        self.regretSum = np.array([[0, 0], [0, 0], [0, 0]], np.int32)
        self.strategy = np.array([[0, 0], [0, 0], [0, 0]], np.float64)
    
    def getProbability(self, card):
        regretSum = np.clip(self.regretSum[card], a_min=0, a_max=None)
        normalizedSum = np.sum(regretSum)
        if normalizedSum > 0:
            probability = regretSum/normalizedSum
        else:
            probability = np.repeat(0.5, 2)
        self.strategy[card] += probability
        return probability
    
    def getStrategy(self, card):
        strategySum = np.sum(self.strategy[card])
        if strategySum > 0:
            return self.strategy[card]/strategySum
        else:
            return np.repeat(0.5, 2)
    

class KuhnPoker:
    def __init__(self):
        self.cards = np.array([0, 1, 2])

    def getActualReward(self, gameTree, c1, c2):
        if np.random.choice([0, 1], 1, p=gameTree.getProbability(c1))[0] == 0:
            if np.random.choice([0, 1], 1, p=gameTree.left.getProbability(c2))[0] == 0:
                if c1>c2:
                    return [1, 'pp']
                else:
                    return [-1, 'pp']
            else:
                if np.random.choice([0, 1], 1, p=gameTree.left.right.getProbability(c1))[0] == 0:
                    return [-1, 'pbp']
                else:
                    if c1>c2:
                        return [2, 'pbb']
                    else:
                        return [-2, 'pbb']
        else:
            if np.random.choice([0, 1], 1, p=gameTree.right.getProbability(c2))[0] == 0:
                return [1, 'bp']
            else:
                if c1>c2:
                    return [2, 'bb']
                else:
                    return [-2, 'bb']
    
    def playerCounterfactReward(self, gameTree, playerReward, path, c1, c2):
        if path[1] == 'p':
            if c1>c2:
                gameTree.regretSum[c1][0] += 1-playerReward
            else:
                gameTree.regretSum[c1][0] += -1-playerReward
            gameTree.regretSum[c1][1] += 1-playerReward
        else:
            gameTree.left.right.regretSum[c1][0] += -1-playerReward
            if c1>c2:
                gameTree.left.right.regretSum[c1][1] += 2-playerReward
                gameTree.regretSum[c1][0] += 2-playerReward
                gameTree.regretSum[c1][1] += 2-playerReward
            else:
                gameTree.left.right.regretSum[c1][1] += -2-playerReward
                gameTree.regretSum[c1][0] += -1-playerReward
                gameTree.regretSum[c1][1] += -2-playerReward

    def opponentCounterfactReward(self, gameTree, opponentReward, path, c1, c2):
        if path[0]=='p':
            if c2>c1:
                gameTree.left.regretSum[c2][0] += 1-opponentReward
            else:
                gameTree.left.regretSum[c2][0] += -1-opponentReward
            gameTree.left.regretSum[c2][1] += 1-opponentReward
        else:
            gameTree.right.regretSum[c2][0] = -1-opponentReward
            if c2>c1:
                gameTree.right.regretSum[c2][1] += 2-opponentReward
            else:
                gameTree.right.regretSum[c2][1] += -2-opponentReward

    def train(self, iterations, gameTree):
        for i in range(iterations):
            np.random.shuffle(self.cards)
            c1 = self.cards[0]
            c2 = self.cards[1]
            [playerReward, path] = self.getActualReward(gameTree, c1, c2)
            opponentReward = -1*playerReward
            self.playerCounterfactReward(gameTree, playerReward, path, c1, c2)
            self.opponentCounterfactReward(gameTree, opponentReward, path, c1, c2)


if __name__=='__main__':
    np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
    gameTree = Node('P1')
    gameTree.left = Node('P2')
    gameTree.right = Node('P2')
    gameTree.left.right = Node('P1')
    kuhnPoker = KuhnPoker()
    kuhnPoker.train(100000, gameTree)
    c1 = int(input("Enter Card : "))
    if np.random.choice([0, 1], 1, p=gameTree.getStrategy(c1))[0] == 0:
        print("PASS")
        p2 = int(input("Player 2 Choice : "))
        if p2==1:
            if np.random.choice([0, 1], 1, p=gameTree.left.right.getStrategy(c1))[0] == 0:
                print("PASS")
            else:
                print("BET")
    else:
        print("BET")
