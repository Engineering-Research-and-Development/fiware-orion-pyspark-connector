#!/usr/bin/env python
# coding: utf-8

# In[2]:


class Attributev2():
    
    def __init__(self, attrype, value, metadata):
        self.type = attrype
        self.value = value
        self.metadata = metadata
        


# In[3]:


class Entityv2():
    
    def __init__(self, entityid, nodetype, attributes):
        self.id = entityid
        self.type = nodetype
        self.attrs = attributes
        
    
    def getAttrs():
        for key in list(self.attrs):
            attr = self.attrs[key]
            print(attr.type, attr.value, attr.metadata)
        
    


# In[4]:


class NGSIEventv2():
    
    def __init__(self, timestamp, svc, svcpath, entities):
        self.creationtime = timestamp
        self.service = svc
        self.servicePath = svcpath
        self.entities = entities
        
        
    def getEntities():
        for entity in self.entities:
            print(entity.id, entity.type)
        
    
    
    


# In[ ]:




