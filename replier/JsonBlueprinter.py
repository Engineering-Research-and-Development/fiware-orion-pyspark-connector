import replyconf as rconf

def ChooseType(types, n):
    
    while True:
        try:
            n = int(input("Select a type for the field under the root {}_:\n 0: String\n 1: Number\n 2: Nested Object\n 3: List of Strings\n 4: List of Numbers\n 5: List of Nested Object\n".format(n)))
            if n >= 0 or n<len(types):
                break
            else:
                print("Please, select a type correctly")
        except:
            print("Please, select a type correctly")
            pass
        
    
    return types[n]


def Fields(fields_numb):
    
    
    while True:
        try:
            n_fields = int(input("Insert the number of fields\n"))
            if n_fields > 0:
                fields_numb.append(n_fields)
                break
            else:
                print("Please, insert a correct number of fields")
        except:
            print("Please, insert a correct number of fields")
            
    return fields_numb
    
    
def ComposeLine(t, name):
    
    if t == "S":
        string =  '{} {}:'.format(t, name) + '"{}"\n'
    elif t == "N" or t =="LS" or t =="LN":
        string = '{} {}:'.format(t, name) + '{}\n'
        
    return string
    
    
def WriteFields(fields_numb, types, file, root = ""):
    
    fields_numb = Fields(fields_numb)    
    for i in range(0, fields_numb[-1]):
        t = ChooseType(types, root)
        while True:
            try:
                name = input("Insert the name of the field under the root {}_:\n".format(root))
                if (' ' in name):
                    raise InputException
                else:
                    name = root+name
                    break
            except:
                print("Please, insert a correct name without spaces")
        
        if t == "S" or t == "N" or t =="LS" or t =="LN":
            line = ComposeLine(t, name)
            file.write(line)
            print("Inserting field: {}".format(name))
        else:
            WriteFields(fields_numb, types, file, name+"\\")
            

def BlueprintJSON():
    
    types = ["S", "N", "D", "LS", "LN", "LD"]
    f = open(rconf.BLUEPRINTFILE, "w")
    fields_numb = []
    
    WriteFields(fields_numb, types, f)
    f.close()


BlueprintJSON()  
