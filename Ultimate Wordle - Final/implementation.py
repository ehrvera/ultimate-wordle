import pygame, os, threading, time
from sys import argv
import ctypes
from pygame.locals import *
import re

user32 = ctypes.windll.user32;  '''source from: https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python''' 
from application_assistance import debug_manager as debug
from application_assistance import quick_tools as uti
from wordle_algorithm import *


clientIsRunning, assistantIsRunning = True, True

class DisplayApplication:
    WINDOW_RATIO = (1600, 950)  # client window ratio
    
    def initiate_setup(self):
        pygame.init()
        pygame.display.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1';  # single line of code - alligns window to center '''source from: https://stackoverflow.com/questions/5814125/how-to-designate-where-pygame-creates-the-game-window'''
        
        self.monitorSize = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))  #width, height
        self.allowed_debug_outputs = ['debug', 'window_resize']

    def screen_defaults(self):  #AUTOMATIC CALLING if reset is needed
        self.win_maxDisplaySize = 0.89    # shrink %
        self.win_Resize = (self.win_maxDisplaySize, False)

    def verify_client(self):
        while assistantIsRunning:
            print("Client monitor matched successfully...") 

            compared_monitorSize = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
            if self.monitorSize != compared_monitorSize:  #if monitor size changes > calculate new dimension
                return
                print("New client display found\n") 

                self.monitorSize = compared_monitorSize
                DISPLAY_APPLICATION.window_size()
                time.sleep(60)
            time.sleep(30) # executes every 10s

    def change_debug_output(self, append_content=None, remove_content=None):
        if uti.check_list(append_content):
            for i in range(len(append_content)):
                if append_content[i] == 'window_resize':
                    self.allowed_debug_outputs += ['window_resize']
                elif append_content[i] == 'PLACEHOLDER1':
                    self.allowed_debug_outputs += ['PLACEHOLDER1']
                elif append_content[i] == 'PLACEHOLDER2':
                    self.allowed_debug_outputs += ['PLACEHOLDER2']

        if uti.check_list(remove_content):
            for i in range(len(remove_content)):
                if remove_content[i] == 'window_resize':
                    self.allowed_debug_outputs.remove('window_resize')
                elif remove_content[i] == 'PLACEHOLDER1':
                    self.allowed_debug_outputs.remove('PLACEHOLDER1')
                elif remove_content[i] == 'PLACEHOLDER2':
                    self.allowed_debug_outputs.remove('PLACEHOLDER2')
        debug.module_redirect(costom=f"New content list: {self.allowed_debug_outputs}", content_code="debug", event_priority=self.allowed_debug_outputs)

#self.monitorSize = (1200, 800)
    def window_size(self):
        DISPLAY_APPLICATION.screen_defaults()
        debug.module_redirect('Client', self.monitorSize[0], self.monitorSize[1], content_code="window_resize", event_priority=self.allowed_debug_outputs)

        #'''=== Find restore down size for client ==='''
        down_winWidth = round(self.monitorSize[0] * self.win_maxDisplaySize)   #{self.win_maxDisplaySize}% monoitor size => window size
        down_winHeight = round(((self.monitorSize[0] * self.win_maxDisplaySize) / self.WINDOW_RATIO[0]) * self.WINDOW_RATIO[1])

        while down_winHeight > self.monitorSize[1] * self.win_maxDisplaySize:  # if too tall for screen
            debug.module_redirect('Bad', down_winWidth, down_winHeight, content_code="window_resize", event_priority=self.allowed_debug_outputs)
            self.win_Resize = (self.win_Resize[0]-0.01, False) if self.win_Resize[0] >= 0.3 else (0.5, True)
            down_winWidth = round(self.monitorSize[0] * self.win_Resize[0])
            down_winHeight = round(((self.monitorSize[0] * self.win_Resize[0]) / self.WINDOW_RATIO[0]) * self.WINDOW_RATIO[1])
            if self.win_Resize[1]: break
        debug.module_redirect('Final window', down_winWidth, down_winHeight, content_code="window_resize", event_priority=self.allowed_debug_outputs)
        self.down_windowSize = (down_winWidth, down_winHeight)

        #'''=== Find largest size that fits game ratio ==='''
        if self.monitorSize[0] > self.monitorSize[1] and self.monitorSize[0] > 500:  #landscape dimension
            full_winHeight = self.monitorSize[1]
            full_winWidth = round((self.monitorSize[1] / self.WINDOW_RATIO[1]) * self.WINDOW_RATIO[0])

            print(f"Scaling width: {round(self.monitorSize[1] / self.WINDOW_RATIO[1], 7)} times")
            padding_winWidth = round((self.monitorSize[0] - ((self.monitorSize[1] / self.WINDOW_RATIO[1]) * self.WINDOW_RATIO[0])) / 2) + 1

            print(f"L&R padding: {padding_winWidth}")
            self.actual_windowSize = (full_winWidth, full_winHeight)
            print('Max ratio size:', full_winWidth, "x", full_winHeight)
        else:
            self.windowState, self.allowChange_windowState = 'restoreDown', False  # state, allow change

        perecent_lost = abs(round(((down_winWidth / down_winHeight) - (full_winWidth / full_winHeight)) * 100, 5))
        print(f"Lost {perecent_lost}% @screen transformation ")
        if perecent_lost <= 1:
            debug.module_redirect(costom="winRender status: Good\n", content_code="window_resize", event_priority=self.allowed_debug_outputs)
        else: debug.module_redirect(costom="winRender status: >1% lost\n", content_code="window_resize", event_priority=self.allowed_debug_outputs)

        global screen
        self.down_windowSize = 1613, 958 
        screen = pygame.display.set_mode(self.down_windowSize, pygame.NOFRAME)
        #screen = pygame.display.set_mode((1200, 800))

        pygame.display.set_caption(str(argv[-1].split("\\")[-1])) 
        pygame.display.set_caption('Ultimate Wordle') 

        pygame.draw.rect(screen, (255, 0, 0), (100, 400, 100, 200))
        pygame.display.update()
        DISPLAY_APPLICATION.screen_defaults()

