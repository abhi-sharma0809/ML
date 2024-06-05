import sys; args = sys.argv[1:]
import re
import random

def getData(gDir):
    allNums = [int(k) for k in re.findall(r'\d+', gDir)]
    data = [allNums[0], 0, 12]
    ln = allNums[0]
    if len(allNums)==3:
        return allNums
    if len(allNums)==1:
        dimLst = [[i, ln // i] for i in range(1, ln + 1) if (ln % i == 0)]
        dim = dimLst[len(dimLst) // 2]
        data[1] = dim[0]
        return data
    if 'R' in gDir:
        dimLst = [[i, ln // i] for i in range(1, ln + 1) if (ln % i == 0)]
        dim = dimLst[len(dimLst) // 2]
        data[1] = dim[0]
        data[2] = allNums[1]
        return data
    if 'W' in gDir:
        data[1] = allNums[1]
        return data
    return data

def defaultEdges(graph):
    WIDTH = graph['width']
    complements = {'hi'}
    for v in range(graph['size']):
        complements.add((v, v - WIDTH))
        complements.add((v, v + WIDTH))
        if v % WIDTH == 0:
            complements.add((v, v + 1))
        elif v % WIDTH == WIDTH - 1:
            complements.add((v, v - 1))
        else:
            complements.add((v, v - 1))
            complements.add((v, v + 1))
        complements = complements - {'hi'}
    return {k for k in complements if (0 <= k[1] < graph['size'])}

def vSlices(size, vPrs):
    allIndices = [i for i in range(size)]
    vIndices = []
    index_r, index_b = vPrs.find('R'), vPrs.find('B')
    if index_r > 0 and index_b > 0:
        vPrs = vPrs[0:min(index_r,index_b)]

    elif index_r > 0:
        vPrs = vPrs[0:index_r]

    elif index_b > 0:
        vPrs = vPrs[0:index_b]

    allSlices = vPrs.split(',')

    for slice in allSlices:
        sliceInts = [int(k) for k in re.findall(r'-*\d+', slice)]
        if ":" not in slice and '::' not in slice:
            vIndices.append(allIndices[sliceInts[0]])
        elif "::" in slice:
            if not sliceInts:
                continue
            elif len(sliceInts)==2:
                toAdd = allIndices[sliceInts[0]::sliceInts[1]]
                vIndices.extend(toAdd)
            else:
                if slice[0]==':':
                    toAdd = allIndices[::sliceInts[0]]
                    if len(toAdd) != size: vIndices.extend(toAdd)
                else:
                    toAdd = allIndices[sliceInts[0]::]
                    if len(toAdd) != size: vIndices.extend(toAdd)
        elif slice.count(":")==2 and ('::') not in slice:
            if len(sliceInts)==3:
                toAdd = allIndices[sliceInts[0]:sliceInts[1]:sliceInts[2]]
                if len(toAdd) != size: vIndices.extend(toAdd)
            elif len(sliceInts)==1:
                toAdd = allIndices[:sliceInts[0]:]
                if len(toAdd) != size: vIndices.extend(toAdd)
            else:
                if slice[0]==':':
                    toAdd = allIndices[:sliceInts[0]:sliceInts[1]]
                    if len(toAdd) != size: vIndices.extend(toAdd)
                else:
                    toAdd = allIndices[sliceInts[0]:sliceInts[1]:]
                    if len(toAdd) != size: vIndices.extend(toAdd)
        else:
            if not sliceInts:
                continue
            elif len(sliceInts)==2:
                toAdd = allIndices[sliceInts[0]:sliceInts[1]]
                vIndices.extend(toAdd)
            else:
                if slice[0]==':':
                    toAdd = allIndices[:sliceInts[0]]
                    vIndices.extend(toAdd)
                else:
                    toAdd = allIndices[sliceInts[0]:]
                    vIndices.extend(toAdd)
    toRet = []
    for v in vIndices:
        if vIndices not in toRet:
            toRet.append(v)
    return toRet

def processV(graph, vDir):
    allInts = [int(k) for k in re.findall(r'\d+', vDir)]
    reward = graph['reward']
    if re.findall(r'R\d+', vDir):
        reward = allInts[-1]

    if ('R' not in vDir) and ('B' not in vDir):
        return graph

    allV = vSlices(graph['size'], vDir)
    if 'R' in vDir:
        vertexes = graph['vertices']
        for v in allV:
            vertexes[v] = reward
        graph['vertices'] = vertexes
    if 'B' in vDir:
        edges = graph['edges']
        W = set(allV)
        X = {i for i in range(graph['size'])} - W
        default = defaultEdges(graph)

        for h in W:
            for k in X:
                if (h,k) in default:
                    if (h,k) in edges:
                        edges.remove((h,k))
                    else:
                        edges.add((h,k))
                    if (k,h) in edges:
                        edges.remove((k,h))
                    else:
                        edges.add((k,h))
                else:
                    if (h,k) in edges:
                        edges.remove((h,k))
                    if (k,h) in edges:
                        edges.remove((k,h))

        graph['edges'] = edges

    return graph

def processMngmnt(graph, edges, mngmnt, eDir):
    allInts = [int(k) for k in re.findall(r'\d+', eDir)]
    reward = graph['reward']
    if re.findall(r'R\d+', eDir):
        reward = allInts[-1]
    current = graph['edges']
    edgeRwds = graph['edgeRwds']

    if mngmnt == "!":
        for tup in edges:
            if tup in current:
                current.remove(tup)
    elif mngmnt == "~":
        for tup in edges:
            if tup in current:
                current.remove(tup)
            else:
                current.add(tup)
                if "R" in eDir:
                    edgeRwds[tup] = reward
    elif mngmnt == "@":
        for tup in edges:
            if tup in current:
                if "R" in eDir:
                    edgeRwds[tup] = reward
    elif mngmnt == "+":
        for tup in edges:
            if tup not in current:
                current.add(tup)
                if "R" in eDir:
                    edgeRwds[tup] = reward
    elif mngmnt == "*":
        for tup in edges:
            current.add(tup)
            if "R" in eDir:
                edgeRwds[tup] = reward

    graph['edges'] = current
    graph['edgeRwds'] = edgeRwds
    for tup in graph['edges']:
        if tup not in graph['edgeRwds']:
            graph['edgeRwds'][tup]=-1

    return graph

def processE(graph, eDir):
    if len(eDir) > 1 and eDir[1] in "!+*~@":
        mngmnt = eDir[1]
        fIdx = -1
        for idx in range(2, len(eDir)):
            if eDir[idx] in "NSEW~=":
                fIdx = idx - 2
                break
        slice = 2 + fIdx if fIdx != -1 else len(eDir)
        v1 = eDir[2:slice]
    else:
        mngmnt = "~"
        fIdx = -1
        for idx in range(1, len(eDir)):
            if eDir[idx] in "NSEW~=":
                fIdx = idx - 1
                break
        slice = fIdx + 1 if fIdx != -1 else len(eDir)
        v1 = eDir[1:slice]

    sIdx = -1
    for idx in range(2, len(eDir)):
        if eDir[idx] in "RT":
            sIdx = idx - 2
            break
    if sIdx != -1:
        v2_end = sIdx + 2
    else:
        v2_end = None

    if not any(ch in "NSEW" for ch in eDir[1:]):
        v2 = eDir[slice + 1:v2_end]
    else:
        v2 = None

    doubled = "=" in eDir

    if v2:
        v1s = vSlices(graph['size'], v1)
        v2s = vSlices(graph['size'], v2)
        edges = list(zip(v1s, v2s))
    else:
        v1s = vSlices(graph['size'], v1)
        edges = generateEdges(graph, v1s, eDir[1:])

    edges_set = set()
    for (v1, v2) in edges:
        edges_set.add((v1, v2))
        if doubled:
            edges_set.add((v2, v1))

    edges = edges_set

    return processMngmnt(graph, edges, mngmnt, eDir)

def generateEdges(graph, vertices, eDir):
    new_edges = []
    for v in vertices:
        for direction in re.findall(r'[NSEW]+', eDir[1:])[0]:
            if direction == "N" and v >= graph['width']:
                new_edges.append((v, v - graph['width']))
            elif direction == "E" and v % graph['width'] < graph['width'] - 1:
                new_edges.append((v, v + 1))
            elif direction == "S" and v < graph['size'] - graph['width']:
                new_edges.append((v, v + graph['width']))
            elif direction == "W" and v % graph['width'] > 0:
                new_edges.append((v, v - 1))
    return new_edges

def argMax(graph, valuation, vertex):
    edgeSet = {edge[1] for edge in graph['edges'] if edge[0]==vertex}
    if not edgeSet:
        return set()
    maxVal = -100000
    optimal = set()
    for edge in edgeSet:
        if ((vertex, edge) in graph['edgeRwds']) and (graph['edgeRwds'][(vertex, edge)] > maxVal) and (graph['edgeRwds'][(vertex,edge)] != -1):
            optimal = {edge}
            maxVal = graph['edgeRwds'][(vertex,edge)]
        if (valuation[edge]) and (valuation[edge]>maxVal) and (graph['edgeRwds'][(vertex, edge)] == -1):
            optimal = {edge}
            maxVal = valuation[edge]
        if (valuation[edge] and valuation[edge]==maxVal) or ((vertex, edge) in graph['edgeRwds'] and graph['edgeRwds'][(vertex, edge)] == maxVal and graph['edgeRwds'][(vertex,edge)] != -1):
            optimal.add(edge)
    return optimal

def maxValuationDelta(prevValuation, valuation):
    return max(abs(valuation[i]-prevValuation[i]) for i in range(len(valuation)))

def grfValuePolicy(graph,policy,gamma):
    valuation = []
    endState = []
    for i in range(graph['size']):
        value = graph['vertices'][i]
        if value != 'none':
            valuation.append(value)
            endState.append(i)
        else:
            valuation.append('')
    if graph['width']==0:
        return valuation
    for i in range(len(valuation)):
        if valuation[i]=='':
            valuation[i]=0

    valuationDelta = 1000000
    while(valuationDelta>.001):
        prevValuation = valuation.copy()
        for vtx in range(len(policy)):
            if vtx not in endState:
                val = 0
                edgeSet = policy[vtx]
                if edgeSet:
                    #val = sum(prevValuation[edge] for edge in edgeSet)/len(edgeSet)
                    for edge in edgeSet:
                        if (vtx,edge) in graph['edgeRwds'] and graph['edgeRwds'][(vtx,edge)] != -1:
                            val+=graph['edgeRwds'][(vtx,edge)]
                        else:
                            val += prevValuation[edge]
                    val /= len(edgeSet)
                    if gamma>0.5:
                        val *= gamma
                    else:
                        val -= gamma
                valuation[vtx]=val
        valuationDelta = maxValuationDelta(prevValuation, valuation)

    for i in range(len(valuation)):
        if valuation[i]==0:
            valuation[i]=''
    return valuation

def grfPolicyFromValuation(graph,valuation):
    policy = []
    for i in range(graph['size']):
        if graph['vertices'][i] != 'none':
            policy.append(set())
        else:
            policy.append(argMax(graph, valuation, i))

    return policy

def grfFindOptimalPolicy(graph):
    valuation = []
    for i in range(graph['size']):
        value = graph['vertices'][i]
        if value != 'none':
            valuation.append(value)
        else:
            valuation.append(0)
    if graph['width']==0:
        return [set() for i in range(graph['size'])]

    policy = grfPolicyFromValuation(graph, valuation)
    prevPolicy = [{'temp'} for i in range(graph['size'])]
    while(policy != prevPolicy):
        valuation = grfValuePolicy(graph, (prevPolicy := policy), .01)
        policy = grfPolicyFromValuation(graph, valuation)
    for i in range(len(valuation)):
        if valuation[i] != '':
            valuation[i] = round(valuation[i], 4)
    return grfPolicyFromValuation(graph, valuation)

def getValuation(graph):
    valuation = []
    for i in range(graph['size']):
        value = graph['vertices'][i]
        if value != 'none':
            valuation.append(value)
        else:
            valuation.append(0)
    if graph['width']==0:
        new = []
        for v in valuation:
            if v == 0:
                new.append(f" {'00'}")
            else:
                new.append(f" {float(v):.5g}"[-6:])
        return "".join(new)[1:]

    policy = grfPolicyFromValuation(graph, valuation)
    prevPolicy = [{'temp'} for i in range(graph['size'])]
    while(policy != prevPolicy):
        valuation = grfValuePolicy(graph, (prevPolicy := policy), .01)
        policy = grfPolicyFromValuation(graph, valuation)
    for i in range(len(valuation)):
        if valuation[i] == '':
            valuation[i] = 0
    new = []
    for v in valuation:
        if v == 0:
            new.append(f" {'00'}")
        else:
            new.append(f" {float(v):.5g}"[-6:])
    toRet = ''
    for i in range(len(new)):
        if i % graph['width']==0:
            toRet += new[i][1:]
        elif i % graph['width']==graph['width']-1:
            toRet = toRet + new[i] + '\n'
        else:
            toRet += new[i]
    return toRet[:-1]

def getMove(WIDTH, k, i):
  diff = k-i
  if diff == -WIDTH: return 'S'
  if diff == WIDTH: return 'N'
  if diff == 1: return 'W'
  if diff == -1: return 'E'

def grfParse(lstArgs):
    graph = {'type': 'G', 'size': 0, 'width': 0, 'reward': 12, 'edges': set(), 'vertices': {}, 'edgeRwds': {}, 'gdir': lstArgs[0]}
    dims = getData(lstArgs[0])
    graph['size'] = dims[0]
    graph['width'] = dims[1]
    graph['reward'] = dims[2]
    graph['vertices'] = {i:'none' for i in range(graph['size'])}
    if('N' in lstArgs[0]):
        graph['width'] = 0
    if graph['width'] > 0:
        defaults = defaultEdges(graph)
        graph['edges'] = defaults
        graph['edgeRwds']={tup:-1 for tup in defaults}

    if len(lstArgs)>1:
        for arg in lstArgs[1:]:
            if arg[0]=='V':
                graph = processV(graph, arg[1:])
            if arg[0]=='E':
                graph = processE(graph, arg)
    return graph

def grfSize(graph):
    return graph['size']

def grfNbrs(graph, v):
    allEdges = graph['edges']
    return {tup[1] for tup in allEdges if tup[0]==v}

def grfGProps(graph):
    if 'N' in graph['gdir']: return {'rwd': graph['reward']}
    properties = {'rwd': graph['reward'], 'width': graph['width']}
    return properties

def grfVProps(graph, v):
    vertexes = graph['vertices']
    if vertexes[v] != 'none': return {'rwd': vertexes[v]}
    return {}

def grfEProps(graph, v1, v2):
    edges = graph['edges']
    edgeRwds = graph['edgeRwds']
    if (v1,v2) in edges and (v1,v2) in edgeRwds and edgeRwds[(v1,v2)] != -1: return {'rwd': edgeRwds[(v1,v2)]}
    return {}
def grfStrEdges(graph):
    width = graph['width']
    if width == 0:
        return ''
    allMoves = {i:set() for i in range(graph['size'])}

    for tup in graph['edges']:
        k = tup[0]
        i = tup[1]
        if getMove(width, k, i): allMoves[k].add(getMove(width, k, i))

    for i in allMoves:
        if not allMoves[i]:
            allMoves[i].add('.')

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
        '.':'.'}

    moveStr = "".join(DIRLOOKUP.get("".join(sorted(dirs))) for dirs in allMoves.values())
    newMoves = [moveStr[i:i+width] for i in range(0, len(moveStr), width)]
    if newMoves: moveStr = '\n'.join(newMoves)


    v1, v2 = '',''
    for tup in graph['edges']:
        if not (abs(tup[0] - tup[1]) == 1 or abs(tup[0] - tup[1]) == width):
            v1 = v1 + str(tup[0]) + ','
            v2 = v2+ str(tup[1]) + ','

    if v1:
        return moveStr + '\n' +  v1[:-1] + '~' + v2[:-1]
    return moveStr

def grfStrProps(graph):
    properties = grfGProps(graph)
    if 'N' in graph['gdir']: return 'rwd: ' + str(properties['rwd'])
    toRet = ', '.join([f"{key}: {value}" for key, value in properties.items()])
    for i in graph['vertices']:
        if graph['vertices'][i] != 'none':
            toRet += f"\n{i}: rwd: {graph['vertices'][i]}"
    for tup in graph['edgeRwds']:
        if graph['edgeRwds'][tup] !=-1 and tup in graph['edges']:
            toRet += f"\n{tup}: rwd: {graph['edgeRwds'][tup]}"

    return toRet

def grfOptimalStr(graph, policy):
    width = graph['width']
    if width == 0:
        return '.'*graph['size']
    allMoves = {i:set() for i in range(graph['size'])}

    for k in range(len(policy)):
        for i in policy[k]:
            if getMove(width, k, i): allMoves[k].add(getMove(width, k, i))

    for i in allMoves:
        if not allMoves[i]:
            if graph['vertices'][i] != 'none':
                allMoves[i].add('*')
            else:
                allMoves[i].add('.')


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
        '.':'.'}

    moveStr = "".join(DIRLOOKUP.get("".join(sorted(dirs))) for dirs in allMoves.values())
    newMoves = [moveStr[i:i+width] for i in range(0, len(moveStr), width)]
    if newMoves: moveStr = '\n'.join(newMoves)

    v1, v2 = '', ''
    for k in range(len(policy)):
        for i in policy[k]:
            if getMove(width, k, i) == None:
                v1 = v1 + str(k) + ','
                v2 = v2 + str(i) + ','

    if v1:
        return moveStr + '\nJumps: ' +  v1[:-1] + '~' + v2[:-1]

    return moveStr

# def main():
#     #args = 'GG45 E~15,18,41,4=37,14,5,42R E*38,31=27,44R13 V25B'.split(' ')
#     graph = grfParse(args)
#     print('Graph:')
#     grfStr = grfStrEdges(graph)
#     if grfStr: print(grfStr)
#     print(grfStrProps(graph))
#     print()
#     print('Optimal policy:')
#     print(grfOptimalStr(graph, grfFindOptimalPolicy(graph)))
#     print()
#     print('Valuation:')
#     print(getValuation(graph))
#
# main()

#Abhisheik Sharma 6 2024
