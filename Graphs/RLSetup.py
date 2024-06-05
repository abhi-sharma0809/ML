import sys; args=sys.argv[1:]
import re

BLOCKS = set()
JUMPSMADE = set()
def setGlobals():
    global HEIGHT, WIDTH, DEFREWARD, GRID, DIRLOOKUP, CONNECTIONS, QUEUE, PATHS, DIRECTIONS, SEEN, PROBLEMTYPE, REWARDS
    REWARDS = []
    DEFREWARD = 12
    PROBLEMTYPE = 0
    rewardDirs = []
    if len(args[1])==1:
        WIDTH = int(args[1])
        HEIGHT = int(args[0])//WIDTH
        rewardDirs = args[2:]
    else:
        WIDTH, HEIGHT = dimension(int(args[0]))
        rewardDirs = args[1:]
    GRID = {idx: 'P' for idx in range(WIDTH*HEIGHT)}
    inputProcess(rewardDirs)
    #rewards added later
    #print(GRID)
    #print(REWARDS)
    #print(BLOCKS)
    CONNECTIONS = {idx: set() for idx in range(WIDTH*HEIGHT)}
    for idx in CONNECTIONS:
        connected = getComplements(idx)
        for num in connected:
            if (idx, num) not in BLOCKS:
                CONNECTIONS.get(idx).add(num)
    DIRLOOKUP = { #DICT of direction list ultimate directions
        'N':'U', #
        'E':'R', #
        'S':'D', #
        'W':'L', #
        'EN':'V', #
        'NW':'M', #
        'SW':'E', #
        'ES':'S', #
        'EW': '-', #
        'NS': '|', #
        'ENW':'N', #
        'ENS':'W', #
        'ESW':'T', #
        'NSW':'F', #
        'ENSW':'+', #
        '*':'*',
        '.':'.',
    }
    QUEUE, SEEN = [], []
    PATHS = [0]*HEIGHT*WIDTH
    DIRECTIONS = [set() for i in range(HEIGHT*WIDTH)]


