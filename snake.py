import pygame
from snake_base import SnakeHead, spawn_fruit
import pygamegui as pg

TILE_SIZE = 20
TILE_AMOUNT = 40
WINDOW_SIZE = (TILE_SIZE*TILE_AMOUNT, TILE_SIZE*TILE_AMOUNT)

class Game:
    """
    Some Snake
    """
    def __init__(self, screen, snake_bars=None):
        self.screen = screen
        self.grid = [['0' for x in range(TILE_AMOUNT)] for y in range(TILE_AMOUNT)]
        self.snakes = {"s1":SnakeHead(self.grid, 20, 20)} if snake_bars is None else {}#name: SnakeHead(self.grid, 20, 20)
        self.controls = {pygame.K_w: ("s1", "up"), pygame.K_s: ("s1", "down"), pygame.K_d: ("s1", "right"), pygame.K_a: ("s1", "left")} if snake_bars is None else {}#pygame.K_?: (name, direc)
        self.simple_ai_snake = []
        self.get_snakes(snake_bars)
        self.clock = pygame.time.Clock()#Controls framerate
        self.COLORS = {
            "bg": (10, 10, 10),
            "f": (155, 0, 0)
        }
        #self.score_menu = pg.Menu(self.screen, color_bg=(0,0,0,0))
        self.score_labels = {}
        self.create_score_labels()
        self.food_loc = spawn_fruit(self.grid)

    def create_score_labels(self):
        score_x_offset = 50
        if len(self.snakes) == 1:
            x_inc = (WINDOW_SIZE[0]-score_x_offset*2)//2
        else:
            x_inc = (WINDOW_SIZE[0]-score_x_offset*2)//(len(self.snakes)-1)
        i = 0
        for snake in self.snakes.values():
            x = x_inc*i + score_x_offset
            i += 1
            y = 15
            self.score_labels[snake.name] = pg.Label(self.screen, x, y, "0", text_color=snake.color, text_bold=True)

    def get_snakes(self, snake_bars):
        for snake_bar in snake_bars:
            self.snakes[snake_bar.name] = SnakeHead(self.grid, snake_bar.start[0], snake_bar.start[1], snake_bar.name, snake_bar.color)
            if snake_bar.mode == "player":
                self.controls[snake_bar.keys[0].key] = (snake_bar.name, "left")
                self.controls[snake_bar.keys[1].key] = (snake_bar.name, "up")
                self.controls[snake_bar.keys[2].key] = (snake_bar.name, "down")
                self.controls[snake_bar.keys[3].key] = (snake_bar.name, "right")
            elif snake_bar.mode == "simple_ai":
                self.simple_ai_snake.append(snake_bar.name)

    def draw(self):
        self.screen.fill(self.COLORS["bg"])
        for y in range(TILE_AMOUNT):
            for x in range(TILE_AMOUNT):
                tile = self.grid[x][y]
                if tile in self.snakes:
                    pygame.draw.rect(self.screen, self.snakes[tile].color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if tile == "f":
                    pygame.draw.rect(self.screen, self.COLORS["f"], (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def check_events(self): #+ai
        events = pygame.event.get()
        _return = "self"
        _moved = {key:False for key in self.snakes}
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key not in self.controls:
                    continue
                _name, _dir = self.controls[event.key]
                if _moved[_name] is False:
                    self.snakes[_name].change_dir(_dir)
                    _moved[_name] = True
        for snake_name in self.simple_ai_snake:
            self.simple_ai(self.snakes[snake_name])
        return _return

    def update(self):
        result = self.check_events()
        snake_events = []
        snakes = self.snakes.values()
        for snake in snakes:
            snake_events.append(snake.eval_action())
        next_tiles = {}
        for event in snake_events:
            if event[1] == "death":
                self.snakes[event[0]].kill()
                self.score_labels[event[0]].set_text("0")
            else:
                if event[2] in next_tiles:
                    self.snakes[event[0]].kill()
                    self.score_labels[event[0]].set_text("0")
                    self.snakes[next_tiles[event[2]]].kill()
                    self.score_labels[next_tiles[event[2]]].set_text("0")

                else:
                    next_tiles[event[2]] = event[0]
        snake_events = []
        for snake in snakes:
            snake_events.append(snake.move())
        for event in snake_events:
            if event[1] == "food":
                self.food_loc = spawn_fruit(self.grid)
                self.score_labels[event[0]].set_text(str(event[2]-1))
                if int(event[2]) > 10:
                    return event
        self.draw()
        for widget in self.score_labels.values():
            widget.draw()
        pygame.display.update()
        self.clock.tick(10)
        return result

    def simple_ai_util_up_down(self, snake):
        if snake.x < self.food_loc[0] and snake.x < len(self.grid)-1 and self.grid[snake.x+1][snake.y] == "0":
            snake.change_dir("right")
            return
        if snake.x > -1 and self.grid[snake.x-1][snake.y] == "0":
            snake.change_dir("left")
            return
        if snake.x < len(self.grid)-1 and self.grid[snake.x+1][snake.y] == "0":
            snake.change_dir("right")
            return

    def simple_ai_util_left_right(self, snake):
        if snake.y < self.food_loc[1] and snake.y < len(self.grid[0])-1 and self.grid[snake.x][snake.y+1] == "0":
            snake.change_dir("down")
            return
        if snake.y > 0 and self.grid[snake.x][snake.y-1] == "0":
            snake.change_dir("up")
            return
        if snake.y < len(self.grid[0])-1 and self.grid[snake.x][snake.y+1] == "0":
            snake.change_dir("down")
            return

    def simple_ai(self, snake):
        if snake.dir == "up":
            if snake.y == self.food_loc[1]:
                if snake.x < self.food_loc[0]:
                    snake.change_dir("right")
                else:
                    snake.change_dir("left")
            elif snake.y < self.food_loc[1]:
                self.simple_ai_util_up_down(snake)
            elif self.grid[snake.x][snake.y-1] not in ["0", "f"]:
                self.simple_ai_util_up_down(snake)
        elif snake.dir == "down":
            if snake.y == self.food_loc[1]:
                if snake.x < self.food_loc[0]:
                    snake.change_dir("right")
                else:
                    snake.change_dir("left")
            elif snake.y > self.food_loc[1]:
                self.simple_ai_util_up_down(snake)
            elif self.grid[snake.x][snake.y+1] not in ["0", "f"]:
                self.simple_ai_util_up_down(snake)
        elif snake.dir == "right":
            if snake.x == self.food_loc[0]:
                if snake.y > self.food_loc[1]:
                    snake.change_dir("up")
                else:
                    snake.change_dir("down")
            elif snake.x > self.food_loc[0]:
                self.simple_ai_util_left_right(snake)
            elif self.grid[snake.x+1][snake.y] not in ["0", "f"]:
                self.simple_ai_util_left_right(snake)
        elif snake.dir == "left":
            if snake.x == self.food_loc[0]:
                if snake.y > self.food_loc[1]:
                    snake.change_dir("up")
                else:
                    snake.change_dir("down")
            elif snake.x < self.food_loc[0]:
                self.simple_ai_util_left_right(snake)
            elif self.grid[snake.x-1][snake.y] not in ["0", "f"]:
                self.simple_ai_util_left_right(snake)


class SnakeBar:
    """
    Info about a snake. has height of 100px
    """
    def __init__(self, menu, y, name, color, def_keys, start):
        self.menu = menu
        self.y = y
        self.name = name
        self.color = color
        self.def_keys = def_keys
        self.start = start
        self.height = 100
        self.widgets = []
        self.widgets.append(pg.Rectangle(menu, TILE_SIZE*2, y+(self.height-TILE_SIZE)//2, TILE_SIZE, TILE_SIZE, color))
        self.widgets.append(pg.Rectangle(menu, TILE_SIZE*3, y+(self.height-TILE_SIZE)//2, TILE_SIZE, TILE_SIZE, color))
        self.widgets.append(pg.Rectangle(menu, TILE_SIZE*4, y+(self.height-TILE_SIZE)//2, TILE_SIZE, TILE_SIZE, color))

        keybind_start = 550
        keybind_width, keybind_height = 60, 40
        offset = (self.height-keybind_height*2)//2
        self.keys = []
        self.keys.append(pg.KeyBind(menu, keybind_start, y+offset+keybind_height, keybind_width, keybind_height, def_key=self.def_keys[0]))
        self.keys.append(pg.KeyBind(menu, keybind_start+keybind_width, y+offset, keybind_width, keybind_height, def_key=self.def_keys[1]))
        self.keys.append(pg.KeyBind(menu, keybind_start+keybind_width, y+offset+keybind_height, keybind_width, keybind_height, def_key=self.def_keys[2]))
        self.keys.append(pg.KeyBind(menu, keybind_start+keybind_width*2, y+offset+keybind_height, keybind_width, keybind_height, def_key=self.def_keys[3]))

        mode_start = 200
        mode_width, mode_height = 120, 40
        offset = (self.height-mode_height)//2
        self.player = pg.Button(menu, mode_start, y+offset, mode_width, mode_height, lambda: self.disable_modes("player"), text="Player")
        self.simple_ai = pg.Button(menu, mode_start+mode_width, y+offset, mode_width, mode_height, lambda: self.disable_modes("simple_ai"), text="Simple 'AI'")
        self.disable_modes("player")

    def remove(self):
        for widget in self.widgets:
            self.menu.remove_widget(widget)
        for key in self.keys:
            self.menu.remove_widget(key)
        self.menu.remove_widget(self.player)
        self.menu.remove_widget(self.simple_ai)
        del self.menu
        
    def disable_modes(self, mode):
        self.mode = mode
        if self.mode == "player":
            self.player.state = "disabled"
            for key in self.keys:
                key.state = "normal"
            self.simple_ai.state = "normal"
        elif self.mode == "simple_ai":
            self.simple_ai.state = "disabled"
            self.player.state = "normal"
            for key in self.keys:
                key.state = "disabled"

def create_snake_bar(snake_bars, menu):
    #A lot of placeholder shit should be changed
    if len(snake_bars) == 4:
        return
    colors = [(0, 150, 0), (150, 25, 50), (150, 75, 0), (75, 150, 75)]
    names = ["s1", "s2", "s3", "s4"]
    starts = [(10, 15), (30, 15), (15, 30), (25, 30)]
    y = snake_bars[-1].y + 100 if snake_bars != [] else 250
    def_keys = [(pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_d),
                (pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT),
                (pygame.K_j, pygame.K_i, pygame.K_k, pygame.K_l),
                (pygame.K_KP1, pygame.K_KP5, pygame.K_KP2, pygame.K_KP3)]

    snake_bars.append(SnakeBar(menu, y, names[len(snake_bars)], colors[len(snake_bars)], def_keys[len(snake_bars)], starts[len(snake_bars)]))

def remove_snake_bar(snake_bars):
    if len(snake_bars) <= 1:
        return
    snake_bars[-1].remove()
    del snake_bars[-1]

def game():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Multi Snake')

    snake_theme = pg.Theme(text_color=(0, 155, 0))
    start_menu = pg.Menu(screen, snake_theme, (10, 10, 10))
    pg.Label(start_menu, 415, 100, "Snake", text_size=75, text_anchor="W")
    pg.Label(start_menu, 385, 100, 'Multi', text_size=75, text_anchor="E", text_color=(150, 25, 50))
    snake_bars = []
    create_snake_bar(snake_bars, start_menu)
    pg.Button(start_menu, 50, 175, 175, 50, lambda: create_snake_bar(snake_bars, start_menu), text="Add Snake")
    pg.Button(start_menu, 575, 175, 175, 50, lambda: remove_snake_bar(snake_bars), text="Remove Snake")
    pg.Button(start_menu, 300, 675, 200, 100, "start", text="Start")

    active_screen = start_menu
    done = False
    while not done:
        result = active_screen.update()
        if result == "start":
            active_screen = Game(screen, snake_bars)
        elif result == 'quit':
            done = True
        elif result == "menu":
            active_screen = start_menu
        elif isinstance(result, tuple):
            end_menu = pg.Menu(screen, snake_theme, (10, 10, 10))
            pg.Label(end_menu, 500, 300, "won", text_size=75, text_color=active_screen.snakes[result[0]].color)
            pg.Button(end_menu, 150, 600, 200, 100, "start", text="Restart")
            pg.Button(end_menu, 450, 600, 200, 100, "menu", text="Menu")
            #pg.Label(end_menu, 400, 450, f"Score: {result[2]-1}", text_color=active_screen.snakes[result[0]].color)
            pg.Label(end_menu, 300, 300, result[0], text_size=75, text_color=active_screen.snakes[result[0]].color)
            active_screen = end_menu
    pygame.quit()

if __name__ == "__main__":
    game()
