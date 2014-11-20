#######################
### RENDERNODE v1.0 ###
#######################

### SETTING VARIABLES ###
# Use this top section to alter the RenderNode in whatever way works best for your production. 

""" OUTPUT FOLDER """
# Change this value to whatever folder you would like to render to
# ie. If your show's naming convention is to have a folder structure such as this :
# ABC-> ABC0001-> Comp -> Scripts
#                      -> Output 
# The scripts folder being where your nuke script files are usually located, and the Output folder being the folder you normally render to, 
# then set the variable to Output
destFold = "comp"

""" SEQUENCE NAMING """
# Change this value in accordance to how many letters your sequence names contain. 
# ie. if your show's naming convention is as follows: QRS0123_comp_v001, then it should be 3 because the sequence name is QRS and there are 3 letters. 
numSeqChars = 3

""" SEQUENCE NUMBERING """
# Change this value in accordance to how many digits your sequence numbers contain. 
# ie. if your show's naming convention is as follows: QRS0123_comp_v001, then it should be 4 because the shot number is 0123 and there are 4 numbers. 
numShotChars = 4

""" START FRAME """
# Use this to control which frame you would like your renders to start on.  This is mostly for users that have need to render a slate, but don't want 
# to include the slate frame in their global settings while they work.  Setting it to a value of 0 means that the first frame 
# of the render will be the global settings' first frame.  Setting it to a value of 1 means that your render will be a frame BEFORE the first 
# frame of your project settings.  This only affects the rendering of Quicktimes and importing of DPX files after they are rendered.  Since 
# DPX files are per frame, you can choose which frames to render.
startFrame = 0

""" QUICKTIME RENDERS """
# Change this value in accordance to the number of quicktime files you would like to render when using the RenderQT's button.
# If you decide to chose only one, make sure to delete the write node named VFX_RenderNode, the Editorial_RenderNode will continue to function. 
numQTS = 2

""" LUT FOLDER """
# Change this value to whatever folder the shot's LUT is located in.  WARNING: the search algorithm will NOT exceed the shot's folder, so if there is 
# a shot or sequence LUT, rather than a per-shot LUT, it would be best to navigate to the location manually or change the default path of the RenderNode.
lutDestFolder = "LUTfolder"

""" DPX IMPORT """
# Change this variable to whichever number represents the colorspace that you are working in.  You can figure this out by creating a read node and hovering
# over the colorspace knob.  This is currently set to 10, which results in AlexaV3LogC colorspace because that is the 11th item on the lsit.  
# This is only used to set the colorspace of the read node that is created after a DPX render is completed, it does NOT affect the render.
dpxImportColor = 0

""" RENDERNODE VERSION (mostly for team environments)"""
# Use this to control which version of the RenderNode artists should be using, as well as declaring the filepath AND filename of the RenderNode.
# If you plan on placing the node on a server, then switch rendernodeOnServer to "yes" and put the filepath location of node and the .py files 
# in renderNodeFolder.
renNodeVer = 01
rendernodeOnServer = "no"
rendernodeFile = "/Path/To/The/Node/Toolsets/RenderNode.nk"
renderNodeFolder = "/Path/To/The/Node/"

# If you are a TD and are installing this node on a server for a team of artists, simply copy the following line of code and paste it into each artists' init.py.
# nuke.pluginAddPath([root for root, dirs, files in os.walk(/Path/To/The/Node/)])
# As long as this init.py file is there, as well as the gizmo or Toolset file, it will work.

###########################################################################################################################################################
###########################################################################################################################################################

# END USER INPUT- going past this point without knowledge of nuke's python commands, or python in general, will potentially ruin the RenderNode.

###########################################################################################################################################################
###########################################################################################################################################################

# Default settings
def renderNodeLocation():
    if rendernodeOnServer == "no":
        pass 
    else:
        nuke.pluginAddPath([root for root, dirs, files in os.walk(renderNodeFolder)])

