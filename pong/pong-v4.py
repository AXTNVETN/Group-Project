# PONG pygame
# Original version by Vinoth Pandian
# Modified for lzscc.200 by Marco Caminati
# You might need to install pygame:
# python3 -m pip install --user pygame
# If the command above doesn't work, try venv:
# python3 -m venv ~/pongenv
# source ~/pongenv/bin/activate
# python3 -m pip install pygame

import pygame, random, sys, math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

#colors
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0,0,0)


#globals
WIDTH = 1200
HEIGHT = 1000       
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2

ball_pos = []
ball_pos.append([0, 0])
ball_vel = []
ball_vel.append([0, 0])
paddle1_vel = 0
paddle2_vel = 0
l_score = 0
r_score = 0

ball_count = 1      # counts how many balls are on the screen
ball_bounces = 0    # counts how many bounces took place game-wide
ball_bounces_l = 0  # counts the bounces from theleft paddle
ball_bounces_r = 0  # counts the bounces from the right paddle
ball_spawnrate = 2  # sets how many bounces it takes to spawn an additional ball (default should be 2 I feel like)

BOOST_DURATION_MS = 5000 # amount of time the length boost is active for
BOOST_EXTRA = 200        # the boost length
boost_time_l = None      # time in which
boost_time_r = None 
last_boost_l = 0         # the last boost's activation bounce count
last_boost_r = 0


     
#canvas declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('F L O F')

# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
# "i" is the index of the ball
def ball_init(right, i):
    global ball_pos, ball_vel # these are vectors stored as lists
    ball_pos[i] = [WIDTH//2,HEIGHT//2]
    horz = random.randrange(2,4)
    vert = random.randrange(1,3)
    
    if right == False:
        horz = - horz
        
    ball_vel[i] = [horz,-vert]

def ball_add(right):

    global ball_pos, ball_vel, ball_count # these are vectors stored as lists
    print("A new ball has appeared!")
    ball_count += 1
    for i, ball in enumerate(ball_pos):
        if len(ball) == 1:
            ball_init(right, i)
            return
    ball_pos.append([0, 0])
    ball_pos[len(ball_pos) - 1] = [WIDTH//2,HEIGHT//2]
    horz = random.randrange(2,4)
    vert = random.randrange(1,3)
    
    if right == False:
        horz = - horz
    ball_vel.append([0, 0])
    ball_vel[len(ball_pos) - 1] = [horz,-vert]


# define event handlers
def init():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, l_score, r_score, START_TIME, colour_inv
    global score1, score2  # these are ints
    paddle1_pos = [HALF_PAD_WIDTH - 1,HEIGHT//2]
    paddle2_pos = [WIDTH +1 - HALF_PAD_WIDTH,HEIGHT//2]
    l_score = 0
    r_score = 0
    colour_inv = False # colour inversion


    START_TIME = pygame.time.get_ticks()
    
    if random.randrange(0,2) == 0:
        ball_init(True, 0)
    else:
        ball_init(False, 0)


#draw function of canvas
def draw(canvas):
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, ball_count, ball_bounces, ball_bounces_l, ball_bounces_r
    global l_score, r_score, boost_time_l, boost_time_r, last_boost_l, last_boost_r, colour_inv
    
    elapsed_time = pygame.time.get_ticks()

    dh =  (elapsed_time - START_TIME) // 1000
        

    if (dh // 5) % 2 == 0:
        colour_inv = False
        canvas.fill(BLACK)
        pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0],[WIDTH // 2, HEIGHT], 1)
        pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1)
        pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1)
        pygame.draw.circle(canvas, WHITE, [WIDTH//2, HEIGHT//2], 70, 1)

    else: 
        colour_inv = True
        canvas.fill(WHITE)
        pygame.draw.line(canvas, BLACK, [WIDTH // 2, 0],[WIDTH // 2, HEIGHT], 2)
        pygame.draw.line(canvas, BLACK, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 2)
        pygame.draw.line(canvas, BLACK, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 2)
        pygame.draw.circle(canvas, BLACK, [WIDTH//2, HEIGHT//2], 70, 2)
    
        # Trigger boost once at bounces 3, 6, 9, ...
    if (ball_bounces_l % 3 == 0) and (ball_bounces_l != 0) and (boost_time_l != elapsed_time):
        boost_time_l = elapsed_time
        # last_boost_l = ball_bounces_l

    if (ball_bounces_r % 3 == 0) and (ball_bounces_r != 0) and (last_boost_r != ball_bounces_r):
        boost_time_r = elapsed_time
        # last_boost_r = ball_bounces_r

    # Is boost active?
    l_boost_active = (boost_time_l is not None) and (elapsed_time - boost_time_l) < BOOST_DURATION_MS
    r_boost_active = (boost_time_r is not None) and (elapsed_time - boost_time_r) < BOOST_DURATION_MS

    # Paddle sizes for this frame
    l_New_HALF_PAD_HEIGHT = HALF_PAD_HEIGHT + (BOOST_EXTRA if l_boost_active else 0)
    r_New_HALF_PAD_HEIGHT = HALF_PAD_HEIGHT + (BOOST_EXTRA if r_boost_active else 0)

    # update paddle's vertical position, keep paddle on the screen
    if paddle1_pos[1] > l_New_HALF_PAD_HEIGHT and paddle1_pos[1] < HEIGHT - l_New_HALF_PAD_HEIGHT:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == l_New_HALF_PAD_HEIGHT and paddle1_vel > 0:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == HEIGHT - l_New_HALF_PAD_HEIGHT and paddle1_vel < 0:
        paddle1_pos[1] += paddle1_vel
    
    if paddle2_pos[1] > r_New_HALF_PAD_HEIGHT and paddle2_pos[1] < HEIGHT - r_New_HALF_PAD_HEIGHT:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == r_New_HALF_PAD_HEIGHT and paddle2_vel > 0:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == HEIGHT - r_New_HALF_PAD_HEIGHT and paddle2_vel < 0:
        paddle2_pos[1] += paddle2_vel

    paddle1_pos[1] = max(l_New_HALF_PAD_HEIGHT, min(paddle1_pos[1], HEIGHT - l_New_HALF_PAD_HEIGHT))
    paddle2_pos[1] = max(r_New_HALF_PAD_HEIGHT, min(paddle2_pos[1], HEIGHT - r_New_HALF_PAD_HEIGHT))


    i = 0
    #update ball
    while i < len(ball_pos):


        #print("pos:", ball_pos,"vel:", ball_vel, "count:", ball_cont, "len of pos vec:", len(ball_pos[i]))        #DEBUG
        if len(ball_pos[i]) == 1:
            i += 1
            continue
        
        ball_pos[i][0] += int(ball_vel[i][0])
        ball_pos[i][1] += int(ball_vel[i][1])

        #draw paddles and ball
        if not colour_inv:
            pygame.draw.circle(canvas, RED, ball_pos[i], 20, 0)
            pygame.draw.polygon(canvas, GREEN, [[paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] + l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] + l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] - l_New_HALF_PAD_HEIGHT]], 0)
            pygame.draw.polygon(canvas, GREEN, [[paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] + r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] + r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] - r_New_HALF_PAD_HEIGHT]], 0)

        else:
            pygame.draw.circle(canvas, (245,212,66), ball_pos[i], 20, 0)
            pygame.draw.polygon(canvas, (13, 43, 2), [[paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] + l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] + l_New_HALF_PAD_HEIGHT], [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] - l_New_HALF_PAD_HEIGHT]], 0)
            pygame.draw.polygon(canvas, (13, 43, 2), [[paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] + r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] + r_New_HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] - r_New_HALF_PAD_HEIGHT]], 0)

        
        #ball collision check on top and bottom walls
        if int(ball_pos[i][1]) <= BALL_RADIUS:
            ball_vel[i][1] = - ball_vel[i][1]
        if int(ball_pos[i][1]) >= HEIGHT + 1 - BALL_RADIUS:
            ball_vel[i][1] = -ball_vel[i][1]
        
        #ball collison check on gutters or paddles
        # left paddle
        if int(ball_pos[i][0]) <= BALL_RADIUS + PAD_WIDTH and int(ball_pos[i][1]) in range(paddle1_pos[1] - l_New_HALF_PAD_HEIGHT,paddle1_pos[1] + l_New_HALF_PAD_HEIGHT,1):
            ball_vel[i][0] = -ball_vel[i][0]
            ball_vel[i][0] *= 1.1
            ball_vel[i][1] *= 1.1
            #print("bounces:", ball_bounces, "spawnrate:", ball_spawnrate, "result:", (ball_bounces + 1) % ball_spawnrate)      #DEBUG
            # spawning balls according to spawnrate
            if (ball_bounces_l + 1) % ball_spawnrate == 0:
                ball_add(True)
            ball_bounces += 1
            ball_bounces_l += 1


        elif int(ball_pos[i][0]) <= BALL_RADIUS + PAD_WIDTH:
            r_score += 1
            if ball_count == 1:
                ball_init(True, i)
            else:
                #print("LEFT COLLISION    vel:", ball_vel[i], "pos:", ball_pos[i])      #DEBUG
                ball_vel[i].pop()
                ball_pos[i].pop()
                ball_count -= 1
                continue


        # right paddle
        if int(ball_pos[i][0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[i][1]) in range(paddle2_pos[1] - r_New_HALF_PAD_HEIGHT,paddle2_pos[1] + r_New_HALF_PAD_HEIGHT,1):
            ball_vel[i][0] = -ball_vel[i][0]
            ball_vel[i][0] *= 1.1
            ball_vel[i][1] *= 1.1
            #print("bounces:", ball_bounces, "spawnrate:", ball_spawnrate, "result:", (ball_bounces + 1) % ball_spawnrate)      #DEBUG
            # spawning balls according to spawnrate
            if (ball_bounces_r + 1) % ball_spawnrate == 0:
                ball_add(False)
            ball_bounces += 1
            ball_bounces_r += 1


        elif int(ball_pos[i][0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
            l_score += 1
            if ball_count == 1:
                ball_init(False, i)
            else:
                #print("RIGHT COLLISION    vel:", ball_vel[i], "pos:", ball_pos[i])     #DEBUG
                ball_vel[i].pop()
                ball_pos[i].pop()
                ball_count -= 1
                continue
        i += 1

    if not colour_inv:
        score_colour = (255,255,0)
    else:
        score_colour = (245,66,66)

    #update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", WIDTH//20)
    label1 = myfont1.render("Score "+str(l_score), 1, score_colour)
    canvas.blit(label1, (WIDTH/10,HEIGHT/10))

    myfont2 = pygame.font.SysFont("Comic Sans MS", WIDTH//20)
    label2 = myfont2.render("Score "+str(r_score), 1, score_colour)
    canvas.blit(label2, (WIDTH/1.8, HEIGHT/10))  
    
    
#keydown handler
def keydown(event):
    global paddle1_vel, paddle2_vel
    
    if event.key == K_UP:
        paddle2_vel = -10
    elif event.key == K_DOWN:
        paddle2_vel = 10
    elif event.key == K_w:
        paddle1_vel = -10
    elif event.key == K_s:
        paddle1_vel = 10

#keyup handler
def keyup(event):
    global paddle1_vel, paddle2_vel
    
    if event.key in (K_w, K_s):
        paddle1_vel = 0
    elif event.key in (K_UP, K_DOWN):
        paddle2_vel = 0

init()


#game loop
while True:

    draw(window)
    #print(fps, l_score, r_score)       #DEBUG
    for event in pygame.event.get():
        
        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == KEYUP:
            keyup(event)
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fps.tick(60)
