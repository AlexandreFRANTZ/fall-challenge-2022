import sys
import math
import random
from dataclasses import dataclass

@dataclass
class Plate:
    xPos: int
    yPos: int
    scraps: int
    owner: int
    units: int
    recycler: bool
    can_build: bool
    can_spawn: bool
    in_range_of_recycler: bool

def nullPlate() -> Plate:
    return Plate(-1,-1,-1,-1,-1,False,False,False,False)

def isPlateNull(plate: Plate) -> bool:
    if plate == Plate(-1,-1,-1,-1,-1,False,False,False,False):
        return True
    return False

class Map:
    def __init__(self):
        self.map = []
        self.cmd = []

    def clearCmd(self):
        self.cmd.clear()

    def update(self, myMatter, oppMatter):
        self.myMatter = myMatter
        self.oppMatter = oppMatter
    
    def getMyMatter(self):
        return self.myMatter

    def getOppMatter(self):
        return self.oppMatter

    def addCmd(self, cmd):
        self.cmd.append(cmd)

    def printCmd(self):
        print(*self.cmd, sep=";")

    def reinitMap(self):
        self.map.clear()

    def addPlate(self, plate: Plate):
        self.map.append(plate)

    def getPlate(self, index: int) -> Plate:
        return self.map[index]

    def getPlateByPos(self, x: int, y: int) -> Plate:
        for i in self.map:
            if i.xPos == x and i.yPos == y:
                return i
        return nullPlate()
    
    def getMap(self) -> list[Plate]:
        return self.map


def move(mp: Map, amount, fromx, fromy, tox, toy):
    mp.addCmd("MOVE "+str(amount)+" "+str(fromx)+" "+str(fromy)+" "+str(tox)+" "+str(toy))

def build(mp: Map, x, y):
    mp.addCmd("BUILD "+str(x)+" "+str(y))

def spawn(mp: Map, n, x, y):
    mp.addCmd("SPAWN "+str(n)+" "+str(x)+" "+str(y))

def isPerfectBuild(mp, x, y):
    p = mp.getPlateByPos(x, y)
    if (p.scraps < mp.getPlateByPos(x+1, y).scraps and p.scraps < mp.getPlateByPos(x-1, y).scraps and p.scraps < mp.getPlateByPos(x, y+1).scraps and p.scraps < mp.getPlateByPos(x, y-1).scraps and p.scraps > 2):
        return True
    return False

def buildRecycler(mp: Map):
    for p in mp.getMap():
        if p.owner == 1 and p.can_build == True:
            if isPerfectBuild(mp, p.xPos, p.yPos) == True:
                build(mp, p.xPos, p.yPos)
                break
    
def spawnTank(mp: Map):
    toSpawn = []
    for p in mp.getMap():
        if p.owner == 1 and p.can_spawn == True and ((p.in_range_of_recycler == True and p.scraps > 1) or p.in_range_of_recycler == False):
            toSpawn.append((p.xPos, p.yPos))
    for i in range(len(toSpawn)-1):
        t = random.choice(toSpawn)
        spawn(mp, 1, t[0], t[1])
    for i in range(len(toSpawn)-1):
        spawn(mp, 1, toSpawn[i][0], toSpawn[i][1])

def makeMove(mp: Map):
    didMove = False
    lst = []
    for p in mp.getMap():
        if p.owner == 0 and p.units > 0:
            lst.append((p.xPos, p.yPos))
    if lst:
        toFight = lst[random.randint(0,len(lst)-1)]
        for p in mp.getMap():
            if p.owner == 1 and p.units > 0:
                move(mp, p.units, p.xPos, p.yPos, toFight[0], toFight[1])
                didMove = True
    return didMove

def makeSecondMove(mp: Map):
    target = (-1,-1)
    for p in mp.getMap():
        if p.owner == 0:
            target = (p.xPos, p.yPos)
            break
    if target != (-1,-1):
        for p in mp.getMap():
            if p.owner == 1 and p.units > 0:
                move(mp, p.units, p.xPos, p.yPos, target[0], target[1])
    else:
        for p in mp.getMap():
            if p.owner == 1 and p.units > 0:
                move(mp, p.units, p.xPos, p.yPos, 0, 0)

def moveRand(mp: Map):
    lst = []
    for p in mp.getMap():
        if p.owner == 1 and p.units > 0:
            lst.append((p.xPos, p.yPos))
    if lst:
        rand = lst[random.randint(0,len(lst)-1) if len(lst) > 1 else 0]
        for p in mp.getMap():
            if p.owner == -1:
                plate = mp.getPlateByPos(rand[0], rand[1])
                if isPlateNull(plate) == False:
                    move(mp, 1, plate.xPos, plate.yPos, p.xPos, p.yPos)

def getNeutralNeighbor(mp: Map, x, y) -> Plate:
    p = mp.getPlateByPos(x+1, y)
    if p.owner == -1 and p.scraps > 0 or p.owner == 0:
        return p
    p = mp.getPlateByPos(x-1, y)
    if p.owner == -1 and p.scraps > 0 or p.owner == 0:
        return p
    p = mp.getPlateByPos(x, y+1)
    if p.owner == -1 and p.scraps > 0 or p.owner == 0:
        return p
    p = mp.getPlateByPos(x, y-1)
    if p.owner == -1 and p.scraps > 0 or p.owner == 0:
        return p
    return nullPlate()

def conquere(mp: Map):
    didMove = False
    lst = []
    for p in mp.getMap():
        if p.owner == 1 and p.units > 0:
            lst.append(p)
    for l in lst:
        tmp = getNeutralNeighbor(mp, l.xPos, l.yPos)
        if not(isPlateNull(tmp)):
            move(mp, l.units, l.xPos, l.yPos, tmp.xPos, tmp.yPos)
            didMove = True
    return didMove

def lastMove(mp: Map):
    lst = []
    for p in mp.getMap():
        if p.owner == -1 and p.scraps > 0:
            lst.append(p)
    if not(lst):
        return
    for p in mp.getMap():
        rand = lst[random.randint(0, len(lst)-1) if len(lst) > 1 else 0]
        if p.owner == 1 and p.units > 0:
            move(mp, p.units, p.xPos, p.yPos, rand.xPos, rand.yPos)

def gameLoop():
    rnd = 0
    width, height = [int(i) for i in input().split()]
    mp = Map()
    while True:
        mp.clearCmd()
        my_matter, opp_matter = [int(i) for i in input().split()]
        mp.update(my_matter, opp_matter)
        mp.reinitMap()
        for i in range(height):
            for j in range(width):
                # owner: 1 = me, 0 = foe, -1 = neutral
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in input().split()]
                mp.addPlate(Plate(j, i, scrap_amount, owner, units, True if recycler > 0 else False, True if can_build > 0 else False, True if can_spawn > 0 else False, True if in_range_of_recycler > 0 else False))
        buildRecycler(mp)
        spawnTank(mp)
        if rnd < 15:
            conquere(mp)
            lastMove(mp)
        else:
            makeMove(mp)
            makeSecondMove(mp)
            conquere(mp)
            lastMove(mp)
        mp.printCmd()
        rnd+=1

gameLoop()
