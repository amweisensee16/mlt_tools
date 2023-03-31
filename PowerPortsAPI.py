import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import PySimpleGUI as sg
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables SSL Cert checking

#You must create the ports before use of this script**INCLUDING INPUT**
#This script is used for automating alternative phaselegs/breakers
#Mostly for interal use only works in main library or custom models
#Will auto convert voltage for single phase/double phase


def changemodel(ip,user,password,modelname,breaker,breakercnt,amps,legoption):
   auth = HTTPBasicAuth(user,password) #Needed for authetication

   headers = {
   'Content-Type': 'application/json'
   } #Basic header

   search = "https://" + ip + "/api/v2/quicksearch/models?pageNumber=1&pageSize=100"


   singlephasevolt = {
      "208": "120",
      "380": "220",
      "400": "230",
      "415": "415",
      "480": "277"
   }

   f = open("search.json",'r')
   thing = json.load(f) #Loads search.json file for searching
   thing['columns'][0]['filter']['contains'] = modelname #Puts ID in json this is the name of item
   thing['columns'][0]['displayValue'] = modelname

   item = requests.request("POST",search,json = thing,headers=headers,verify=False,auth=auth)
   item_raw = item.text
   item_json = json.loads(item_raw)
   #print(item_json)
   
   modelID = item_json['searchResults']['models'][0]['modelId'] #Pulls ID of first result
   print("ModelID: " + str(modelID))
   if item_json['searchResults']['models'][0]['model'] != modelname:
      return "No model"

   detail = "https://" + ip + "/api/v2/models/" + str(modelID)
   details = requests.request("GET",detail,headers=headers,verify=False,auth=auth)
   details_json = json.loads(details.text)

   inputvoltage = details_json['powerPorts'][0]['volts']

   with open("output.json", "w") as outfile:
      outfile.write(json.dumps(details_json,indent=4))

   outputcount = len(details_json['powerPorts'])-1 #count minus input

   #For testing
   with open("example.json", "w") as outfile:
      outfile.write(json.dumps(details_json,indent=4))

   
   previousloc = 1

   #With breakers
   if(breaker == True):
      loopcount = int(int(breakercnt)/3)
      smallloopsize = int(len(details_json['powerPorts'])/loopcount)
      for y in range(0,loopcount):
         print(y)
         if(legoption == True):
            for x in range(previousloc,(smallloopsize*y)+smallloopsize,3):
               details_json['powerPorts'][x]['phaseLegs'] = "AB"
               details_json['powerPorts'][x]['fuseBreakerName'] = "CB"+str(((y*3)+1)).zfill(2)
               details_json['powerPorts'][x]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x]['volts'] = inputvoltage
               details_json['powerPorts'][x+1]['phaseLegs'] = "BC"
               details_json['powerPorts'][x+1]['fuseBreakerName'] = "CB"+str(((y*3)+2)).zfill(2)
               details_json['powerPorts'][x+1]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x+1]['volts'] = inputvoltage
               details_json['powerPorts'][x+2]['phaseLegs'] = "CA"
               details_json['powerPorts'][x+2]['fuseBreakerName'] = "CB"+str(((y*3)+3)).zfill(2)
               details_json['powerPorts'][x+2]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x+2]['volts'] = inputvoltage
            previousloc += smallloopsize 
         if(legoption == False):
            for x in range(previousloc,(smallloopsize*y)+smallloopsize,3):
               details_json['powerPorts'][x]['phaseLegs'] = "A"
               details_json['powerPorts'][x]['fuseBreakerName'] = "CB"+str(((y*3)+1)).zfill(2)
               details_json['powerPorts'][x]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x]['volts'] = singlephasevolt[inputvoltage]
               details_json['powerPorts'][x+1]['phaseLegs'] = "B"
               details_json['powerPorts'][x+1]['fuseBreakerName'] = "CB"+str(((y*3)+2)).zfill(2)
               details_json['powerPorts'][x+1]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x+1]['volts'] = singlephasevolt[inputvoltage]
               details_json['powerPorts'][x+2]['phaseLegs'] = "C"
               details_json['powerPorts'][x+2]['fuseBreakerName'] = "CB"+str(((y*3)+3)).zfill(2)
               details_json['powerPorts'][x+2]['fuseBreakerAmps'] = amps
               details_json['powerPorts'][x+2]['volts'] = singlephasevolt[inputvoltage]
            previousloc += smallloopsize 

   #Without breakers
   else:
      if(legoption == True):
         for x in range(1,len(details_json['powerPorts']),3):
            details_json['powerPorts'][x]['phaseLegs'] = "AB"
            details_json['powerPorts'][x]['volts'] = inputvoltage
            try:
               del details_json['powerPorts'][x]['fuseBreakerName']
               del details_json['powerPorts'][x]['fuseBreakerAmps']
            except:
               pass
            details_json['powerPorts'][x+1]['phaseLegs'] = "BC"
            details_json['powerPorts'][x]['volts'] = inputvoltage
            try:
               del details_json['powerPorts'][x+1]['fuseBreakerName']
               del details_json['powerPorts'][x+1]['fuseBreakerAmps']
            except:
               pass
            details_json['powerPorts'][x+2]['phaseLegs'] = "CB"
            details_json['powerPorts'][x]['volts'] = inputvoltage
            try:
               del details_json['powerPorts'][x+2]['fuseBreakerName']
               del details_json['powerPorts'][x+2]['fuseBreakerAmps']
            except:
               pass
      if(legoption == False):
         for x in range(1,len(details_json['powerPorts']),3):
            details_json['powerPorts'][x]['phaseLegs'] = "A"
            details_json['powerPorts'][x]['volts'] = singlephasevolt[inputvoltage]
            try:
               del details_json['powerPorts'][x]['fuseBreakerName']
               del details_json['powerPorts'][x]['fuseBreakerAmps']
            except:
               pass
            details_json['powerPorts'][x+1]['phaseLegs'] = "B"
            details_json['powerPorts'][x+1]['volts'] = singlephasevolt[inputvoltage]
            try:
               del details_json['powerPorts'][x+1]['fuseBreakerName']
               del details_json['powerPorts'][x+1]['fuseBreakerAmps']
            except:
               pass
            details_json['powerPorts'][x+2]['phaseLegs'] = "C"
            details_json['powerPorts'][x+2]['volts'] = singlephasevolt[inputvoltage]
            try:
               del details_json['powerPorts'][x+2]['fuseBreakerName']
               del details_json['powerPorts'][x+2]['fuseBreakerAmps']
            except:
               pass
      

   #Can be used for troubleshooting
   #with open("example.json", "w") as outfile:
   #   outfile.write(json.dumps(details_json,indent=4))


   #Sends the changes that we made
   modifymodel = "https://" + ip + "/api/v2/models/" + str(modelID) + "?ReturnDetails=true" +"&proceedOnWarning=false"
   change =  requests.put(modifymodel,json=details_json, headers=headers,verify=False,auth=auth)
   print(change)
   change_json = json.loads(change.text)
   #print(change.text) #For testing
   return change