def dimension(ln):
    #return a 2 long array of the puzzles dimension: width/height
    dimLst = [[i, ln//i] for i in range(1, ln+1) if (ln%i==0)]
    dim = dimLst[len(dimLst)//2]
    return dim[0],dim[1]

def inputProcess(rDirs):
    global DEFREWARD, GRID, PROBLEMTYPE, REWARDS
    for vDir in rDirs:
        allData = [int(k) for k in re.findall(r'\d+', vDir)]
        if 'G' in  vDir:
            PROBLEMTYPE = allData[0]
        if 'R' in vDir or 'r' in vDir:
            if len(allData)==1 and vDir.find(':')==-1:
                GRID[allData[0]]=DEFREWARD
                REWARDS.append(DEFREWARD)
            elif len(allData)==1 and vDir.find(':')==1:
                DEFREWARD=allData[0]
            else:
                if GRID[allData[0]] !='P': REWARDS.remove(GRID[allData[0]])
                GRID[allData[0]]=allData[1]
                REWARDS.append(allData[1])


        if 'B' in vDir:
            B = allData[0]
            dirs = re.findall(r'[NESW]+', vDir)
            blocks = []
            for direction in dirs:
                toAdd = cardinalEdge(B, direction)
                blocks.append(toAdd)
            if not dirs:
                for k in getComplements(B):
                    blocks.append((k, B))
            for block in blocks:
                if block in BLOCKS:
                    BLOCKS.remove(block)
                    BLOCKS.remove((block[1], block[0]))
                else:
                    if block:
                        BLOCKS.add(block)
                        BLOCKS.add((block[1], block[0]))



def cardinalEdge(edge, direction):
    move = 0
    if direction == 'N':
        move = edge-WIDTH
    if direction == 'S':
        move = edge+WIDTH
    if direction == 'E':
        move = edge+1
    if direction == 'W':
        move = edge-1
    if move not in getComplements(edge): return None
    return (edge, move)

def getComplements(idx): #gets all complements of an index
    complements = {'hi'}
    complements.add(idx-WIDTH)
    complements.add(idx+WIDTH)
    if idx%WIDTH == 0:
        complements.add(idx+1)
    elif idx%WIDTH == WIDTH-1:
        complements.add(idx-1)
    else:
        complements.add(idx-1)
        complements.add(idx+1)
    complements = complements - {'hi'}
    return {k for k in complements if (0<=k<len(GRID))}

def getMove(k, i):
    diff = k-i
    if k not in getComplements(i):
        JUMPSMADE.add((k,i))
        return 'JUMP'
    if diff == -WIDTH: return 'S'
    if diff == WIDTH: return 'N'
    if diff == 1: return 'W'
    if diff == -1: return 'E'

def makeTempBlocks(rewards):
    global tempBlocks
    tempBlocks = {reward: set() for reward in rewards}
    for reward in rewards:
        for reward2 in rewards:
            if reward2 != reward:
                for vertex in rewards[reward2]:
                    for k in getComplements(vertex):
                        tempBlocks[reward].add((vertex, k))
                        tempBlocks[reward].add((k, vertex))

def solve(i, count, currBlocked):
    global SEEN, PATHS, DIRECTIONS, QUEUE
    if i in SEEN:
        return
    if len(SEEN) == HEIGHT*WIDTH:
        return

    SEEN.append(i)
    PATHS[i] = count
    for k in CONNECTIONS.get(i):
        if (k,i) in currBlocked:
            continue
        if PATHS[k] <= count+1 and PATHS[k] != 0:
            continue
        if k in SEEN:
            continue
        if not DIRECTIONS[k]:
            DIRECTIONS[k].add(count+1)
        if count+1 in DIRECTIONS[k]:
            DIRECTIONS[k].add(getMove(k, i))
        QUEUE.append((k,count+1))

def sortRewardsByDistance(start):
    sortedRewards = sorted(REWARDS, key=lambda reward: abs(start - reward))
    return sortedRewards


def run1():
    global SEEN, DIRECTIONS

    # Compute distances from every vertex to each reward
    distances = {reward: {idx: abs(idx - reward) for idx in GRID.keys() if GRID[idx] != 'P'} for reward in REWARDS}

    dirs = ['N', 'E', 'S', 'W']
    POLICY = [set() for _ in range(len(GRID))]

    for idx in GRID.keys():
        if GRID[idx] == 'P':  # Skip start vertex
            continue

        max_ratio = float('-inf')
        optimal_reward = None

        for reward in REWARDS:
            distance = distances[reward][idx]
            ratio = reward / (distance + 1)
            if ratio > max_ratio:
                max_ratio = ratio
                optimal_reward = reward

        DIRECTIONS = [set() for _ in range(HEIGHT * WIDTH)]
        QUEUE = [(idx, 0)]
        PATHS = [0] * HEIGHT * WIDTH
        SEEN = []

        while QUEUE:
            i, count = QUEUE.pop(0)

            if i in SEEN:
                continue
            if len(SEEN) == HEIGHT * WIDTH:
                break

            SEEN.append(i)
            PATHS[i] = count

            for k in CONNECTIONS.get(i):
                if (k, i) in tempBlocks.get(optimal_reward, set()):
                    continue
                if PATHS[k] <= count + 1 and PATHS[k] != 0:
                    continue
                if k in SEEN:
                    continue

                if not DIRECTIONS[k]:
                    DIRECTIONS[k].add(count + 1)

                if count + 1 in DIRECTIONS[k]:
                    DIRECTIONS[k].add(getMove(k, i))
                QUEUE.append((k, count + 1))

        for idx in range(len(POLICY)):
            if POLICY[idx] == set():
                POLICY[idx] = DIRECTIONS

    NEWPOLICY = [set() for _ in range(HEIGHT * WIDTH)]

    for i in range(WIDTH * HEIGHT):
        if not POLICY[i] and not NEWPOLICY[i]:
            NEWPOLICY[i].add('.')
        if '*' in POLICY[i]:
            NEWPOLICY[i] = {'*'}
        else:
            for itm in POLICY[i]:
                if itm in dirs:
                    NEWPOLICY[i].add(itm)

    policy = "".join([DIRLOOKUP.get("".join(sorted(dirs))) for dirs in NEWPOLICY])
    print(f'Policy: {policy}')




def run0():
    global SEEN, DIRECTIONS, REWARDS, QUEUE, PATHS, SEEN
    REWARDS = sorted(REWARDS)[::-1]
    rewards = {idx: set() for idx in sorted(list(set(REWARDS)))[::-1]}
    seenRewards = set()
    for reward in REWARDS:
        for k in GRID:
            if GRID[k]==reward and (k, reward) not in seenRewards:
                seenRewards.add((k,reward))
                rewards[reward].add(k)
    makeTempBlocks(rewards)
    dirs = ['N', 'E', 'S', 'W']
    POLICY = [set() for i in range(len(GRID))]
    for reward in rewards:
        if set() not in POLICY: break
        DIRECTIONS = [set() for i in range(HEIGHT*WIDTH)]
        QUEUE = []
        PATHS = [0]*HEIGHT*WIDTH
        SEEN = []
        currBlocked = tempBlocks.get(reward)
        for vertex in rewards[reward]:
            POLICY[vertex].add('*')
            QUEUE.append((vertex, 0))
        for tup in QUEUE:
            i, count = tup
            solve(i, count, currBlocked)
        for idx in range(len(POLICY)):
            if POLICY[idx]==set(): POLICY[idx]=DIRECTIONS[idx]

    NEWPOLICY = [set() for i in range(HEIGHT*WIDTH)]
    for i in range(WIDTH*HEIGHT):
        if not POLICY[i] and not NEWPOLICY[i]:
            NEWPOLICY[i].add('.')
        if '*' in POLICY[i]:
            NEWPOLICY[i] = {'*'}
        else:
            for itm in POLICY[i]:
                if itm in dirs:
                    NEWPOLICY[i].add(itm)

    policy = "".join([DIRLOOKUP.get("".join(sorted(dirs))) for dirs in NEWPOLICY])
    print(f'Policy: {policy}')




def main():
    setGlobals()
    if PROBLEMTYPE == 0:
        run0()
    else:
        run1()
main()
#Abhisheik Sharma 6 2024