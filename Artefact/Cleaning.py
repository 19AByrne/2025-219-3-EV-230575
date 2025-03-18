import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("Key/lc-comsci-firebase-adminsdk-7esx3-e0ddadf21b.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://lc-comsci-default-rtdb.europe-west1.firebasedatabase.app/'})


# opening the csv file, reading the first line to split into a list to have a value for each heading for the columns
f = open('Brickset-allsets.csv','r')
header = f.readline()
header = header.strip('\n')
header = header.split(',')
header = [x.strip('"') for x in header]

dictionary = {}
for line in f:
    
    #Ignoring blank lines
    if not line.strip(): 
        break
    
    #splitting with "," as some values contain commas without intent of seperating the values, the quotes surround each value
    line = line.split('","')
    line = [x.strip('"\n') for x in line]
    
    #creating the inner dictionary where the key is the heading of that column and the value is that value in that column
    innerdic = {}
    for i in range(len(line)):
        innerdic[header[i]] = line[i]
    
    #creates (key,value) pair as such (setID, inner dictionary)
    dictionary[line[0]] = innerdic
    
    
# Removing unwanted columns
unwantedHeadings = ['AdditionalImageCount','Variant','USRetailPrice' ,'Minifigs','UKRetailPrice', 'CARetailPrice', 'DERetailPrice', 'USDateAdded','USDateRemoved','PackagingType','Availability','USItemNumber', 'EUItemNumber', 'EAN', 'UPC', 'Width', 'Height', 'Depth', 'Weight','AgeMin', 'AgeMax', 'OwnCount', 'WantCount', 'InstructionsCount', 'AdditionalImageCount','Rating', 'BrickLinkSoldPriceNew', 'BrickLinkSoldPriceUsed', 'Designers', 'LaunchDate', 'ExitDate']
for setID, v in dictionary.items():
    for header in unwantedHeadings:
        if header in v:
            del v[header]

#Checking if the value contains '.' and if it didnt contain '.' would it only have digits, Casts to float
for k,v in dictionary.items(): 
    for x,y in v.items():
        if '.' in y and (y.replace('.','')).isdigit():
            dictionary[k][x] = float(y)
        

#replacing . with ,
for k,v in dictionary.items(): 
    for x,y in v.items():
        if type(y) == str and '.' in y:
            dictionary[k][x] = y.replace('.',',')
            
#filling blanks
for k,v in dictionary.items(): 
    for x,y in v.items():
        if y == '':
            dictionary[k][x] = 'N\\A'

#replacing hashtags as its illegal character for firebase
for k,v in dictionary.items(): 
    for x,y in v.items():
        if type(y) == str and '#' in y:
            dictionary[k][x] = y.replace('#', 'no, ')

#replacing slash as its an illegal character for firebase
for k,v in dictionary.items():
    for x,y in v.items():
        if type(y) == str and '/' in y:
            dictionary[k][x] = y.replace('/', '\\')

#Removes leading or trailing spaces in any values
for k,v in dictionary.items():
    for x,y in v.items():
        if type(y) == str:
            dictionary[k][x] = y.strip(' ')


''' This function takes an inputted heading and an inputted heading value,
this deletes any entry with a given value under a given heading
for example, input (dictionary, 'Released', 'N\\A'), any entry that has the value N\\A under released will be removed from the dictionary'''
def CleanDictionary(dic, Heading, HeadingValue):
    set_IDs = []
    for ID,v in dic.items():
        for h, x in v.items():
            if h == Heading and x == HeadingValue:
                set_IDs.append(ID)
    for ID in set_IDs:
        del dic[ID]
    
    return dic

# This function checks if a given substring is present in any value for the entry, removes it from dictionary if so
def CleanByKeyword(dic, Keyword):
    set_IDs = []
    for ID, v in dic.items():
        for h, x in v.items():
            if type(x) == str and Keyword.upper() in x.upper():
                set_IDs.append(ID)
    for ID in set_IDs:
        del dic[ID]
    return dic

dictionary = CleanDictionary(dictionary, 'Released', 'N\\A')
dictionary = CleanDictionary(dictionary, 'Image', 'N\\A')
dictionary = CleanDictionary(dictionary, 'Category', 'Book')
dictionary = CleanDictionary(dictionary, 'Category', 'Gear')
dictionary = CleanDictionary(dictionary, 'Theme', 'Duplo')
dictionary = CleanDictionary(dictionary, 'Subtheme', 'Duplo')
dictionary = CleanDictionary(dictionary, 'Pieces', 'N\\A')
dictionary = CleanDictionary(dictionary, 'Theme', 'Scala')
dictionary = CleanDictionary(dictionary, 'Theme', 'Clikits')

dictionary = CleanByKeyword(dictionary, 'DUPLO')

#this sends the cleaned dictionary to firebase
ref = db.reference('/Cleaned/')
ref.set(dictionary)

f.close()
