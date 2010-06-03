#*******************************************************************************************************************
# Eden Kung and Matt Clark
# Comp 190 - Enabling Technologies
# Myst/Resident Evil for people with visual impairments
#*******************************************************************************************************************
# go to the program directory before importing my files
import os, sys

mydir = os.path.dirname(sys.argv[0])
if mydir:
  os.chdir(mydir)

from UserDict import UserDict
import pickle         #for loading and saving data
import sys            #for sys.exit()
import pySonic, time  #for fmod
import pyTTS          #for text to speech
from threading import Timer


#global currentRoom, roomDict
currentRoom = None
roomDict = None

#******** PYGAME INITIALIZATION ********************************************************************
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((750, 550))
pygame.display.set_caption('Descent Into Madness')
pygame.mouse.set_visible(0)

titleScreen = pygame.image.load('images\Descent Into Madness.jpg')
tSrect = titleScreen.get_rect()

screen.blit(titleScreen, tSrect)
pygame.display.flip()


#************* CLASS TYPES *************************************************************************
class Room(UserDict):
    "Room"
    def __init__(self):
        UserDict.__init__(self)

    def construct(self, stringName, soundName, soundDescription, connectingRooms, examineItems):
        self["name"]=stringName
        self["sName"]=soundName
        self["sDescription"]=soundDescription
        self["rooms"]=connectingRooms
        self["items"]=examineItems
        
class Item(UserDict):
    "Items"
    def __init__(self):
        UserDict.__init__(self)

    def construct(self, stringName, soundName, soundDescription, canYouTakeIt):
        self["name"]=stringName
        self["sName"]=soundName
        self["sDescription"]=soundDescription
        #takable: 0 = not takable, 1 = takable
        self["takable"]=canYouTakeIt

class DeadException(Exception):
    "Thrown when player dies"
    def __init__(self):
        pass


#*************** ACTIONS **************************************************************************
def useItem():
    "When an item is used"
    global currentRoom, roomDict
    #prints will have to be replaced by sound files
    #print "What item will you use?"
    playSound("whatItemWillYouUse.mp3")
    #select will return the item selected
    #itemUsed = select(items that are in the inventory room)
    itemUsed = select([elem for elem in roomDict["inventory"]["items"]])
    if itemUsed == "esc":
        return 0
    #if itemUsed == 0:   #this should never happen assuming you can use player
    #    print "No items in inventory"
    #    return 0

    #print "Use this on what?"
    playSound("useThisOnWhat.mp3")
    #select amongst items still not picked up or used
    usedOn = select([elem for elem in roomDict[currentRoom]["items"]])
    if usedOn == 0:
        #print "No examinable items in this room"
        playSound("noItems.mp3")
        return 0
    elif usedOn == "esc":
        return 0

    successfulUse = 0
    #itemUses[itemUsed["name]] is the list of usedOn and function for a given itemUsed
    #e.g. itemUses[player] is returns [["journal", save], ["painting", punch]]
    for elem in itemUses[itemUsed["name"]]:      #elem is a single usedOn, function combination 
#        if itemUses[itemUsed["name"]][0] == usedOn["name"]:
#            itemUses[itemUsed["name"]][1]() 
        if elem[0] == usedOn["name"]:
            elem[1]()   #elem[1] is the function to call upon successful use
            successfulUse = 1
            
    if successfulUse == 0:
        #print "Nothing happened"
        playSound("nothingHappened.mp3")

def examine():
    "Examine objects in room"
    global currentRoom, roomDict
    if len(roomDict[currentRoom]["items"]) == 0:
        #print "There are no items in this room"
        playSound("noItems.mp3")
    else:            
        #print "The following items in this room seem suspicious"
        soundInterrupt = playSound("itemsSeemSuspicious.mp3")
        if soundInterrupt:
          pass
        else:
          for item in roomDict[currentRoom]["items"]:              
              #print item["name"]
              soundInterrupt = playSound(item["sName"])
              if soundInterrupt:
                break
              else:
                pass
    while 1:
      #print "What would you like to examine?"
      playSound("whatToExamine.mp3")
      examined = select([elem for elem in roomDict[currentRoom]["items"]] + [roomDict[currentRoom]])
      if examined == "esc":
          return 0
      
      #print examined["sDescription"]
      playSound(examined["sDescription"])

      #rooms can't be takable, so break if it's a room
      if examined.__doc__ == "Room":
          pass
      elif examined["takable"]==1:
          #print "Would you like to take this item?"
          soundInterrupt = playSound("takeItem.mp3")
          yesOrNo = selectOption(yesNoList)
          if (yesOrNo == "yes"):
              roomDict["inventory"]["items"].append(examined)
              roomDict[currentRoom]["items"].remove(examined)
              #print "You have taken the " + examined["name"]
              soundInterrupt = playSound("youHaveTakenThe.mp3")
              if soundInterrupt:
                pass
              else:
                playSound(examined["sName"])

      playSound("continueExamine.mp3")
      yesOrNo = selectOption(yesNoList)
      if yesOrNo == "no":
        break
      else:
        pass

def move():
    "When player wants to move"
    global currentRoom, roomDict

    if len(roomDict[currentRoom]["rooms"]) == 0:
      #print "You can't move anywhere"
      playSound("cantMoveAnywhere.mp3")
      return 0
    
    #print "Where do you want to move?"
    playSound("whereToMove.mp3")
    moveTo = select(roomDict[currentRoom]["rooms"])
    if moveTo == "esc":
        return 0
    currentRoom = moveTo["name"]
    #print "You are now in the " + currentRoom["name"]
    soundInterrupt = playSound("youAreNowInThe.mp3")
    if soundInterrupt:
      return 0
    playSound(roomDict[currentRoom]["sName"])
    if soundInterrupt:
      return 0
    playSound(roomDict[currentRoom]["sDescription"])
    

#************** MENU FUNCTIONS **************************************************************************
def menu():
    "Menu"
    while 1 == 1:        
        #print "Welcome to the game, use the spacebar to select, the esc key to cancel, and any other key to scroll"
        playSound("descentIntoMadness.mp3")
        playSound("menuInstructions.mp3")
        #print "Choose a menu option"
        playSound("menu.mp3")
        menuOption = selectOption(menuList)

        #to prevent accidental quits
        if menuOption == "esc":
            pass
        #elif menuOption == loadGame:
        #    loadGame()
        else: 
            menuOption()

def newGame():
    "New Game"
    global currentRoom
    currentRoom = operatingRoom["name"]

    #print "You awaken to find yourself strapped to a operating table"
    playSound("intro.mp3")
    #playSound("instructions.mp3")
    gameLoop()
    
