from datetime import datetime
import requests
import json

from fpc.connectorconf import *
import sys



def ReturnEntityIfExists(ent):

    isLD = False
    keys = list(ent)
    attrs = {}
        
    ID = ent['id']
    keys.remove('id')
    typ = ent['type']
    keys.remove('type')
        
    if '@context' in keys:
        context = ent['@context']
        isLD = True
        keys.remove('@context')
        
    for i in range (0, len(keys)):
        att = ent[keys[i]]
        atttype = att['type']
            
        if atttype == "Relationship":
            attval = att['object']
        else:
            attval = att['value']
            
            
        try:
            attmeta = att['metadata']
        except:
            attmeta = {}
            
        attribute = NGSIAttribute(atttype, attval, attmeta)
        attrs[keys[i]] = attribute
       
    if isLD:
        entity = NGSIEntityLD(ID, typ, attrs, context)
    else:
        entity = NGSIEntityv2(ID, typ, attrs)
        
    
    return entity, isLD
    



def CreateSubscriptionPayload(name, typ, desc, attrlist, condlist):
    
    payload = {}
    payload['description']=desc
    payload['subject']={}
    payload['subject']['entities'] = []
    payload['subject']['entities'].append({'id':name, 'type':typ})
    payload['subject']['condition'] = {'attrs':condlist}
    payload['notification'] = {}
    payload['notification']['http'] = {'url':'http://'+RECV_SINGLETON.HTTPADDRESS+":"+str(RECV_SINGLETON.HTTPPORT)}
    payload['notification']['attrs'] = attrlist
    payload['expires'] = "2099-01-01T14:00:00.00Z"
    

    payload = json.dumps(payload)
    #print(payload)
    return payload
    
    
    
    
def CreateLDSubscriptionPayload(name, typ, desc, attrlist):
    
    payload = {}
    payload['description']=desc
    payload['@context']="https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
    payload['type']='Subscription'
    payload['entities'] = []
    payload['entities'].append({'id':name, 'type':typ})
    #payload['watchedAttributes'] = attrlist
    #payload['q'] = ""
    payload['notification'] = {}
    payload['notification']['attributes'] = attrlist
    payload['notification']['format'] = 'normalized'
    payload['notification']['endpoint'] = {'uri':'http://'+RECV_SINGLETON.HTTPADDRESS+":"+str(RECV_SINGLETON.HTTPPORT), 'accept':'application/ld+json'}
    

    payload = json.dumps(payload)
    print(payload)
    return payload
    
    
#TODO: Create subscription Conditions
#TODO: Add numbers for entities and attributes




def SelectEntity(get_entities_request, headers):

    select_entity = True
    try:
        
        reply = requests.get(get_entities_request, headers=headers)
        ents = reply.json()
        #print(ents)
        print("Found {} entities:".format(len(ents)))
        entx = [str(idx+1)+"):"+ent['id'] for idx, ent in enumerate(ents)]
        print(entx)
        
        while select_entity:
            try:
                entity_id = int(input("Please, type an entity number from the ones listed above: "))
                if entity_id >0 and entity_id <= len(entx):
                    select_entity = False
                    ent = ents[entity_id -1]
                else:
                    print("Entity not Found, please, insert a correct number:\n",entx)
            except Exception as e:
                print(e)
               
    except Exception as e:
        print(e)
        sys.exit("An error occurred while selecting the entity")
        
    return ent
    

   
def SelectAttributes(entity, mode='MONITOR'):

        
    attrlist = [attr for attr in entity.attrs]
        
    if mode == 'MONITOR':    
        print("Type the attribute number you want to RETURN. Type '>QUIT' to stop. Type '>ALL' to insert all attributes")
    elif mode == 'CONDITION':
        print("Type the attribute number you want to set as CONDITION. Type '>QUIT' to stop. Type '>ALL' or '>QUIT' if no attribute is selected to insert all attributes")
    continuing = True
    returnlist = []
    while continuing:
        showlist = [str(idx+1)+"):"+attr for idx, attr in enumerate(attrlist)]
        print(showlist)
        try:
            if len(attrlist) <= 0:
                continuing = False
                print("Attribute list is now empty, quitting selection...")
                continue
            string = str(input("Insert attribute name: "))
                
                    
            if string.upper() == '>QUIT':
                print("Quitting Selection")
                continuing = False
                
                
            elif string.upper() == '>ALL':
                print("Inserting All attributes")
                continuing = False
                if mode == 'MONITOR':
                    returnlist = attrlist
                elif mode == 'CONDITION':
                    returnlist = []
                    
                    
            elif int(string) > 0 and int(string) <= len(attrlist):
                index = int(string) -1
                print("Attribute {} found. Adding to attributes".format(attrlist[index]))
                returnlist.append(attrlist[index])
                attrlist.remove(attrlist[index])
              
            else:
                print("Attribute not found, please, type it correctly. The remaining list of attributes is:", showlist)
        except Exception as e:
            print(e)
            #return
                
    return returnlist



def SubscribeToEntity(base_url):


    headers= {"Fiware-Service" : REPL_SINGLETON.FIWARE_SERVICE, "Fiware-Servicepath": REPL_SINGLETON.FIWARE_SERVICEPATH}
    
    if 'ngsi-ld' in base_url:
        isLD = True
        get_entities_request = base_url+"entities/?type="
    else:
        isLD = False
        get_entities_request = base_url+"entities/"
    
    
    ent = SelectEntity(get_entities_request, headers)
        

    
    try:

        entity, _ = ReturnEntityIfExists(ent)

        
        print("Entity found!")
        
        attrlist = [attr for attr in entity.attrs]
        
        returnlist = SelectAttributes(entity, mode='MONITOR')
        conditionlist = SelectAttributes(entity, mode='CONDITION')       
        
        try:
            description = str(input("Please, insert a description to add: "))
        except Exception as e:
            print("Your description contained some errors. Using default description")
            description = "Default SUBTOOL description"
        
        if isLD:
            payload = CreateLDSubscriptionPayload(entity.id, entity.type, description, returnlist, conditionlist)
            headers= {"Content-Type": "application/ld+json", "Fiware-Service" : REPL_SINGLETON.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}
        else:
            payload= CreateSubscriptionPayload(entity.id, entity.type, description, returnlist, conditionlist)
            print(payload)
            headers= {"Content-Type": "application/json", "Fiware-Service" : REPL_SINGLETON.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}
        
        
        
        
        try:
            post_reply = requests.post(base_url+"subscriptions/", payload, headers=headers)
            post_reply.raise_for_status()
            print("Subscription Created Succesfully")
        except Exception as e:
            print(e)
            return
        
        
        
    except Exception as e:
        print("raised exception")
        print(e)
        return
    	
    	