class UltimateWordle():
    def __init__(self):
        word_length = 4
        GAME_moderatedWord_dict = {}
        GAME_completeWord_dict = {}

        for mode in ['moderated', 'complete']:
            for length in range(4, 6):  #4-5 
                wordImport_file = open(f'assets/{length}_wordList_{mode}.txt', "r" )
                wordImport_word = wordImport_file.read()

                if mode == 'moderated':
                    GAME_moderatedWord_dict[length] = re.findall(r'\b\w+\b', wordImport_word)
                if mode == 'complete':
                    GAME_completeWord_dict[length] = re.findall(r'\b\w+\b', wordImport_word)
                #setattr(self, f"_{length}_wordList_{mode}", re.findall(r'\b\w+\b', wordImport_word))
                wordImport_file.close()
        
        #return GAME_moderatedWord_dict, GAME_completeWord_dict

        #print(GAME_moderatedWord_dict[4])
        GAME_MODERATEDWORD_DICT = GAME_moderatedWord_dict
        GAME_COMPLETEWORD_DICT = GAME_completeWord_dict

        for key, value in GAME_MODERATEDWORD_DICT.items():
            if key == word_length:
                random_index = random.randint(0, len([item for item in value if item]) - 1)
                #print(random_index, value[random_index])

        for key, value in GAME_COMPLETEWORD_DICT.items():
            if key == word_length:
                if 'nice' in [item for item in value if item]:
                    print('no')
                else:
                    print('wqasn')




    def new_game(self, letter_length=int):
        self.correct_comparedWord = None
        pygame.draw.rect(screen, (255, 0, 0), (1000, 400, 100, 200))
        pygame.display.update()
        
        if False:
            wordle_algorithm = wordleAlgorithm(self.correct_comparedWord)
            wordle_algorithm.analyse(self.guess_comparedWord)
            wordle_algorithm.dupe_basicHint()
            wordle_algorithm.dupe_advancedHint()

    def check_input(self):
        self.userWord_list.append(self.wordInput)


DISPLAY_APPLICATION = DisplayApplication()
DISPLAY_APPLICATION.initiate_setup()
DISPLAY_APPLICATION.window_size()

ULTIMATE_WORDLE = UltimateWordle()
ULTIMATE_WORDLE.new_game()

periodic_thread = threading.Thread(target=DISPLAY_APPLICATION.verify_client)
periodic_thread.daemon = True
periodic_thread.start()  #starts the window check in a seperate thread


UltimateWordle().new_game()

# img=pygame.transform.scale(img, (int(width), int(height)))  #Scales image => create function
# imgrect=img.get_rect()
# Main.blit(img, imgrect)


while clientIsRunning:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            assistantIsRunning = False
            pygame.quit()
            exit()

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP or K_SPACE:
                pass
                #if air_timer < 6:
                    #player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
        