import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables SSL Cert checking

#You must create the ports before use of this script**INCLUDING INPUT**
#This script is used for automating alternative phaselegs/breakers
#Mostly for interal use only works in main library or custom models
#Will auto convert voltage for single phase/double phase


user = str(input("Username: "))
password = str(input("Password: "))
auth = HTTPBasicAuth(user,password) #Needed for authetication
modelname =  str(input("Model Name: "))

headers = {
  'Content-Type': 'application/json'
} #Basic header

search = "https://10.34.0.155/api/v2/quicksearch/models?pageNumber=1&pageSize=100"


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
print(modelID)


detail = "https://10.34.0.155/api/v2/models/" + str(modelID)
details = requests.request("GET",detail,headers=headers,verify=False,auth=auth)
details_json = json.loads(details.text)

inputvoltage = details_json['powerPorts'][0]['volts']

with open("output.json", "w") as outfile:
   outfile.write(json.dumps(details_json,indent=4))

outputcount = len(details_json['powerPorts'])-1 #count minus input

print("Will there be breakers in this model(y/n)")
breaker = input()
if(breaker == "y"):
   print("How many breakers are there(Multiple of 3)?")
   ans = input()
   breakernum = int(ans)
   if(breakernum % 3 != 0):
      print("Not multiple of 3")
      exit
   print("What is the breaker Fuse amps?")
   amps = int(input())


print("Phaseleg Pattern:")
print("1: for AB,BC,CA ")
print("2: for A,B,C")
bruh = input()

loopcount = int(breakernum/3)

#For testing
with open("example.json", "w") as outfile:
   outfile.write(json.dumps(details_json,indent=4))

smallloopsize = int(len(details_json['powerPorts'])/loopcount)
previousloc = 1

#With breakers
if(breaker == "y"):
   for y in range(0,loopcount):
      print(y)
      if(int(bruh) == 1):
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
      if(int(bruh) == 2):
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
   if(int(bruh) == 1):
      for x in range(1,len(details_json['powerPorts']),3):
            print(x)
            details_json['powerPorts'][x]['phaseLegs'] = "AB"
            details_json['powerPorts'][x+1]['phaseLegs'] = "BC"
            details_json['powerPorts'][x+2]['phaseLegs'] = "CA"
   if(int(bruh) == 2):
      for x in range(1,len(details_json['model']['tabPowerPorts']),3):
         details_json['powerPorts'][x]['phaseLegs'] = "A"
         details_json['powerPorts'][x]['volts'] = singlephasevolt[inputvoltage]
         details_json['powerPorts'][x+1]['phaseLegs'] = "B"
         details_json['powerPorts'][x+1]['volts'] = singlephasevolt[inputvoltage]
         details_json['powerPorts'][x+2]['phaseLegs'] = "C"
         details_json['powerPorts'][x+2]['volts'] = singlephasevolt[inputvoltage]
    

#Can be used for troubleshooting
#with open("example.json", "w") as outfile:
#   outfile.write(json.dumps(details_json,indent=4))


#Sends the changes that we made
modifymodel = "https://10.34.0.155/api/v2/models/" + str(modelID) + "?ReturnDetails=true" +"&proceedOnWarning=false"
change =  requests.put(modifymodel,json=details_json, headers=headers,verify=False,auth=auth)
print(change)
change_json = json.loads(change.text)
#print(change.text) #For testing
print("Done!")