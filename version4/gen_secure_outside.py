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
        
    signedInO = pygame.image.load("../signedIn.png") #load the signed in screen image
    notSignedInO = pygame.image.load("../notSignedInO.png") #load the not signed in screen image
   
    font = pygame.font.Font('../Algerian.ttf', 32) #renders Algerian type font

    #-----------------------------Main Program Loop---------------------------------------------#
    while True:      
        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll() #looks for any event
        if ev.type == pygame.QUIT: #checks for window close button click
            break #end the program

        #-----------------------------Program Logic---------------------------------------------#
           
        if state == "signedIn":
            mainSurface.blit(signedInO, (0,0))
        elif state == "notSignedIn":
            mainSurface.blit(notSignedInO, (0,0))
       
        #-----------------------------Drawing Everything-------------------------------------#

        pygame.display.flip() #displays the surface
       
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()