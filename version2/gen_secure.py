#Import the libraries to be used
import pygame
import cv2
import os
import numpy
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

def main():
    #-----------------------------Setup------------------------------------------------------#
    """ Set up the game and run the main game loop """
    pygame.init() #prepares the pygame module for use
    surfaceSize = 600 #desired physical surface size, in pixels
   
    clock = pygame.time.Clock() #forces the frame rate to be slower

    mainSurface = pygame.display.set_mode((surfaceSize, surfaceSize)) #creates the surface of (width, height), and its window

    #-----------------------------Program Variable Initialization----------------------------#
    size = (224, 224)
   
    curRecI = 0 #current recording number of the inside feed
    curRecO = 0 #current recording number of the outside feed
   
    videoI = VideoWriter('tempInside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream for the inside feed
    videoO = VideoWriter('tempOutside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream for the outside feed
   
    #button image imports
    recordButton = pygame.image.load("../recordButton.png") #load the record button image
    insideButton = pygame.image.load("../insideButton.png") #load the inside button image
    outsideButton = pygame.image.load("../outsideButton.png") #load the outside button image
    backButton = pygame.image.load("../backButton.png") #load the back button image
   
    #resizing button images
    recordButton = pygame.transform.scale(recordButton, (200, 50))
    backButton = pygame.transform.scale(backButton, (200, 50))
   
    state = "main"
   
    main = pygame.image.load("../mainScreen.png") #load the main screen image
   
    ranOnce = False
   
    #-----------------------------Main Program Loop---------------------------------------------#
    while True:      
        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll() #looks for any event
        if ev.type == pygame.QUIT: #checks for window close button click
            videoI.release()
            videoO.release()
            os.remove("tempInside.avi") #deletes the temporary recording file for the inside feed
            os.remove("tempOutside.avi") #deletes the temporary recording file for the outside feed
            break #ends the program
               
        if ev.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos() #gets the x and y position of the mouse, if a click occurs
            if state == "main":
                if pos[0] > surfaceSize-470 and pos[0] < surfaceSize-130 and pos[1] > surfaceSize-300 and pos[1] < surfaceSize-235:
                    state = "insideCam"
                if pos[0] > surfaceSize-470 and pos[0] < surfaceSize-130 and pos[1] > surfaceSize-200 and pos[1] < surfaceSize-135:
                    state = "outsideCam"
            if (state == "insideCam" or state == "outsideCam"): #detects for a mouse press on one of the camera feed screens
                 if state == "insideCam":
                     if pos[0] > surfaceSize-250 and pos[0] < surfaceSize-50 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the inside feed screen
                        videoI.release()
                        clip = VideoFileClip("tempInside.avi")
                        length = clip.duration #find the length of the inside feed till now
                        if length < 30:
                            ffmpeg_extract_subclip("tempInside.avi", 0, length, targetname="recordingInside" + str(curRecI) + ".avi") #save the initial inside feed as a recording (since its length is less than 30 seconds)
                        else:
                            ffmpeg_extract_subclip("tempInside.avi", (length-30), length, targetname="recordingInside" + str(curRecI) + ".avi") #save the last thirty seconds of the feed as a recording for the inside feed
                        clip.close()
                        videoI = VideoWriter('tempInside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream again for the inside feed
                        curRecI += 1 #increment the current recording number of the inside feed
                     elif pos[0] > surfaceSize-550 and pos[0] < surfaceSize-350 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50:
                        state = "main"
                        ranOnce = False
                 elif state == "outsideCam":
                    if pos[0] > surfaceSize-250 and pos[0] < surfaceSize-50 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the outside feed screen
                        videoO.release()
                        clip = VideoFileClip("tempOutside.avi")
                        length = clip.duration #find the length of the outside feed till now
                        if length < 30:
                            ffmpeg_extract_subclip("tempOutside.avi", 0, length, targetname="recordingOutside" + str(curRecO) + ".avi") #save the initial outside feed as a recording (since its length is less than 30 seconds)
                        else:
                            ffmpeg_extract_subclip("tempOutside.avi", (length-30), length, targetname="recordingOutside" + str(curRecO) + ".avi") #save the last thirty seconds of the feed as a recording for the outside feed
                        clip.close()
                        videoO = VideoWriter('tempOutside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream again for the outside feed
                        curRecO += 1 #increment the current recording number of the outside feed
                    elif pos[0] > surfaceSize-550 and pos[0] < surfaceSize-350 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50:
                        state = "main"
                        ranOnce = False

        #-----------------------------Program Logic---------------------------------------------#
       
        if state == "main":
            mainSurface.blit(main, (0,0))
            mainSurface.blit(insideButton, (surfaceSize-470, surfaceSize-300))
            mainSurface.blit(outsideButton, (surfaceSize-470, surfaceSize-200))
        elif state == "insideCam":
           
            if ranOnce == False:
                cap = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret, img = cap.read()
            if not ret:
                break
           
            mainSurface.blit(recordButton, (surfaceSize-250, surfaceSize-100)) #displays the record button on the screen
            mainSurface.blit(backButton, (surfaceSize-550, surfaceSize-100)) #displays the back button on the screen

            img = cv2.flip(img, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            displayImage = numpy.fliplr(displayImage)
            displayImage = numpy.rot90(displayImage)
            displayImage = pygame.surfarray.make_surface(displayImage)
           
            videoI.write(img) #saves the inside feed to the temporary video file, to be extracted
           
            #drawing each frame
            mainSurface.blit(displayImage, (0, 0)) #puts the camera image on the main surface
           
        elif state == "outsideCam":
           
            if ranOnce == False:
                cap = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret, img = cap.read()
            if not ret:
                break
           
            mainSurface.blit(recordButton, (surfaceSize-250, surfaceSize-100)) #displays the record button on the screen
            mainSurface.blit(backButton, (surfaceSize-550, surfaceSize-100)) #displays the back button on the screen

            img = cv2.flip(img, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            displayImage = numpy.fliplr(displayImage)
            displayImage = numpy.rot90(displayImage)
            displayImage = pygame.surfarray.make_surface(displayImage)
           
            videoO.write(img) #saves the outside feed to the temporary video file, to be extracted
           
            #drawing each frame
            mainSurface.blit(displayImage, (0, 0)) #puts the camera image on the main surface
       
        #-----------------------------Drawing Everything-------------------------------------#

        pygame.display.flip() #displays the surface
       
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()