import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import PySimpleGUI as sg
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables SSL Cert checking

#You must create the ports before use of this script**INCLUDING INPUT**
#This script is used for automating alternative phaselegs/breakers
#Mostly for interal use only works in main library or custom models
#Will auto convert voltage for single phase/double phase
#Also now works for grouped phase legs

#TODO: Add grouping for breakers
#TODO: Allow for port creation


def searchModel(auth,ip,modelname):
   headers = {
   'Content-Type': 'application/json'
   } #Basic header

   search = "https://" + ip + "/api/v2/quicksearch/models?pageNumber=1&pageSize=100"

   thing ={
      "columns": [
         {
            "displayValue": "APITestingmodel",
            "filter": {
               "contains": "APITestingmodel"
            },
            "name": "cmbModel"
         }
      ],
      "selectedColumns": []
   }
   thing['columns'][0]['filter']['contains'] = modelname #Puts ID in json this is the name of item
   thing['columns'][0]['displayValue'] = modelname

   item = requests.request("POST",search,json = thing,headers=headers,verify=False,auth=auth)
   item_raw = item.text
   item_json = json.loads(item_raw)
   #print(item_json)
   return item_json

def getModelInfo(auth,ip,modelID):
   headers = {
   'Content-Type': 'application/json'
   } #Basic header
   detail = "https://" + ip + "/api/v2/models/" + str(modelID)
   details = requests.request("GET",detail,headers=headers,verify=False,auth=auth)
   details_json = json.loads(details.text)
   return details_json

def modifyModel(ip,auth,modelID,json):
   headers = {
   'Content-Type': 'application/json'
   } #Basic header
   modifymodel = "https://" + ip + "/api/v2/models/" + str(modelID) + "?ReturnDetails=true" +"&proceedOnWarning=false"
   change =  requests.put(modifymodel,json=json, headers=headers,verify=False,auth=auth)
   return change



def incrementModel(ip,user,password,modelname,breaker,breakercnt,amps,legoption):
   auth = HTTPBasicAuth(user,password) #Needed for authetication

   headers = {
   'Content-Type': 'application/json'
   } #Basic header

   singlephasevolt = {
      "208": "120",
      "380": "220",
      "400": "230",
      "415": "415",
      "480": "277"
   }

   item_json = searchModel(auth,ip,modelname)
   
   try:
      modelID = item_json['searchResults']['models'][0]['modelId'] #Pulls ID of first result
   except:
      return "No model"
   print("ModelID: " + str(modelID))
   if item_json['searchResults']['models'][0]['model'] != modelname:
      return "No model"
   print("Something")

   details_json = getModelInfo(auth,ip,modelID)
   
   inputvoltage = details_json['powerPorts'][0]['volts']

   #with open("output.json", "w") as outfile:
   #   outfile.write(json.dumps(details_json,indent=4))

   outputcount = len(details_json['powerPorts'])-1 #count minus input

   #For testing
   #with open("example.json", "w") as outfile:
   #   outfile.write(json.dumps(details_json,indent=4))

   
   previousloc = 1
   #Least messy/indented for loop
   #With breakers
   details_json = incLeg(legoption,details_json,singlephasevolt)

   details_json = followBreaker(breaker,details_json,breakercnt)
   
   #Sends the changes that we made
   change = modifyModel(ip,auth,modelID,details_json)
   return change

