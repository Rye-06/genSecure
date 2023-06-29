#Import the libraries to be used
import pygame
import os
import argparse
import sys
import os.path

def main():
    #-----------------------------Setup------------------------------------------------------#
    pygame.init() #prepares the pygame module for use
    surfaceSize = 600 #desired physical surface size, in pixels
   
    clock = pygame.time.Clock() #forces the frame rate to be slower

    mainSurface = pygame.display.set_mode((surfaceSize, surfaceSize)) #creates the surface of (width, height), and its window

    #-----------------------------Program Variable Initialization----------------------------#
    if os.path.isfile('Auth.txt') == False:
        state = "notSignedIn"
    else:
        state = "signedIn"
        with open('Auth.txt', 'r') as file:
            content = file.readlines()
        status = content[2]
        if status == "off":
            genXStatus = False
        else:
            genXStatus = True
        
    signedInO = pygame.image.load("../signedIn.png") #load the signed in screen image
    notSignedInO = pygame.image.load("../notSignedInP.png") #load the not signed in screen image
    
    genXOn = pygame.image.load("../buttons/genXOnButton.png") #load the genX on image
    genXOff = pygame.image.load("../buttons/genXOffButton.png") #load the genX off image
   
    font = pygame.font.Font('../Algerian.ttf', 32) #renders Algerian type font
    
    genXOn = pygame.transform.scale(genXOn, (200, 200))
    genXOff = pygame.transform.scale(genXOff, (200, 200))

    #-----------------------------Main Program Loop---------------------------------------------#
    while True:      
        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll() #looks for any event
        if ev.type == pygame.QUIT: #checks for window close button click
            break #end the program
        
        if ev.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos() #gets the x and y position of the mouse, if a click occurs
            if state == "signedIn":
                
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                    
                if pos[0] > surfaceSize-390 and pos[0] < surfaceSize-190 and pos[1] > (surfaceSize/2) and pos[1] < (surfaceSize/2)+200:
                    genXStatus = not(genXStatus)
                    if genXStatus == True:
                        status = "on"
                    else:
                        status = "off"
                        
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                    data[2] = status
              
                if data[2] == "on":
                    genXStatus = True
                    status = "on"
                else:
                    genXStatus = False
                    status = "off"
     
                with open('Auth.txt', 'w') as file:
                    file.writelines(data)
        #-----------------------------Program Logic---------------------------------------------#
           
        if state == "signedIn":
            mainSurface.blit(signedInO, (0,0))
            if genXStatus == False:
                mainSurface.blit(genXOff, (surfaceSize-390,surfaceSize/2))
            else:
                mainSurface.blit(genXOn, (surfaceSize-390,surfaceSize/2))
        elif state == "notSignedIn":
            mainSurface.blit(notSignedInO, (0,0))
       
        #-----------------------------Drawing Everything-------------------------------------#

        pygame.display.flip() #displays the surface
       
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()