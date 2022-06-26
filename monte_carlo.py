from math import sqrt
import pygame
from random import randint
from time import sleep

class Direction:
    directions = []
    def __init__(self, ini_pos):
        self.outbound = False
        self.pos_in = {ini_pos}
        self.added_new_pos_to_discover = True
        self.directions.append(self)

pygame.init()
print("Starting")

SIZE = pygame.display.list_modes()[len(pygame.display.list_modes())//4] #feel free to set any default size you want

screen = pygame.display.set_mode(SIZE)
screen.fill("black")

pygame.display.set_caption("Monte-Carlo Estimator")

clock = pygame.time.Clock()
last_cursor_pos = None

pixels_in_studied_zone = set()

def try_to_fill():
    global pixels_in_studied_zone
    #we will propagate to see if we closed a surface
    mouse_pos = pygame.mouse.get_pos()
    queue = [[mouse_pos, Direction(mouse_pos)]] #[pos, direction]
    saw_pos = {mouse_pos}
    while queue:
        new_queue = []
        for pos, direction in queue:
            if direction.outbound:
                continue #this dir is useless
            for x_vector in range(-1, 2):
                for y_vector in range(-1, 2):
                    new_pos = (pos[0] + x_vector, pos[1] + y_vector)
                    if new_pos not in saw_pos:
                        saw_pos.add(new_pos)
                        try:
                            if screen.get_at(new_pos) != (255, 0, 0, 255): #red color
                                direction.added_new_pos_to_discover = True
                                new_queue.append([new_pos, direction])
                                direction.pos_in.add(pos)
                                screen.set_at(new_pos, "gray")
                        except:
                            #means we are outbound
                            direction.outbound = True
        
        for dir in Direction.directions:
            if not dir.outbound and not dir.added_new_pos_to_discover:
                #we consider that we have a full surface
                #so we set it as outbound to avoid dectect it another time
                dir.outbound = True
                for pos in dir.pos_in:
                    screen.set_at(pos, "red")
                    pixels_in_studied_zone.add(pos)
            dir.added_new_pos_to_discover = False #reinitialisation before each turn

        queue = new_queue
        pygame.display.update()

def draw_mode():
    print("You're in draw mode, you can draw with your mouse\nTo fill an area, press Space with your mouse cursor in the specified area\nOnly the filled pixels will be saved for Monte-Carlo estimation\n*the gray color will disappear*\npress Escape to switch mode")
    global pixels_in_studied_zone
    pixels_in_studied_zone = set()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            try_to_fill()    
        
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if last_cursor_pos and mouse_pos != last_cursor_pos:
                pygame.draw.line(screen, "red", last_cursor_pos, mouse_pos, 2)
            
            last_cursor_pos = mouse_pos
        else:
            last_cursor_pos = None
        
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            break

        pygame.display.update()
        clock.tick(120)

def monte_carlo():
    global screen, SIZE
    print("You're in Monte-Carlo mode, press Escape to switch mode")
    screen.fill("black")
    file = input("Which file do you want to use for Monte-Carlo ? Press enter in the console without writing nothing if you want to use a drawed area\n>>> ")
    if not file:
        for pos in pixels_in_studied_zone:
            screen.set_at(pos, "red")
    else:
        img = pygame.image.load(file)
        #img = pygame.transform.smoothscale(img, SIZE)
        SIZE = (img.get_width(), img.get_height())
        screen = pygame.display.set_mode(SIZE)
        screen.blit(img, (0, 0))
        print("You can draw on the loaded image: Click on a wanted color and then draw\nPress Escape to continue")
        color, last_cursor_pos = None, None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not color:
                    color = screen.get_at(pygame.mouse.get_pos())[:3]
                    print("colo set", color)
                    sleep(0.4)
            
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if last_cursor_pos and color and mouse_pos != last_cursor_pos:
                    pygame.draw.line(screen, color, last_cursor_pos, mouse_pos, 8)
            last_cursor_pos = mouse_pos

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                break
            
            clock.tick(60)
            pygame.display.update()
            

    pygame.display.update()
    print("Please, click on the colors you want to use as the area to scan (like click on red and blue if you want the programm to detect red and blue pixels as in the area)\nPress Escape when you added the different colors")
    sleep(0.5)
    colors = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cur_color = screen.get_at(pygame.mouse.get_pos())[:3]
                colors.append(cur_color)
                print("added color", cur_color)
        
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            break
        clock.tick(60)
    
    colors = tuple(colors)
    print("Trigger colors are", colors)

    print("Let's define the scale, please draw a line that will be the graduation")
    sleep(0.3)
    first_point = None
    screen_copied = screen.copy()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        if pygame.mouse.get_pressed()[0]:
            if not first_point:
                first_point = pygame.mouse.get_pos()
            screen.blit(screen_copied, (0, 0))
            line = pygame.draw.line(screen, "pink", first_point, pygame.mouse.get_pos(), 3)

        elif first_point:
            break
        
        clock.tick(60)
        pygame.display.update()
    distance = float(input("Enter what distance represents this line (in any unit, without specifing it): "))
    scale = distance / sqrt(line.size[0]**2 + line.size[1]**2)
    print("Scale is", scale)
    screen.blit(screen_copied, (0, 0))

    total_nb_points = 0
    in_area_nb_points = 0
    print("Starting simulation\nPress space to add 100 points")
    points_set = {} #point_pos: is_in_the_area

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            for i in range(100):
                rn_pos = (randint(0, SIZE[0]-1), randint(0, SIZE[1]-1))
                total_nb_points += 1
                if screen.get_at(rn_pos) in colors:
                    in_area_nb_points += 1
                    points_set[rn_pos] = True
                elif rn_pos in points_set:
                    if points_set[rn_pos]: in_area_nb_points += 1
                else:
                    points_set[rn_pos] = False

                screen.set_at(rn_pos, "gray")
                if i%10 == 0: pygame.display.update() #we update every 10 points
            pygame.display.update()
            print("We set", total_nb_points, "with", in_area_nb_points, "in so", round(in_area_nb_points/total_nb_points*100, 1), "% points in")
            print("Estimated area:", SIZE[0]*SIZE[1]*scale**2*in_area_nb_points/total_nb_points)
        
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            break

while True:
    key_to_function = {pygame.K_d: draw_mode, pygame.K_e: monte_carlo}
    print(f"---\nWhich mode do you want ? Press in the Pygame window the mode's associated letter\n- Draw mode (from a black screen) (press D)\n- Start a Monte-Carlo estimation from drawed area or file (with a file you'll be able to draw in it before starting estimation) (press E)")
    
    started_func = False
    while not started_func:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        
        pressed_keys = pygame.key.get_pressed()
        for key, func in key_to_function.items():
            if pressed_keys[key]:
                func()
                started_func = True
        clock.tick(60)