def groupModel(ip,user,password,modelname,breaker,breakercnt,amps,legoption,groupsize):
   auth = HTTPBasicAuth(user,password) #Needed for authetication

   headers = {
   'Content-Type': 'application/json'
   } #Basic header

   singlephasevolt = {
      "208": "120",
      "380": "220",
      "400": "230",
      "415": "415",
      "480": "277"
   }

   item_json = searchModel(auth,ip,modelname)
   amps = int(amps)
   try:
      modelID = item_json['searchResults']['models'][0]['modelId'] #Pulls ID of first result
   except:
      return "No model"
   print("ModelID: " + str(modelID))
   if item_json['searchResults']['models'][0]['model'] != modelname:
      return "No model"
   print("Something")

   details_json = getModelInfo(auth,ip,modelID)
   
   inputvoltage = details_json['powerPorts'][0]['volts']

   #with open("output.json", "w") as outfile:
   #   outfile.write(json.dumps(details_json,indent=4))

   outputcount = len(details_json['powerPorts'])-1 #count minus input

   if outputcount%groupsize != 0:
      print(outputcount,' ',groupsize)
      return "Invalid Group Size"

   #For testing
   
   print(groupsize)
   previousloc = 1
   #Least messy/indented for loop
   #With breakers
   details_json = groupLeg(legoption,details_json,groupsize,amps,singlephasevolt)

   
   
   #Does the circuit Breakers
   #TODO Change to grouping

   details_json = followBreaker(breaker,details_json,breakercnt)

   #with open("example.json", "w") as outfile:
   #   outfile.write(json.dumps(details_json,indent=4))

   #Sends the changes that we made
   change = modifyModel(ip,auth,modelID,details_json)
   return change

def incLeg(legoption,details_json,singlephasevolt):
   inputvoltage = details_json['powerPorts'][0]['volts']
   outputcount = len(details_json['powerPorts'])
   if(legoption == True):
      for x in range(1,outputcount,3):
         details_json['powerPorts'][x]['phaseLegs'] = "AB"
         details_json['powerPorts'][x]['volts'] = inputvoltage
         details_json['powerPorts'][x+1]['phaseLegs'] = "BC"
         details_json['powerPorts'][x+1]['volts'] = inputvoltage
         details_json['powerPorts'][x+2]['phaseLegs'] = "CA"
         details_json['powerPorts'][x+2]['volts'] = inputvoltage
   else:
      for x in range(1,outputcount,3):
         details_json['powerPorts'][x]['phaseLegs'] = "A"
         details_json['powerPorts'][x]['volts'] = singlephasevolt[inputvoltage]
         details_json['powerPorts'][x+1]['phaseLegs'] = "B"
         details_json['powerPorts'][x+1]['volts'] = singlephasevolt[inputvoltage]
         details_json['powerPorts'][x+2]['phaseLegs'] = "C"
         details_json['powerPorts'][x+2]['volts'] = singlephasevolt[inputvoltage]
   return details_json


def groupLeg(legoption,details_json,groupsize,amps,singlephasevolt):
   inputvoltage = details_json['powerPorts'][0]['volts']
   outputcount = len(details_json['powerPorts'])
   if(legoption==True):
      #Makes Phases/voltage
      for x in range(1,outputcount,groupsize*3):
         for y in range(x,x+groupsize):
            details_json['powerPorts'][y]['phaseLegs'] = "AB"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = inputvoltage
         for y in range(x+groupsize,x+(groupsize*2)):
            details_json['powerPorts'][y]['phaseLegs'] = "BC"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = inputvoltage
         for y in range(x+(groupsize*2),x+(groupsize*3)):
            details_json['powerPorts'][y]['phaseLegs'] = "CA"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = inputvoltage

   if(legoption == False):
      #Makes Phases/voltage
      for x in range(1,outputcount,groupsize*3):
         for y in range(x,x+groupsize):
            details_json['powerPorts'][y]['phaseLegs'] = "A"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = singlephasevolt[inputvoltage]
         for y in range(x+groupsize,x+(groupsize*2)):
            details_json['powerPorts'][y]['phaseLegs'] = "B"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = singlephasevolt[inputvoltage]
         for y in range(x+(groupsize*2),x+(groupsize*3)):
            details_json['powerPorts'][y]['phaseLegs'] = "C"
            details_json['powerPorts'][y]['fuseBreakerAmps'] = amps
            details_json['powerPorts'][y]['volts'] = singlephasevolt[inputvoltage]
   return details_json