from sys import platform as _platform
import subprocess
import shutil
import fnmatch
import re
import socket
import nuke
import os

### SHOT NAMING ###

def namingConvention(node=nuke.thisParent()):
    if node['verControl'].value() == False:
        return "knobs"
    else:
        return "root"

def scriptName():
    return nuke.root().name().split("/")[-1].split("_")

def sceneName():
    return scriptName()[0]

def sequence():
    return scriptName()[1][:2]

def shotNumber():
    return scriptName()[1][2:]

def descriptor():
    return scriptName()[2]

def shotVersion(node=nuke.thisParent()):
    if namingConvention(node) is "knobs":
        return node['v_num'].value()
    else:
        # Using regular expression to search through the filename for "_v##"
        for match in re.findall(r'_v\d{2,}', nuke.root().name().split("/")[-1]):
            return match.replace("_", "")

def postVer(node=nuke.thisParent()):
    if namingConvention(node) is "knobs":
        return ""
    else:
        postVer = scriptName().split(shotVersion(node))[-1]
        if postVer.startswith("."):
            return ""
        else:
            return postVer.split(".")[0]

def shotName(node=nuke.thisParent()):
    if namingConvention(node) is "knobs":
        return sceneName() + "_" + sequence() + shotNumber() + "_" + descriptor() + "_" + shotVersion(node) + postVer(node)
    else: 
        return nuke.root().name().split("/")[-1].split(".")[0] 

### RENDERNODE FUNCTIONS ###

# Checks to see what the latest version of the RenderNode and updates it if it is old.
# The check is performed when a user tries to initiate a render.
def verCheck(node=nuke.thisNode()):
    nodeName = nuke.thisNode().name()
    message = "Would you like to update the %s to the latest version?" % (nodeName)
    try:
        curVer = node['renderNodeVersion'].value()
        # Checks to see what the current version is.
        if curVer >= renNodeVer:
            return "pass"
        # Load Latest RenderNode Version
        else:
            if nuke.ask(message):
                # Number of inputs of the RenderNode
                inputNum = 2
                renNode = node
                # Saves original inputs
                prevInputs = []
                for x in range(inputNum):
                    prevInputs.append(renNode.input(x))
                # Saves the values of the knobs
                knobs = ["v_num", "verControl", "curVer", "cropCheck","shotNotes", "lutFile", "lutControl", "format","viewMenu"]
                knobValues = []
                for x in knobs:
                    knobValues.append(renNode[x].value())
                xPos = renNode["xpos"].value()
                yPos = renNode["ypos"].value()
                # Create updated RenderNode- if you make the node into a gizmo, change nuke.loadToolset into nuke.createNode
                nuke.root().begin()
                newNode = nuke.loadToolset(rendernodeFile.replace("\\","/"))
                newNode.setXYpos(int(xPos), int(yPos))
                # Applies values to the new knobs
                for x in knobs:
                    newNode[x].setValue(knobValues[knobs.index(x)])
                # Sets the original inputs    
                for x in range(inputNum):
                    newNode.setInput(x, prevInputs[x])
                nuke.root().end()
                nuke.delete(renNode)
                return "break"
    except:
        pass

# Used to find what the latest render of the current script is
def latestCompRender():
    curPath = outputPath()
    folders = []
    # Sorts through the render directory and creates a list of the current renders
    for theFile in os.listdir(curPath):
        if sequence() + shotNumber() + "_" + descriptor() in theFile:
            folders.append(theFile)
    newFolder = []
    # Filters the list of renders into a new one, with only the version numbers getting appened
    for listItem in folders:
        for match in re.findall(r'_v\d{2,}', listItem):
            newFolder.append(match.replace("_v", ""))
    # Checks to see what is the highest version number in the list
    if len(newFolder) > 0:
        latVer = max(newFolder)
        nuke.thisNode()['curVer'].setValue("v" + latVer)
    else:
        message = "No previous versions found"
        nuke.thisNode()['curVer'].setValue(message)