def loadGame():
    "Load Game"
    global currentRoom, roomDict
    #retrieve currentRoom and roomDict
    #print "Please select a save slot to load"
    playSound("selectLoad.mp3")
    try:
		slot = selectOption(saveList)
		print slot
		fileHandle = open ( slot )
		[currentRoom, roomDict] = pickle.load ( fileHandle )
		fileHandle.close()
    except IOError:
      #print "That file is empty or doesn't exist. You will now be returned to the main menu"
      playSound("loadError.mp3")
      return 0

    gameLoop()

def save():
    "Save"
    global currentRoom, roomDict
    #write out roomDict and currentRoom to the file
    #print "Choose a slot to save your game"
    playSound("saveSlot.mp3")
    try:
      slot = selectOption(saveList)
      fileHandle = open ( slot, 'w' )
      pickle.dump ( [currentRoom, roomDict], fileHandle ) #hopefully this works
      fileHandle.close()
      #print "Your game was successfully saved"
      playSound("saveSuccessful.mp3")
    except IOError:
      #print "Error while saving game. Game was not saved."
      playSound("saveError.mp3")    

def options():
    "Set the game options"
    #set voice speed
    #print "Choose the speed at which the voices will be spoken. Choosing fast will make the voices faster and higher pitched, and may work better for non-horror games"
    playSound("voiceSpeed1.mp3")
    voiceList = [["normal.mp3", SPEED_NORMAL], ["fast.mp3", SPEED_FAST]]
    global voiceSpeed
    voiceSpeed = selectOption(voiceList)

def quit():
    "Quit"
    pygame.quit()   #closes pygame window
    sys.exit()
    

#************** UTILITY FUNCTIONS ********************************************************************
def select(list):
    "Selecting something, will have to wait for keyboard input and return the item selected. Takes a list as an argument and goes through them via keyboard"
    global currentRoom, roomDict
    #Down or Right arrow goes to next item, Up or Left goes to prev item, Space bar uses elem
    if len(list) == 0:      # return 0 if case the list is empty
        return 0
    index = 0
    
    while 1 == 1:
        soundInterrupt = playSound(list[index]["sName"])
        if soundInterrupt:
            keyboardInput = soundInterrupt
        else:
            keyboardInput = getInput()
            
        if keyboardInput == K_ESCAPE:
            return "esc"
        elif keyboardInput == K_SPACE:
            return list[index]
        elif (keyboardInput == K_DOWN) or (keyboardInput == K_RIGHT):
            if index == len(list)-1:
                index = 0
            else:
                index += 1
        elif (keyboardInput == K_UP) or (keyboardInput == K_LEFT):
            if index == 0:
                index = len(list)-1
            else:
                index -= 1
        else:
            pass      

def selectOption(list):
    "Selecting non-item, non-room options, such as actions, or load files"
    global currentRoom, roomDict
    #Down or Right arrow goes to next item, Up or Left goes to prev item, Space bar uses elem
    index = 0
    
    while 1 == 1:
        soundInterrupt = playSound(list[index][0])
        if soundInterrupt:
            keyboardInput = soundInterrupt
        else:
            keyboardInput = getInput()

        if keyboardInput == K_ESCAPE:
            return "esc"
        elif keyboardInput == K_SPACE:
            return list[index][1]
        elif keyboardInput == K_DOWN or keyboardInput == K_RIGHT:
            if index == len(list)-1:
                index = 0
            else:
                index += 1
        elif keyboardInput == K_UP or keyboardInput == K_LEFT:
            if index == 0:
                index = len(list)-1
            else:
                index -= 1
        else:
            pass

def gameOver():
    "Game Over"
    #print "Game Over"
    playSound("gameOver.mp3")
    raise DeadException
    #menu()  #may have other functions on the stack, don't know what to do about that

def getInput():
  "Waits for keyboard input and returns key that is pressed."
  while 1==1:
   for event in pygame.event.get():
      if (event.type == KEYUP): # or (event.type == KEYDOWN)
        return event.key
      if (event.type == QUIT):
        pygame.quit()
        sys.exit()
        
def playSound(sound):
    "Plays a sound"
    file = "sounds/" + sound
    #create source
    src = pySonic.Source()
    #load audio from disk
    src.Sound = pySonic.FileSample(file)
    #src.Frequency = voiceSpeed
    src.Play()
    while src.IsPlaying():
      for event in pygame.event.get():
        if (event.type == KEYUP): # or (event.type == KEYDOWN)
          return event.key
        if (event.type == QUIT):
          pygame.quit()
          sys.exit()
        
def playSoundLoop(sound):
    "Plays a sound"
    file = "sounds/" + sound
    #create source
    src = pySonic.Source()
    #load audio from disk
    src.Sound = pySonic.FileSample(file, pySonic.Constants.FSOUND_LOOP_NORMAL)
    src.Play()
    while src.IsPlaying():
      for event in pygame.event.get():
        if (event.type == KEYUP): # or (event.type == KEYDOWN)
          return event.key
        if (event.type == QUIT):
          pygame.quit()
          sys.exit()      

def playTTS(string):
    "Plays text to speech"
    tts.Speak(string, pyTTS.tts_async)
    for event in pygame.event.get():
      if (event.type == KEYUP):
        tts.Stop()
        return(0)


#************** GAME LOOP *******************************************************************************
def gameLoop():
    #print "You are in the " + currentRoom["name"]
    global currentRoom, roomDict
    for i in range(1):
        soundInterrupt = playSound("youAreNowInThe.mp3")
        if soundInterrupt:
            break
        playSound(roomDict[currentRoom]["sName"])
        if soundInterrupt:
            break
        playSound(roomDict[currentRoom]["sDescription"])

    try:    
        while 1 == 1:
            #print "Choose an option"
            playSound("chooseAnOption.mp3")
            action = selectOption(actionList)              
            if action == "esc": #esc was pressed
                pass #to prevent accidental quits
            else:
                action()
    except DeadException:
        return 0

    
#************** useItem FUNCTIONS ***********************************************************************
def scalpelToOperatingTable():
    #print "You cut the straps on the operating table. You are now free!"
    playSound("cutStraps.mp3")
    playSound("cutStraps2.mp3")
    roomDict["inventory"]["items"].remove(scalpel)
    roomDict["operatingRoom"]["rooms"].append(freezer)
    roomDict["operatingRoom"]["items"].remove(operatingTable)
    roomDict["operatingRoom"]["items"].append(operatingRoomRecording)
    roomDict["operatingRoom"]["items"].append(operatingRoomDoor)

def playerToPainting():
    #print "You move the painting and a tune plays"
    playSound("movePainting.mp3")
    #print "Play tune"
    playSound("pianoC.mp3")
    playSound("pianoE.mp3")
    playSound("pianoG.mp3")