file_list_column = [

   [
      sg.Text("IP Address"),
      sg.InputText(size=(20, 1)),

      sg.Text("Username"),
      sg.InputText(size=(10, 1)),

      sg.Text("Password"),
      sg.InputText(size=(10, 1))
   ],
   [
      sg.Text("Model Name(MUST BE ACCURATE)"),
      sg.InputText(size=(10, 1)),
   ],

   [
      sg.Checkbox("Has Breakers",default=False)
   ],
   [
      sg.Text("Breaker Count(MUST be multple of 3)"),
      sg.InputText(size=(10, 1)),
      sg.Text("Breaker Amps"),
      sg.InputText(size=(10, 1))
   ],
   [
      sg.Radio("Phase Legs: AB, BC, CA","RADI01",default=True),
      sg.Radio("Phase Legs: A, B, C","RADI01",default=False),

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
while True:

   event, values = window.read()
   if event == "Exit" or event == sg.WIN_CLOSED:
      exit()
   if event == "Run" and int(values[4]) % 3 == 0:         
      print(values[0],values[1],values[2],values[3],values[4],values[5])
      response = changemodel(values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7])
      if response == "No model":
         window['-OUTPUT-'].update("Couldn't Find model") 
      elif response.status_code == 200:
         window['-OUTPUT-'].update("Changes Made")
      elif response.status_code == 400:
         window['-OUTPUT-'].update("Bad Request")  
      elif response.status_code == 401:
         window['-OUTPUT-'].update("Authenitcation failed")
      elif response.status_code == 404:
         window['-OUTPUT-'].update("Invalid Path")
      
   else:
      values[4] = ''