def incBreaker(breaker,details_json,amps):
   outputcount = len(details_json['powerPorts'])
   if(breaker == True):
      for x in range(1,outputcount,3):
         bnum = int(x/3)
         details_json['powerPorts'][x]['fuseBreakerName'] = "CB"+str(bnum).zfill(2)
         details_json['powerPorts'][x]['fuseBreakerAmps'] = amps
         details_json['powerPorts'][x+1]['fuseBreakerName'] = "CB"+str(bnum+1).zfill(2)
         details_json['powerPorts'][x+1]['fuseBreakerAmps'] = amps
         details_json['powerPorts'][x+2]['fuseBreakerName'] = "CB"+str(bnum+2).zfill(2)
         details_json['powerPorts'][x+2]['fuseBreakerAmps'] = amps
   else:
      for x in range(1,outputcount):
         try:
            del details_json['powerPorts'][x]['fuseBreakerName']
            del details_json['powerPorts'][x]['fuseBreakerAmps']
         except:
            pass
   return details_json

def followBreaker(breaker,details_json,breakercnt):
   outputcount = len(details_json['powerPorts'])
   loopcount = int(int(breakercnt)/3)
   smallloopsize = int(len(details_json['powerPorts'])/loopcount)
   if(breaker == True):
      for x in range(1,outputcount,smallloopsize):
         b = int(((x/smallloopsize)*3)+1)
         for y in range(x,outputcount):
            if(details_json['powerPorts'][y]['phaseLegs'] == "AB" or details_json['powerPorts'][y]['phaseLegs'] == "A"):
               details_json['powerPorts'][y]['fuseBreakerName'] = "CB"+str(b).zfill(2)
            if(details_json['powerPorts'][y]['phaseLegs'] == "BC" or details_json['powerPorts'][y]['phaseLegs'] == "B"):
               details_json['powerPorts'][y]['fuseBreakerName'] = "CB"+str(b+1).zfill(2)
            if(details_json['powerPorts'][y]['phaseLegs'] == "CA" or details_json['powerPorts'][y]['phaseLegs'] == "C"):
               details_json['powerPorts'][y]['fuseBreakerName'] = "CB"+str(b+2).zfill(2)
   if(breaker == False):
      for x in range(1,outputcount):
         try:
            del details_json['powerPorts'][x]['fuseBreakerName']
            del details_json['powerPorts'][x]['fuseBreakerAmps']
         except:
            pass
   return details_json

#def groupBreaker(legoption):
   

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
      sg.Radio("Incrimental(A B C A B C)","RADI02",default=False,key='incr/group'),
      sg.Radio("Grouped(A A B B C C)","RADI02",default=True),

   ],

   [
      sg.Text("If Grouped:"),
      sg.Text("Group Size (2: A A, 3: A A A)"),
      sg.InputText(size=(10, 1),key = '-GROUPSIZE-')
   ],

   [
      sg.Text("OUTPUT:"),
      sg.Text(size=(15,1),key='-OUTPUT-')
   ],

   [
      sg.Button('Run'),
      sg.Exit()
   ]

]

window = sg.Window("Model PDU Phase Breaker Fix",file_list_column)

#Makes up event statements
#TODO: Allow turning off modifying phase or breaker
while True:

   event, values = window.read()
   if event == "Exit" or event == sg.WIN_CLOSED:
      sys.exit("Exit Program")
   if event == "Run" and int(values['breakercount']) % 3 == 0:
      if(values['incr/group'] == True):
         response = incrementModel(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'],values['phaselegs'])
      else:
         #groupModel(ip,user,password,modelname,breaker,breakercnt,amps,legoption,groupsize):
         response = groupModel(values['ip'],values['user'],values['password'],values['modelname'],values['breaker'],values['breakercount'],values['amps'],values['phaselegs'],int(values['-GROUPSIZE-']))
      if response == "No model":
         window['-OUTPUT-'].update("Couldn't Find model") 
      elif response == "Invalid Group Size":
         window['-OUTPUT-'].update("Invalid Group Size") 
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