def playerToPiano():
    pianoKeyList = [ ["pianoChooseC.mp3", "pianoC.mp3"], ["pianoChooseD.mp3", "pianoD.mp3"], ["pianoChooseE.mp3", "pianoE.mp3"], ["pianoChooseF.mp3", "pianoF.mp3"], ["pianoChooseG.mp3", "pianoG.mp3"], ["pianoChooseA.mp3", "pianoA.mp3"], ["pianoChooseB.mp3", "pianoB.mp3"], ["cancel.mp3", "Cancel"] ]
    missCount = 0

    while 1 == 1:    
      #print "Press a key"
      playSound("pianoPressKey1.mp3")
      keyPressed1 = selectOption(pianoKeyList)
      if keyPressed1 == "Cancel":
        break
      #print keyPressed1
      playSound(keyPressed1)
      
      #print "Press a 2nd key"
      playSound("pianoPressKey2.mp3")
      keyPressed2 = selectOption(pianoKeyList)
      if keyPressed2 == "Cancel":
        break
      #print keyPressed2
      playSound(keyPressed2)

      #print "Press a 3rd key"
      playSound("pianoPressKey3.mp3")
      keyPressed3 = selectOption(pianoKeyList)
      if keyPressed3 == "Cancel":
        break
      #print keyPressed3
      playSound(keyPressed3)

      if(keyPressed1 == "pianoC.mp3" and keyPressed2 == "pianoE.mp3" and keyPressed3 == "pianoG.mp3"):
        #print "Ding!"
        playSound("chime.mp3")
        #print "You hear a loud rumble from the hallway that sounds like a wall moving"
        playSound("pianoSolve.mp3")
        roomDict["basementHallway"]["rooms"].insert(0, elevator)
        #basementHallway["rooms"].insert(0, elevator) #added elevator
        break
      else:
        missCount = missCount + 1
        #print "Err!"
        playSound("buzzer.mp3")
        if(missCount == 3):
          #print "You have failed too many times. A trap door opens underneath you, revealing a pit of spikes. You fall to your death."
          playSound("pianoFail.mp3")
          gameOver()
        else:
          playSound("pianoTryAgain.mp3")

def operatingRoomKeyToOperatingRoomDoor():
    #print "You unlocked the door to the hallway. You can now move to the hallway."
    playSound("unlockOperatingRoom.mp3")
    roomDict["inventory"]["items"].remove(operatingRoomKey)
    roomDict["operatingRoom"]["rooms"].insert(0, basementHallway)
    roomDict["operatingRoom"]["items"].remove(operatingRoomDoor)

def broomToShelf():
    "Knocks box off of the shelf"
    #print "You hit the box off of the shelf"
    playSound("broomToShelf.mp3")
    roomDict["bathroom"]["items"].insert(0, box)

def playerToBox():
    "Stand on box, can reach star hole"
    #print "You stand on the box. You can now reach the star-shaped hole"
    playSound("playerToBox.mp3")
    roomDict["bathroom"]["items"].insert(0, starHole)
    roomDict["bathroom"]["items"].remove(box)

def starToStarHole():
    "Mirror open, revealing a small dark hallway with a door at the end"
    #print "You put the star in the star-shaped hole. Sound plays. Mirror moves"
    playSound("starToStarHole.mp3")
    roomDict["bathroom"]["rooms"].insert(0, bathroomHallway)

def deskKeyToDesk():
    "Unlock desk, reveals recording"
    #print "The desk opens, revealing a recording"
    playSound("deskKeyToDesk.mp3")
    roomDict["bedroom"]["items"].insert(0, bedroomRecording)
    roomDict["bedroom"]["items"].insert(0, star)
    roomDict["inventory"]["items"].remove(deskKey)

def hammerToMirror():
    "Break mirror, Dr hears the noise and game over"
    #print "You break the mirror with the hammer with a loud crash!, revealing a hallway hidden behind the mirror. Unfortunately, the Dr hears the loud crash and find you in the bathroom. You try to defend yourself with the hammer, but you miss, and he injects you with a tranquilizer, puts you to sleep, and takes you away"
    playSound("hammerToMirror.mp3")
    gameOver()

def playerToBathroomHallwayDoor():
    "Knock on door, talk to friend"
    #print "You knock on the door to get the attention of the person inside."
    playSound("playerToBathroomHallwayDoor.mp3")
    playSound("friend010_cell.mp3")
    
def playerToSafe():
    "Open safe with passcode 2 1 6"
    numberList = [ ["1.mp3", "1"], ["2.mp3", "2"], ["3.mp3", "3"], ["4.mp3", "4"], ["5.mp3", "5"], ["6.mp3", "6"], ["7.mp3", "7"], ["8.mp3", "8"], ["9.mp3", "9"], ["0.mp3", "0"] ]

    #print "Enter the combination"
    playSound("safe1.mp3")
    #print "Choose a number"
    playSound("safeChoose1.mp3")
    numberChosen1 = selectOption(numberList)
    
    #print "Choose a second number"
    playSound("safeChoose2.mp3")
    numberChosen2 = selectOption(numberList)

    #print "Choose a third number"
    playSound("safeChoose3.mp3")
    numberChosen3 = selectOption(numberList)

    if(numberChosen1 == "2" and numberChosen2 == "1" and numberChosen3 == "6"):
      #print "Ding!"
      playSound("chime.mp3")
      #print "The safe opens. Inside you find a recording, a key, and a pass card"
      playSound("safeOpen1.mp3")
      roomDict["study"]["items"].remove(safe)
      roomDict["study"]["items"].insert(0, safeRecording)
      roomDict["study"]["items"].insert(0, cellKey)
      roomDict["study"]["items"].insert(0, passCard)
      #print "phone ring"
      playSound("phoneRing.mp3")
      #print "Strange, the phone suddenly rings. You pick it up"
      playSound("safeOpen2.mp3")
      #print "Professor talks"
      playSound("safeOpen3.mp3")
    else:
      #print "Err!"
      playSound("buzzer.mp3")

def cellKeyToBathroomHallwayDoor():
    "Opens the cell"
    roomDict["bathroomHallway"]["items"].remove(bathroomHallwayDoor)
    roomDict["inventory"]["items"].remove(cellKey)
    #print "Let's go to the main hallway and open the strange locked door"
    playSound("cellKeyToBathroomHallwayDoor.mp3")
    global currentRoom
    currentRoom = upperHallway["name"]
    playSound("cellKeyToBathroomHallwayDoor2.mp3")
    
    #condition something = true? for not letting people just open the door with the hammer earlier?
    #or maybe he gives you something to open the door with

