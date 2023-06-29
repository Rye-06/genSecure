#Import the libraries to be used
import pygame
import cv2
import os
import numpy
import argparse
import sys
import os.path
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

class userInfo():
    """Holds user information- email and password."""
   
    def __init__(self):
        """Initializes a critical variable, used to check if the user logged in successfully or not."""
        self.loginCheck = False #detects if the user failed the login or not-
   
    def signUp(self, email, password):
        """Creates a file- "Auth.txt" that holds the details of the user, which they inputted, during sign-up."""
       
        #the email and password of the user is stored in the file "Auth.txt"
        file = open("Auth.txt","w")
        file.write (email)
        file.write ("\n")
        file.write (password)
        file.close()
       
    def login(self, email, password):
        """Verifies if the email and password inputted in the login matches those in the Auth.txt file (created during sign-up).
        Hence, determining if the user has successfully logged in or not."""
       
        #opens the "Auth.txt" (user information file) to retrieve the email and password in the form an array (to verify during login)
        with open ("Auth.txt", "r") as myfile:
            data = myfile.read().splitlines()
       
        #checks if user enters the right email and password
        if(email == data[0] and password == data[1]):
            #user enters the details right
            self.loginCheck = True
        else:
            #user enters the wrong email and/or password
            self.loginCheck = False

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
    retryButton = pygame.image.load("../retryButton.png") #load the retry button image
    takePhotoButton = pygame.image.load("../takePhotoButton.png") #load the take the photo button image
    nextButton = pygame.image.load("../nextButton.png") #load the next button image
   
    #resizing button images
    recordButton = pygame.transform.scale(recordButton, (200, 50))
    backButton = pygame.transform.scale(backButton, (200, 50))
    retryButton = pygame.transform.scale(retryButton, (200, 50))
    takePhotoButton = pygame.transform.scale(takePhotoButton, (200, 50))
    nextButton = pygame.transform.scale(nextButton, (200, 50))
   
    state = "main"
   
    main = pygame.image.load("../mainScreen.png") #load the main screen image
   
    #Login Screen
    loginScreen = pygame.image.load("../login.png") #load the login screen image
   
    #Sign-up Screen
    signupScreen = pygame.image.load("../signup.png") #load the sign-up screen image
   
    #initializes the color of the textbox of the email and password fields
    field_color1 = pygame.Color(207, 226, 243)
    field_color2 = pygame.Color(207, 226, 243)
   
    #email field variables
    email = '' #email is currently empty (nothing inputted)
    text_box1 = pygame.Rect((surfaceSize/2)-50, surfaceSize/2, 150, 50)
    text_active1 = False
   
    #password field variables
    password = '' #password is currently empty (nothing inputted)
    text_box2 = pygame.Rect((surfaceSize/2)-50, (surfaceSize/2)+110, 150, 50)
    text_active2 = False
   
    user = userInfo() #user object is created
   
    #checks if the user has already signed up or not
    if os.path.isfile('Auth.txt') == True:
        #the user has already signed up
        state = "login" #the user is on the login screen
    else:
        #the user hasn't signed up
        state = "signup" #the user is on the sign-up screen
   
    font = pygame.font.Font('../Algerian.ttf', 32) #renders Algerian type font
   
    ranOnce = False
    clickPhoto = False
   
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
               
        #checks if a key is pressed
        if ev.type == pygame.KEYDOWN:
            if text_active1:
                #key is pressed on the email field
                if ev.key == pygame.K_BACKSPACE:
                    #backspace is pressed
                    email = email[:-1] #removes the last character entered in the email field
                else:
                    if ev.key != pygame.K_RETURN and len(email) < 14:
                        #makes sure the length of the email field is less than 14 and that the enter key is not inputted as a character
                        email += ev.unicode #adds the character inputted to the email
            if text_active2:
                #key is pressed on the password field
                if ev.key == pygame.K_BACKSPACE:
                    #backspace is pressed
                    password = password[:-1] #removes the last character entered in the password field
                else:
                    if ev.key != pygame.K_RETURN and len(password) < 14:
                        #makes sure the length of the password field is less than 14 and that the enter key is not inputted as a character
                        password += ev.unicode #adds the character inputted to the password
                   
            #detects if the enter key is pressed and atleast one character is typed into both the fields (email and password)
            if ev.key == pygame.K_RETURN and len(email) > 0 and len(password) > 0:
                if state == "signup":
                    #sign-up process
                    
                    if "@gmail.com" in email:
                        user.signUp(email, password)
                        state = "identification"
                    else:
                        email = ''
                        password = ''
                           
                if state == "login":
                    #login process
                   
                    user.login(email, password)
                     
                    #checks if the login was successful or not
                    if user.loginCheck == False:
                        #login wasn't successful
                        email = ''
                        password = ''
                    else:
                        #login was successful
                        state = "main"
               
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
                            ffmpeg_extract_subclip("tempInside.avi", 0, length, targetemail="recordingInside" + str(curRecI) + ".avi") #save the initial inside feed as a recording (since its length is less than 30 seconds)
                        else:
                            ffmpeg_extract_subclip("tempInside.avi", (length-30), length, targetemail="recordingInside" + str(curRecI) + ".avi") #save the last thirty seconds of the feed as a recording for the inside feed
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
                            ffmpeg_extract_subclip("tempOutside.avi", 0, length, targetemail="recordingOutside" + str(curRecO) + ".avi") #save the initial outside feed as a recording (since its length is less than 30 seconds)
                        else:
                            ffmpeg_extract_subclip("tempOutside.avi", (length-30), length, targetemail="recordingOutside" + str(curRecO) + ".avi") #save the last thirty seconds of the feed as a recording for the outside feed
                        clip.close()
                        videoO = VideoWriter('tempOutside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream again for the outside feed
                        curRecO += 1 #increment the current recording number of the outside feed
                    elif pos[0] > surfaceSize-550 and pos[0] < surfaceSize-350 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50:
                        state = "main"
                        ranOnce = False
            elif state == "login" or state == "signup":
                #checks if the email or password field is clicked
                if text_box1.collidepoint(ev.pos):
                    text_active1 = True #email field is clicked
                else:
                    text_active1 = False
               
                if text_box2.collidepoint(ev.pos):
                    text_active2 = True #password field is clicked
                else:
                    text_active2 = False
            elif state == "identification":
                if pos[0] > surfaceSize-570 and pos[0] < surfaceSize-370 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50:
                    clickPhoto = True
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-350 and pos[0] < surfaceSize-150 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    os.remove("user_face.jpg") #deletes the previous user face image
                    clickPhoto = True
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-180 and pos[0] < surfaceSize+20 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    state = "main"
                    ranOnce = False

        #-----------------------------Program Logic---------------------------------------------#
       
        if state == "login":
            #the user is on the login screen
            mainSurface.blit(loginScreen, (0, 0)) #displays the login screen image
           
            emailF = font.render(('Email: '), True, (255, 255, 255))
            mainSurface.blit(emailF, (surfaceSize-500, surfaceSize-300))
           
            #displays the email field text and textbox
            pygame.draw.rect(mainSurface, field_color1, text_box1)
            surf = font.render(email, True, 'black')
            mainSurface.blit(surf, (text_box1.x+5 , text_box1.y+5))
            text_box1.w = max(100, surf.get_width()+10)
           
            passwordF = font.render(('Password: '), True, (255, 255, 255))
            mainSurface.blit(passwordF, (surfaceSize-550, surfaceSize-200))
           
            #displays the password field text and textbox
            pygame.draw.rect(mainSurface, field_color2, text_box2)
            surf = font.render(password, True, 'black')
            mainSurface.blit(surf, (text_box2.x+5, text_box2.y+5))
            text_box2.w = max(100, surf.get_width()+10)
           
            #changes the color of the field that is clicked
            if text_active1:
                field_color1 = pygame.Color('red')
            else:
                field_color1 = pygame.Color(207, 226, 243)
           
            if text_active2:
                field_color2 = pygame.Color('red')
            else:
                field_color2 = pygame.Color(207, 226, 243)
           
        elif state == "signup":
            #the user is on the sign-up screen
            mainSurface.blit(signupScreen, (0, 0)) #displays the sign-up screen image
           
            emailF = font.render(('Email: '), True, (255, 255, 255))
            mainSurface.blit(emailF, (surfaceSize-500, surfaceSize-300))
           
            #displays the email field text and textbox
            pygame.draw.rect(mainSurface, field_color1, text_box1)
            surf = font.render(email, True, 'black')
            mainSurface.blit(surf, (text_box1.x+5 , text_box1.y+5))
            text_box1.w = max(100, surf.get_width()+10)
           
            passwordF = font.render(('Password: '), True, (255, 255, 255))
            mainSurface.blit(passwordF, (surfaceSize-550, surfaceSize-200))
           
            #displays the password field text and textbox
            pygame.draw.rect(mainSurface, field_color2, text_box2)
            surf = font.render(password, True, 'black')
            mainSurface.blit(surf, (text_box2.x+5, text_box2.y+5))
            text_box2.w = max(100, surf.get_width()+10)
           
            #changes the color of the field that is clicked
            if text_active1:
                field_color1 = pygame.Color('red')
            else:
                field_color1 = pygame.Color(207, 226, 243)
           
            if text_active2:
                field_color2 = pygame.Color('red')
            else:
                field_color2 = pygame.Color(207, 226, 243)
        elif state == "identification":
            if ranOnce == False:
                cap = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret, img = cap.read()
            if not ret:
                break
           
            mainSurface.blit(takePhotoButton, (surfaceSize-570, surfaceSize-100)) #displays the take the photo button on the screen

            img = cv2.flip(img, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            displayImage = numpy.fliplr(displayImage)
            displayImage = numpy.rot90(displayImage)
            displayImage = pygame.surfarray.make_surface(displayImage)
           
            #drawing each frame
            mainSurface.blit(displayImage, (0, 0)) #puts the camera image on the main surface
           
            if clickPhoto == True:
                cv2.imwrite("user_face.jpg", img)
                clickPhoto = False
                mainSurface.blit(retryButton, (surfaceSize-350, surfaceSize-100)) #displays the retry button on the screen
                mainSurface.blit(nextButton, (surfaceSize-180, surfaceSize-100)) #displays the next button on the screen
           
        elif state == "main":
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