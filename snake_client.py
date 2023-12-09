import socket
import pygame
import random
import snake
import threading
import rsa
import time

global rgb_colors, rgb_colors_list
rgb_colors = {
    "1" : (245, 147, 147),
    "2" : (245, 161, 147),
    "3" : (245, 175, 147),
    "4" : (245, 189, 147),
    "5" : (245, 203, 147),
    "6" : (245, 217, 147),
    "7" : (245, 231, 147),
    "8" : (245, 245, 147),
    "9" : (231, 245, 147),
    "10" : (217, 245, 147),
    "11" : (203, 245, 147),
    "12" : (189, 245, 147),
    "13" : (175, 245, 147),
    "14" : (161, 245, 147),
    "15" : (147, 245, 147),
    "16" : (147, 245, 161),
    "17" : (147, 245, 175),
    "18" : (147, 245, 189),
    "19" : (147, 245, 203),
    "20" : (147, 245, 217),
    "21" : (147, 245, 231),
    "22" : (147, 245, 245),
    "23" : (147, 231, 245),
    "24" : (147, 203, 245),
    "25" : (147, 189, 245),
    "26" : (147, 175, 245),
    "27" : (147, 161, 245),
    "28" : (147, 147, 245),
    "29" : (161, 147, 245),
    "30" : (175, 147, 245),
    "31" : (189, 147, 245),
    "32" : (203, 147, 245),
    "33" : (231, 147, 245),
    "34" : (245, 147, 245),
    "35" : (245, 147, 231),
    "36" : (245, 147, 203),
    "37" : (245, 147, 189),
} 
rgb_colors_list = list(rgb_colors.values()) 

# initialize the game
pygame.init()

# send data to the server that contains the action of the player
# parse the game state received from the server,
# e.g. (2, 17)*(3, 17)*(4, 17)*(5, 17)|(18, 1)**(10, 14)**(12, 1)**(4, 1)**(10, 11)
# draw the game interface based on the game state

# receive data from the server 
# this is going to be run as a thread
def receiveData(socket):
    try:
        dataLength = socket.recv(4).decode()
        # print("data length: ", dataLength)
        # print("receiving data")
        # print("received data: ", receivedMsg)
        
        if dataLength != "":
            # if the message doesnt starts with -999
            # then it is an encrypted message
            if dataLength != "-999":
                receivedMsg = socket.recv(int(dataLength))
                # print("received encrypted message: ", receivedMsg)
                # decrypt the message using client's private key
                decryptedMsg = rsa.decrypt(receivedMsg, privkey).decode()
                print(decryptedMsg)
            else:
                # print("received game state len: ", dataLength)
                receivedGameStateLen = socket.recv(4).decode()
                receivedGameState = socket.recv(int(receivedGameStateLen)).decode()
                parseGameState(receivedGameState)
        
        # print("parsed game state: ", allSnakePos, foodPos)
    except Exception as e:
        print("error receiving data", e)
        

def parseGameState(game_state):
    try:
        global allSnakePos, foodPos
        # if the game state is not complete, ignore it 
        # and wait for the next game state
        allSnakePos.clear()
        foodPos.clear()
        
        snakeFood = game_state.split("|")

        # this is so fucking retarded
        # split all snakes into individual snakes
        formattedSnakePos = snakeFood[0].split("**")
        for individualSnakePos in formattedSnakePos:
            # remove the first and last parenthesis, except the first color element
            cleanedIndividualSnakePos = individualSnakePos.replace("(", "").replace(")", "")
            snakePosParts = cleanedIndividualSnakePos.split("*")
            
            # convert each position from string to a tuple of integers
            allSnakePos.append([tuple(map(int, pos.split(","))) for pos in snakePosParts])
            
        foodPos = snakeFood[1].split("**")
        for i in range(len(foodPos)):
            foodPos[i] = foodPos[i].replace("(", "")
            foodPos[i] = foodPos[i].replace(")", "")
        foodPos = [tuple(map(int, pos.split(","))) for pos in foodPos]

    except Exception as e:
        print(e)
        return False
    
    return True