def hammerToUpperHallwayDoor():
    "You need to hit the door and it opens. You can now move to the balcony"
    #print "You hit the door and it opens"
    playSound("hammerToUpperHallwayDoor.mp3")
    playSound("hammerToUpperHallwayDoor2.mp3")
    roomDict["upperHallway"]["items"].remove(upperHallwayDoor)
    roomDict["upperHallway"]["rooms"].insert(0, balcony)
    roomDict["inventory"]["items"].remove(hammer)
    #do you still need the hammer?

def passCardToMainEntrance():
    "Open and dogs will eat you"
    #print "You use the pass card and the main entrance opens. Unfortunately, as soon as you open it, you find a pack of growling dogs waiting outside. They look pretty hungry, and apparently, they find you pretty tasty."
    playSound("passCardToMainEntrance.mp3")
    gameOver()

def masterBedroomDeskKeyToMasterBedroomDesk():
    "Open desk"
    #print "You open the desk and find a key and another recording"
    playSound("masterBedroomDeskKeyToMasterBedroomDesk.mp3")
#    roomDict["masterBedroom"]["items"].insert(0, masterBathroomKey)
    roomDict["masterBedroom"]["items"].insert(0, masterBedroomRecording)
    roomDict["masterBedroom"]["items"].remove(masterBedroomDesk)
    roomDict["inventory"]["items"].remove(masterBedroomDeskKey)

def starToMasterBathroomStarHole():
    "Opens mirror"
    #print "The mirror moves, revealing an elevator"
    playSound("starToMasterBathroomStarHole.mp3")    
    roomDict["masterBathroom"]["rooms"].insert(0, masterElevator)
    roomDict["masterBathroom"]["items"].remove(masterBathroomStarHole)
    roomDict["masterBathroom"]["items"].remove(masterBathroomMirror)

def playLeftSound():
    "For the passCardToSittingRoomDoor puzzle. Plays a sound to the left"
    leftSound = pySonic.Source()
    leftSound.Sound = pySonic.FileSample("sounds/pianoC.mp3")
    leftSound.Position = (-3, 0, 0)
    leftSound.Velocity = (0, 0, 0)
    leftSound.Play()
    while leftSound.IsPlaying():
      time.sleep(0.5)

def playRightSound():
    "For the passCardToSittingRoomDoor puzzle. Plays a sound to the right"
    rightSound = pySonic.Source()
    rightSound.Sound = pySonic.FileSample("sounds/pianoF.mp3")
    rightSound.Position = (3, 0, 0)
    rightSound.Velocity = (0, 0, 0)
    rightSound.Play()
    while rightSound.IsPlaying():
      time.sleep(0.5)
    
def passCardToSittingRoomDoor():
    "Puzzle to open Eleanor's room"
    #print "There are 2 speakers in front of you, one on the left, one on the right. Below each speaker is a button. When you insert the pass key, sounds start playing from the left and right speakers.
    playSound("passCardToSittingRoomDoor1.mp3")
    buttonList=[ ["leftButton.mp3", "leftButton"], ["rightButton.mp3", "rightButton"], ["cancel.mp3", "cancel"] ] 
    #sequence is L, R, L, L
    playLeftSound()
    playRightSound()
    playLeftSound()
    playLeftSound()
    #print "Press a button"
    playSound("passCardToSittingRoomDoor2.mp3")
    buttonPressed = selectOption(buttonList)
    if buttonPressed == "cancel":
        return 0
    buttonSequence = buttonPressed
    for i in range(3):
      #print "Press a button"
      playSound("passCardToSittingRoomDoor2.mp3")
      buttonPressed = selectOption(buttonList)
      if buttonPressed == "cancel":
        return 0
      buttonSequence += buttonPressed
    if(buttonSequence != "leftButtonrightButtonleftButtonleftButton"):
      playSound("buzzer.mp3")
      #print "Apparently you've inputted the wrong sequence of button presses. A trap door opens underneath you, revealing a pit of spikes. You fall to your death"
      playSound("passCardToSittingRoomDoor3.mp3")
      gameOver()
    playSound("chime.mp3")

    #second sequence is R, R, R, L, R, L
    playRightSound()
    playRightSound()
    playRightSound()
    playLeftSound()
    playRightSound()
    playLeftSound()
    #print "Press a button"
    playSound("passCardToSittingRoomDoor2.mp3")
    buttonPressed = selectOption(buttonList)
    if buttonPressed == "cancel":
        return 0
    buttonSequence = buttonPressed
    for i in range(5):
      #print "Press a button"
      playSound("passCardToSittingRoomDoor2.mp3")
      buttonPressed = selectOption(buttonList)
      if buttonPressed == "cancel":
        return 0
      buttonSequence += buttonPressed
    if(buttonSequence != "rightButtonrightButtonrightButtonleftButtonrightButtonleftButton"):
      playSound("buzzer.mp3")
      #print "Apparently you've inputted the wrong sequence of button presses. A trap door opens underneath you, revealing a pit of spikes. You fall to your death"
      playSound("passCardToSittingRoomDoor3.mp3")
      gameOver()

    playSound("chime.mp3")
    #print "The door slides open. You can now move into the dark room ahead"
    playSound("passCardToSittingRoomDoor4.mp3")
    roomDict["sittingRoom"]["rooms"].insert(0, eleanorsRoom)
    roomDict["sittingRoom"]["items"].remove(sittingRoomDoor)

def knifeToEleanor():
    "Cut her bindings"
    #print "Eleanor conversation"
    playSound("knifeToEleanor.mp3")
    roomDict["inventory"]["items"].append(gun)
#!!! This might not work
    roomDict["eleanorsRoom"]["items"].remove(eleanor)
    #eleanor["sDescription"]="eleanorDesc2.mp3"
      
