import time
import os
import cv2 as cv
import Adafruit_BBIO.GPIO as GPIO
import threading

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv.CascadeClassifier("/home/debian/ece350_final_projectV2/haar_face.xml")
sysfsDir = "/sys/class/gpio/"

# Log file to record access attempts
logFile = 'logfile.txt' 

# Dictionary of users and their passwords
users = {
        "Joel": '1234',
        "Jordan": '4321',
        "Operator": '5555'
        }
Passwords = users.values()
# GPIO pin definitions for LEDs. Indicators for access granted/denied
ledGreen = "P8_9"
ledRed = "P8_8"





#This function writes the value passed to the file in the path
def WRITEsysfs (GPIOpin, filename, value):
    global sysfsDir
    cmdFile=sysfsDir + GPIOpin + "/" + filename
    #print(f'     write "{value}" into file {cmdFile}')
    fo = open(cmdFile ,"w")  
    fo.write(value)
    fo.close()
    return
    
#This function reads the value within a file
def READsysfs (GPIOpin, filename="value"):
    global sysfsDir
    cmdFile=sysfsDir + GPIOpin + "/" + filename
    #print(f"     read file:     {cmdFile}")
    fo = open(cmdFile, "r")
    ReadVal=fo.read()
    #print(f"     The value I am reading is = {ReadVal}")
    fo.close()
    return ReadVal