# control the snake, and send the action to the server
def control():
    events = pygame.event.get()
    if len(events) > 0:
        for event in events:
            # code stole from https://www.techwithtim.net/tutorials/game-development-with-python/snake-pygame/snake-tutorial-4
            # keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sendData("left")

                elif event.key == pygame.K_RIGHT:
                    sendData("right")

                elif event.key == pygame.K_UP:
                    sendData("up")

                elif event.key == pygame.K_DOWN:
                    sendData("down")

                elif event.key == pygame.K_ESCAPE:
                    sendData("quit")
                    client_socket.close()
                    pygame.quit()
                
                # talking shit in a snake game
                elif event.key == pygame.K_SPACE:
                    sendData("reset")
                    
                elif event.key == pygame.K_z:
                    sendData("GG")
                
                elif event.key == pygame.K_x:
                    sendData("git gud kid")
                    
                elif event.key == pygame.K_c:
                    sendData("cheater")
                    
                elif event.key == pygame.K_v:
                    sendData("L")
                    
                elif event.key == pygame.K_b:
                    sendData("nice")
                    
                elif event.key == pygame.K_n:
                    sendData("wp")

# send encrypted messages and commands to the server
def sendData(rawData):
    data = rawData.encode()
    # message = data.encode()
    encryptedMsg = rsa.encrypt(data, serverPubkey)
    dataLength = str(len(encryptedMsg)).zfill(4).encode()
    client_socket.send(dataLength + encryptedMsg)

# function stole from https://www.techwithtim.net/tutorials/game-development-with-python/snake-pygame/snake-tutorial-4
def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0
    
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn
        pygame.draw.line(surface, (255,255,255), (x,0),(x,w))
        pygame.draw.line(surface, (255,255,255), (0,y),(w,y))

# modified stolen code that i shamlessly claim to be my own work
# it draws the snake and the food on the screen
def redrawWindow(surface, snakeCubeList, foodCubeList):
    surface.fill((0,0,0))
    if len(snakeCubeList) != 0 and len(foodCubeList) != 0:
        # draw the snake
        for snakeCube in snakeCubeList:
            # draw the eyes 
            if snakeCube.isHead:
                snakeCube.draw(surface, True)
            else:
                snakeCube.draw(surface)
                
        # draw the food
        for foodCube in foodCubeList:
            foodCube.draw(surface)

    drawGrid(width,rows, surface)
    pygame.display.update()

# update the list that contains the cube objects
def updateCubes():
    # global snakeThatMoves, foodObj, snakePos, foodPos
    snakeThatMoves.clear()
    foodObj.clear()
    # skip the fitse element as it is the color of the snake
    for i, snakePos in enumerate(allSnakePos):
        for j in range(len(snakePos)):
            if j == 0:
                snakeThatMoves.append(snake.cube(list(snakePos[j]), color=rgb_colors_list[(4 * i)%len(rgb_colors_list)], isHead=True))
            else:
                snakeThatMoves.append(snake.cube(list(snakePos[j]), color=rgb_colors_list[(4 * i)%len(rgb_colors_list)]))

    for i in range(len(foodPos)):
        foodObj.append(snake.cube(foodPos[i], color=(235,235,235)))


if __name__ == "__main__":
    server_addr = "localhost"
    server_port = 5555
    width = 500
    rows = 20
    # list of tuples for the snake position
    allSnakePos = []
    # list of tuples for the food position
    foodPos = []
    # list of cube objects for all the snakes 
    snakeThatMoves = []
    # list of cube objects for the food
    foodObj = []
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
    client_socket.connect((server_addr, server_port))
    
    # receive public key sent from the server
    serverPubkey = rsa.PublicKey.load_pkcs1(client_socket.recv(1024).decode())
    
    # generate a pair of public and private key
    (pubkey, privkey) = rsa.newkeys(256,accurate=False)
    
    savedPubkey = pubkey.save_pkcs1()
    # send the public key to the server
    client_socket.send(savedPubkey)
    
    win = pygame.display.set_mode((width, width))
    clock = pygame.time.Clock()
    pygame.key.set_repeat()
    # recvThread = threading.Thread(target=receiveData, args=(client_socket,), daemon=True)
    # recvThread.start()
    
    # the main loop
    while True:
        # sending something constantly to keep getting the lastest game state
        client_socket.send("-999".encode())
        receiveData(client_socket)
        control()
        updateCubes()
        # pygame.time.delay(0)
        # clock.tick(30)
        redrawWindow(win, snakeThatMoves, foodObj)