def passCardToMazeDoor():
    "Starts the maze. Follow the sound to get to the exit"
    playSound("passCardToMazeDoor0.mp3")
  
    song.Stop()
    exitSound = pySonic.Source()
    exitSound.Sound = pySonic.FileStream("sounds/pianoC.mp3", pySonic.Constants.FSOUND_LOOP_NORMAL)
    exitSound.Position = (0, 4, 0)
    exitSound.Velocity = (0, 0, 0)
    exitSound.Volume = 50
    exitSound.Play()
    
    #maze is 5 x 5 matrix. 0 denotes not movable. 1 denotes movable. 2 denotes monster. 3 denotes end.
    mazeMatrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    mazeMatrix[0][0]=2
    mazeMatrix[1][0]=1
    mazeMatrix[2][0]=1
    mazeMatrix[3][0]=1
    mazeMatrix[3][1]=1
    mazeMatrix[3][2]=1
    mazeMatrix[2][2]=1
    mazeMatrix[1][2]=1
    mazeMatrix[1][3]=1
    mazeMatrix[1][4]=1
    mazeMatrix[0][4]=3
    mazeMatrix[0][2]=2
    mazeMatrix[3][3]=2
    mazeMatrix[4][2]=2

    #start at (3,0)
    positionX=3
    positionY=0
    #w.Listener.Position = (positionX, positionY, 0) 

    #print "You are now in the maze. Navigate by going north, west, south, or east. There is a sound coming from the exit, and you can assume that you are always facing north "
    playSound("passCardToMazeDoor1.mp3")

    while 1:
      #make the move list
      mazeMoveList = []
      #north
      if (positionY + 1 <= 4) and (mazeMatrix[positionX][positionY+1] != 0):
          mazeMoveList.append(["north.mp3", "north"])
      #west
      if (positionX - 1 >= 0) and (mazeMatrix[positionX-1][positionY] != 0):
          mazeMoveList.append(["west.mp3", "west"])
      #south
      if (positionY - 1 >= 0) and (mazeMatrix[positionX][positionY-1] != 0):
          mazeMoveList.append(["south.mp3", "south"])
      #east
      if (positionX + 1 <= 4) and (mazeMatrix[positionX+1][positionY] != 0):
          mazeMoveList.append(["east.mp3", "east"])		
      
      #move
      #print "The following paths are open:"
      playSound("passCardToMazeDoor2.mp3")
      for elem in mazeMoveList:
          playSound(elem[0])
      #print "Select a direction to move."
      playSound("passCardToMazeDoor3.mp3")
      mazeMove = selectOption(mazeMoveList)
      
      #update position
      if mazeMove == "north":
          positionY += 1
      elif mazeMove == "south":
          positionY -= 1
      elif mazeMove == "east":
          positionX += 1
      elif mazeMove == "west":
          positionX -= 1
      exitSound.Position = (0-positionX, 4-positionY, 0)
      exitSound.Play()
    
          
      if(mazeMatrix[positionX][positionY] == 2):
          #print "ROAR! It's a monster."
          playSound("passCardToMazeDoor4.mp3")
          playSound("whatItemWillYouUse.mp3")
          itemUsed = select([elem for elem in roomDict["inventory"]["items"]])
          if itemUsed["name"] == "gun":
              #print "The monster lunges at you, but you side step and fire your gun! BANG! And the monster falls dead"
              playSound("passCardToMazeDoor5.mp3")
          else:
              #print "The monster is not phased, and lunges straight for your neck, ripping out your throat"
              playSound("passCardToMazeDoor6.mp3")
              song.Play()
              gameOver()
      elif(mazeMatrix[positionX][positionY]==3):
          #print "You've reached the end of the maze. After rummaging through stacks of chemicals, you find the ingredients that Eleanor told you about. You make your way back to the entrance of the maze, and are now back in the basement"
          playSound("passCardToMazeDoor7.mp3")
          roomDict["inventory"]["items"].append(ingredients)
          exitSound.Stop()
          song.Play()
          return 0

def playerToComputer():
    "Attempt to logon to computer. Need passkey from notebook, which is 9 3 1"
    numberList = [ ["1.mp3", "1"], ["2.mp3", "2"], ["3.mp3", "3"], ["4.mp3", "4"], ["5.mp3", "5"], ["6.mp3", "6"], ["7.mp3", "7"], ["8.mp3", "8"], ["9.mp3", "9"], ["0.mp3", "0"] ]

    #print "You attempt to use the computer and it starts to speak
    #playTTS("Please enter the pass key to unlock the basement lab")
    #print "Choose a number"
    playSound("safeChoose1.mp3")
    numberChosen1 = selectOption(numberList)
    
    #print "Choose a second number"
    playSound("safeChoose2.mp3")
    numberChosen2 = selectOption(numberList)

    #print "Choose a third number"
    playSound("safeChoose3.mp3")
    numberChosen3 = selectOption(numberList)

    if(numberChosen1 == "9" and numberChosen2 == "3" and numberChosen3 == "1"):
      #print "Ding!"
      playSound("chime.mp3")
      #print "The basement lab is now unlocked. You can access the lab by going down the elevator in this room"
      
      playTTS("The Elevator has been activated")
      time.sleep(2)
        
      roomDict["basementHallway"]["rooms"].insert(0, lab)
      roomDict["basementHallway"]["items"].remove(labDoor)
      roomDict["study"]["rooms"].insert(0, elevator)
#!!! this might not work
      eleanor["sDescription"]="eleanorDesc2.mp3"
      #roomDict["eleanorsRoom"]["items"].remove(eleanor)
      roomDict["lab"]["items"].insert(0, eleanor)
    else:
      #print "Err!"
      playSound("buzzer.mp3")

def ingredientsToEleanor():
	"Give ingredients to Eleanor"
	#print "Eleanor conversation"
	playSound("ingredientsToEleanor.mp3")
	playSound("ingredientsToEleanor2.mp3")
	roomDict["inventory"]["items"].append(garageKey)
	roomDict["inventory"]["items"].remove(ingredients)
	eleanor["sDescription"]="eleanorDesc3.mp3"
	
def garageKeyToGarageDoor():
	"Doesn't work"
	#print "You try the key to the door, but the lock seems to be rusted shut. Maybe you can just shoot it out"
	playSound("garageKeyToGarageDoor.mp3")
	
def gunToGarageDoor():
	"Shoot open lock"
	#print "You shoot the lock on the door and it shatters. You can now move to the garage"
	playSound("gunToGarageDoor.mp3")
	roomDict["inventory"]["items"].remove(garageKey)
	roomDict["kitchen"]["items"].remove(garageDoor)
	roomDict["kitchen"]["rooms"].insert(0, garage)
	
def dieInTrappedHallway():
	"For use in trappedHallwayDoorKeyToTrappedHallwayDoor()"
	#print "You fail to act fast enough, and a large blade cuts in you half"
	playSound("dieInTrappedHallway.mp3")
	gameOver()
	
def trappedHallwayReact(direction):
    if direction == "up":
        soundFile = "jump.mp3"
        expectedInput = K_UP
    elif direction == "down":
        soundFile = "duck.mp3"
        expectedInput = K_DOWN
    elif direction == "left":
        soundFile = "left.mp3"
        expectedInput = K_LEFT
    elif direction == "right":
        soundFile = "right.mp3"
        expectedInput = K_RIGHT
    elif direction == "shoot":
        soundFile = "shoot.mp3"
        expectedInput = K_SPACE
    else:
        print "Error in trappedHallwayReact()"

    t = Timer(2.0, dieInTrappedHallway)
    playSound(soundFile)
    t.start() # after 2 seconds, player dies if he hasn't inputted correct key
    while 1:
      keyboardInput = getInput()
      if keyboardInput == expectedInput:
          t.cancel()
          return 0
      else:
          #print "You act as fast you can, but you did the wrong thing and a blade cuts you in half"
          t.cancel()
          playSound("dieInTrappedHallway2.mp3")
          gameOver()

