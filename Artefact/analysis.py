import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import matplotlib.pyplot as plt

cred = credentials.Certificate("Key/lc-comsci-firebase-adminsdk-7esx3-e0ddadf21b.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://lc-comsci-default-rtdb.europe-west1.firebasedatabase.app/'})

#Setting reference to the folder the cleaned data is at
ref = db.reference('/Cleaned/')
dictionary = ref.get()

#This function takes the cleaned data and totals the amount of lego sets released for every year
def TotalSetsReleasedByYear(dic):
    yearCounter = {}
    for setID, v in dictionary.items():
        for heading, x in v.items():
            if heading == 'YearFrom':
                #If x inside counter dictionary, its not first time seeing this Year, +1
                if x in yearCounter: 
                    yearCounter[x] += 1
                    
                #else x not inside counter dictionary, first time encountering this year therefore, should be added as a key to the counter dictionary and value should begin at 1
                else: 
                    yearCounter[x] = 1
    #sorts the dictionary by years lowest to highest
    yearCounter = dict(sorted(yearCounter.items())) 
    
    #Creates a folder with the name of the data being graphed, and sends data to it
    ref = db.reference('/Total_Sets_Released_By_Year/')
    ref.set(yearCounter)
    
    return yearCounter

TotalSetsReleasedByYear(dictionary)


#this function gets average amount of pieces in the average lego set per year, Mean number of pieces in a set for that year
def MeanPiecesByYear(dic):
    #calls other function to grab keys and values needed for this analysis
    yearCounter = TotalSetsReleasedByYear(dic)
    
    #keys used here to create a dictionary with all keys filled and values empty, ready to be added onto
    PieceCounter = dict.fromkeys(yearCounter.keys(), 0)
    
    
    for setID,v in dic.items():
        for heading, x in v.items():
            if heading == 'Pieces': 
                year = dic[setID]['YearFrom']
                #if heading is Pieces, x is number of pieces for that entry, this adds the amount on to the total for that entries year
                PieceCounter[year] += int(x)
                
    for year, totalPieces in PieceCounter.items():
        #dictionary contains total piece amount per year, this divides by the amount released in that Year using values of dictionary grabbed from function
        PieceCounter[year] = round( totalPieces / yearCounter[year] ) 
    
    
    #Creates a folder with the name of the data being graphed, and sends data to it
    ref = db.reference('/Mean_Piece_Count_By_Year/')
    ref.set(PieceCounter)
    
    return PieceCounter

MeanPiecesByYear(dictionary)
    
#this function is a frequency counter for each theme released, it includes a total theme frequency from all years, and it includes data specific to each year
def ThemeCounter(dic):
    #Allyears in here from start as cannot be added from just iterating
    ThemeCounterByYears = {'AllYears' : {}} 
    for setID, v in dic.items(): #for each entry
        
        #if current year not a key, create an empty dictionary inside the main counter
        if not v['YearFrom'] in ThemeCounterByYears: 
            ThemeCounterByYears[ v['YearFrom'] ] = {} 
        
        
        #if current entries theme is not in the counter for the current year, set value to 1
        if not v['Theme'] in ThemeCounterByYears[v['YearFrom']]: 
            ThemeCounterByYears[v['YearFrom']][v['Theme']] = 1
        #else it exists, so add 1
        else: 
            ThemeCounterByYears[v['YearFrom']][v['Theme']] += 1


        #if this current entries theme is not in allYear counter, set counter value to 1
        if not v['Theme'] in ThemeCounterByYears['AllYears']: 
            ThemeCounterByYears['AllYears'][v['Theme']] = 1
        #else it exists, so add 1
        else: 
            ThemeCounterByYears['AllYears'][v['Theme']] += 1
         
         
    #Creates a folder with the name of the data being graphed, and sends data to it        
    ref = db.reference('/Theme_Frequency_By_Year/')
    ref.set(ThemeCounterByYears)
    
    return ThemeCounterByYears

ThemeCounter(dictionary)

#this functions sends necessary data for showing pictures from doughnut chart on website
def ThemeYearIMGurl(dic): 
    ThemeYearIMGdic = {}
    for setID, v in dic.items():
        ThemeYearIMGdic[setID] = {'Theme':v['Theme'], 'Year':v['YearFrom'],'imgID': v['ImageFilename'], 'setTitle' : v['SetName']}
    
    #Creates a folder for the data to be used for displaying pictures 
    ref = db.reference('/Theme_Year_imgURL/')
    ref.set(ThemeYearIMGdic)
    
ThemeYearIMGurl(dictionary)


#this function gets the first year a set of a certain theme was released in
def FirstThemeRelease(dic):
    #calling this function to get necessary data of what themes were released in what years
    ThemeCounterByYears = ThemeCounter(dic)
    #removing all years as not necessary
    del ThemeCounterByYears['AllYears']
    #sorting by years from lowest to highest
    ThemeCounterByYears = dict(sorted(ThemeCounterByYears.items()))

    
    FirstThemes = {}
    for Year, Counter in ThemeCounterByYears.items():
        for Theme, Value in Counter.items():
            #if theme is not in FirstThemes dictionary, this {theme} first occurs in {year}
            if not Theme in FirstThemes:
                FirstThemes[Theme] = Year
                
    #Sends result of this question to its own folder, key being the input from user, value being the answer to the question of this input
    ref = db.reference('/First_Theme_Released_Question/')
    ref.set(FirstThemes)
    
FirstThemeRelease(dictionary)


#dictionary in firebase is of the form {YEAR : {SETID : PIECECOUNT} }
#this function gathers answers to this question with year as input
def LargestSetByYear(dic):
    YearIDPieceAllDic = {}
    #Creates a dictionary with data of each setID and its piece count corresponding to what year it was released in
    #Creates a dictionary with data of each Year, containing each set released then, and its piece count
    for setID, v in dic.items():
        if v['YearFrom'] in YearIDPieceAllDic:
            YearIDPieceAllDic[v['YearFrom']].append({setID:int(dic[setID]['Pieces'])})
        else:
            YearIDPieceAllDic[v['YearFrom']] = [{setID:int(dic[setID]['Pieces'])}]


    #dictionary needs to be sorted by year from lowest to highest
    YearIDPieceAllDic = dict(sorted(YearIDPieceAllDic.items()))
    
    
    LargestSetByYear = {}
    for year, listofSets in YearIDPieceAllDic.items():
        #this sorts the list of each set per year by piece count
        SortedListOfSets = sorted(listofSets, key=lambda x: list(x.values())[0])
        
        #taking the maximum value
        LargestSetByYear[year] = SortedListOfSets[-1] 
    
    
    ref = db.reference('/Largest_Set_Question/')
    ref.set(LargestSetByYear)
LargestSetByYear(dictionary)


while 1:
    print('''Select Data to View Graphs
1) Lego Sets released by Year
2) Average Piece Count of every lego set by Year
3) Theme Frequency
4) Quit''')
    choice = int(input())
    while not choice in [1,2,3,4]:
        choice = int(input('Enter Valid Choice'))
        
    if choice == 1:
        plt.rcParams.update({'font.size': 7})
        plt.xticks(rotation=45)
        plt.title('Total Lego Sets Released per Year')
        plt.xlabel('Years')
        plt.ylabel('Lego Sets Released')
        AxisLabels = TotalSetsReleasedByYear(dictionary)
        plt.bar(AxisLabels.keys(),AxisLabels.values())
        plt.show()

    if choice == 2:
        plt.rcParams.update({'font.size': 8})
        plt.xticks(rotation=45)
        plt.title('Mean Number of pieces in a Lego Set per year')
        plt.xlabel('Years')
        plt.ylabel('Average Number of Pieces')
        AxisLabels = MeanPiecesByYear(dictionary)
        plt.bar(AxisLabels.keys(),AxisLabels.values())
        plt.show()

    if choice == 3:
        AxisLabels = ThemeCounter(dictionary)['AllYears']
        AxisLabels = dict(sorted(AxisLabels.items(), key=lambda x: x[1]))
        plt.title('Lego Set Theme Frequency, All Years')
        plt.pie(AxisLabels.values(),labels = AxisLabels.keys(), startangle=90)
        plt.show()
        
    if choice == 4:
        break
