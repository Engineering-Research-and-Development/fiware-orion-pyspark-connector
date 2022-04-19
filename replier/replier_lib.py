import replyconf as rconf
import requests

def ComputeDifferenceInDepth(prev, act):
    diff = 0
    for w in act:
        if w in prev:
            diff += 1
            
    return diff


def Listify(values):
    
    if type(values) != type(list):
        values = [values]
            
    return values

        
        
def ReplaceJSON(values):
    
    values = Listify(values)
    f = open(rconf.BLUEPRINTFILE, "r")
    text=f.read()
    f.close()
    text = text.replace("\n", " ")
    for v in values:
        text = text.replace(rconf.PLACEHOLDER, str(v), 1)
        
    return text
        
        
def ReplyToBroker(values, apiURL=rconf.API_URL, apiMethod=rconf.METHOD):
    
    headers= {"Content-Type": rconf.CONTENT_TYPE, "Fiware-Service" : rconf.FIWARE_SERVICE, "Fiware-Servicepath": rconf.FIWARE_SERVICEPATH}
    msg = ReplaceJSON(values)
    
    try:
        if apiMethod == "POST":
            reply = requests.post(apiURL, msg, headers=headers)
        elif apiMethod == "PUT":
            reply = requests.put(apiURL, msg, headers=headers)
        elif apiMethod == "PATCH":
            reply = requests.patch(apiURL, msg, headers=headers)
        else:
            print("Method not allowed")
        reply = reply.text
    except Exception as e:
        reply = e
        
    return reply
    
    

def UnstructuredReplyToBroker(values, body, apiURL=rconf.API_URL, apiMethod=rconf.METHOD):
    
    headers= {"Content-Type": rconf.CONTENT_TYPE, "Fiware-Service" : rconf.FIWARE_SERVICE, "Fiware-Servicepath": rconf.FIWARE_SERVICEPATH}

    values = Listify(values)
    for v in values:
        body = body.replace(rconf.PLACEHOLDER, str(v), 1)
    
    
    try:
        if apiMethod == "POST":
            reply = requests.post(apiURL, body, headers=headers)
        elif apiMethod == "PUT":
            reply = requests.put(apiURL, body, headers=headers)
        elif apiMethod == "PATCH":
            reply = requests.patch(apiURL, body, headers=headers)
        else:
            print("Method not allowed")
        reply = reply.text
    except Exception as e:
        reply = e
        
    return reply
