import pygame
import random

class Game():
    def __init__(self):
        pygame.init()
        self.running = True
        self.START_KEY = False

        #Display height and width
        self.DISPLAY_H = 800
        self.DISPLAY_W = 800

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0 , 0)
        self.YELLOW = (255, 255, 100)
        self.BLUE = (0, 0, 255)

        #Initialise window
        self.screen = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.screenrect = self.screen.get_rect()
        pygame.display.set_caption("SOME COOL GAME NAME")
        self.background = pygame.Surface((self.screen.get_size()))
        self.backgroundrect = self.background.get_rect()
        self.background.fill(self.BLACK)  # black

        #Define grid content - change this later.
        self.grid = ["      ",
                "ABCDEF",
                "GHIJKL",
                "MNOPQR",
                "STUVWX",
                "YZ1234",
                "56789_"]

        self.phrase = [""]

        self.lines = len(self.grid)
        self.columns = len(self.grid[0])

        self.length = self.screenrect.width / self.columns
        self.height = self.screenrect.height / self.lines

        self.highlighted = 0
        self.last_highlight = 0
        self.new_highlight = 0
        self.row_or_col = 0

        self.clock = pygame.time.Clock()
        self.FPS = 2  # 2 FPS should give us epochs of 500 ms

        self.waittime = 1000
        self.interval = 50
        self.timer_interval = 1000
        self.timer_event = pygame.USEREVENT + 1

        self.numtrials = 0
        self.targets = [[1, 1], [3, 5], [1, 0], [2, 2], [3, 1], [4, 0], [6, 5]]
        self.targetcounter = 0

        self.face_img = pygame.transform.scale(pygame.image.load('barack-face.jpg').convert_alpha(), (50, 50))

    def write(self, text, colour):
        myfont = pygame.font.SysFont("Courier", 90)
        mytext = myfont.render(text, True, colour)
        self.screen.blit(mytext, (10, 10))
        mytext = mytext.convert_alpha()
        return mytext

    def make_grid(self):
        for y in range(self.lines):
            for x in range(self.columns):
                textsurface = self.write(self.grid[y][x], self.BLUE)
                self.background.blit(textsurface, self.set_position(x, y))
        #self.writePhrase()
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def draw_face(self, x, y):
        self.screen.blit(self.face_img, (x,y))
        pygame.display.flip()

    def writePhrase(self):
        for z in range(len(self.phrase)):
            textsurface = self.write(self.phrase[z], self.WHITE)
            self.background.blit(textsurface, (self.length * z + self.length/4, self.height * 5 + self.height/4))

    def highlight(self, target, oldhighlight = 0):
        self.row_or_col = random.randint(0, 1)  # determines whether to highlight a row or column
        if self.row_or_col == 0:
            self.highlighted = random.randint(0, self.lines - 1)  # determines which row or column
        else:
            self.highlighted = random.randint(0, self.columns - 1)

        if self.highlighted == oldhighlight:  # adjusts repeated values
            if self.highlighted == 0 or 2 or 4:
                self.highlighted += 1
            else:
                self.highlighted -= 1

        self.new_highlight = self.highlighted

        for y in range(self.lines):
            for x in range(self.columns):
                if self.row_or_col == 0:  # highlight a row
                    if y == self.highlighted:
                        self.screen.blit(self.face_img, self.set_position(x, y))
                        '''textsurface = self.write(self.grid[y][x], self.YELLOW)
                        self.background.blit(textsurface, (self.set_position(x, y)))'''
                    else:
                        textsurface = self.write(self.grid[y][x], self.BLUE)
                        self.background.blit(textsurface, (self.set_position(x, y)))
                else:  # highlight a column
                    if x == self.highlighted:
                        self.screen.blit(self.face_img, self.set_position(x, y))
                        '''textsurface = self.write(self.grid[y][x], self.YELLOW)
                        self.background.blit(textsurface, (self.set_position(x, y)))'''
                    else:
                        textsurface = self.write(self.grid[y][x], self.BLUE)
                        self.background.blit(textsurface, (self.set_position(x, y)))
            #self.writePhrase()

        # record on the parallel port; test to see if row is the same as target
        if self.row_or_col == 0:  # if it is a row
            if target[0] == self.highlighted:
                # parallel.setData(2) #this is the target; record it in the parallel
                print(self.highlighted)
                print(target)
                print(str(self.numtrials) + " **target row")
                # core.wait(0.005)
                # parallel.setData(0)
            else:
                # parallel.setData(1) #this is not the target
                print(self.highlighted)
                print(target)
                print(str(self.numtrials) + " row")
                # core.wait(0.005)
                # parallel.setData(0)
        else:  # it is a column
            if target[1] == self.highlighted:
                # parallel.setData(2) #this is the target; record it in the parallel
                print(self.highlighted)
                print(target)
                print(str(self.numtrials) + " **target column")
                # core.wait(0.005)
                # parallel.setData(0)
            else:
                # parallel.setData(1) #this is not the target
                print(self.highlighted)
                print(target)
                print(str(self.numtrials) + " column")
                # core.wait(0.005)
                # parallel.setData(0)

        return (self.new_highlight)

    def set_position(self, x, y):
        return self.length * x + self.length / 4, self.height * (y - 1) + self.height / 4

    def make_target(self, target):
        for y in range(self.lines):
            for x in range(self.columns):
                if y == target[0] and x == target[1]:
                    textsurface = self.write(self.grid[y][x], self.RED)
                    self.background.blit(textsurface, (self.set_position(x, y)))
                    self.phrase += self.grid[y][x]
                else:
                    textsurface = self.write(self.grid[y][x], self.BLUE)
                    self.background.blit(textsurface, (self.set_position(x, y)))

    def reset_keys(self):
        self.START_KEY = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True

    def game_loop(self):
        while self.running:
            self.events()
            if self.START_KEY:
                self.running = False

            if self.targetcounter < 6:
                if self.numtrials == 0:
                    self.make_target(self.targets[self.targetcounter])
                    self.screen.blit(self.background, (0, 0))  # clean whole screen
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.wait(self.waittime)
                    self.numtrials += 1
                elif self.numtrials == 121:
                    self.targetcounter += 1
                    self.numtrials = 0
                else:
                    self.make_grid()
                    # self.draw_face(0,0)
                    self.highlight(self.targets[self.targetcounter], self.last_highlight)
                    self.screen.blit(self.background, (0, 0))
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.wait(self.interval)
                    self.numtrials += 1

            else:
                pygame.quit()