from requests.auth import HTTPBasicAuth
import urllib3
import PySimpleGUI as sg
import sys
from modifyPorts import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables SSL Cert checking

#You must create the ports before use of this script**INCLUDING INPUT**
#This script is used for automating alternative phaselegs/breakers
#Mostly for interal use only works in main library or custom models
#Will auto convert voltage for single phase/double phase
#Also now works for grouped phase legs

#TODO: Have program check input phase type
#TODO: Allow for port creation

file_list_column = [

   [
      sg.Text("IP Address"),
      sg.InputText(size=(20, 1),key='ip'),

      sg.Text("Username"),
      sg.InputText(size=(10, 1),key='user'),

      sg.Text("Password"),
      sg.InputText(size=(10, 1),key='password')
   ],
   [
      sg.Text("Model Name(MUST BE ACCURATE)"),
      sg.InputText(size=(10, 1),key='modelname'),
   ],

   [
      sg.Checkbox("Has Breakers",default=False,key='breaker')
   ],
   [
      sg.Text("Breaker Count(MUST be multple of 3)"),
      sg.InputText(size=(10, 1),key='breakercount'),
      sg.Text("Breaker Amps"),
      sg.InputText(size=(10, 1),key='amps')
   ],
   [
      sg.Radio("Phase Legs: AB, BC, CA","RADI01",default=True,key='phaselegs'),
      sg.Radio("Phase Legs: A, B, C","RADI01",default=False),

   ],

   [
      sg.Radio("Incremental(A B C A B C)","RADI02",default=False,key='incr/group'),
      sg.Radio("Grouped(A A B B C C)","RADI02",default=True),

   ],

   [
      sg.Text("If Grouped:"),
      sg.Text("Group Size (2: A A, 3: A A A)"),
      sg.InputText(size=(10, 1),key = '-GROUPSIZE-')
   ],

   [
      sg.Text("Phase:"),
      sg.Radio("Singlephase","RADI04",default=False,key='singlephase'),
      sg.Radio("Is singlephase","RADI04",default=False,key='singlephase'),
      sg.Radio("Is singlephase","RADI04",default=False,key='singlephase')
   ],

   [
      sg.Text("If Single Phase & Has Breaker"),
      sg.Radio("Incremental(CB01,CB02,CB03)","RADI03",default=True,key='incr/group/single'),
      sg.Radio("Grouped(A A B B C C)","RADI03",default=False),
      
   ],

   [
      sg.Text("OUTPUT:"),
      sg.Text(size=(15,1),key='-OUTPUT-')
   ],

   [
      sg.Button('Create'),
      sg.Exit()
   ]

]
mainmenu = [
   [
      sg.Text("Edit Existing Ports"),
      sg.Button('Edit'),
      sg.Text("Create New Ports"),
      sg.Button('Create')
   ],
   [
      sg.Exit()
   ]
]


def ModifyWindow():
   window = sg.Window("Model PDU Phase Breaker Fix",file_list_column)
   while True:
      event, values = window.read()
      if event == "Exit" or event == sg.WIN_CLOSED:
         sys.exit("Exit Program")
      if event == "Create":


         if(values['incr/group'] == True and values['singlephase'] == False):
            response = incrementModel(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'],values['phaselegs'])
         elif(values['singlephase'] == True and values['incr/group/single'] == True):
            response = incSinglePhase(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'])
         elif(values['singlephase'] == True and values['incr/group/single'] == False):
            response = groupSinglePhase(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'],int(values['-GROUPSIZE-']))
         else:
            #groupModel(ip,user,password,modelname,breaker,breakercnt,amps,legoption,groupsize):
            response = groupModel(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'],values['phaselegs'],int(values['-GROUPSIZE-']))
         if response == "No model":
            window['-OUTPUT-'].update("Couldn't Find model") 
         elif response == "Invalid Group Size":
            window['-OUTPUT-'].update("Invalid Group Size") 
         elif response == "Wrong Phase Type":
            window['-OUTPUT-'].update("Wrong Phase Type") 
         elif response.status_code == 200:
            window['-OUTPUT-'].update("Changes Made")
         elif response.status_code == 400:
            window['-OUTPUT-'].update("Bad Request")  
         elif response.status_code == 401:
            window['-OUTPUT-'].update("Authenitcation failed")
         elif response.status_code == 404:
            window['-OUTPUT-'].update("Invalid Path")
         else:
            window['-OUTPUT-'].update("Unkown Error")
      else:
         values[4] = ''
def CreateWindow():
   print("BRUHDIS")
window = sg.Window("Model PDU Phase Breaker Fix",mainmenu)

while True:

   event, values = window.read()
   if event == "Exit" or event == sg.WIN_CLOSED:
      sys.exit("Exit Program")
   if event == "Create":
      ModifyWindow()
   if event == "Edit":
      ModifyWindow()