import pygame
from random import randint
from numpy import sqrt

pygame.init()

# COLOR CONSTANTS
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
GRAY = (40, 40, 40)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (60, 60, 60)
WALL_COLOR = (25, 25, 35)
TRANSPARENT_BLACK = (0, 0, 0, 180)

# GRID SETTINGS

cols = 25
rows = 25

width = 700     
height = 700

wr = width / cols
hr = height / rows

screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Snake Game - Manual & AI Accuracy")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Arial", 48, bold=True)
font_small = pygame.font.SysFont("Arial", 26, bold=True)
font_menu = pygame.font.SysFont("Arial", 32, bold=True)
font_pause = pygame.font.SysFont("Arial", 56, bold=True)

# SPOT CLASS FOR PATHFINDING
# ==========================================================
class Spot:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.is_wall = False
        self.neighbors = []
        self.f = self.g = self.h = 0
        self.camefrom = None

    def add_neighbors(self, grid):
        if self.x > 0: self.neighbors.append(grid[self.x - 1][self.y])
        if self.x < rows - 1: self.neighbors.append(grid[self.x + 1][self.y])
        if self.y > 0: self.neighbors.append(grid[self.x][self.y - 1])
        if self.y < cols - 1: self.neighbors.append(grid[self.x][self.y + 1])

    def show(self, color, head=False):
        if self.is_wall:
            pygame.draw.rect(screen, WALL_COLOR, pygame.Rect(self.x * hr, self.y * wr, hr, wr))
            return

        rect = pygame.Rect(self.x*hr + 2, self.y*wr + 2, hr - 4, wr - 4)
        if head:
            pygame.draw.ellipse(screen, color, rect)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=6)


# build grid
grid = [[Spot(i, j) for j in range(cols)] for i in range(rows)]
for r in grid:
    for c in r:
        c.add_neighbors(grid)

# WALL GENERATOR
# ==========================================================
def create_walls():
    for r in grid:
        for c in r:
            c.is_wall = False

    walls = [
        (4,4),(5,4),(4,5),(5,5),
        (4,cols-5),(5,cols-5),(4,cols-6),(5,cols-6),
        (rows-5,4),(rows-6,4),(rows-5,5),(rows-6,5),
        (rows-5,cols-5),(rows-6,cols-5),(rows-5,cols-6),(rows-6,cols-6),
        (12,8),(12,9),(12,10),(12,11),(12,12),(12,13),(12,14),(12,15),(12,16)
    ]
    for x,y in walls:
        grid[x][y].is_wall = True

# A* PATHFINDING
def getpath(food, snake):
    for r in grid:
        for c in r:
            c.g = c.h = c.f = 0
            c.camefrom = None

    start = snake[-1]
    openset = [start]
    closed = []

    while openset:
        current = min(openset, key=lambda x:x.f)

        if current == food:
            path = []
            t = current
            while t:
                path.append(t)
                t = t.camefrom
            return path[::-1]

        openset.remove(current)
        closed.append(current)

        for nb in current.neighbors:
            if nb in closed or nb in snake[:-1] or nb.is_wall:
                continue

            tempg = current.g + 1
            new_path = False

            if nb not in openset:
                openset.append(nb)
                new_path = True
            elif tempg < nb.g:
                new_path = True

            if new_path:
                nb.g = tempg
                nb.h = sqrt((nb.x - food.x)**2 + (nb.y - food.y)**2)
                nb.f = nb.g + nb.h
                nb.camefrom = current

    return []

def get_dir_from_path(path):
    if len(path) < 2:
        return []
    dirs = []
    for i in range(len(path)-1):
        a, b = path[i], path[i+1]
        if b.y < a.y: dirs.append(2)
        elif b.y > a.y: dirs.append(0)
        elif b.x < a.x: dirs.append(3)
        elif b.x > a.x: dirs.append(1)
    return dirs

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================
def spawn_food(snake):
    while True:
        f = grid[randint(0,rows-1)][randint(0,cols-1)]
        if f not in snake and not f.is_wall:
            return f

def draw_background():
    screen.fill(GRAY)
    for i in range(rows):
        for j in range(cols):
            rect = pygame.Rect(i*hr, j*wr, hr, wr)
            pygame.draw.rect(screen, DARK_GRAY if (i+j)%2==0 else LIGHT_GRAY, rect)

