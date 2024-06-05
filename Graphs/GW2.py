import sys; args=sys.argv[1:]
import re

BLOCKS = set()
EDGEREWARDS = {}
JUMPSMADE = set()
def setGlobals():
    global HEIGHT, WIDTH, DEFREWARD, GRID, DIRLOOKUP, CONNECTIONS, QUEUE, PATHS, DIRECTIONS, SEEN, BACKCONNECTIONS
    WIDTH, HEIGHT, reward = g_process(args[0])
    if reward !=0: DEFREWARD = reward 
    GRID = ['P']*WIDTH*HEIGHT #rewards added later
    CONNECTIONS = {idx: set() for idx in range(HEIGHT*WIDTH)}
    for directive in args[1:]:
        if directive[0]=='V': #sets up rewards and blocks
            v_process(directive)
        if directive[0]=='E':
            e_process(directive) #Neighbors for each index, excludes blocks
    for idx in CONNECTIONS:
        connected = getComplements(idx)
        for num in connected:
            if (idx, num) not in BLOCKS:
                CONNECTIONS.get(idx).add(num) 
    BACKCONNECTIONS = {i: set() for i in range(HEIGHT*WIDTH)}
    for idx in CONNECTIONS:
        for k in CONNECTIONS[idx]:
            BACKCONNECTIONS[k].add(idx)
    DIRLOOKUP = { #DICT of direction list ultimate directions
        'N':'N',
        'E':'E',
        'S':'S',
        'W':'W',
        'EN':'L',
        'NW':'J',
        'SW':'7',
        'ES':'r',
        'EW': '-',
        'NS': '|',
        'ENW':'^',
        'ENS':'>',
        'ESW':'v',
        'NSW':'<',
        'ENSW':'+',
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

def g_process(gDir):
    width, height, reward = 0, 0, 0
    allData = re.findall(r'\d+', gDir)
    nodes = int(allData[0])
    
    if 'W' in gDir:
        width = int(allData[1])
        height = nodes//width
        if 'R' in gDir:
            reward = int(allData[2])
      
    else:
        width, height = dimension(nodes)
        if 'R' in gDir:
            reward = int(allData[1])
    return width, height, reward

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


def toggles(eDir):
    reward = 0
    allData = re.findall(r'\d+', eDir)
    if 'R' in eDir:
        if 'R'==eDir[-1]:
            reward = DEFREWARD
        else:
            reward = int(allData[-1])
            allData = allData[:-1]
    if 'N' in eDir[:][1:] or 'E' in eDir[:][1:] or 'S' in eDir[:][1:] or 'W' in eDir[:][1:]:
        direction = re.findall(r'[NESW]', eDir[1:])
        edge = cardinalEdge(int(allData[0]), direction[0])
        if edge and edge not in BLOCKS:
            if reward != 0:
                EDGEREWARDS[edge]=reward
                if '=' in eDir:
                    EDGEREWARDS[(edge[1], edge[0])]=reward
        return
    half = len(allData)//2
    for tup in list(zip(allData[:][:half], allData[:][half:])):
        if (int(tup[0]), int(tup[1])) not in BLOCKS or (CONNECTIONS[int(tup[0])] and int(tup[1]) in CONNECTIONS[int(tup[0])]):
            if reward != 0:
                EDGEREWARDS[(int(tup[0]), int(tup[1]))]=reward
                if '=' in eDir:
                    EDGEREWARDS[(int(tup[1]), int(tup[0]))]=reward
    return

def additions(eDir):
    reward = 0
    allData = re.findall(r'\d+', eDir)
    if 'R' in eDir:
        if 'R'==eDir[-1]:
            reward = DEFREWARD
        else:
            reward = int(allData[-1])
            allData = allData[:-1]
    if 'N' in eDir[:][1:] or 'E' in eDir[:][1:] or 'S' in eDir[:][1:] or 'W' in eDir[:][1:]:
        direction = re.findall(r'[NESW]', eDir[1:])
        edge = cardinalEdge(int(allData[0]), direction[0])
        if edge and edge in BLOCKS:
            CONNECTIONS[edge[0]].add(edge[1])
            if '=' in eDir:
                CONNECTIONS[edge[1]].add(edge[0])
            if reward != 0:
                EDGEREWARDS[edge]=reward
                if '=' in eDir:
                    EDGEREWARDS[(edge[1], edge[0])]=reward
        return
    half = len(allData)//2
    for tup in list(zip(allData[:][:half], allData[:][half:])):
        if (int(tup[0]), int(tup[1])) in BLOCKS or int(tup[0]) not in getComplements(int(tup[1])):
            CONNECTIONS[int(tup[0])].add(int(tup[1]))
            if '=' in eDir:
                CONNECTIONS[int(tup[1])].add(int(tup[0]))
            if reward != 0:
                EDGEREWARDS[(int(tup[0]), int(tup[1]))]=reward
                if '=' in eDir:
                    EDGEREWARDS[(int(tup[1]), int(tup[0]))]=reward
    return

def subtractions(eDir):
    allData = re.findall(r'\d+', eDir)
    if 'N' in eDir[:][1:] or 'E' in eDir[:][1:] or 'S' in eDir[:][1:] or 'W' in eDir[:][1:]:
        direction = re.findall(r'[NESW]', eDir[1:])
        edge = cardinalEdge(int(allData[0]), direction[0])
        if edge:
            BLOCKS.add(edge)
            if '=' in eDir:
                BLOCKS.add((edge[1],edge[0]))
        return
    half = len(allData)//2
    for tup in list(zip(allData[:][:half], allData[:][half:])):
        if CONNECTIONS[int(tup[0])] and int(tup[1]) in CONNECTIONS[int(tup[0])]:
            CONNECTIONS[int(tup[0])].remove(int(tup[1]))
            if '=' in eDir and CONNECTIONS[int(tup[1])]:
                CONNECTIONS[int(tup[1])].remove(int(tup[0]))
        else:
            BLOCKS.add((int(tup[0]),int(tup[1])))
            if '=' in eDir:
                BLOCKS.add((int(tup[1]),int(tup[0])))
    return

def getSecondList(slices, direction):
    toAdd = 0
    if direction == 'N':
        toAdd = -WIDTH
    if direction == 'S':
        toAdd = WIDTH
    if direction == 'E':
        toAdd = 1
    if direction == 'W':
        toAdd = -1
    return [i+toAdd for i in slices]



def sliceEdge(eDir):
    sliceList = [i for i in range(WIDTH*HEIGHT)]
    finList = []
    allData = re.findall(r'[-\d]+', eDir)
    cleaned = []
    for data in allData:
        if data[0]=='-':
            cleaned.append(-1*int(data[1:]))
        else:
            cleaned.append(int(data))


    if 'N' in eDir[:][1:] or 'E' in eDir[:][1:] or 'S' in eDir[:][1:] or 'W' in eDir[:][1:]:
        direction = re.findall(r'[NESW]', eDir[1:])
        if len(cleaned)==1: cleaned.append(HEIGHT*WIDTH)
        slices = sliceList[cleaned[0]:cleaned[1]]
        secondHalf = getSecondList(slices, direction[0])
        return slices + secondHalf
    #print (sliceList[cleaned[0]::cleaned[1]] + sliceList[cleaned[2]::cleaned[3]])
    return sliceList[cleaned[0]::cleaned[1]] + sliceList[cleaned[2]::cleaned[3]]

        

def e_process(eDir):
    reward = 0
    allData = re.findall(r'\d+', eDir)
    isSlice = False
    if 'R' in eDir:
        if 'R'==eDir[-1]:
            reward = DEFREWARD
        else:
            reward = int(allData[-1])
            allData = allData[:-1]
    global CONNECTIONS
    if ':' in eDir:
        allData = sliceEdge(eDir)
        isSlice = True
    elif '+~' in eDir:
        toggles(eDir)
        return
    elif eDir[1]=='+':
        additions(eDir)
        return
    elif eDir[1]=='~':
        subtractions(eDir)
        return

    if ('N' in eDir[:][1:] or 'E' in eDir[:][1:] or 'S' in eDir[:][1:] or 'W' in eDir[:][1:]) and not isSlice:
        direction = re.findall(r'[NESW]', eDir[1:])
        edge = cardinalEdge(int(allData[0]), direction[0])
        if edge:
            if edge not in BLOCKS:
                print(edge)
                BLOCKS.add(edge)
                if '=' in eDir:
                    BLOCKS.add((edge[1],edge[0]))
            else:
                BLOCKS.remove((edge[0], edge[1]))
                if '=' in eDir:
                    BLOCKS.remove((edge[1], edge[0]))
                if reward != 0:
                    EDGEREWARDS[(edge[0], edge[1])]=reward
                    if '=' in eDir:
                        EDGEREWARDS[(edge[1], edge[0])]=reward
        return

    half = len(allData)//2
    for tup in list(zip(allData[:][:half], allData[:][half:])):
        if  int(tup[0]) not in getComplements(int(tup[1])) or (int(tup[0]), int(tup[1])) in BLOCKS:
            CONNECTIONS[int(tup[0])].add(int(tup[1]))
            if '=' in eDir:
                CONNECTIONS[int(tup[1])].add(int(tup[0]))
            if reward != 0:
                EDGEREWARDS[(int(tup[0]), int(tup[1]))]=reward
                if '=' in eDir:
                    EDGEREWARDS[(int(tup[1]), int(tup[0]))]=reward
        else:
            edge = (int(tup[0]), int(tup[1]))
            if edge in BLOCKS: BLOCKS.remove(edge)
            else:BLOCKS.add(edge)
            if '=' in eDir:
                edge2 = (int(tup[1]), int(tup[0]))
                if edge2 in BLOCKS: BLOCKS.remove(edge2)
                else:BLOCKS.add(edge2)
    return


def v_process(vDir):
    allData = re.findall(r'\d+', vDir)
    if 'R' in vDir and 'B' in vDir:
        vertexes = allData[:][:-1]
        reward = int(allData[-1])
        allData = list(set(allData))
        if 'RB' in vDir:
            reward = DEFREWARD
            vertexes = allData
        for vertex in vertexes: 
            GRID[int(vertex)] = reward
            for k in getComplements(int(vertex)):
                if (int(vertex),k) in BLOCKS:
                    BLOCKS.remove((int(vertex),k))
                    BLOCKS.remove((k,int(vertex)))
                else:
                    BLOCKS.add((int(vertex),k))
                    BLOCKS.add((k,int(vertex)))
        return


    if 'R' in vDir:
        if 'R' == vDir[-1]:
            for i in range(len(allData)):
                GRID[int(allData[i])]=DEFREWARD 
        else:
            reward = int(allData[-1])
            for i in range(len(allData)-1):
                GRID[int(allData[i])]=reward
    if 'B' in vDir:
        allData = list(set(allData))
        for k in allData:
            k = int(k)
            for comp in getComplements(k):
                if (comp,k) in BLOCKS:
                    BLOCKS.remove((comp,k))
                    BLOCKS.remove((k,comp))
                else:
                    BLOCKS.add((comp,k))
                    BLOCKS.add((k,comp))

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

def solve(i, count):
  global SEEN, PATHS, DIRECTIONS, QUEUE, TEMPBLOCKS, BACKCONNECTIONS
  if i in SEEN: 
      return
  if len(SEEN) == HEIGHT*WIDTH: 
      return

  SEEN.append(i)
  PATHS[i] = count
  for k in BACKCONNECTIONS.get(i):
      if CONNECTIONS[k] and i not in CONNECTIONS[k]:
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


def run():
    global SEEN, DIRECTIONS
    #print(BLOCKS)
    #print(CONNECTIONS)
    dirs = ['N', 'E', 'S', 'W']
    POLICY = [set() for i in range(len(GRID))]
    for i in range(len(GRID)):
        if GRID[i] != 'P':
            QUEUE.append((i,0))
            POLICY[i].add('*')
    for tup in EDGEREWARDS:
        QUEUE.append((tup[0],1))
        DIRECTIONS[tup[1]].add(getMove(tup[1], tup[0]))
    for tup in QUEUE:
        i, count = tup 
        solve(i, count)

    for i in range(WIDTH*HEIGHT):
        if not DIRECTIONS[i] and not POLICY[i]:
            POLICY[i].add('.')
        if POLICY[i]=={'*'}:
            continue
        else:
            if 'JUMP' in DIRECTIONS[i] and len(DIRECTIONS[i])<3:
                POLICY[i].add('.')
            else:
                if 'JUMP' in DIRECTIONS[i]: DIRECTIONS[i].remove('JUMP')
                for itm in DIRECTIONS[i]:
                    if itm in dirs:
                        POLICY[i].add(itm)

    #print(DIRECTIONS)
    #print(JUMPSMADE)
    #print(POLICY)
    policy = "".join([DIRLOOKUP.get("".join(sorted(dirs))) for dirs in POLICY])
    print(f'Policy: {policy}')
    jumpstr = ''
    for tup in JUMPSMADE:
       jumpstr = jumpstr+str(tup[0])+'>'+str(tup[1])+';' 
    if JUMPSMADE:
        print(jumpstr[:-1])




def main():
    setGlobals()
    run()
main()

#Abhisheik Sharma 6 2024