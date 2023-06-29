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
from deepface import DeepFace
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class userInfo():
    """Holds user information- email and password."""
   
    def signUp(self, email, password):
        """Creates a file- "Auth.txt" that holds the details of the user, which they inputted, during sign-up."""
       
        #the email and password of the user is stored in the file "Auth.txt"
        file = open("Auth.txt","w")
        file.write (email)
        file.write ("\n")
        file.write (password)
        file.write ("\n")
        file.write ("off")
        file.close()

def SendMail(ImgFileName):
    with open(ImgFileName, 'rb') as f:
        img_data = f.read()

    msg = MIMEMultipart()
    msg['Subject'] = 'PERSON SEEN INSIDE THE HOUSE'

    text = MIMEText("ALERT! A PERSON SEEN INSIDE THE HOUSE, HAS FAILED TO ENTER THE PASSWORD TO DISABLE GENX. DISABLE GENX IF YOU KNOW THE PERSON OR THE AUTHORITIES WILL BE CALLED TO YOUR LOCATION WITHIN 10 MINUTES.")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('1sareensha@hdsb.ca', 'lcviruxiygyvaexu')
    s.sendmail('1sareensha@hdsb.ca', '1sareensha@hdsb.ca', msg.as_string())
    s.quit()

def main():
    #-----------------------------Setup------------------------------------------------------#
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
    recordButton = pygame.image.load("../buttons/recordButton.png") #load the record button image
    cameraFeedButton = pygame.image.load("../buttons/cameraFeed.png") #load the camera feed button image
    backButton = pygame.image.load("../buttons/backButton.png") #load the back button image
    retryButton = pygame.image.load("../buttons/retryButton.png") #load the retry button image
    takePhotoButton = pygame.image.load("../buttons/takePhotoButton.png") #load the take the photo button image
    nextButton = pygame.image.load("../buttons/nextButton.png") #load the next button image
   
    #resizing button images
    recordButton = pygame.transform.scale(recordButton, (200, 50))
    backButton = pygame.transform.scale(backButton, (200, 50))
    retryButton = pygame.transform.scale(retryButton, (200, 50))
    takePhotoButton = pygame.transform.scale(takePhotoButton, (200, 50))
    nextButton = pygame.transform.scale(nextButton, (200, 50))
   
    #status of the genx
    genxOn = pygame.image.load("../genxOn.png") #load the genX on status image
    genxOff = pygame.image.load("../genxOff.png") #load the genX off status image
    genxOn = pygame.transform.scale(genxOn, (200, 50))
    genxOff = pygame.transform.scale(genxOff, (200, 50))
    state = "disableGenX"
   
    #screen image imports
    main = pygame.image.load("../mainScreen.png") #load the main screen image
    disableGenX = pygame.image.load("../disableGenX.png") #load the disabling genx screen image
    lockedOut = pygame.image.load("../lockedOut.png")
    signupScreen = pygame.image.load("../signup.png") #load the sign-up screen image
   
    #initializes the color of the textbox of the email and password fields
    field_color1 = pygame.Color(207, 226, 243)
    field_color2 = pygame.Color(207, 226, 243)
    field_color3 = pygame.Color(207, 226, 243)
   
    #email field variables
    email = '' #email is currently empty (nothing inputted)
    text_box1 = pygame.Rect((surfaceSize/2)-50, surfaceSize/2, 150, 50)
    text_active1 = False
   
    #password field variables
    password = '' #password is currently empty (nothing inputted)
    text_box2 = pygame.Rect((surfaceSize/2)-50, (surfaceSize/2)+110, 150, 50)
    text_active2 = False
    
    #disable genx password field variables
    password_disable = ''
    text_box3 = pygame.Rect((surfaceSize/2)-50, (surfaceSize/2)+110, 150, 50)
    text_active3 = False
   
    user = userInfo() #user object is created
   
    #checks if the user has already signed up or not
    if os.path.isfile('Auth.txt') == False:
        #the user hasn't signed up
        state = "signup" #the user is on the sign-up screen
   
    font = pygame.font.Font('../Algerian.ttf', 32) #renders Algerian type font
   
    ranOnce = False
    clickPhoto = False
    
    startTime = 0
    totalTime = 0
    alertTime = 0
    startTracked = False
    
    font = pygame.font.SysFont("Arial", 26)  #Create a font object 
    
    # Load pre-trained face data from open cv
    trained_face_data = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
   
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
            if state == "signup":
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
            elif state == "disableGenX":
                if text_active3:
                    #key is pressed on the disable genx password field
                    if ev.key == pygame.K_BACKSPACE:
                        #backspace is pressed
                        password_disable = password_disable[:-1] #removes the last character entered in the disable genx password field
                    else:
                        if ev.key != pygame.K_RETURN and len(password_disable) < 14:
                            #makes sure the length of the disable genx password field is less than 14 and that the enter key is not inputted as a character
                            password_disable += ev.unicode #adds the character inputted to the disable genx password
                   
            #detects if the enter key is pressed
            if ev.key == pygame.K_RETURN:
                if state == "signup" and len(email) > 0 and len(password) > 0:
                    #sign-up process
                    
                    if "@gmail.com" in email:
                        state = "identification"
                    else:
                        email = ''
                        password = ''
              
                if state == "disableGenX":
                    with open('Auth.txt', 'r') as file:
                        data = file.readlines()
                    data[1] = data[1].replace('\n', '')
                    if data[1] == password_disable:
                        state = "main"
                        startTracked = False
                    else:
                        password_disable = ''
               
        if ev.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos() #gets the x and y position of the mouse, if a click occurs
            if state == "main":
                if pos[0] > surfaceSize-470 and pos[0] < surfaceSize-130 and pos[1] > surfaceSize-300 and pos[1] < surfaceSize-235:
                    state = "cam"
                    ranOnce = False
            if (state == "cam"): #detects for a mouse press on one of the camera feed screens
                if pos[0] > surfaceSize-260 and pos[0] < surfaceSize-60 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the inside feed
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
                if pos[0] > surfaceSize-540 and pos[0] < surfaceSize-340 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50: #checks if the record button is clicked in the outside feed
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
                elif pos[0] > surfaceSize-400 and pos[0] < surfaceSize-200 and pos[1] > surfaceSize-60 and pos[1] < surfaceSize-10:
                    state = "main"
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
                    clickPhoto = True
                    user.signUp(email, password)
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-350 and pos[0] < surfaceSize-150 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    os.remove("user_face.jpg") #deletes the previous user face image
                    clickPhoto = True
                elif os.path.isfile('user_face.jpg') and (pos[0] > surfaceSize-180 and pos[0] < surfaceSize+20 and pos[1] > surfaceSize-100 and pos[1] < surfaceSize-50):
                    state = "main"
                    ranOnce = False
            elif state == "disableGenX":
                #checks if the disable genx password field is clicked
                if text_box3.collidepoint(ev.pos):
                    text_active3 = True #disable genx password field is clicked
                else:
                    text_active3 = False

        #-----------------------------Program Logic---------------------------------------------#
        if state == "signup":
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
            #the user is on the owner identification screen
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
            #the user is on the main screen
            mainSurface.blit(main, (0,0))
            mainSurface.blit(cameraFeedButton, (surfaceSize-470, surfaceSize-300))
            
            totalTime = pygame.time.get_ticks() #stores the total time of the program
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1)
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
           
            mainSurface.blit(displayImage1, (0, 0)) #puts the inside camera feed on the screen
            mainSurface.blit(displayImage2, (300, 0)) #puts the outside camera feed on the screen
            
            with open('Auth.txt', 'r') as file:
                data = file.readlines()
            if data[2] == "off":
                startTime = False
                alertTime = 0
                startTracked = False
            elif data[2] == "on":
                # Converts to Grey Scale
                gray_scale = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                
                # Detects Faces
                face_coordinates = trained_face_data.detectMultiScale(gray_scale)
                
                for (x,y,w,h) in face_coordinates:
                        #face is detected
                        print("face detected")
                        cv2.imwrite("detected.jpg", img1)
                        img1_path = 'C:/Users/shaur/OneDrive/Documents/GitHub/final-project-Rye06/version4/user_face.jpg'
                        img2_path = 'C:/Users/shaur/OneDrive/Documents/GitHub/final-project-Rye06/version4/detected.jpg'
                        
                        #checks if the detected face matches the picture of the owner
                        model_name = 'Facenet'

                        resp = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, enforce_detection=False, model_name = model_name)['verified']
                        if resp == True:
                            #owner is detected
                            print("Owner detected")
                            data[2] = "off"
         
                            with open('Auth.txt', 'w') as file:
                                file.writelines(data)
                        else:
                            state = "disableGenX" #stranger inside the space is forced to disable genx
                            startTracked = False

        elif state == "cam":
            #the user is on the camera feed screens
            #buttons
            mainSurface.blit(recordButton, (surfaceSize-260, surfaceSize-100)) #displays the record button on the screen for the inside camera feed
            mainSurface.blit(recordButton, (surfaceSize-540, surfaceSize-100)) #displays the record button on the screen for the outside camera feed
            mainSurface.blit(backButton, (surfaceSize-400, surfaceSize-60)) #displays the record button on the screen for the back button
            
            if ranOnce == False:
                cap_1 = cv2.VideoCapture(0) #sets up the video capture device for the inside feed
                cap_2 = cv2.VideoCapture(1)
                ranOnce = True
               
            #reads an image from the video stream
            ret1, img1 = cap_1.read()
            ret2, img2 = cap_2.read()
            if not ret1 or not ret2:
                break

            img1 = cv2.flip(img1, 1) #the required image processing to format it correctly
            img2 = cv2.flip(img2, 1) #the required image processing to format it correctly
           
            #converts the cv2 image format to a pygame image format
            displayImage1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            displayImage1 = numpy.fliplr(displayImage1)
            displayImage1 = numpy.rot90(displayImage1)
            displayImage1 = pygame.surfarray.make_surface(displayImage1)
            
            #converts the cv2 image format to a pygame image format
            displayImage2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            displayImage2 = numpy.fliplr(displayImage2)
            displayImage2 = numpy.rot90(displayImage2)
            displayImage2 = pygame.surfarray.make_surface(displayImage2)
           
            videoI.write(img1) #saves the inside feed to the temporary video file, to be extracted
            videoO.write(img2) #saves the outside feed to the temporary video file, to be extracted
           
            #drawing each frame for the inside feed
            mainSurface.blit(displayImage1, (0, 0)) #puts the camera image on the main surface
            #drawing each frame for the outside feed
            mainSurface.blit(displayImage2, (300, 0)) #puts the camera image on the main surface
            
            with open('Auth.txt', 'r') as file:
                data = file.readlines()
            if data[2] == "off":
                startTime = False
                alertTime = 0
                startTracked = False
            elif data[2] == "on":
                # Converts to Grey Scale
                gray_scale = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                
                # Detects Faces
                face_coordinates = trained_face_data.detectMultiScale(gray_scale)
                
                for (x,y,w,h) in face_coordinates:
                        #face is detected
                        print("face detected")
                        cv2.imwrite("detected.jpg", img1)
                        img1_path = 'C:/Users/shaur/OneDrive/Documents/GitHub/final-project-Rye06/version4/user_face.jpg'
                        img2_path = 'C:/Users/shaur/OneDrive/Documents/GitHub/final-project-Rye06/version4/detected.jpg'
                        
                        #checks if the detected face matches the picture of the owner
                        model_name = 'Facenet'

                        resp = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, enforce_detection=False, model_name = model_name)['verified']
                        if resp == True:
                            #owner is detected
                            print("Owner detected")
                            data[2] = "off"
         
                            with open('Auth.txt', 'w') as file:
                                file.writelines(data)
                        else:
                            state = "disableGenX" #stranger inside the space is forced to disable genx
                            startTracked = False
                            
        elif state == "disableGenX":

            if (startTracked == False):
                startTime = pygame.time.get_ticks() #stores the start time
                startTracked = True
            mainSurface.blit(disableGenX, (0, 0)) #displays the disabling genx screen image
            
            renderedText = font.render(str((int(totalTime/1000)) - (int(startTime/1000))), 1, pygame.Color("white"))
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
            
            if (int(totalTime/1000)) - (int(startTime/1000)) >= 60:
                #1 minute has passed
                #10 minute alert timer is started
                SendMail('detected.jpg') #a mail is sent to the user, alerting them about an unknown presence within the house
                #10 minute alert timer is started
                if (startTracked == False):
                    alertTime = pygame.time.get_ticks() #stores the start alert time
                    startTracked = True
                with open('Auth.txt', 'r') as file:
                    data = file.readlines()
                if (int(totalTime/1000)) - (int(alertTime/1000)) >= 600 and data[2] == "on":
                    mainSurface.blit(lockedOut, (0, 0)) #displays the locked out screen image
                    print("Authorities are called!!!")
       
        #-----------------------------Drawing Everything-------------------------------------#

        pygame.display.flip() #displays the surface
       
        clock.tick(24) #forces the frame rate to be slower

    pygame.quit() #closes the window, once we leave the loop

main()

#TO DO:
#multiple ppl detection