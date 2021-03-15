import pygame
import neat
import os
import time
import random
pygame.font.init()

WIN_WIDTH = 550
WIN_HEIGHT = 690

BIRD_IMGS = [(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             (pygame.image.load(os.path.join("imgs", "bird2.png"))),
             (pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

GEN = -1
SIZE = 0

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img  = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel*self.tick_count + 1.5*self.tick_count**2

        if displacement >= 16:
            displacement = 16

        elif displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
                
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]

        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]

        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]

        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]

        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 136
    VEL = 7

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(60, 420)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if t_point or b_point:
            return True

        return False

class Base:
    VEL = 7
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2  =self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self. x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self. x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, gen, size):
    win.blit(BG_IMG, (0, -200))
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))
    text = STAT_FONT.render("Alive: " + str(size), 1, (255, 255, 255))
    win.blit(text, (10, 45))
    pygame.display.update()

def main (genomes, config):
    global GEN
    GEN += 1
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    birds = []
    base = Base(625)
    pipes = [Pipe(650)]

    nets = []
    ge = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(150,200))
        g.fitness = 0
        ge.append(g)

    SIZE = len(birds)
    score = 0
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) >= 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1

        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()

        base.move()

        add_pipe = False
        rem = []
        for pipe in range(len(pipes)):
            for x, bird in enumerate(birds):
                if pipes[pipe].collide(bird, win):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    SIZE -= 1

                if not pipes[pipe].passed and pipes[pipe].x < bird.x:
                    pipes[pipe].passed = True
                    add_pipe = True

            if pipes[pipe].x + pipes[pipe].PIPE_TOP.get_width() < 0:
                rem.append(pipes[pipe])

            pipes[pipe].move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 2
            pipes.append(Pipe(650))
            add_pipe = False

        for i in rem:
            pipes.remove(i)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 650 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                SIZE -= 1

        draw_window(win, birds, pipes, base, score, GEN, SIZE)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #numero maximo de gerações
    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)