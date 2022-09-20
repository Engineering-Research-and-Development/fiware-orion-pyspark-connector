from datetime import datetime
import requests
import json

import connectorconf
from connectorconf import NGSIAttribute, NGSIEntityv2, NGSIEntityLD



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
    



def CreateSubscriptionPayload(name, typ, desc, attrlist):

    
    payload = {}
    payload['description']=desc
    payload['subject']={}
    payload['subject']['entities'] = []
    payload['subject']['entities'].append({'id':name, 'type':typ})
    payload['subject']['condition'] = {'attrs':[]}
    payload['notification'] = {}
    payload['notification']['http'] = {'url':'http://'+connectorconf.HTTPADDRESS+":"+str(connectorconf.HTTPPORT)}
    payload['notification']['attrs'] = attrlist
    payload['expires'] = "2099-01-01T14:00:00.00Z"
    

    payload = json.dumps(payload)
    #print(payload)
    return payload
    
    
#TODO: Create subscription Conditions
#TODO: Browsing entità 
#TODO: Separare il tutto
def SubscribeToEntity(base_url, description):


    # localhost:1026/v2/subscriptions

    headers= {"Fiware-Service" : connectorconf.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}

    
    
    #print(get_entity_request)
    select_entity = True
    try:
        get_entities_request = base_url+"entities/"
        reply = requests.get(get_entities_request, headers=headers)
        ents = reply.json()
        print("Found {} entities:".format(len(ents)))
        entx = [ent['id'] for ent in ents]
        print(entx)
        
        while select_entity:
            entity_id = str(input("Please, select an entity name from the ones listed above: "))
            if entity_id.upper() in [ent.upper() for ent in entx]:
                select_entity = False
                ent = [ent for ent in ents if ent['id'].upper() == entity_id.upper()][0]

            else:
                print("Entity not Found, please, insert the correct name among this ones:\n",entx)
    except Exception as e:
        print(e)
        return
        

    
    try:

        
        

        entity, isLD = ReturnEntityIfExists(ent)
        #print(message)
        
        print("Entity found: the attributes are the following ones:")
        
        attrlist = [attr for attr in entity.attrs]
        print(attrlist)
        
        print("Type which attributes to return in your subscription. Type 'QUIT' to stop")
        continuing = True
        returnlist = []
        while continuing:
            try:
                if len(attrlist) <= 0:
                    continuing = False
                    print("Attribute list is now empty, quitting selection...")
                    continue
                string = str(input("Insert attribute name: "))
                if string in attrlist:
                    print("Attribute {} found. Adding to attributes".format(string))
                    attrlist.remove(string)
                    returnlist.append(string)
                    
                elif string.upper() == 'QUIT':
                    print("Quitting Selection")
                    continuing = False
                else:
                    print("Attribute not found, please, type it correctly. The remaining list of attributes is:", attrlist)
            except Exception as e:
                print(e)
                return
                
        payload = CreateSubscriptionPayload(entity.id, entity.type, description, returnlist)
        
        
        
        headers= {"Content-Type": connectorconf.CONTENT_TYPE, "Fiware-Service" : connectorconf.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}
        try:
            post_reply = requests.post(base_url+"subscriptions/", payload, headers=headers)
            print("Subscription Created Succesfully")
            print(post_reply.text)
        except Exception as e:
            print(e)
        
        
    except Exception as e:
        print("raised exception")
        print(e)
        return
    	
    	
