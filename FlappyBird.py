'''

Practice Project: Teaching an AI to Play Flappy Bird using an Evolutionary Algorithm
Watts Dietrich
Nov 9 2020

In this practice project, the evolutionary AI algorithm called NEAT (NeuroEvolution of Augmenting Topologies)
is used to teach an AI to play the game "Flappy Bird." See the readme for more info.

'''

import pygame
import neat
import time
import os
import random
pygame.font.init()

# Set window size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Get images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Font for the score
STAT_FONT = pygame.font.SysFont("comicsans", 50)

GEN = 0

class Bird:
    # Define some constants
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # This defines the mas degrees that the bird image can rotate while going up or down
    ROT_VEL = 20  # Rotation velocity: how much the bird can rotate per frame of animation
    ANIMATION_TIME = 5  # How long each animation will take

    def __init__(self, x, y):
        # Define initial conditions of the bird
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # jump() is what happens when the bird jumps upward
    def jump(self):
        self.vel = -10.5  # Note: in pygame, the top-left window corner is (0,0), so to go up, a negative vel is needed
        self.tick_count = 0  # Reset the counter that keeps track of when the last jump occurred
        self.height = self.y  # The starting height of the jump

    # move() is called each frame to move the bird
    def move(self):
        self.tick_count += 1  # increment the tick_count (time since last jump)

        # Calculate displacement d, the number of pixels up or down the bird will move this frame
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        # Set terminal velocity
        if d >= 16:
            d = 16

        # This is a tuning mechanism. Fiddle with this to change the overall height of a jump
        if d < 0:
            d -= 2

        # Update y position based on calculated displacement
        self.y = self.y + d

        # Tilt the bird according to movement
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # Draw the bird.
    def draw(self, win):
        self.img_count += 1  # increment image counter

        # Choose bird image based on image counter, animation time, cycle back and forth through the images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*5:
            self.img = self.IMGS[0]
            self.img_count = 0  # reset image counter

        # If the bird is diving hard, display just bird2.png, so it looks like it's gliding
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # Rotate image about its center based on current tilt
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # This returns info needed for collision detection
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200  # The space between pipes
    VEL = 5  # How fast the pipes move

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100  # Gap size
        self.top = 0  # Will store position where top of pipe will be drawn
        self.bottom = 0  # Will store position where bottom of pipe will be drawn
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False  # When bird passes the pipe, this is set to True
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)  # Height is the top of the gap
        self.top = self.height - self.PIPE_TOP.get_height()  # Top is the top-left corner of the pipe image
        self.bottom = self.height + self.GAP  # Bottom is the bottom of the gap

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    # Collision detection
    # Uses pygame masks to determine if drawn pixels are colliding
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Get collision points, if any. These are set to None if no collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Check for collision
        if t_point or b_point:
            return True

        return False

# The Base class uses cycles two images of the ground through the canvas to create the illusion of movement
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0  # position of the 1st image
        self.x2 = self.WIDTH  # position of the 2nd image

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # If 1st image scrolls off the screen, cycles it back behind the 2nd image
        if self.x1 + self.WIDTH <0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH <0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, living):
    # Note that blit() simply draws something on the screen
    # Draw the background
    win.blit(BG_IMG, (0,0))

    # Draw pipes
    for pipe in pipes:
        pipe.draw(win)

    # Draw score
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # Display generation count
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    # Display number of living birds
    text = STAT_FONT.render("Birds: " + str(living), 1, (255, 255, 255))
    win.blit(text, (10, 50))

    # Draw base
    base.draw(win)

    # Draw bird
    for bird in birds:
        bird.draw(win)

    pygame.display.update()

# This main() function doubles as the fitness function that is passed to the NEAT algorithm in run() below
def main(genomes, config):
    global GEN
    GEN += 1
    nets = []  # Stores the neural networks for each bird
    ge = []  # Stores the genomes for each bird
    birds = []  # Stores info specific to each bird

    # Initialize all neural networks, genomes, birds
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Need to ensure birds move according to next pipe, ignore passed pipes
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # Increase fitness slightly for moving forward

            # Get neural network output
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # Get birds to jump when the network tells them to
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []  # This stores pipes to be removed

        # Remove birds that collide and their associated genomes, networks
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                # Once the bird passes a pipe, call for a new pipe to be generated
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # Remove pipes as they leave the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        # Make a new pipe and increment score
        if add_pipe:
            score += 1

            # Increase fitness for surviving birds
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # Remove old pipes
        for r in rem:
            pipes.remove(r)

        # If bird hits the ground, or flies off top of screen, remove it
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        living = len(birds)
        draw_window(win, birds, pipes, base, score, GEN, living)





def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Generate a population
    p = neat.Population(config)

    # Output statistics
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Determine winners using fitness function
    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