# ==========================================================
# INSTRUCTIONS SCREEN
# ==========================================================
def instruction_screen():
    while True:
        draw_background()

        title = font_big.render("HOW TO PLAY", True, GREEN)
        screen.blit(title, title.get_rect(center=(width/2,80)))

        lines = [
            "Manual Mode: Arrow Keys / WASD to Move",
            "AI Mode: Snake automatically follows shortest path",
            "P = Pause",
            "",
            "ACCURACY SYSTEM:",
            "Live Accuracy = current food efficiency",
            "Total Accuracy = whole game efficiency",
            
            "",
            "GAME MODES:",
            "Classic: No walls (wrap-around)",
            "Arcade: Walls enabled (collision = death)",
        ]

        y = 170
        for line in lines:
            t = font_small.render(line, True, WHITE)
            screen.blit(t, (60, y))
            y += 32

        cont = font_menu.render("Press ENTER to continue", True, YELLOW)
        screen.blit(cont, cont.get_rect(center=(width/2, height-70)))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return True

# ==========================================================
# START MENU
# ==========================================================
def start_screen():
    if not instruction_screen(): return None, None

    mode = "manual"
    wall_mode = False
    menu_state = "player"

    while True:
        draw_background()

        title = font_big.render("Snake Game", True, GREEN)
        screen.blit(title, title.get_rect(center=(width/2,120)))

        indicator = font_menu.render(">", True, GREEN)

        if menu_state == "player":
            header = font_menu.render("Select Mode", True, WHITE)
            screen.blit(header, header.get_rect(center=(width/2,220)))

            m = font_menu.render("Manual Play", True, WHITE)
            a = font_menu.render("AI Play", True, WHITE)

            mr = m.get_rect(center=(width/2,300))
            ar = a.get_rect(center=(width/2,350))

            screen.blit(indicator, indicator.get_rect(midright=(mr.midleft if mode=="manual" else ar.midleft)))
            screen.blit(m, mr)
            screen.blit(a, ar)

        elif menu_state == "style":
            header = font_menu.render("Select Style", True, WHITE)
            screen.blit(header, header.get_rect(center=(width/2,220)))

            c = font_menu.render("Classic (No Walls)", True, YELLOW)
            arc = font_menu.render("Arcade (Walls)", True, RED)

            cr = c.get_rect(center=(width/2,300))
            ar = arc.get_rect(center=(width/2,350))

            screen.blit(indicator, indicator.get_rect(midright=(ar.midleft if wall_mode else cr.midleft)))
            screen.blit(c, cr)
            screen.blit(arc, ar)

        inst = font_small.render("Use UP/DOWN and ENTER", True, WHITE)
        screen.blit(inst, inst.get_rect(center=(width/2, height-60)))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None, None

            if e.type == pygame.KEYDOWN:
                if menu_state == "player":
                    if e.key in [pygame.K_UP, pygame.K_DOWN]:
                        mode = "auto" if mode=="manual" else "manual"
                    if e.key == pygame.K_RETURN:
                        menu_state = "style"

                elif menu_state == "style":
                    if e.key in [pygame.K_UP, pygame.K_DOWN]:
                        wall_mode = not wall_mode
                    if e.key == pygame.K_RETURN:
                        return mode, wall_mode

# ==========================================================
# PAUSE
# ==========================================================
def pause_screen():
    overlay = pygame.Surface((width,height), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay,(0,0))

    t = font_pause.render("PAUSED", True, WHITE)
    screen.blit(t, t.get_rect(center=(width/2,height/2 - 40)))

    r = font_small.render("ENTER = Resume", True, GREEN)
    q = font_small.render("Q = Quit to Menu", True, YELLOW)

    screen.blit(r, r.get_rect(center=(width/2,height/2 + 20)))
    screen.blit(q, q.get_rect(center=(width/2,height/2 + 60)))

    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: return "resume"
                if e.key == pygame.K_q: return "quit"

# ==========================================================
# GAME OVER
# ==========================================================
def game_over_screen(score, total_acc):
    while True:
        draw_background()

        t = font_big.render("GAME OVER", True, RED)
        screen.blit(t, t.get_rect(center=(width/2,200)))

        s = font_small.render(f"Score: {score}", True, WHITE)
        screen.blit(s, s.get_rect(center=(width/2,260)))

        if total_acc is not None:
            acc = font_small.render(f"Total Accuracy: {total_acc:.1f}%", True, GREEN)
            screen.blit(acc, acc.get_rect(center=(width/2,300)))

        r = font_small.render("Press ENTER to Restart", True, YELLOW)
        q = font_small.render("Press Q to Quit", True, WHITE)

        screen.blit(r, r.get_rect(center=(width/2,360)))
        screen.blit(q, q.get_rect(center=(width/2,400)))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: return True
                if e.key == pygame.K_q: return False