# Used to direct the user to the folder containing the shot's LUT files.
def lutCheck():
    lutPath = outputPath(lutDestFolder)
    try:  
        lutDest = nuke.getFilename('Select Latest LUT', default= lutPath)
        if isinstance(lutDest, str) is True:
            nuke.thisNode()['lutFile'].setValue(lutDest)
    except TypeError:
        pass

### PATHS ###

checkedFold = [""]
counter = 0

# Gets the current path of the script
def getCurPath():
    return os.path.dirname(nuke.root().name())

# Finds the location of the destFold folder. 
def outputPath(safety="on", targetFolder=destFold, currentPath=getCurPath(), counter=counter):
    # Stops the function if it seems that the script name is not consistant with the filename conventions
    if scriptName() == 'Root' or "_".join(scriptName()).count("_") < 3:
        return "This script is not properly named, terminating the search process."
    # Checks to see if the current folder matches
    if counter == 0:
        currentPath = getCurPath()
    else:
        pass

    def getCurDir(currentPath):
        directory = currentPath.split("/")[-1]
        if directory == "":
            return currentPath
        else:
            return directory
            
    currentDir = str(getCurDir(currentPath))
    if fnmatch.fnmatchcase(currentDir, targetFolder):
        return os.path.join(currentPath).replace("\\", "/") + "/"
    # Lists all of the subdirectories of the current folder
    curSubDirs = os.listdir(currentPath)
    # Searches through the subdirectories
    for folder in curSubDirs:
        # Filters the contents of curSubDirs for only folders and exempts the folder we just came out of
        if os.path.isdir(os.path.join(currentPath, folder)) and folder != "".join(checkedFold):
            # Checks to see if any of the subdirectories are a match
            if fnmatch.fnmatchcase(folder, targetFolder):
                return os.path.join(currentPath, folder).replace("\\", "/") + "/"
            # Walks down each of the folder directories and checks all of its contents 
            for root, dirs, files in os.walk(os.path.join(currentPath, folder)):
                for subFolder in dirs:
                    if fnmatch.fnmatchcase(subFolder, targetFolder):
                        return os.path.normpath(os.path.join(root, subFolder)).replace("\\", "/") + "/"
    counter += 1
    # Setting checkedFold to whatever directory we just traversed, so that we don't check it again
    checkedFold[0] = currentDir
    # Move one level up from the directory we just chekced
    newPath = os.path.dirname(currentPath)
    newDir = getCurDir(newPath)
    warning = "The RenderNode was unable to find the folder '%s' within:\n%s." %(targetFolder, currentPath)
    # Safety net to prevent excessive recursion.  Will stop looking if it finds the shot's main folder
    # or if it moves up more than 5 folder structures. 
    sequenceFolders = [sceneName() + "_" + sequence() + shotNumber(), sceneName()]
    rootFolders = [r'[a-zA-Z]:/$', r'/$']
    if safety == "on":
        for x in range(2):
            if re.match(sequenceFolders[x], currentDir) or re.match(rootFolders[x], newDir) or counter >5:
                return nuke.message(warning) 
    return outputPath(safety, targetFolder, newPath, counter)

def dpxPath(node=nuke.thisParent()):
    try:
        return outputPath() + shotName(node) + "/" + shotName(node)
    except (AttributeError, TypeError):
        return "break"

def exrPath(node=nuke.thisParent()):
    try:
        return outputPath() + shotName(node) + "/" + shotName(node)
    except (AttributeError, TypeError):
        return "break"

def qtPath(node=nuke.thisParent()):
    try:
        return outputPath() + shotName(node)
    except (AttributeError, TypeError):
        return "break"

### SLATE ###

# Artist Name- you can use this function to automatically detect which artist is working on any given shot
# The current method searches for specific folders in each user's home directory, and recognizes which user 
# it is based on what folder it finds.
# If artists are bringing in their own machines you can find match their names to their hostnames.
# ie. Code:     import socket
#               if socket.gethostname() == "Davide's-PC":
#                    return "Davide Curletti" 
# 12core
# 

