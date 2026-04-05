import tkinter as tk
import copy
import heapq

class Coord:
    x = 0
    y = 0
    heuristic = 10000
    def __init__(self, x, y):
        self.x=x % 3
        self.y=y % 3
    def __repr__(self):
        return f"{{{self.x},{self.y}}}"
    def __eq__(self, value):
        if value is None: return False
        return self.x == value.x and self.y == value.y

    def getTaxiBlockDistance(self, other):
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return dx + dy
    


class Board:
    finalConfig = (
        (1, 2, 3),
        (8, 0, 4),
        (7, 6, 5)
    )
        
    def __init__(self, iState, cost=0, pMove=None, lastMove=None):
        self.cost = cost
        self.state = tuple(tuple(row) for row in iState)
        self.pMove = pMove
        self.lastMove = lastMove

    def __hash__(self):
        return hash(self.state)
    
    def __eq__(self, other):
        return isinstance(other,Board) and self.state == other.state

    def getBlank(self):
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 0:
                    return Coord(i,j)

    def getMoves(self, allowBackTracks):
        moves = []
        blank = self.getBlank()
        if blank.x != 2: #Right
            c = Coord(blank.x+1,blank.y)
            if c != self.lastMove or allowBackTracks:
                moves.append(c)
        if blank.x != 0: #Left
            c = Coord(blank.x-1,blank.y)
            if c != self.lastMove or allowBackTracks:
                moves.append(c)
        if blank.y != 2: #Down
            c = Coord(blank.x,blank.y+1)
            if c != self.lastMove or allowBackTracks:
                moves.append(c)
        if blank.y != 0: #Up
            c = Coord(blank.x,blank.y-1)
            if c != self.lastMove or allowBackTracks:
                moves.append(c)
        return moves

    def swap(self, tile):
        blank = self.getBlank()
        rows = [list(row) for row in self.state]
        rows[blank.x][blank.y], rows[tile.x][tile.y] = rows[tile.x][tile.y], rows[blank.x][blank.y]
        newState = tuple(tuple(row) for row in rows)
        return Board(newState, cost=self.cost+1, pMove=tile, lastMove=blank)

    def getTile(self, tile):
        return self.state[tile.x][tile.y]

    def __lt__(self, other):
        return self.getAStarFunc() < other.getAStarFunc()

    def printBoard(self):
        print()
        for row in self.state:
                print(' '.join(str(x) for x in row))

    def getOutOfPlaceHeuristic(self):
        count=0
        for i in range(3):
            for j in range(3):
                if self.state[i][j] != self.finalConfig[i][j] & self.state[i][j] != 0:
                    count += 1
        return count
    
    def getDistanceHeuristic(self):
        goalPos = {}
        for i in range(3):
            for j in range(3):
                goalPos[finalState[i][j]] = Coord(i,j)
        distance=0
        for i in range(3):
            for j in range(3):
                val = self.state[i][j]
                if val == 0:
                    continue
                goal = goalPos[val]
                distance += Coord(i,j).getTaxiBlockDistance(goal)
        return distance
    
    def getAStarFunc(self):
        return self.getDistanceHeuristic() + self.cost
    
    def getBestMoveSet(self, finalState):
        Board.finalConfig = tuple(tuple(row) for row in finalState )
        initialBoard = Board(self.state, cost = 0, pMove=None, lastMove=None)
        initialBoard.state = self.state
        states = []
        heapq.heappush(states, (initialBoard.getAStarFunc(), initialBoard))
        parentBoard = {}
        parentMove = {}
        bestCost = {}
        initialKey = initialBoard.state
        parentBoard[initialKey] = None
        parentMove[initialKey] = None
        bestCost[initialKey] = 0

        goalKey = tuple(tuple(row) for row in finalState)

        goalFound = None

        while states:
            #Get current state and check for win
            _, current = heapq.heappop(states)
            currentKey = current.state
            print(f"This board has a utility of {current.getAStarFunc()}")
            current.printBoard()
            if currentKey == goalKey:
                goalFound = current
                break

            #Get neighbours
            for move in current.getMoves(False):
                neighbour = current.swap(move)
                neighbourKey = neighbour.state
                newCost = neighbour.cost

                if neighbourKey not in bestCost or newCost < bestCost[neighbourKey]:
                        bestCost[neighbourKey] = newCost
                        utility = newCost + neighbour.getDistanceHeuristic()
                        heapq.heappush(states, (utility, neighbour))
                        parentBoard[neighbourKey] = currentKey
                        parentMove[neighbourKey] = move

        stateList = []
        moveList = []
        movecount = 0
        if goalFound is not None:
            current = goalKey
            while current is not None and current in parentBoard:
                stateList.append(current)
                move = parentMove.get(current)
                moveList.append(move)
                current = parentBoard[current]
                if current is not None:
                    movecount += 1

        stateList.reverse()
        moveList.reverse()
        return stateList, movecount, moveList

def on_click_tile(event):
    global gameBoard
    for i in range(3):
        for j in range(3):
            x, y = canvas.coords(f"tile{i}{j}")[:2]
            dx = x + tileSize
            dy = y + tileSize
            if event.x > x and event.x < dx and event.y > y and event.y < dy:
                print(f"Clicked on {gameBoard.state[j][i]}")
                gameBoard = gameBoard.swap(Coord(j,i))
    for i in range(13):
        x, y = canvas.coords(f"button{i}")[:2]
        dx = x + tileSize
        dy = y + tileSize/2
        if event.x > x and event.x < dx and event.y > y and event.y < dy:
            canvas.itemconfig(f"button{i}", fill=highlight)
            gameBoard.state = initialStates[i]
        else:
            canvas.itemconfig(f"button{i}", fill=tileCol)
    x, y = canvas.coords("CALCULATE")[:2]
    dx = x + tileSize*2
    dy = y + tileSize
    if event.x > x and event.x < dx and event.y > y and event.y < dy:
        make_best_moves()
    update(canvas)


