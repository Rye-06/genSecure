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
    #sets up the video capture device
    cap = cv2.VideoCapture(0)
    size = (224, 224)
    
    curRec = 0 #current recording number
    
    video = VideoWriter('tempInside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream
    
    recordButton = pygame.image.load("../recordButton.png") #load the record button image
    
    #-----------------------------Main Program Loop---------------------------------------------#
    while cap.isOpened():       
        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll() #looks for any event
        if ev.type == pygame.QUIT: #checks for window close button click
            video.release()
            os.remove("tempInside.avi") #deletes the temporary recording file
            break #ends the program
        
        if ev.type == pygame.MOUSEBUTTONUP: #detects for a mouse press
             pos = pygame.mouse.get_pos() #gets the x and y position of the mouse, if a click occurs
             if pos[0] > surfaceSize-350 and pos[0] < surfaceSize-20 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-40: #checks if the record button is clicked
                video.release()
                clip = VideoFileClip("tempInside.avi")
                length = clip.duration #find the length of the feed till now
                if length < 30:
                    ffmpeg_extract_subclip("tempInside.avi", 0, length, targetname="recordingInside" + str(curRec) + ".avi") #save the initial feed as a recording (since its length is less than 30 seconds)
                else:
                    ffmpeg_extract_subclip("tempInside.avi", (length-30), length, targetname="recordingInside" + str(curRec) + ".avi") #save the last thirty seconds of the feed as a recording
                clip.close()
                video = VideoWriter('tempInside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream again
                curRec += 1 #increment the current recording number
            
        #-----------------------------Program Logic---------------------------------------------#
        #reads an image from the video stream
        ret, img = cap.read()
        if not ret:
            break
        
        mainSurface.blit(recordButton, (surfaceSize-350, surfaceSize-100)) #draw the record button on the screen

        img = cv2.flip(img, 1) #the required image processing to format it correctly
        
        #converts the cv2 image format to a pygame image format
        displayImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        displayImage = numpy.fliplr(displayImage)
        displayImage = numpy.rot90(displayImage)
        displayImage = pygame.surfarray.make_surface(displayImage)
        
        video.write(img) #saves the feed to the temporary video file, to be extracted
        
        #-----------------------------Drawing Everything-------------------------------------#
        
        #drawing each frame
        
        mainSurface.blit(displayImage, (0, 0)) #puts the camera image on the main surface

        pygame.display.flip() #displays the surface
        
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()