def artName():
    hostName = socket.gethostname()
    if hostName == "Davide-PC":
        return "Davide Curletti"
    elif hostName == "12core":
        return "Artist #2"
    else:
        return "Unregistered User"


### RENDERING ###

# Used to initialize the rendering process for DPX files
def renderDPX(node=nuke.thisNode()):
    verCheck(node)
    if verCheck(node) == "pass" and dpxPath(node) != 'break':
        # Assign values
        renDPX = nuke.toNode("Final_RenderNode")
        renderNode = node
        xPos = renderNode['xpos'].value()
        yPos = renderNode['ypos'].value()
        renFolder = os.path.dirname(dpxPath(node))
        # If a previous render exists, asks the user whether they would like to delete the files
        if os.path.exists(renFolder):
            if nuke.ask("Would you like to remove the previously rendered files?"):
                shutil.rmtree(renFolder)
        # Render the comp
        """ This part needs a callback to stop the function if the render is canceled """
        renDPX['Render'].execute()
        # Create the read node
        nuke.root().begin()
        if renderNode.input(1):
            readNode = renderNode.input(1)
            readNode['file'].fromUserText(dpxPath(node) + ".####.exr" + ' ' + str(nuke.root().firstFrame() - startFrame) + '-' + str(nuke.root().lastFrame()))
            readNode['reload'].execute()
            nuke.root().end()
        else:
            readNode = nuke.nodes.Read(colorspace = dpxImportColor)
            readNode['file'].fromUserText(dpxPath(node) + ".####.exr" + ' ' + str(nuke.root().firstFrame() - startFrame) + '-' + str(nuke.root().lastFrame()))
            # Place the read node
            readNode.setXYpos(int(xPos - 170), int(yPos - 36))
            # nuke.autoplaceSnap(readNode)
            renderNode.setInput(1, readNode)
            nuke.root().end()
    else:
        pass

# Used to initialize the rendering process for the Qucktime files
def renderQTS(node=nuke.thisNode()):
    verCheck(node)
    if verCheck(node) == "pass" and dpxPath(node) != 'break':
        # Assign Variables
        renderNode = node
        qtPath = outputPath()
        node.begin()
        switch = nuke.toNode("Controller")['which']
        origSwitchValue = switch.animation(0).expression()
        editRender = nuke.toNode("Editorial_RenderNode")
        vfxRender = nuke.toNode("VFX_RenderNode")
        # If QTs already exist, remove them
        for the_file in os.listdir(qtPath):
            file_path = os.path.join(qtPath, the_file)
            if os.path.isfile(file_path) and shotName(node) in the_file:
                os.remove(file_path)
        # Begin rendering
        switch.setExpression(str(0))
        # Sets off specific write nodes depending on the user input
        """ This part needs a callback to stop the function if the render is canceled """
        warning = "In order to render a Quicktime file you must have the DPX input connected to an input."
        if node.input(1):
            try:
                if numQTS == 1:
                    nuke.execute(editRender, (nuke.root().firstFrame()-startFrame), (nuke.root().lastFrame()))
                else:
                    nuke.execute(vfxRender, (nuke.root().firstFrame()-startFrame), (nuke.root().lastFrame()))
                    nuke.execute(editRender, (nuke.root().firstFrame()-startFrame), (nuke.root().lastFrame()))
            except RuntimeError:
                switch.setExpression(origSwitchValue)
                node.end()
                nuke.message(warning)
        else:
            nuke.message(warning)
        switch.setExpression(origSwitchValue)
        node.end()
    else:
        pass

# # Used to initialize the rendering process for both the DPXs and the Quicktimes
def renderAll(node=nuke.thisNode()):
    verCheck(node)
    if verCheck(node) == "pass" and dpxPath(node) != 'break':
        """ This part needs a callback to stop the function if the render is canceled """
        renderDPX(node)
        renderQTS(node)
    else:
        pass