def make_best_moves():
    gameBoard.cost = 0
    global stateSet
    stateSet, movecount = gameBoard.getBestMoveSet(finalState)[0:2]
    canvas.itemconfig("CALCTEXT", text=f"Found Solution With {movecount} Moves")
    moveLoop()

def moveLoop():
    if len(stateSet) > 0:
        gameBoard.state = stateSet.pop(0)
        update(canvas)
        root.after(300, moveLoop)
    else:
        canvas.itemconfig("CALCTEXT", text="Calculate Best Moves")

        
             
finalState = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]
initState = [
    [2, 1, 6],
    [4, 0, 8],
    [7, 5, 3]
]

initialStates = [
    (  # Initial Configuration 1 (5 moves)
        (2, 8, 3),
        (1, 6, 4),
        (7, 0, 5)
    ),
    (  # Initial Configuration 2 (18 moves)
        (2, 1, 6),
        (4, 0, 8),
        (7, 5, 3)
    ),
    (  # Initial Configuration 3 (21 moves)
        (5, 7, 2),
        (0, 8, 6),
        (4, 1, 3)
    ),
    (  # Initial Configuration 4 (26 moves)
        (0, 6, 5),
        (4, 1, 7),
        (3, 2, 8)
    ),
    (  # Initial Configuration 5 (26 moves)
        (0, 6, 5),
        (4, 1, 8),
        (3, 7, 2)
    ),
    (  # Initial Configuration 6 (27 moves)
        (6, 5, 7),
        (4, 1, 0),
        (3, 2, 8)
    ),
    (  # Initial Configuration 7 (27 moves)
        (6, 5, 7),
        (4, 0, 1),
        (3, 2, 8)
    ),
    (  # Initial Configuration 8 (29 moves, takes a while)
        (6, 5, 7),
        (4, 2, 1),
        (3, 0, 8)
    ),
    (  # Initial Configuration 9 (29 moves)
        (5, 6, 7),
        (0, 4, 8),
        (3, 2, 1)
    ),
    (  # Initial Configuration 10 (30 moves, takes a while)
        (6, 5, 7),
        (4, 2, 1),
        (3, 8, 0)
    ),
    (  # Initial Configuration 11 (30 moves, takes a while)
        (0, 5, 7),
        (6, 4, 1),
        (3, 2, 8)
    ),
    (  # Initial Configuration 12 (30 moves)
        (5, 6, 7),
        (4, 0, 8),
        (3, 2, 1)
    ),
    (  # Initial Configuration 13 (47 moves? 9 moves!)
        (2, 0, 4),
        (1, 3, 5),
        (7, 8, 6)
    )
]

aspect_ratio = 1
margin = 50
data_width = 500
data_height = 500
min_x, min_y = 0,0
max_x, max_y = 0,0
tileCol = "lightblue"
highlight = "SteelBlue1"


canvas_width = data_width + 2 * margin
canvas_height = data_height + 2 * margin

root = tk.Tk()
root.title("8 Puzzle")
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)
tileSize = 100


gameBoard = Board(initState)

def update(canvas):
    for i in range(3):
            for j in range(3):
                canvas.itemconfig(f"tile{i}{j}", fill = "white" if gameBoard.state[j][i]==0 else tileCol)
                canvas.itemconfig(f"text{i}{j}", text = gameBoard.state[j][i])

def redraw(canvas, width, height):
    # Lock aspect ratio
    if width / height > aspect_ratio:
        # Too wide, adjust width
        width = int(height * aspect_ratio)
    else:
        # Too tall, adjust height
        height = int(width / aspect_ratio)
    canvas.config(width=width, height=height)
    canvas.delete("all")

    def get_scaled_pos(x, y):
        sx = (x - min_x)  * tileSize + margin
        sy = (y - min_y)  * tileSize + margin
        return sx, sy

    # Draw Tiles
    for i in range(3):
        for j in range(3):
            col = tileCol
            if gameBoard.state[j][i] == 0:
                col = "white"
            x1, y1 = get_scaled_pos(i, j)
            x2, y2 = get_scaled_pos(i, j)
            x2 +=tileSize
            y2 +=tileSize
            canvas.create_rectangle(x1, y1, x2, y2, fill=col, tags = f"tile{i}{j}")
            canvas.create_text(x1+tileSize/2, y1+tileSize/2, text=gameBoard.state[j][i], font=("Arial", 10), tags=f"text{i}{j}")
    for i in range(13):
        x1,y1= get_scaled_pos(4, i/2)
        x2,y2= get_scaled_pos(4, i/2)
        x2 += tileSize
        y2 += tileSize/2
        canvas.create_rectangle(x1,y1,x2,y2, fill = col, tags = f"button{i}")
        canvas.create_text(x1+tileSize/2, y1+tileSize/4, text=f"Initial Conf {i+1}", font=("Arial", 10))
    
    canvas.create_rectangle(get_scaled_pos(0,3.5), get_scaled_pos(2,4.5), fill = col, tags="CALCULATE")
    canvas.create_text(get_scaled_pos(1,4), text=f"Calculate Best Moves", font=("Arial", 10), tags = "CALCTEXT")
    
def on_canvas_resize(event):
    redraw(canvas, event.width, event.height)

canvas.bind("<Configure>", on_canvas_resize)
canvas.bind("<Button-1>", on_click_tile)
root.mainloop()