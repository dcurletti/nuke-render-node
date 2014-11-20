nuke-render-node
================

Render node gizmo for The Foundry's Nuke


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
