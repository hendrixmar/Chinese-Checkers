import pygame
import socket
import time
import pickle
import _thread
import sys
from threading import Lock, Thread

pygame.init()

display_width = 975
display_height = 975

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
COLORS = {'_':(250,240,230),0:(220,220,220), 1:(128,0,128), 2:(255,165,0), 3:(0,128,0), 4:(0,0, 255), 5:(255,0,0), 6:(255,255,0)}
img = pygame.image.load('icon.png')

block_color = (53,115,255)
FLAG = 2
car_width = 73
table = None
intro = True
actual = 1
stop = False
gameDisplay = pygame.display.set_mode((975,975))

clock = pygame.time.Clock()
button = pygame.Rect(700,100, 128, 128)
################### Socket initiliaze ###################
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(("127.0.0.1", 8080))
player = None
###################  ###################  ###################
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

#this create a matrix of rect object
def initiliaze(table):
    x = 100
    y = 200

    map = []
    for rows in table:
        temp = []
        for elem in rows:
            temp.append(pygame.Rect(x,y, 30, 30))
            x += 31
        map.append(temp)

        x = 100
        y += 31

    return map
#fetch the data received from the client Socket
def recieve_data():
    data = clientsocket.recv(1024)
    data = pickle.loads(data)

    return data


def explore(Y,X):

    global table

    tiles = []

    # all the basic moves possible
    moves = [ (-1, -1), (-1,1), (0,2), (1, 1), ( 1, -1), (0, -2)]

    #it check if all the moves we have generated from our current position are valid
    #If that is the case we add them to the list tiles
    for y,x in moves:
        if Y + y in range(17) and X + x in range(25):
            if table[Y + y][X + x] == 0:
                tiles.append((Y + y,X + x))
            elif Y + y*2 in range(17) and X + x*2 in range(25) and table[Y + y*2][X + x*2] == 0:
                tiles.append((Y + y*2, X + x*2))

    return tiles




def run():

    global table, stop
    map = initiliaze(table)
    pygame.display.set_caption(f'Damas chinas jugador {player}')

    tiles = []
    while not stop:
        gameDisplay.fill(white)

        largeText = pygame.font.Font('freesansbold.ttf',30)
        texto = "Es tu turno" if player == actual else f'Es turno del jugador {actual}'
        TextSurf,  TextRect = text_objects(texto, largeText)
        TextRect.center = (500,100)
        gameDisplay.blit(TextSurf, TextRect)


        gameDisplay.blit(img,(700,30))

        for i in range(17):
            for j in range(25):
                C = (112,128,144) if (i,j) in tiles  else  COLORS[ table[i][j] ]
                pygame.draw.rect(gameDisplay, C, map[i][j],0)

        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN and player == actual:
                # This is true when right click is pressed
                #= map[i][j].collidepoint(pygame.mouse.get_pos())

                if button.collidepoint(pygame.mouse.get_pos()):
                    data_arr = pickle.dumps('save')
                    clientsocket.send(data_arr)
                    continue

                for i in range(17):
                    for j in range(25):

                        click = map[i][j].collidepoint(pygame.mouse.get_pos())

                        if click == 1 and table[i][j] == player:
                            print ("CLICKED a valid tile!",i,j)
                            actual_position = (i,j)
                            tiles = explore(i,j)

                            break
                        elif click == 1 and (i,j) in tiles:
                            table[ i ][ j ] = table[ actual_position[0] ][ actual_position[1] ]
                            table[ actual_position[0] ][ actual_position[1] ] = 0
                            # It send the table updated with the new movement made by the actual player

                            data_arr = pickle.dumps(table)
                            clientsocket.send(data_arr)
                            tiles = []
                            actual_position = None

                            print ("CLICKED an invalid tile!",i,j)
                            break




            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


def start_conection_socket():

    data = []
    global player
    while 1:
        info = recieve_data()
        if  player != None:
            return info
        else:
            data_arr = pickle.dumps(True)
            print(info)
            player = info
            clientsocket.send(data_arr)

def game_intro():

    global intro

    while intro:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("Damas chinas", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(15)

def game_finish(user):


    winner = "Has ganado"if player == user else "Has perdido"
    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects(winner, largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(15)

def game():

    global FLAG, table
    game_intro()
    while(table == None):
        pass

    run()
    FLAG -= 1

def online():

    global FLAG, table, intro, actual, map, stop

    temp = start_conection_socket();
    intro = temp[0]
    table = temp[1]

    while 1:
        temp = recieve_data()
        if type(temp) is not tuple and temp in range(1,7):
            stop = True
            game_finish(temp)

        actual = temp[0]
        table = temp[1]




    FLAG -= 1


try:
   _thread.start_new_thread( game, () )
   _thread.start_new_thread( online, () )
except:
   print ("Error: unable to start thread")


while FLAG:
   pass