def trappedHallwayDoorKeyToTrappedHallwayDoor():
    "Use key on door, triggers cut scene"
    roomDict["inventory"]["items"].remove(trappedHallwayDoorKey)
    #print "Conversation"
    playSound("trappedHallwayDoorKeyToDoor0.mp3")
    playSound("trappedHallwayDoorKeyToDoor1.mp3")
    playSound("trappedHallwayDoorKeyToDoor2.mp3")

    #sequence up, down, left, right, up, up, down, down, right, down
    trappedHallwayReact("up")
    trappedHallwayReact("down")
    trappedHallwayReact("left")
    trappedHallwayReact("right")
    trappedHallwayReact("up")
    trappedHallwayReact("up")
    trappedHallwayReact("down")
    trappedHallwayReact("down")
    trappedHallwayReact("right")
    trappedHallwayReact("down")
    #print "conversation"
    playSound("friend070_road.mp3")

    global currentRoom
    currentRoom = outside["name"]
    soundInterrupt = playSound("youAreNowInThe.mp3")
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sName"])
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sDescription"])

def passCardToBarnDoor():
	"Unlock barn"
	#print "You have unlocked the barn door. You can now move into the barn"
	playSound("passCardToBarnDoor.mp3")
	roomDict["outside"]["rooms"].insert(0, barn)
	
def playerToBarnSwitch():
	"Unlocks cages, monsters kill you"
	#print "You hit the switch, and all of the cages open. You've freed all of the monsters, and they show their thanks by eating you alive."
	playSound("playerToBarnSwitch.mp3")
	gameOver()
	
def knifeToEleanor2():
	"Cut her bindings"
	#print "conversation"
	playSound("knifeToEleanor2.mp3")
	playSound("eleanor050_barn.mp3")
	
def dieInBarn():
	"Killed by doctor"
	#print "You try to pull out your gun, but you aren't fast enough. The doctor bounds up the stairs with surprising speed, steals your gun right out of your hand and shoots you with it"
	playSound("dieInBarn.mp3")
	gameOver()
	
def gasolineToEleanor2():
	"Give her the gas"
	#print "conversation"
	playSound("doc140_barn.mp3")
	playSound("friend080_shoot_the_doctor.mp3")
	
	t = Timer(2.0, dieInBarn) 
	t.start() # after 2 seconds, player dies if he hasn't inputted correct key 
	while 1:
		keyboardInput = getInput()
		if keyboardInput == K_SPACE:
			t.cancel()
			break
		else:
			pass

	playSound("doc150_barn_hit.mp3")
	
	#print "ending"
	playSound("narrator_before_final_scene.mp3")
	playSound("final_scene.mp3")
	
	

