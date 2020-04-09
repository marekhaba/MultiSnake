import random

class SnakeHead:
    '''
        Controls all the movement and grid modification done by snake
    '''
    def __init__(self, grid, x=0, y=0, name="s1", color=(0, 155, 0), direc="up"):
        '''
        SnakeHead = grid, x=0, y=0, name="s", direc="up"
        grid is a matrix
        controls: expects a dictionary of key: move. example = {pygame.K_w: "up", ...}
        '''
        self.grid = grid
        self.name = name
        self.color = color
        self.turned_at = [] #(x,y,dir)
        self.segments = [SnakeBody(x, y, direc)]
        self.ate_food = False
        self.dir = direc #for ai
        self.x = x
        self.y = y

        self.grid[x][y] = self.name

    def dir_to_cords(self, direc):
        if direc == "up":
            return (0, -1)
        if direc == "down":
            return (0, 1)
        if direc == "right":
            return (1, 0)
        if direc == "left":
            return (-1, 0)

    def kill(self):
        self.turned_at = []
        self._ate_food = False
        for segment in self.segments:
            self.grid[segment.x][segment.y] = "0"
        x = random.randrange(len(self.grid))
        y = random.randrange(len(self.grid[0]))
        while True:
            if self.grid[x][y] == "0":
                self.grid[x][y] = "f"
                break
            else:
                x = random.randrange(len(self.grid))
                y = random.randrange(len(self.grid[0]))
        self.segments = [SnakeBody(x, y, "up")]

    def move_util(self, dirxy, segment):
        self.grid[segment.x][segment.y] = "0"
        segment.x += dirxy[0]
        segment.y += dirxy[1]
        self.grid[segment.x][segment.y] = self.name #+"h"

    def eval_action(self):
        """
        MUST be called before move()
        """
        self._ate_food = False
        dirxy = self.dir_to_cords(self.segments[0].dir)
        if (self.segments[0].x+dirxy[0] <= -1 or 
            self.segments[0].x+dirxy[0] >= len(self.grid) or
            self.segments[0].y+dirxy[1] <= -1 or
            self.segments[0].y+dirxy[1] >= len(self.grid[0])):
            return (self.name, "death", str(len(self.segments)))
        next_tile = self.grid[self.segments[0].x+dirxy[0]][self.segments[0].y+dirxy[1]]
        if next_tile == "f":
            self._ate_food = True
        elif next_tile != "0":
            return (self.name,"death", str(len(self.segments)))
        return (self.name, "self", (self.segments[0].x+dirxy[0],self.segments[0].y+dirxy[1]))

    def move(self):
        """
        moves the snake, call the eval function FIRST (check this if snake ate food)
        """
        temp_cords = (self.segments[-1].x, self.segments[-1].y) #used only if snake ate food
        for segment in self.segments:
            for turned in self.turned_at:
                if turned[0] == segment.x and turned[1] == segment.y:
                    segment.dir = turned[2]
                    if segment == self.segments[-1]:
                        self.turned_at.pop(0)
                    break
            dirxy = self.dir_to_cords(segment.dir)
            self.move_util(dirxy, segment)
        if self._ate_food:
            self.add_segment(temp_cords)
            return (self.name, "food", len(self.segments))
        self.x = self.segments[0].x
        self.y = self.segments[0].y
        self.dir = self.segments[0].dir
        return (self.name, "self")


    def change_dir(self, direc):
        self.dir = direc
        if self.segments[0].dir in ["left", "right"]:
            if direc in ["left", "right"]:
                return
        if self.segments[0].dir in ["up", "down"]:
            if direc in ["up", "down"]:
                return
        self.turned_at.append((self.segments[0].x, self.segments[0].y, direc))
        self.segments[0].dir = direc
    
    def add_segment(self, cords):
        self.segments.append(SnakeBody(cords[0], cords[1], self.segments[-1].dir))

class SnakeBody:
    def __init__(self, x, y, direc):
        self.x = x
        self.y = y
        self.dir = direc

def spawn_fruit(grid):
    cords = (random.randrange(len(grid)), random.randrange(len(grid[0])))
    while True:
        if grid[cords[0]][cords[1]] == "0":
            grid[cords[0]][cords[1]] = "f"
            return cords
        else:
            cords = (random.randrange(len(grid)), random.randrange(len(grid[0])))
