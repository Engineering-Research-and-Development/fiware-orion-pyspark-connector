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


def EncodeMsgFromBlueprint(values):
    
    values = Listify(values)

    
    prev_root = ""
    prev_depth = 0
    msg = "{"
    try:
        f = open(rconf.BLUEPRINTFILE, "r")
    except:
        print("No JSON blueprint file found. Please, check the conf file and make sure the path to the blueprint file is correct.")
        print("If no blueprint file was created, please, make one by calling the function BlueprintJSON()")
        return
    
    try:
        lines = f.readlines()
        if len(values) != len(lines):
            print("The number of values and the number of fields does not match!")
            return
        for index, line in enumerate(lines):
            line = line.replace("\n", "")
            t, content = line.split(" ")
            depth = content.count("\\")
            recursion_vars = content.split("\\")

            root = recursion_vars[0:-1]
            var = recursion_vars[-1]

            if root != prev_root:
                if (msg[-1] == ","):
                    msg = msg[:-1]
                    
                diff = ComputeDifferenceInDepth(prev_root, root)
                if diff >0:
                    for j in range (0, diff):
                        msg = msg + "}"
                else:
                    for j in range (0, prev_depth):
                        msg = msg + "}"
                    
                    
                if (len(msg) > 1):
                    msg = msg + ","

                
                for w in root:
                    if w not in prev_root:
                        msg = msg + '"{}":'.format(w) + "{"
                
                varname, val = var.split(":")
                msg = msg + '"{}":{},'.format(varname, val).format(values[index])
                
                prev_root = root
                prev_depth = depth
            else:
                varname, val = var.split(":")
                msg = msg + '"{}":{},'.format(varname, val).format(values[index])
                

        msg = msg[:-1]
        for j in range (0, prev_depth):
            msg = msg + "}"
        msg = msg + "}\n"        
        f.close()
        return msg
    except Exception as e:
        print(e)
        print("An error occurred in reading the JSON Blueprint.")
        print("Make sure that the blueprint is generated correctly by the BlueprintJSON() function in the library")
        
        
def ReplyToBroker(values, apiURL=rconf.API_URL, apiMethod=rconf.METHOD):
    msg = EncodeMsgFromBlueprint(values)
    headers= {"Content-Type": "application/json; charset=utf-8"}
    
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