#************** MAIN METHOD *****************************************************************************
if __name__ == "__main__":
  try:
    #player, journal, and inventory are part of the game engine, so separate them out
    player = Item()
    journal = Item()
    player.construct("player", "self.mp3", "selfDesc.mp3", 0)
    journal.construct("journal", "journal.mp3", "journalDesc.mp3", 0)
    #inventory isn't really a room, but it's easier to treat it as one. All of the player's inventory is in the "items" list of the inventory room
    inventory = Room()
    inventory.construct("inventory", "inventory.mp3", "inventory.mp3", [], [player])
    
    #initialize the rooms and items
    operatingRoom = Room()
    freezer = Room()
    basementHallway = Room()
    pianoRoom = Room()
    elevator = Room()
    study = Room()
    upperHallway = Room()
    bedroom = Room()
    bathroom = Room()
    closet = Room()
    bathroomHallway = Room()
    balcony = Room()
    westHallway = Room()
    lobby = Room()
    library = Room()
    masterBedroom = Room()
    masterBathroom = Room()
    masterElevator = Room()
    eleanorsRoom = Room()
    sittingRoom = Room()
    basement = Room()
    kitchen = Room()
    lab = Room()
    garage = Room()
    trappedHallway = Room()
    outside = Room()
    barn = Room()
    barnLoft = Room()
    
    operatingTable = Item()
    scalpel = Item()
    operatingRoomRecording = Item()
    operatingRoomDoor = Item()
    operatingRoomKey = Item()
    freezerBodies = Item()
    piano = Item()
    painting = Item()
    deskKey = Item()
    studyRecording = Item()
    computer = Item()
    phone = Item()
    safe = Item()
    desk = Item()
    bedroomRecording = Item()
    bed = Item()
    mirror = Item()
    bathtub = Item()
    shelf = Item()
    box = Item()
    broom = Item()
    hammer = Item()
    star = Item()
    starHole = Item()
    bathroomHallwayDoor = Item()
    safeRecording = Item()
    cellKey = Item()
    passCard = Item()
    upperHallwayDoor = Item()
    notebook = Item()
    mainEntrance = Item()
    masterBedroomDeskKey = Item()
    masterBedroomDesk = Item()
    masterBedroomBed = Item()
    libraryRecording = Item()
    masterBedroomRecording = Item()
    masterBathroomStarHole = Item()
    masterBathroomMirror = Item()
    sittingRoomDoor = Item()
    knife = Item()
    trappedHallwayDoorKey = Item()
    eleanor = Item()
    gun = Item()
    labDoor = Item()
    ingredients = Item()
    mazeDoor = Item()
    garageDoor = Item()
    garageKey = Item()
    gasoline = Item()
    trappedHallwayDoor = Item()
    barnDoor = Item()
    barnSwitch = Item()
    eleanor2 = Item()

      
    #construct the rooms and items
    operatingRoom.construct("operatingRoom", "operatingRoom.mp3", "operatingRoomDesc.mp3", [], [operatingTable, scalpel])   #freezer, operatingRoomDoor accessible after scalpelToOperatingTable, locked door to basementHallway
    freezer.construct("freezer", "freezer.mp3", "freezerDesc.mp3", [operatingRoom], [freezerBodies, operatingRoomKey])
    basementHallway.construct("basementHallway", "basementHallway.mp3", "basementHallwayDesc.mp3", [operatingRoom, pianoRoom], [journal, labDoor]) #hidden door to elevator
    pianoRoom.construct("pianoRoom", "pianoRoom.mp3", "pianoRoomDesc.mp3", [basementHallway], [painting, piano])
    elevator.construct("elevator", "elevator.mp3", "elevatorDesc.mp3", [basementHallway, study], [])
    study.construct("study", "study.mp3", "studyDesc.mp3", [upperHallway], [deskKey, studyRecording, computer, phone, safe])
    upperHallway.construct("upperHallway", "upperHallway.mp3", "upperHallwayDesc.mp3", [study, bedroom, closet], [upperHallwayDoor, journal])
    bedroom.construct("bedroom", "bedroom.mp3", "bedroomDesc.mp3", [upperHallway, bathroom], [desk, bed])
    bathroom.construct("bathroom", "bathroom.mp3", "bathroomDesc.mp3", [bedroom], [journal, mirror, bathtub, shelf])
    closet.construct("closet", "closet.mp3", "closetDesc.mp3", [upperHallway], [broom, hammer])
    bathroomHallway.construct("bathroomHallway", "bathroomHallway.mp3", "bathroomHallwayDesc.mp3", [bathroom], [bathroomHallwayDoor])
    balcony.construct("balcony", "balcony.mp3", "balconyDesc.mp3", [upperHallway, westHallway, lobby], [])
    westHallway.construct("westHallway", "westHallway.mp3", "westHallwayDesc.mp3", [balcony, masterBedroom, library], [journal])
    lobby.construct("lobby", "lobby.mp3", "lobbyDesc.mp3", [balcony, kitchen], [journal, mainEntrance, trappedHallwayDoor])
    library.construct("library", "library.mp3", "libraryDesc.mp3", [westHallway], [notebook, masterBedroomDeskKey, libraryRecording])
    masterBedroom.construct("masterBedroom", "masterBedroom.mp3", "masterBedroomDesc.mp3", [westHallway, masterBathroom], [masterBedroomDesk, masterBedroomBed])
    masterBathroom.construct("masterBathroom", "masterBathroom.mp3", "masterBathroomDesc.mp3", [masterBedroom], [masterBathroomMirror, masterBathroomStarHole])
    masterElevator.construct("masterElevator", "masterElevator.mp3", "masterElevatorDesc.mp3", [masterBathroom, sittingRoom, basement], [])
    eleanorsRoom.construct("eleanorsRoom", "eleanorsRoom.mp3", "eleanorsRoomDesc.mp3", [sittingRoom], [eleanor])
    sittingRoom.construct("sittingRoom", "sittingRoom.mp3", "sittingRoomDesc.mp3", [masterElevator], [journal, sittingRoomDoor])
    basement.construct("basement", "basement.mp3", "basementDesc.mp3", [masterElevator], [journal, mazeDoor])
    kitchen.construct("kitchen", "kitchen.mp3", "kitchenDesc.mp3", [lobby], [knife, garageDoor])
    lab.construct("lab", "lab.mp3", "labDesc.mp3", [basementHallway], [])
    garage.construct("garage", "garage.mp3", "garageDesc.mp3", [kitchen], [journal, gasoline, trappedHallwayDoorKey])
    trappedHallway.construct("trappedHallway", "trappedHallway.mp3", "trappedHallwayDesc.mp3", [lobby, outside], []) #Desc, traps have been deactivated
    outside.construct("outside", "outside.mp3", "outsideDesc.mp3", [trappedHallway], [journal, barnDoor])
    barn.construct("barn", "barn.mp3", "barnDesc.mp3", [outside, barnLoft], [barnSwitch])
    barnLoft.construct("barnLoft", "barnLoft.mp3", "barnLoftDesc.mp3", [barn], [eleanor2])
   
    operatingTable.construct("operatingTable", "operatingTable.mp3", "operatingTableDesc.mp3", 0)
    scalpel.construct("scalpel", "scalpel.mp3", "scalpelDesc.mp3", 1)
    operatingRoomRecording.construct("operatingRoomRecording", "recording.mp3", "operatingRoomRecordingDesc.mp3", 0)
    operatingRoomDoor.construct("operatingRoomDoor", "operatingRoomDoor.mp3", "operatingRoomDoorDesc.mp3", 0)
    operatingRoomKey.construct("operatingRoomKey", "operatingRoomKey.mp3", "operatingRoomKeyDesc.mp3", 1)
    freezerBodies.construct("freezerBodies", "freezerBodies.mp3", "freezerBodiesDesc.mp3", 0)
    piano.construct("piano", "piano.mp3", "pianoDesc.mp3", 0)
    painting.construct("painting", "painting.mp3", "paintingDesc.mp3", 0)
    deskKey.construct("deskKey", "deskKey.mp3", "deskKeyDesc.mp3", 1)
    studyRecording.construct("studyRecording", "recording.mp3", "studyRecordingDesc.mp3", 0)
    computer.construct("computer", "computer.mp3", "computerDesc.mp3", 0)
    phone.construct("phone", "phone.mp3", "phoneDesc.mp3", 0)
    safe.construct("safe", "safe.mp3", "safeDesc.mp3", 0)
    desk.construct("desk", "desk.mp3", "deskDesc.mp3", 0)
    bedroomRecording.construct("bedroomRecording", "recording.mp3", "bedroomRecordingDesc.mp3", 0)
    bed.construct("bed", "bed.mp3", "bedDesc.mp3", 0)
    mirror.construct("mirror", "mirror.mp3", "mirrorDesc.mp3", 0)
    bathtub.construct("bathtub", "bathtub.mp3", "bathtubDesc.mp3", 0)
    shelf.construct("shelf", "shelf.mp3", "shelfDesc.mp3", 0)
    box.construct("box", "box.mp3", "boxDesc.mp3", 0)
    broom.construct("broom", "broom.mp3", "broomDesc.mp3", 1)
    hammer.construct("hammer", "hammer.mp3", "hammerDesc.mp3", 1)
    star.construct("star", "star.mp3", "starDesc.mp3", 1)
    starHole.construct("starHole", "starHole.mp3", "starHoleDesc.mp3", 0)
    bathroomHallwayDoor.construct("bathroomHallwayDoor", "bathroomHallwayDoor.mp3", "bathroomHallwayDoorDesc.mp3", 0)
    safeRecording.construct("safeRecording", "safeRecording.mp3", "safeRecordingDesc.mp3", 0)
    cellKey.construct("cellKey", "cellKey.mp3", "cellKeyDesc.mp3", 1)
    passCard.construct("passCard", "passCard.mp3", "passCardDesc.mp3", 1)
    upperHallwayDoor.construct("upperHallwayDoor", "upperHallwayDoor.mp3", "upperHallwayDoorDesc.mp3", 0)
    notebook.construct("notebook", "notebook.mp3", "notebookDesc.mp3", 0)
    mainEntrance.construct("mainEntrance", "mainEntrance.mp3", "mainEntranceDesc.mp3", 0)
    masterBedroomDeskKey.construct("masterBedroomDeskKey", "masterBedroomDeskKey.mp3", "masterBedroomDeskKeyDesc.mp3", 1)
    masterBedroomBed.construct("masterBedroomBed", "bed.mp3", "masterBedroomBedDesc.mp3", 0)
    masterBedroomDesk.construct("masterBedroomDesk", "desk.mp3", "masterBedroomDeskDesc.mp3", 0)
    libraryRecording.construct("libraryRecording", "recording.mp3", "libraryRecordingDesc.mp3", 0)
    masterBedroomRecording.construct("masterBedroomRecording", "recording.mp3", "masterBedroomRecordingDesc.mp3", 0)
    masterBathroomStarHole.construct("masterBathroomStarHole", "starHole.mp3", "starHoleDesc.mp3", 0)    
    masterBathroomMirror.construct("masterBathroomMirror", "mirror.mp3", "mirrorDesc.mp3", 0)
    knife.construct("knife", "knife.mp3", "knifeDesc.mp3", 1)
    trappedHallwayDoorKey.construct("trappedHallwayDoorKey", "trappedHallwayDoorKey.mp3", "trappedHallwayDoorKeyDesc.mp3", 1)
    sittingRoomDoor.construct("sittingRoomDoor", "sittingRoomDoor.mp3", "sittingRoomDoorDesc.mp3", 0)
    eleanor.construct("eleanor", "eleanor.mp3", "eleanorDesc.mp3", 0)
    gun.construct("gun", "gun.mp3", "gunDesc.mp3", 1)
    labDoor.construct("labDoor", "labDoor.mp3", "labDoorDesc.mp3", 0)
    ingredients.construct("ingredients", "ingredients.mp3", "ingredientsDesc.mp3", 1)
    mazeDoor.construct("mazeDoor", "mazeDoor.mp3", "mazeDoorDesc.mp3", 0)
    garageDoor.construct("garageDoor", "garageDoor.mp3", "garageDoorDesc.mp3", 0)
    garageKey.construct("garageKey", "garageKey.mp3", "garageKeyDesc.mp3", 1)
    gasoline.construct("gasoline", "gasoline.mp3", "gasolineDesc.mp3", 1)
    trappedHallwayDoor.construct("trappedHallwayDoor", "trappedHallwayDoor.mp3", "trappedHallwayDoorDesc.mp3", 0)
    barnDoor.construct("barnDoor", "barnDoor.mp3", "barnDoorDesc.mp3", 0)
    barnSwitch.construct("barnSwitch", "barnSwitch.mp3", "barnSwitchDesc.mp3", 0)
    eleanor2.construct("eleanor2", "eleanor.mp3", "eleanorDesc4.mp3", 0)
   
   
    #itemUses stores all the possible item use combinations
    #"itemUsed": [ ["usedOn", function], ["usedOn", function] ]
    itemUses = {"player":[["journal", save], ["painting", playerToPainting], ["piano", playerToPiano], ["box", playerToBox], ["bathroomHallwayDoor", playerToBathroomHallwayDoor], ["computer", playerToComputer], ["safe", playerToSafe], ["barnSwitch", playerToBarnSwitch]],
                "scalpel":[["operatingTable", scalpelToOperatingTable]],
                "operatingRoomKey":[["operatingRoomDoor", operatingRoomKeyToOperatingRoomDoor]],
                "broom":[["shelf", broomToShelf]],
                "star":[["starHole", starToStarHole], ["masterBathroomStarHole", starToMasterBathroomStarHole]],
                "deskKey":[["desk", deskKeyToDesk]],
                "hammer":[["mirror", hammerToMirror], ["upperHallwayDoor", hammerToUpperHallwayDoor]],
                "cellKey":[["bathroomHallwayDoor", cellKeyToBathroomHallwayDoor]],
                "passCard":[["mainEntrance", passCardToMainEntrance], ["sittingRoomDoor", passCardToSittingRoomDoor], ["mazeDoor", passCardToMazeDoor], ["barnDoor", passCardToBarnDoor]],
                "masterBedroomDeskKey":[["masterBedroomDesk", masterBedroomDeskKeyToMasterBedroomDesk]],
                "knife":[["eleanor", knifeToEleanor], ["eleanor2", knifeToEleanor2]],
                "ingredients":[["eleanor", ingredientsToEleanor]],
                "garageKey":[["garageDoor", garageKeyToGarageDoor]],
                "gun":[["garageDoor", gunToGarageDoor]],
                "trappedHallwayDoorKey":[["trappedHallwayDoor", trappedHallwayDoorKeyToTrappedHallwayDoor]],
                "gasoline":[["eleanor2", gasolineToEleanor2]]}
    roomDict = {"inventory":inventory,
                "operatingRoom":operatingRoom,
                "freezer":freezer,
                "basementHallway":basementHallway,
                "pianoRoom":pianoRoom,
                "elevator":elevator,
                "study":study,
                "upperHallway":upperHallway,
                "bedroom":bedroom,
                "bathroom":bathroom,
                "closet":closet,
                "bathroomHallway":bathroomHallway,
                "balcony":balcony,
                "westHallway":westHallway,
                "lobby":lobby,
                "library":library,
                "masterBedroom":masterBedroom,
                "masterBathroom":masterBathroom,
                "masterElevator":masterElevator,
                "eleanorsRoom":eleanorsRoom,
                "sittingRoom":sittingRoom,
                "basement":basement,
                "kitchen":kitchen,
                "lab":lab,
                "garage":garage,
                "trappedHallway":trappedHallway,
                "outside":outside,
                "barn":barn,
                "barnLoft":barnLoft}
    actionList = [["move.mp3", move], ["useItem.mp3", useItem], ["examine.mp3", examine], ["quit.mp3", quit]]
    yesNoList = [["yes.mp3", "yes"], ["no.mp3", "no"]]
    menuList = [["newGame.mp3", newGame], ["loadGame.mp3", loadGame], ["options.mp3", options], ["quit.mp3", quit]]
    saveList = [["slot1.mp3", "save1.txt"], ["slot2.mp3", "save2.txt"], ["slot3.mp3", "save3.txt"], ["slot4.mp3", "save4.txt"], ["slot5.mp3", "save5.txt"]]

    SPEED_NORMAL = 45000
    SPEED_FAST = 65000
    voiceSpeed = SPEED_NORMAL

    w = pySonic.World()
    w.Listener.Position = (0,0,0)
    song = pySonic.Source()
    song.Sound = pySonic.FileStream("sounds/music1.mp3", pySonic.Constants.FSOUND_LOOP_NORMAL)
    song.Volume = 50
    song.Play()

    tts = pyTTS.Create()
    #tts.SetVoiceByName('MSMary')
    
    menu()    
  finally:        
    pygame.quit()
    del w


    
