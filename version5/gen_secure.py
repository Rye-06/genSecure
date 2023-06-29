#-----------------------------------------------------------------------------
# Name:        Gen Secure
# Purpose:     Gen Secure is an all-in-one, easy-to-use, graphical security device. It includes basic functionalities such as allowing the user to arm and disarm the space (GenX ON or OFF). You also have an alert system for any unknown presence inside the space, through email.
#              Users can also save recordings from the feeds (inside and outside) and see the camera feeds. The product even has face recognition technology that can track when the user enters the space, immediately disarming the system.
#              People can also leave a voice message from the outside for the owner by interacting with the graphical interface. Visitors can also be added, whose names are announced if they are outside. These are some of the many features of GenX, making it extremely handy for safety purposes, especially for spaces like houses.
#
# Author:      Shaurya Sareen (Rye)
# Created:     16-May-2023
# Updated:     7-June-2023
#-----------------------------------------------------------------------------
#I think this project deserves a level 4+ because ...
#
#Features Added:
#   Program runs without any error
#   Face Identification
#   Produce a modular program that is divided among multiple functions and classes (both custom)
#   User-friendly sign-up and disable GenX form
#   Uses appropriate data types (Integer, String, Boolean)
#   Uses conditional structures (if-statement, boolean operators)
#   Uses loop structures (for, while)
#   Uses built-in functions and properties
#   Uses lists
#   Has different simulation modes (inside, phone and outside) and screens within them
#   Program is fully documented and follows class naming conventions
#   Reads and writes to a user file (Auth.txt)- the email, password, recording numbers of the feeds and the voice recording numbers. We also write the feed recordings and the voice recordings
#
#Extra Features Added:
#   There is an enhanced UI, with smooth button functioning
#   The code is clean and easy to follow
#   The program is efficient, and uses functions, lists, loops, conditional statements and global variables to eliminate redundancy
#   User input like the email (makes sure it's valid) and the owner's face (makes sure a face can be seen) is checked for
#   Involves voice announcing feature for visitors (unknown and known), if any are detected
#   Sends an email to the user, with the detected person image
#   Person identification and comparison feature is present
#   Voice detection feature is present
#   Code modifications regularly (every day) uploaded to github via descriptive commit process
#   Added timer for the disabling GenX screen
#
#-----------------------------------------------------------------------------

# NOTE: PLEASE HAVE A FOLDER NAMED 'photos' IN THE 'Downloads' DIRECTORY. STORE PHOTOS OF PEOPLE THERE BY THEIR NAME (FIRST OR LAST OR BOTH). THIS IS WHAT WOULD BE ANNOUNCED.

#import the libraries to be used
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
from deepface import DeepFace
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from win32com.client import Dispatch
from pathlib import Path
import sounddevice as sd
import soundfile as sf
import shutil
import re

class userInfo():
    '''
    Holds the user information- email and password.
    Holds the GenX status, the recording number for both the inside and outside feed, and the voice recording number.
    Check if the email entered is valid and sends an email, if necessary
    Checks if the password entered to disable GenX is valid or not
    Creates 'Auth.txt' (user information file)
    '''
    def __init__(self):
        '''
        Runs when the user information object is created.
        Holds the email and password of the user, entered during sign-up.

        Parameters
        ----------
        parameter1 : instance of the class (created)
        allows one to access variables of the class
        
        Returns
        -------
        None
        '''
        
        self.email = ""
        self.password = ""
   
    def signUp(self, email, password):
        '''
        Creates a file- "Auth.txt" that holds the details of the user, which they inputted, during sign-up.
        Also includes the GenX status, the recording number for both the inside and outside feed, and the voice recording number.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2 : string
        email entered, during sign-up
        
        parameter3 : string
        password entered, during sign-up
        
        Returns
        -------
        None
        '''
        
        file = open("Auth.txt","w")
        file.write (email)
        file.write ("\n")
        file.write (password)
        file.write ("\n")
        file.write ("off")
        file.write ("\n")
        file.write ("0")
        file.write ("\n")
        file.write ("0")
        file.write ("\n")
        file.write ("0")
        file.close()
        
        self.email = email
        self.password = password
        
    def sendMail(self, imgFileName):
        '''
        Sends an email to the user (inputted during sign-up), alerting them of an unknown presence in the space.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2 : string
        detected person's image file path
        
        Returns
        -------
        None
        '''

        with open(imgFileName, 'rb') as f:
            img_data = f.read()

        msg = MIMEMultipart()
        msg['Subject'] = 'PERSON SEEN INSIDE THE SPACE'

        text = MIMEText("ALERT! A PERSON SEEN INSIDE THE SPACE, HAS FAILED TO ENTER THE PASSWORD TO DISABLE GENX. DISABLE GENX IF YOU KNOW THE PERSON OR THE AUTHORITIES WILL BE CALLED TO YOUR LOCATION WITHIN 10 MINUTES.")
        msg.attach(text)
        image = MIMEImage(img_data, name=os.path.basename(imgFileName))
        msg.attach(image)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login('1sareensha@hdsb.ca', 'lcviruxiygyvaexu')
        s.sendmail('1sareensha@hdsb.ca', self.email, msg.as_string()) #sends the mail to the email address of the user
        s.quit()
    
    def checkEmail(self, email):
        '''
        Verifies the email entered during sign-up, if it is of the right format.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2 : string
        email entered, during sign-up
        
        Returns
        -------
        Boolean
        '''

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if(re.fullmatch(regex, email)):
            return True #right format email
        else:
            return False #user has to retry to enter the email
    
    def validateDisable(self, password_disable):
        '''
        Verifies if the password entered to disable GenX is right or not.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2 : string
        disabling password entered, during disable genx screen
        
        Returns
        -------
        Boolean
        '''

        if self.password == password_disable:
            return True #right password (ie: disable GenX)
        else:
            return False #wrong password (ie: retry)