# ==========================================================
# MAIN GAME LOOP
# ==========================================================
def main():
    while True:
        res = start_screen()
        if res is None:
            break

        mode, wall_mode = res

        # Apply wall mode
        if wall_mode: create_walls()
        else:
            for r in grid:
                for c in r:
                    c.is_wall = False

        snake = [grid[rows//2][cols//2]]
        food = spawn_food(snake)

        score = 0
        speed = 7
        direction = 1

        # Accurate accuracy tracking
        total_optimal = 0
        total_actual = 0

        current_optimal = 0
        current_actual = 0

        # First optimal path
        path = getpath(food, snake)
        if path:
            current_optimal = len(path) - 1

        dir_array = get_dir_from_path(path) if mode=="auto" else []

        running = True
        died = False

        while running:
            clock.tick(speed)
            draw_background()

            # ========================
            # AI movement
            # ========================
            if mode == "auto":
                if not dir_array:
                    path = getpath(food, snake)
                    if not path:
                        died = True; running = False; break

                    current_optimal = len(path)-1
                    current_actual = 0
                    dir_array = get_dir_from_path(path)

                if dir_array:
                    direction = dir_array.pop(0)

            # ========================
            # INPUT (manual)
            # ========================
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE: pygame.quit(); return
                    if e.key == pygame.K_p:
                        if pause_screen()=="quit":
                            running = False; died=False

                    if mode == "manual":
                        if e.key in [pygame.K_DOWN,pygame.K_s] and direction!=2: direction=0
                        elif e.key in [pygame.K_RIGHT,pygame.K_d] and direction!=3: direction=1
                        elif e.key in [pygame.K_UP,pygame.K_w] and direction!=0: direction=2
                        elif e.key in [pygame.K_LEFT,pygame.K_a] and direction!=1: direction=3

            if not running: continue

            # MOVE SNAKE
            nx, ny = snake[-1].x, snake[-1].y
            if direction==0: ny+=1
            elif direction==1: nx+=1
            elif direction==2: ny-=1
            elif direction==3: nx-=1

            if wall_mode:
                if not (0<=nx<rows and 0<=ny<cols):
                    died=True; running=False; continue
            else:
                nx%=rows
                ny%=cols

            new_cell = grid[nx][ny]

            if new_cell.is_wall or new_cell in snake:
                died=True; running=False; continue

            snake.append(new_cell)
            current_actual += 1

            # FOOD EATING
            if new_cell == food:
                score += 1
                food = spawn_food(snake)

                if score % 5 == 0: speed += 1

                total_optimal += current_optimal
                total_actual += current_actual

                path = getpath(food, snake)
                if path:
                    current_optimal = len(path)-1
                else:
                    current_optimal = 0

                current_actual = 0

                if mode=="auto":
                    dir_array = get_dir_from_path(path)
            else:
                snake.pop(0)

            # DRAWING
            for r in grid:
                for c in r:
                    if c.is_wall:
                        c.show(WALL_COLOR)

            for s in snake:
                s.show(BLUE)
            snake[-1].show(GREEN, head=True)
            food.show(RED)

            # Score Text
            t = font_small.render(f"Score: {score}  Speed: {speed}", True, WHITE)
            screen.blit(t, (10, 10))

            # ---------------- Live Accuracy ----------------
            if current_optimal > 0:
                if current_actual >= current_optimal:
                    live_acc = (current_optimal / current_actual) * 100
                else:
                    live_acc = 100.0
            else:
                live_acc = 100.0

            live_txt = font_small.render(f"Live Accuracy: {live_acc:.1f}%", True, YELLOW)
            screen.blit(live_txt, (10, 45))

            # ---------------- Total Accuracy ----------------
            if total_actual > 0:
                total_acc = (total_optimal / total_actual) * 100
            else:
                total_acc = 100.0

            tot_txt = font_small.render(f"Total Accuracy: {total_acc:.1f}%", True, GREEN)
            screen.blit(tot_txt, (10, 80))

            pygame.display.flip()

        # GAME OVER
        if died:
            if total_actual > 0:
                total_accuracy = (total_optimal/total_actual)*100
            else:
                total_accuracy = None

            if not game_over_screen(score, total_accuracy):
                break

# RUN GAME
if __name__ == "__main__":
    main()
    pygame.quit()