class FinalProject():

    # ---------------- Keypad configuration ----------------

    # C1, C2, C3, C4 columns of the keypad
    # P8_7   P8_8   P8_9   P8_10  
    COLSP8 = ["P9_12",   "P9_15",   "P9_23",   "P9_25"]
    COLS   = ["gpio60", "gpio48", "gpio49", "gpio117"]
    
    # R1, R2, R3, R4 rows of the keypad
    # P8_11   P8_12   P8_13   P8_14  
    ROWSP8 = ["P9_27",  "P9_30",  "P9_41",  "P8_7"]
    ROWS   = ["gpio115", "gpio112", "gpio20", "gpio66"]
    
    # Row-Column and the key value table
    KEYPAD = [                                          
    ["1",  "2",  "3",  "A"],
    ["4",  "5",  "6",  "B"],
    ["7",  "8",  "9",  "C"],
    ["*",  "0",  "#",  "D"]
    ]

    # This is the vector that is read from the keypad
    # 0b0000 means nothing pressed. Any "1" indicates a pushed key
    KEYread = [ 0b0000, 0b0000, 0b0000, 0b0000 ]

    # ------------------------------------------------------
 
    def __init__(self):
        # --- Initialize the GPIO pins for keypad scanning ----
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setup(ledGreen,GPIO.OUT)
        GPIO.setup(ledRed,GPIO.OUT)
        # Configure the pull up resistors. Can't do it in sysfs
        # Initialize all rows to input. 
        for i in range(4):
            GPIO.setup(self.ROWSP8[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.COLSP8[i], GPIO.OUT, pull_up_down=GPIO.PUD_UP)
        # ------------------------------------------------------

    # Scan the keypad and return the first key found
    def getKeySingle(self):
        # Set columns to output=0 sequentially
        for i in range(len(self.COLS)):
            # pull down the column we are reading
            WRITEsysfs(self.COLS[i],"direction","out")
            WRITEsysfs(self.COLS[i],"value","0")
            for j in range(len(self.ROWS)):
                r=READsysfs(self.ROWS[j])
                # only use 1 char from the sysfs file. Strip the newline
                if r[0]=="0":
                    # found a pushed key. one is enough.
                    # set the column back to input before returning
                    WRITEsysfs(self.COLS[i],"direction","in")
                    return self.KEYPAD[j][i]
            WRITEsysfs(self.COLS[i],"direction","in")
        return ""

# Camera loop function to run in a separate thread
def camera_loop(face_detection):
    LogiC270 = cv.VideoCapture(0)
    # face_detection will be used to signal when a face is detected
    try:
        while True:
            sucess, C270img = LogiC270.read()
            #Adding text to screen
            FPS = 1
            FPSstr=f"{FPS:3.1f} fps"
            cv.putText(C270img,FPSstr,(10,30),cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)
            # gray scale conversion for face detection
            gray = cv.cvtColor(C270img, cv.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # If faces are detected, set the event; otherwise, clear it
            if(len(faces) > 0):
                face_detection.set()
            else:
                face_detection.clear()
            for(x,y,w,h) in faces:
                cv.rectangle(C270img, (x,y), (x+w, y+h), (255,0,0),2)
            cv.imshow("CAPTURE",C270img)
            cv.waitKey(1)
    finally:
        LogiC270.release()


if __name__ == '__main__':
    print("Setting up camera and keypad ...")
    # Initialize the FinalProject class
    keyp = FinalProject() 
    
    # Create a threading.Event object to signal when a face is detected
    face_detected = threading.Event()
    
    #Starting a camera thread that will run independently from keypad
    camera_thread = threading.Thread(target=camera_loop, args=(face_detected,))
    camera_thread.start()
    
    UserEntry = ""
    NumberofAttempts = 0    #Used to keep track on the attempts of entering passcode
    try:
        while True:
              print("face detected: " + str(face_detected) + "\n")
              # Get a single key press from the keypad
              digit = ""
              while digit =="":          
                  digit=keyp.getKeySingle()
              
              # If user presses '#', it indicates the end of password entry. Otherwise, add the digit to the password string
              if(digit=='#'):
                  time.sleep(0.5) # Debounce delay 
                  # Check if a face is detected before validating the password                     
                  if(not face_detected.is_set()):
                    print("Please make sure your face is in view and re-enter password")
                    UserEntry = ""
                    continue
                  else:      
                      currUser = "Jordan" #store current user
                      if(UserEntry in Passwords):
                          #find user from users dictionary
                          GPIO.output(ledGreen,GPIO.HIGH)
                          # We loop through the dictionary to find the user corresponding to the entered password
                          for key in users.keys():
                            if users[key] == UserEntry:
                              currUser = key    #Saves name of user
                          print("\nCorrect password: " + currUser + " Welcome!\n")
                          # If special code for operator is entered, display log file
                          if(currUser == "Operator"):
                            os.system('cat logfile.txt')
                          #log the time and user into log file
                          os.system('echo %s %s >> %s' % (currUser, str(time.time()), logFile))
                          time.sleep(1.5)
                          GPIO.output(ledGreen,GPIO.LOW)
                      else:
                          # If password is incorrect, indicate failure using red LED
                          print("\nIncorrect password :(")
                          GPIO.output(ledRed,GPIO.HIGH)
                          
                          time.sleep(1)
                          NumberofAttempts +=1
                          GPIO.output(ledRed,GPIO.LOW)
                          if(NumberofAttempts == 3):
                              print("1 Attempt remaining before 15s lock\n")
                              os.system('echo 3 attempts at %s >> %s' % (str(time.time()), logFile))
                              GPIO.output(ledRed,GPIO.HIGH)
                              time.sleep(3)
                              GPIO.output(ledRed,GPIO.LOW)
                          if(NumberofAttempts == 4):
                              print("Please try again later")
                              os.system('echo 4 attempts at %s >> %s' % (str(time.time()), logFile))
                              #create and save current image file to BBB"
                              GPIO.output(ledRed,GPIO.HIGH)
                              # Lock system for 15 seconds
                              time.sleep(15)
                              NumberofAttempts = 0
                              GPIO.output(ledRed,GPIO.LOW)
                   
              else:    
                  UserEntry += str(digit)             # cumulative string
                  print("You entered: " + str(digit))     # the character pressed
                  time.sleep(0.5)  
              
        
    except KeyboardInterrupt:
        print("\nKeypad application is done...  BYE...")

    finally:
        GPIO.cleanup()
        cv.destroyAllWindows()