class phone():
    '''
    Displays the phone simulation mode, its screen and its buttons.
    '''
    
    def signedInP(self, mainSurface, surfaceSize, backButton, genXStatus, cameraFeedButton, signedIn, visitorIdentificationButton, genXOnButton, genXOffButton):
        '''
        When the user is signed in and on the phone simulation mode, this is the main screen that is displayed.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        used to display the images
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''

        cameraFeedButton = pygame.transform.scale(cameraFeedButton, (200, 50))
        mainSurface.blit(signedIn, (0,0))
        mainSurface.blit(visitorIdentificationButton, (surfaceSize-450, surfaceSize-430))
        mainSurface.blit(cameraFeedButton, (surfaceSize-410, surfaceSize-360))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-70))
        
        #changes the GenX button to display on or off, depending on the status
        if genXStatus == False:
            mainSurface.blit(genXOffButton, (surfaceSize-390,surfaceSize/2))
        else:
            mainSurface.blit(genXOnButton, (surfaceSize-390,surfaceSize/2))
            
    def notSignedInP(self, mainSurface, surfaceSize, backButton, notSignedInP):
        '''
        When the user isn't signed in and on the phone simulation mode, this is the screen that is displayed.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        used to display the images
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''

        mainSurface.blit(notSignedInP, (0,0))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-150))
        
    def visitorId(self, mainSurface, surfaceSize, visitorIdScreen, updVisitorButton, backButton):
        '''
        When the user is on the visitor identification screen, this is what is displayed.

        Parameters
        ----------
        parameter1: instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        used to display the images
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''
        mainSurface.blit(visitorIdScreen, (0,0))
        mainSurface.blit(updVisitorButton, (surfaceSize-460, surfaceSize-300))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-60))

class outside():
    '''
    Displays the outside simulation mode, its screens and its buttons.
    '''
    
    def signedInO(self, mainSurface, surfaceSize, backButton, signedIn, voiceRecButton):
        '''
        When the user is signed in and on the outside simulation mode, this is the main screen that is displayed.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        used to display the images
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''
        
        mainSurface.blit(signedIn, (0,0))
        mainSurface.blit(voiceRecButton, (surfaceSize-450, surfaceSize-350))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-150))
        
    def notSignedInO(self, mainSurface, surfaceSize, backButton, notSignedInO):
        '''
        When the user isn't signed in and on the outside simulation mode, this is the screen that is displayed.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        used to display the images
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''
        mainSurface.blit(notSignedInO, (0,0))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-150))
        
    def voiceRec(self, mainSurface, surfaceSize, voiceRecScreen, startVoiceButton, stopVoiceButton, backButton):
        '''
        When the user is on the voice recording screen, this is what is displayed.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: pygame display file
        images displayed
        
        parameter3: integer
        width and height of the program
        
        rest of the parameters: pygame image file
        holds the images to be displayed on this screen
        
        Returns
        -------
        None
        '''

        mainSurface.blit(voiceRecScreen, (0,0))
        mainSurface.blit(startVoiceButton, (surfaceSize-430, surfaceSize-300))
        mainSurface.blit(stopVoiceButton, (surfaceSize-240, surfaceSize-300))
        mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-150))

class detection():
    '''
    Detects visitors (outside) and checks if a face is the owner's.
    '''
    
    def __init__(self):
        '''
        Runs when the detection object is created.
        Holds a variable which checks if the name of the visitor outside, if any, can be announced again (could be unknown too).

        Parameters
        ----------
        parameter1 : instance of the class (created)
        allows one to access variables of the class
        
        Returns
        -------
        None
        '''
        
        self.announced = False #checks if the name of the visitor outside, if any, can be announced again (could be unknown too)

    def visitorDet(self, img, trained_face_data):
        '''
        Detects visitors outside.
        Announces if an unknown visitor is outside and the name of a known one.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: image file
        visitor's image captured file
        
        parameter3: cv2
        model to detect faces
        
        Returns
        -------
        None
        '''

        gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #converts to Grey Scale
        face_coordinates = trained_face_data.detectMultiScale(gray_scale) #detects Faces

        for (x,y,w,h) in face_coordinates:
            #face is detected outside
            print("face detected outside")
            if self.announced == False:
                cv2.imwrite("visitor.jpg", img)
                img2_path = 'visitor.jpg'
                recog = False
                if os.path.isdir("visitors") and self.ownerDet(img2_path, trained_face_data) == False:
                    dir_list = os.listdir('visitors')
                    i = -1
                    for img in dir_list:
                        img1_path = 'visitors/' + img
                        i+=1
                    
                        #checks if the detected face of the visitor matches the picture of a known visitor
                        model_name = 'Facenet'

                        resp = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, enforce_detection=False, model_name = model_name)['verified']
                        if resp == True:
                            recog = True #the detected face of the visitor matches the picture of a known visitor 
                            break
                        
                    speak = Dispatch("SAPI.SpVoice").Speak
                    if recog == True:
                        print(dir_list[i] + ' is seen outside')
                        speak(dir_list[i] + "is outside") #announce the name of the known visitor detected
                        self.announced = True
                    else:
                        print("unknown visitor is seen outside")
                        speak("unknown visitor is outside") #announce that an unknown visitor is detected
                        self.announced = True
            else:
                #makes sure that a new visitor detected is announced, not the same one over and over again
                cv2.imwrite("visitorDupl.jpg", img)
                img1_path = 'visitor.jpg'
                img2_path = 'visitorDupl.jpg'
                
                model_name = 'Facenet'
                
                resp = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, enforce_detection=False, model_name = model_name)['verified']
                
                if resp == False:
                    #a new visitor is seen
                    self.announced = False #we can announce again
    
    def ownerDet(self, img2_path, trained_face_data):
        '''
        Detects if a face is the owner's.

        Parameters
        ----------
        parameter1 : instance of the class
        allows one to access variables of the class
        
        parameter2: string
        comparing image path
        
        parameter3: cv2
        model to detect faces
        
        Returns
        -------
        Boolean
        '''
        img1_path = "user_face.jpg"
        
        #checks if the face (passed in the parameter) matches the picture of the owner
        model_name = 'Facenet'

        resp = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, enforce_detection=False, model_name = model_name)['verified']
        return resp

def main():
    #-----------------------------Setup------------------------------------------------------#
    pygame.init() #prepares the pygame module for use
    surfaceSize = 600 #desired physical surface size, in pixels
   
    clock = pygame.time.Clock() #forces the frame rate to be slower

    mainSurface = pygame.display.set_mode((surfaceSize, surfaceSize)) #creates the surface of (width, height), and its window

    #-----------------------------Program Variable Initialization----------------------------#
    size = (224, 224) #size of the feed
    
    curRecI = 0 #current recording number of the inside feed
    curRecO = 0 #current recording number of the outside feed
    voiceRecNum = 0 #current voice recording number
    
    user = userInfo() #user object is created

    if os.path.isfile('Auth.txt') == True:
        with open('Auth.txt', 'r') as file:
            content = file.readlines()
        user.email = content[0].strip('\n')
        user.password = content[1].strip('\n')
        curRecI = int(content[3]) #updates the recording number of the inside feed
        curRecO = int(content[4]) #updates the recording number of the outside feed
        voiceRecNum = int(content[5]) #updates the voice recording number
   
    videoI = VideoWriter('tempInside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream for the inside feed
    videoO = VideoWriter('tempOutside.avi', VideoWriter_fourcc(*'MP42'), 25.0, (640, 480)) #opens the output video file stream for the outside feed
   
    #button image imports
    recordButton = pygame.image.load("../buttons/recordButton.png")
    cameraFeedButton = pygame.image.load("../buttons/cameraFeedButton.png")
    backButton = pygame.image.load("../buttons/backButton.png")
    retryButton = pygame.image.load("../buttons/retryButton.png")
    takePhotoButton = pygame.image.load("../buttons/takePhotoButton.png")
    nextButton = pygame.image.load("../buttons/nextButton.png")
    genXOnButton = pygame.image.load("../buttons/genXOnButton.png")
    genXOffButton = pygame.image.load("../buttons/genXOffButton.png")
    visitorIdentificationButton = pygame.image.load("../buttons/visitorIdentificationButton.png")
    updVisitorButton = pygame.image.load("../buttons/updVisitorButton.png")
    voiceRecButton = pygame.image.load("../buttons/voiceRecButton.png")
    startVoiceButton = pygame.image.load("../buttons/startVoiceButton.png")
    stopVoiceButton = pygame.image.load("../buttons/stopVoiceButton.png")
    insideSimButton = pygame.image.load("../buttons/insideSimButton.png")
    outsideSimButton = pygame.image.load("../buttons/outsideSimButton.png")
    phoneSimButton = pygame.image.load("../buttons/phoneSimButton.png")

    #resizing button images
    recordButton = pygame.transform.scale(recordButton, (200, 50))
    backButton = pygame.transform.scale(backButton, (200, 50))
    retryButton = pygame.transform.scale(retryButton, (200, 50))
    takePhotoButton = pygame.transform.scale(takePhotoButton, (200, 50))
    nextButton = pygame.transform.scale(nextButton, (200, 50))
    genXOnButton= pygame.transform.scale(genXOnButton, (200, 200))
    genXOffButton = pygame.transform.scale(genXOffButton, (200, 200))
    visitorIdentificationButton = pygame.transform.scale(visitorIdentificationButton, (300, 75))
    updVisitorButton = pygame.transform.scale(updVisitorButton, (300, 75))
    voiceRecButton = pygame.transform.scale(voiceRecButton, (320, 80))
    startVoiceButton = pygame.transform.scale(startVoiceButton, (90,75))
    stopVoiceButton = pygame.transform.scale(stopVoiceButton, (85,75))
    insideSimButton = pygame.transform.scale(insideSimButton, (300, 75))
    outsideSimButton = pygame.transform.scale(outsideSimButton, (300, 75))
    phoneSimButton = pygame.transform.scale(phoneSimButton, (300, 75))
   
    #GenX status images
    genXOnStatus = pygame.image.load("../genXOnStatus.png")
    genXOffStatus = pygame.image.load("../genXOffStatus.png")
    genXOnStatus = pygame.transform.scale(genXOnStatus, (200, 50))
    genXOffStatus = pygame.transform.scale(genXOffStatus, (200, 50))
    
    #screen image imports
    main = pygame.image.load("../screens/main.png") #load the main screen image
    disableGenX = pygame.image.load("../screens/disableGenX.png") #load the disabling genx screen image
    lockedOut = pygame.image.load("../screens/lockedOut.png") #load the locked out screen image
    signupScreen = pygame.image.load("../screens/signup.png") #load the sign-up screen image
    visitorIdScreen = pygame.image.load("../screens/visitorIdentification.png") #load the visitor identification screen image
    signedIn = pygame.image.load("../screens/signedIn.png") #load the signed in screen image
    notSignedInP = pygame.image.load("../screens/notSignedInP.png") #load the not signed in screen image for the phone screen
    notSignedInO = pygame.image.load("../screens/notSignedInO.png") #load the not signed in screen image for the outside screen
    voiceRecScreen = pygame.image.load("../screens/voiceRec.png") #load the voice recording screen image

    #initializes the color of the textbox of the input fields (like password)
    field_color1 = pygame.Color(207, 226, 243)
    field_color2 = pygame.Color(207, 226, 243)
    field_color3 = pygame.Color(207, 226, 243)
   
    #email field variables
    email = '' #email is currently empty (nothing inputted)
    text_box1 = pygame.Rect(surfaceSize-500, surfaceSize/2, 150, 50)
    text_active1 = False
   
    #password field variables
    password = '' #password is currently empty (nothing inputted)
    text_box2 = pygame.Rect(surfaceSize-500, (surfaceSize/2)+110, 150, 50)
    text_active2 = False
    
    #disable GenX password field variables
    password_disable = '' #disabling password is currently empty (nothing inputted)
    text_box3 = pygame.Rect((surfaceSize/2)-50, (surfaceSize/2)+110, 150, 50)
    text_active3 = False
    
    ranOnce = False
    clickPhoto = False
    
    #time variables
    startTime = 0 #start time of disable GenX screen
    totalTime = 0 #total time of the program
    alertTime = 0 #alert time of the locked out screen
    startTracked = False #makes sure the start time is only tracked once
    alertTracked = False #makes sure the alert time is only tracked once
    
    font = pygame.font.SysFont("Arial", 26) #renders Arial type font
    
    trained_face_data = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') #load the pre-trained face data from opencv, to see if a face is present
    
    retryPhoto = False #checks if the retry and next button can be displayed after the initial photo is taken
    retakePhoto = False #checks if the owner identification photo can be retaken by the user
    
    #set the audio parameters
    sample_rate = 44100
    duration = 5  # Recording duration in seconds

    #set up the sounddevice
    sd.default.samplerate = sample_rate
    sd.default.channels = 1 #mono

    audio_buffer = []
    recStart = False #checks if a voice recording was started
    
    state = "home" #current state of the program
    
    wasInside = False #checks to see if the program is on inside simulation mode
    
    sentMail = False #checks if a mail to the user is sent or not
    authorities = False #checks if the authorities are called or not
    
    #create objects for the phone, outside and detection simulation modes
    p = phone()
    o = outside()
    det = detection()
    
    tempEmail = ''
    tempPass = ''
   
    #-----------------------------Main Program Loop---------------------------------------------#
    while True:
        #-----------------------------Event Handling-----------------------------------------#
        ev = pygame.event.poll() #looks for any event
        if ev.type == pygame.QUIT: #checks for window close button click
            videoI.release()
            videoO.release()
            if os.path.isfile('tempInside.avi') == True:
                os.remove("tempInside.avi") #deletes the temporary recording file for the inside feed
                os.remove("tempOutside.avi") #deletes the temporary recording file for the outside feed
            if os.path.isfile('detected.jpg') == True:
                os.remove("detected.jpg") #deletes the detected person image
            if os.path.isfile('visitor.jpg') == True:
                os.remove("visitor.jpg") #deletes the visitor image
            if os.path.isfile('visitorDupl.jpg') == True:
                os.remove("visitorDupl.jpg") #deletes the duplicate visitor image
            if os.path.isfile('Auth.txt') == True:
                #updates the recording number in the user files
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()

                data[3] = str(curRecI) + '\n' #inside feed recording number updated
                data[4] = str(curRecO) + '\n' #outside feed recording number updated
                data[5] = str(voiceRecNum) #voice recording number updated
                with open('Auth.txt', 'w') as file:
                    file.writelines(data)
            break #ends the program
               
        #checks if a key is pressed
        if ev.type == pygame.KEYDOWN:
            if state == "signup":
                if text_active1:
                    #key is pressed on the email field
                    if ev.key == pygame.K_BACKSPACE:
                        #backspace is pressed
                        email = email[:-1] #removes the last character entered in the email field
                    else:
                        if ev.key != pygame.K_RETURN and len(email) < 40:
                            #makes sure the length of the email field is less than 40 and that the enter key is not inputted as a character
                            email += ev.unicode #adds the character inputted to the email
                if text_active2:
                    #key is pressed on the password field
                    if ev.key == pygame.K_BACKSPACE:
                        #backspace is pressed
                        password = password[:-1] #removes the last character entered in the password field
                    else:
                        if ev.key != pygame.K_RETURN and len(password) < 40:
                            #makes sure the length of the password field is less than 40 and that the enter key is not inputted as a character
                            password += ev.unicode #adds the character inputted to the password
            elif state == "disableGenX":
                if text_active3:
                    #key is pressed on the disable genx password field
                    if ev.key == pygame.K_BACKSPACE:
                        #backspace is pressed
                        password_disable = password_disable[:-1] #removes the last character entered in the disable genx password field
                    else:
                        if ev.key != pygame.K_RETURN and len(password_disable) < 40:
                            #makes sure the length of the disable genx password field is less than 40 and that the enter key is not inputted as a character
                            password_disable += ev.unicode #adds the character inputted to the disable genx password
                   
            #detects if the enter key is pressed
            if ev.key == pygame.K_RETURN:
                if state == "signup" and len(email) > 0 and len(password) > 0:
                    #enter key pressed in the sign-up screen
                    
                    if user.checkEmail(email):
                        #email entered is valid
                        tempEmail = email
                        tempPass = password
                        state = "identification" #moves on to the face identification screen
                    else:
                        #email entered is invalid and the user has to enter the email and password again
                        email = ''
                        password = ''
              
                if state == "disableGenX":
                    #enter key pressed in the disable genx screen
                    #checks if the disable genx password entered matches the password on sign-up
                    if user.validateDisable(password_disable) == True:
                        #the disable genx password entered matches the password on sign-up
                        state = "main" #moves on to the main screen
                        data[2] = "off\n" #genx is turned off
                        with open('Auth.txt', 'w') as file:
                            file.writelines(data)
                        password_disable = ''
                    else:
                        #the disable genx password entered doesn't match the password on sign-up
                        password_disable = '' #user has to re-enter the disable genx password
               
        if ev.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos() #gets the x and y position of the mouse, if a click occurs
            if state == "home":
                if pos[0] > surfaceSize-450 and pos[0] < surfaceSize-250 and pos[1] > surfaceSize-400 and pos[1] < surfaceSize-350:
                    #inside simulation mode is chosen
                    state = "main" #moves to the main screen
                    wasInside = True
                    #checks if the user has already signed up or not
                    if os.path.isfile('Auth.txt') == False:
                        #the user hasn't signed up
                        state = "signup" #the user is on the sign-up screen
                    else:
                        ranOnce = False
                elif pos[0] > surfaceSize-450 and pos[0] < surfaceSize-250 and pos[1] > surfaceSize-340 and pos[1] < surfaceSize-290:
                    #outside simulation mode is chosen
                    #checks if the user has already signed up or not
                    if os.path.isfile('Auth.txt') == False:
                        #the user hasn't signed up
                        state = "notSignedInO"
                    else:
                        #the user has signed up
                        state = "signedInO"
                        ranOnce = False
                elif pos[0] > surfaceSize-450 and pos[0] < surfaceSize-250 and pos[1] > surfaceSize-280 and pos[1] < surfaceSize-230:
                    #phone simulation mode is chosen
                    wasInside = False
                    genXStatus = False
                    #checks if the user has already signed up or not
                    if os.path.isfile('Auth.txt') == False:
                        #the user hasn't signed up
                        state = "notSignedInP"
                    else:
                        #the user has signed up
                        state = "signedInP"
                        ranOnce = False
                        with open('Auth.txt', 'r') as file:
                            content = file.readlines()
                        #updates the current status of genx to on or off
                        statusGenX = content[2]
                        if statusGenX.strip('\n') == "off":
                            genXStatus = False
                        else:
                            genXStatus = True
            elif state == "main":
                if pos[0] > surfaceSize-470 and pos[0] < surfaceSize-130 and pos[1] > surfaceSize-330 and pos[1] < surfaceSize-265:
                    #camera feed button is pressed
                    state = "cam" #moves to the camera feed screen
                    ranOnce = False
                elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-200 and pos[1] < surfaceSize-150:
                    #back button is pressed
                    state = "home" #moves back to the home screen
                    ranOnce = False
            elif (state == "cam"):
                if pos[0] > surfaceSize-260 and pos[0] < surfaceSize-60 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the outside feed
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
                elif pos[0] > surfaceSize-540 and pos[0] < surfaceSize-340 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the inside feed
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
                elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-60 and pos[1] < surfaceSize-10:
                    #back button is pressed
                    if wasInside == True:
                        state = "main" #moves to the main screen if the simulation mode chosen was inside
                    else:
                        state = "signedInP" #moves to the signed in phone screen if the simulation mode chosen was phone
                    ranOnce = False
            elif state == "signup":
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
                    #take the photo button is pressed
                    if os.path.isfile('user_face.jpg') == False:
                        clickPhoto = True #the user clicks the button to take their photo
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-350 and pos[0] < surfaceSize-150 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    #the button to retake the photo is clicked
                    os.remove("user_face.jpg") #deletes the previous user face image
                    retakePhoto = True #the user is allowed to retake their photos
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-180 and pos[0] < surfaceSize+20 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    #next button is pressed
                    state = "main" #moves to the main screen
                    ranOnce = False
            elif state == "disableGenX":
                #checks if the disable genx password field is clicked
                if text_box3.collidepoint(ev.pos):
                    text_active3 = True #disable genx password field is clicked
                else:
                    text_active3 = False
            elif state == "signedInO":
               if pos[0] > surfaceSize-450 and pos[0] < surfaceSize-130 and pos[1] > surfaceSize-350 and pos[1] < surfaceSize-270:
                   #voice recording button is pressed
                   state = "voiceRec" #moves to the voice recording screen
                   ranOnce = False
               elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-150 and pos[1] < surfaceSize-100:
                   #back button is pressed
                   state = "home" #moves to the home screen
                   ranOnce = False
            elif state == "voiceRec":
               if pos[0] > surfaceSize-430 and pos[0] < surfaceSize-340 and pos[1] > surfaceSize-300 and pos[1] < surfaceSize-225:
                    #audio recording starts
                    recStart = True
                    audio_buffer = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
               elif pos[0] > surfaceSize-240 and pos[0] < surfaceSize-155 and pos[1] > surfaceSize-300 and pos[1] < surfaceSize-225 and recStart == True:
                    #audio recording stops
                    output_file = "recording" +  str(voiceRecNum) + ".wav"
                    sd.wait()
                    sf.write(output_file, audio_buffer, sample_rate)
                    print("Recording saved as", output_file) #saves the voice recording
                    voiceRecNum += 1
                    recStart = False
               elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-150 and pos[1] < surfaceSize-100:
                    #back button is pressed
                    state = "signedInO" #moves to the signed in outside screen
                    ranOnce = False
            elif state == "signedInP":
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                if pos[0] > surfaceSize-450 and pos[0] < surfaceSize-150 and pos[1] > surfaceSize-430 and pos[1] < surfaceSize-355:
                    #visitor identification button is pressed
                    state = "visitorId" #moves to the visitor identification screen
                    ranOnce = False
                elif pos[0] > surfaceSize-390 and pos[0] < surfaceSize-190 and pos[1] > (surfaceSize/2) and pos[1] < (surfaceSize/2)+200:
                    #depending on the button press, changes the genx status
                    genXStatus = not(genXStatus)
                    if genXStatus == True:
                        statusGenX = "on"
                    else:
                        statusGenX = "off"
                elif pos[0] > surfaceSize-410 and pos[0] < surfaceSize-210 and pos[1] > surfaceSize-360 and pos[1] < surfaceSize-310:
                    #camera feed button is pressed
                    state = "cam" #moves to the camera feed screen
                    ranOnce = False
                elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-70 and pos[1] < surfaceSize-20:
                    #back button is pressed
                    state = "home" #moves to the home screen
                    ranOnce = False
                        
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                  
                data[2] = statusGenX
                
                #updates the 'Auth.txt' file to the current genx status
                if data[2].strip('\n') == "on":
                    genXStatus = True
                    statusGenX = "on"
                    data[2] = "on\n"
                else:
                    genXStatus = False
                    statusGenX = "off"
                    data[2] = "off\n"
                
                with open('Auth.txt', 'w') as file:
                    file.writelines(data)
            elif state == "visitorId":
                if pos[0] > surfaceSize-460 and pos[0] < surfaceSize-160 and pos[1] > surfaceSize-300 and pos[1] < surfaceSize-225:
                    source = str(Path.home() / "Downloads") +'/photos' #get the source of the photos

                    if os.path.isdir("visitors") == False:
                        path = os.path.join("", "visitors") 

                        os.mkdir(path) #create a folder for the photos

                    # gather all files
                    allfiles = os.listdir(source)
                     
                    # iterate on all files to move them to destination folder
                    for f in allfiles:
                        src_path = os.path.join(source, f)
                        dst_path = os.path.join('visitors/', f)
                        shutil.move(src_path, dst_path)
                elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-60 and pos[1] < surfaceSize-10:
                    #back button is pressed
                    state = "signedInP" #moves to the signed in phone screen
                    ranOnce = False
            elif state == "notSignedInP" or state == "notSignedInO":
                if pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-150 and pos[1] < surfaceSize-100:
                    #back button is pressed
                    state = "home" #moves to the home screen
                    ranOnce = False
                            
        #-----------------------------Program Logic---------------------------------------------#

        if state == "home":
            mainSurface.blit(main, (0,0))
            mainSurface.blit(insideSimButton, (surfaceSize-450,surfaceSize-400))
            mainSurface.blit(outsideSimButton, (surfaceSize-450,surfaceSize-340))
            mainSurface.blit(phoneSimButton, (surfaceSize-450,surfaceSize-280))
            
            if os.path.isfile('Auth.txt'):
                if ranOnce == False:
                    cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                    cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                    ranOnce = True
                   
                #reads an image from the video stream
                ret1, img1 = cap_1.read()
                ret2, img2 = cap_2.read()
                if not ret1 or not ret2:
                    break

                img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
                img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
               
                #converts the cv2 image format to a pygame image format for the inside feed
                displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
                displayImage1 = numpy.fliplr(displayImage1)
                displayImage1 = numpy.rot90(displayImage1)
                displayImage1 = pygame.surfarray.make_surface(displayImage1)
                
                #converts the cv2 image format to a pygame image format for the outside feed
                displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                displayImage2 = numpy.fliplr(displayImage2)
                displayImage2 = numpy.rot90(displayImage2)
                displayImage2 = pygame.surfarray.make_surface(displayImage2)
               
                videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
                videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
        elif state == "signup":
            mainSurface.blit(signupScreen, (0, 0))
           
            emailF = font.render(('Email: '), True, (255, 255, 255))
            mainSurface.blit(emailF, (surfaceSize-550, surfaceSize-340))
           
            #displays the email field text and textbox
            pygame.draw.rect(mainSurface, field_color1, text_box1)
            surf = font.render(email, True, 'black')
            mainSurface.blit(surf, (text_box1.x+5 , text_box1.y+5))
            text_box1.w = max(100, surf.get_width()+10)
           
            passwordF = font.render(('Password: '), True, (255, 255, 255))
            mainSurface.blit(passwordF, (surfaceSize-550, surfaceSize-230))
           
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

            img = cv2.flip(img, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            displayImage = numpy.fliplr(displayImage)
            displayImage = numpy.rot90(displayImage)
            displayImage = pygame.surfarray.make_surface(displayImage)
           
            #drawing each frame
            mainSurface.blit(displayImage, (0, 0)) #puts the camera image on the main surface
            
            if clickPhoto or retakePhoto:
                gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #converts to Grey Scale
                face_coordinates = trained_face_data.detectMultiScale(gray_scale) #detects Faces
            
                for (x,y,w,h) in face_coordinates:
                    #a face can be seen in the image of the owner
                    user.signUp(tempEmail, tempPass) #signup is finally completed
                    cv2.imwrite("user_face.jpg", img) #saves the owner's face
                    clickPhoto = False
                    retryPhoto = True
                    retakePhoto = False
            
            mainSurface.blit(takePhotoButton, (surfaceSize-570, surfaceSize-100)) #displays the take the photo button on the screen
                    
            if retryPhoto == True:
                mainSurface.blit(retryButton, (surfaceSize-350, surfaceSize-100)) #displays the retry button on the screen
                mainSurface.blit(nextButton, (surfaceSize-180, surfaceSize-100)) #displays the next button on the screen
           
        elif state == "main":
            mainSurface.blit(main, (0,0))
            mainSurface.blit(cameraFeedButton, (surfaceSize-470, surfaceSize-330))
            mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-200))
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
            
            #checks the current genx status
            with open('Auth.txt', 'r') as file:
                data = file.readlines()
            if data[2].strip('\n') == "off":
                #genx status is off
                mainSurface.blit(genXOffStatus, (surfaceSize-200, surfaceSize-50)) #displays the genx status as off
                startTime = 0
                alertTime = 0
                startTracked = False
                alertTracked = False
                authorities = False
            elif data[2].strip('\n') == "on":
                #genx status is on
                mainSurface.blit(genXOnStatus, (surfaceSize-200, surfaceSize-50)) #displays the genx status as on
                
                gray_scale = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) #converts to Grey Scale
                face_coordinates = trained_face_data.detectMultiScale(gray_scale) #detects Faces
                
                for (x,y,w,h) in face_coordinates:
                    #face is detected inside
                    print("face detected inside")
                    cv2.imwrite("detected.jpg", img1)
                    img1_path = 'user_face.jpg'
                    img2_path = 'detected.jpg'
                    if det.ownerDet(img2_path, trained_face_data) == True:
                        #owner is detected
                        print("Owner detected")
                        data[2] = "off\n"

                        with open('Auth.txt', 'w') as file:
                            file.writelines(data)
                    else:
                        #unknown person is inside the space
                        state = "disableGenX" #stranger is forced to disable genx
                
                #track for visitors, and announce if detected
                det.visitorDet(img2, trained_face_data)
                
        elif state == "cam":
            #buttons to record the inside or outside feed
            if wasInside == False:
                mainSurface.fill((0,0,0))
            mainSurface.blit(recordButton, (surfaceSize-540, surfaceSize-100)) #displays the record button on the screen for the inside camera feed
            mainSurface.blit(recordButton, (surfaceSize-260, surfaceSize-100)) #displays the record button on the screen for the outside camera feed
            mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-60))
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
           
            #drawing each frame for the inside feed
            mainSurface.blit(displayImage1, (0, 0)) #puts the camera image on the main surface for the inside feed
            #drawing each frame for the outside feed
            mainSurface.blit(displayImage2, (surfaceSize-300, 0)) #puts the camera image on the main surface for the inside feed
                
            #checks the current genx status
            with open('Auth.txt', 'r') as file:
                data = file.readlines()
            if data[2].strip('\n') == "off":
                #genx status is off
                mainSurface.blit(genXOffStatus, (surfaceSize-200, surfaceSize-50)) #displays the genx status as off
                startTime = 0
                alertTime = 0
                startTracked = False
                alertTracked = False
                authorities = False
            elif data[2].strip('\n') == "on":
                #genx status is on
                mainSurface.blit(genXOnStatus, (surfaceSize-200, surfaceSize-50)) #displays the genx status as on
                
                gray_scale = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) #converts to Grey Scale
                face_coordinates = trained_face_data.detectMultiScale(gray_scale) #detects Faces
                
                for (x,y,w,h) in face_coordinates:
                    #face is detected inside
                    print("face detected inside")
                    cv2.imwrite("detected.jpg", img1)
                    img1_path = 'user_face.jpg'
                    img2_path = 'detected.jpg'
                    if det.ownerDet(img2_path, trained_face_data) == True:
                        #owner is detected
                        print("Owner detected")
                        data[2] = "off\n"

                        with open('Auth.txt', 'w') as file:
                            file.writelines(data)
                    else:
                        #unknown person is inside the space
                        state = "disableGenX" #stranger is forced to disable genx
                
                #track for visitors, and announce if detected
                det.visitorDet(img2, trained_face_data)

        elif state == "disableGenX":
            if authorities == False:
                if (startTracked == False):
                    startTime = pygame.time.get_ticks() #stores the start time of the disable genx mode
                    startTracked = True
                mainSurface.blit(disableGenX, (0, 0)) #displays the disabling genx screen image
                
                totalTime = pygame.time.get_ticks() #stores the total time of the program
                
                renderedText = font.render(str((int(totalTime/1000)) - (int(startTime/1000))), 1, pygame.Color("white")) #displays the timer till 1 minute
                mainSurface.blit(renderedText, (surfaceSize-530,surfaceSize-100))
                
                text_box3.x = surfaceSize-420
                text_box3.y = surfaceSize-250
                
                #displays the password field text and textbox
                pygame.draw.rect(mainSurface, field_color3, text_box3)
                surf = font.render(password_disable, True, 'black')
                mainSurface.blit(surf, (text_box3.x, text_box3.y))
                text_box3.w = max(100, surf.get_width()+10)
                    
                #changes the color of the field that is clicked
                if text_active3:
                    field_color3 = pygame.Color('red')
                else:
                    field_color3 = pygame.Color(207, 226, 243)
                
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                
                if data[2].strip('\n') == "off":
                    #genx is turned off
                    state = "main" #redirects to the main screen
                    password_disable = ''
                
                if (int(totalTime/1000)) - (int(startTime/1000)) >= 60 and data[2].strip('\n') == "on":
                    #1 minute has passed
                    mainSurface.blit(lockedOut, (0, 0)) #displays the locked out screen image
                    if sentMail == False:
                        user.sendMail('detected.jpg') #mail is sent to the user, alerting them about an unknown presence within the space
                        sentMail = True
                    #10 minute FINAL alert timer is started
                    if (alertTracked == False):
                        alertTime = pygame.time.get_ticks() #stores the start alert time
                        alertTracked = True
                    if (int(totalTime/1000)) - (int(alertTime/1000)) >= 600 and data[2].strip('\n') == "on":
                        if authorities == False:
                            print("Authorities are called!!!") #10 minutes have passed and authorities are called to the location of the space
                            authorities = True
            else:
                mainSurface.blit(lockedOut, (0, 0)) #displays the locked out screen image permanently
        elif state == "signedInO":
            o.signedInO(mainSurface, surfaceSize, backButton, signedIn, voiceRecButton)
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
        elif state == "notSignedInO":
            o.notSignedInO(mainSurface, surfaceSize, backButton, notSignedInO)
        elif state == "voiceRec":
            o.voiceRec(mainSurface, surfaceSize, voiceRecScreen, startVoiceButton, stopVoiceButton, backButton)
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
        elif state == "signedInP":
            p.signedInP(mainSurface, surfaceSize, backButton, genXStatus, cameraFeedButton, signedIn, visitorIdentificationButton, genXOnButton, genXOffButton)
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
        elif state == "notSignedInP":
            p.notSignedInP(mainSurface, surfaceSize, backButton, notSignedInP)
        elif state == "visitorId":
            p.visitorId(mainSurface, surfaceSize, visitorIdScreen, updVisitorButton, backButton)
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1) #sets up the video capture device for the outside feed
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format for the inside feed
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format for the outside feed
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
       
        #-----------------------------Drawing Everything-------------------------------------#

        pygame.display.flip() #displays the surface
       
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()