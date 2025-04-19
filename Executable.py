#region import

from random import randint
import sqlite3

#endregion


class DataStore:
    """dataclass to centrally store data

    """
    today=None
    now=None
    weather=None
    weatherNext=None
    location=None
    path='./Libraries/Campaign/ExampleCampaign.db'
    Settingpath='./Libraries/Setting/Setting Aventurien.db'
    prop_path_intern="./Libraries/ProgrammData/ProgrammData.db"
    defaultFamily=None



#region Database based Generation
#TODO update weather system
class Weather:
    """ class to manage random season appropriate weather generation

    """


    def __init__ (self, weather, wind, temp):
        """initializes a new weather object with current ingame month

        :param weather: int, id of weather
        :param wind: int, wind strength
        :param temp: int, temperature steps
        """
        self.weather = [weather, wind, temp]
        self.month = DataStore.today.month()

    def next(self):
        """generates a season appropriate random weather development

        :return: ->weather object, the next weather
        """

        month = self.month
        weather =self.weather[0]
        wind= self.weather[1]
        temp= self.weather[2]

        conn = sqlite3.connect(DataStore.Settingpath)
        c = conn.cursor()

        if month <= 2 or month >= 10:
            c.execute("SELECT weatherChange FROM Sommer  WHERE random >= (?)",(weather,))
        elif month <= 4:
            c.execute("SELECT weatherChange FROM Herbst WHERE random >= (?) ",(weather,))
        elif month <= 8:
            c.execute("SELECT weatherChange FROM Winter WHERE random >= (?) ",(weather,))
        else:
            c.execute("SELECT weatherChange FROM WHERE random >= (?)",(weather,))

        data = c.fetchone()[0]                    #output: (Weather Veränderung,)


        newWeather = randint(1, 6) + weather + data

        if newWeather < 1:
            newWeather += 20
        elif newWeather > 20:
            newWeather -= 20

        if month <= 2 or month >= 10:
            c.execute("SELECT windChange, tempChange FROM Sommer WHERE random >=(?)",(weather,))
        elif month <= 4:
            c.execute("SELECT windChange, tempChange FROM Herbst WHERE random >=(?)",(weather,))
        elif month <= 8:
            c.execute("SELECT windChange, tempChange FROM Winter WHERE random >=(?)",(weather,))
        else:
            c.execute("SELECT windChange, tempChange FROM Frühling WHERE random >=(?)",(weather,))
        data = c.fetchone()                         #output(windchange, tempchange)


        #Wind
        currentWind = wind
        newWind = randint(1, 6)
        alternativWind = randint(1, 6)
        if abs(newWind - currentWind) > abs(alternativWind - currentWind):
            newWind = alternativWind
        newWind = newWind + data[0]
        newWind
        if newWind>8:
            newWind=8
        elif newWind<0:
            newWind=0

        #Temperatur
        currentTemp = temp
        newTemp =randint(1,6)
        alternativTemp =randint(1,6)
        if abs(newTemp-currentTemp)>abs(alternativTemp-currentTemp):
            newTemp=alternativTemp
        newTemp = newTemp +data[1]

        if newTemp>8:
            newTemp=8
        elif newTemp<0:
            newTemp=0

        conn.close()

        return Weather(newWeather,newTemp,newWind)

    def __str__(self):
        """translates a weather object into readable data

        :return: ->Str
        """

        month = self.month
        weather = self.weather[0]
        wind = self.weather[1]
        temp = self.weather[2]

        conn = sqlite3.connect(DataStore.Settingpath)
        c = conn.cursor()

        if month <= 2 or month >= 10:
            c.execute("SELECT description FROM Sommer WHERE random >=(?)",(weather,))
            season = "Sommer"
        elif month <= 4:
            c.execute("SELECT description FROM Herbst WHERE random >=(?)",(weather,))
            season = "Herbst"
        elif month <= 8:
            c.execute("SELECT description FROM Winter WHERE random >=(?)",(weather,))
            season = "Winter"
        else:
            c.execute("SELECT description FROM Frühling WHERE random >=(?)",(weather,))
            season = ("Frühling")
        weatherText = c.fetchone()[0]

        c.execute("SELECT description FROM Wind WHERE random >=(?)",(wind,))
        windText = c.fetchone()[0]

        c.execute("SELECT description FROM Temp WHERE random <= (?) ORDER BY rowid DESC ",(temp,))
        tempText=c.fetchone()[0]

        conn.close()

        return season+", "+tempText+"\n"+weatherText+", "+windText


class CustomDate:
    """manages ingame date progression

    :var:dict, the current ingame month name, month length and corresponding real month
    """
    kalender = {"Praios": ["August", 30],
            "Rondra": ["September", 30],
            "Efferd": ["Oktober", 30],
            "Travia": ["November", 30],
            "Boron": ["Dezember", 30],
            "Hesinde": ["Januar", 30],
            "Firun": ["Februar", 30],
            "Tsa": ["März", 30],
            "Phex": ["April", 30],
            "Peraine": ["Mai", 30],
            "Ingerimm": ["Juni", 30],
            "Rahja": ["Juli", 30],
            "Namenlose Tage": ["August", 5]}

    Helper = True

    def __init__(self, date):
        """initalizes a new custom date

        :param date: str, date.month.year
        """


        if type(date) is not str:
            raise TypeError("Only Strings Accepted")

        rawdate =[x.split(" ") for x in date.split(".")]
        rawdate=[j for sub in rawdate for j in sub]

        if len(rawdate) < 3:
            raise ValueError("please follow naming Convention: Day.Month.Year")

        self.date = date
        if rawdate[1].isalpha():
            self.date = ("%d.%d.%d" % (int(rawdate[0]), int(list(CustomDate.kalender).index(rawdate[1].title())), int(rawdate[2])))

    def year(self):
        """returns year of the date

        :return: ->int
        """
        return int(self.date.split(".")[2])

    def month(self):
        """returns the month of the date

        :return: ->int
        """
        return int(self.date.split(".")[1])

    def day(self):
        """returns the day of the date

        :return: ->int
        """
        return int(self.date.split(".")[0])

    def __add__(self, other):
        """adds days, months or years to current date

        :param other: str
        :return: ->date
        """
        if type(other) is not str:
            raise ValueError("string expected")

        dateDict = {"d": 0, "m": 0, "y": 0}

        for item in other.split(","):
            if not item.startswith(("w","d", "m", "y")) or not item.strip('wdmy').isnumeric():
                raise ValueError(
                    "please follow naming Convention: d* to add Days m* to add Months y* to add years, while *=amount")

            if item[0] == "w":
                dateDict["d"] += (int(item.strip('wdmy')) * 7)
            else:
                dateDict[item[0]] += int(item.strip('wdmy'))

        newDate = CustomDate("%d.%d.%d" % (
        int(self.day()) + dateDict["d"], int(self.month()) + dateDict["m"], int(self.year()) + dateDict["y"]))
        checked_date = newDate.date_validation()
        return checked_date

    def __sub__(self, other):
        """subtracts days, months or years from current date

        :param other: str
        :return: ->date
        """
        if type(other) is not str:
            raise ValueError("string expected")

        dateDict = {"d": 0, "m": 0, "y": 0}

        for item in other.split(","):
            if not item.startswith(("w","d", "m", "y")) or not item.strip('wdmy').isnumeric():
                raise ValueError(
                    "please follow naming Convention: d* to add Days m* to add Months y* to add years w* add Weeks, while *=amount")

            if item[0] == "w":
                dateDict["d"] += (int(item.strip('wdmy'))*7)
            else:
                dateDict[item[0]] += int(item.strip('wdmy'))

        newDate = CustomDate("%d.%d.%d" % (
        int(self.day()) - dateDict["d"], int(self.month()) - dateDict["m"], int(self.year()) - dateDict["y"]))
        checked_date = newDate.date_validation()
        return checked_date

    def difference(self,other, year=True, month=True, week=False, day=True):
        """Compares the time difference of two dates.

        :param other: CustomDate object, the date to compare with
        :param year: Bool, if True returns difference with all complete years
        :param month: Bool, if True returns difference with all complete month
        :param week: Bool, if True returns difference with all complete weeks
        :param day: Bool, if True returns difference with all complete days
        :return: ->str, the difference embedded in a string
        """
        output=[]
        yeardays1=self.day()
        yeardays2=other.day()
        for index,item in enumerate(self.kalender):
            if index+1<self.month():
                yeardays1+=self.kalender[item][1]
            if index+1<other.month():
                yeardays2+=self.kalender[item][1]

        yeardays1+=self.year()*365
        yeardays2+=other.year()*365

        daysDif=yeardays1-yeardays2
        if daysDif<0:
            relTime="In "
        else:
            relTime="Vor "

        daysDif=abs(daysDif)
        days=0
        weeks=0
        months=0
        years=0
        if daysDif>=365 and year:
            years=daysDif//365
            daysDif=daysDif%365
        if daysDif>=30 and month:
            months = daysDif // 30
            daysDif = daysDif % 30
        if daysDif>=7 and week:
            weeks = daysDif // 7
            daysDif = daysDif % 7
        if daysDif>0 and day:
            days=daysDif

        #construct the return string
        for index,item in enumerate([days,weeks,months,years]):
            keys=[" Tag"," Woche"," Monat"," Jahr"]
            if item>0:
                text = str(item)
                text += keys[index]
                if item>1:
                    text=text.rstrip("e")+"en"
                output.append(text)

        text=""
        if len(output)>1:
            andMarker=True
            for item in output:
                if item!=output[-1]:
                    if andMarker:
                        text=" und "+item
                        andMarker=False
                    else:
                        text=", "+item + text
                else:
                    text=item+text
        else:
            text=output[0]
        return relTime+text


    def date_validation(self, checkOnly=False):
        """checks date for matching with database and remodels it until it fits parameters, if checkonly=true returns if valid

        :param checkOnly: bool, if true returns not date only if it is valid
        :return: ->date|bool
        """
        newDate = self

        if newDate.month() > len(CustomDate.kalender):
            newDate=CustomDate("%d.%d.%d" % (newDate.day(), newDate.month() % len(CustomDate.kalender), newDate.year() +
                                             newDate.month()//len(CustomDate.kalender)))

        elif newDate.month()<0:
            newDate = CustomDate("%d.%d.%d" % (newDate.day(), (newDate.month() % len(CustomDate.kalender)), newDate.year() -
                                             (abs(newDate.month())//(len(CustomDate.kalender)-1))))

        elif newDate.month()==0:
            newDate=CustomDate("%d.%d.%d" % (newDate.day(),len(CustomDate.kalender), newDate.year()-1))

        daysInMonth = CustomDate.kalender[list(CustomDate.kalender)[newDate.month()-1]][1]

        if newDate.day() > daysInMonth:
            daysInMonth = CustomDate.kalender[list(CustomDate.kalender)[newDate.month()-1]][1]
            newDate = CustomDate("%d.%d.%d" % ((newDate.day() - daysInMonth), (newDate.month() + 1), newDate.year()))
            newDate=newDate.date_validation()

        elif newDate.day() < 0:
            daysInMonth = CustomDate.kalender[list(CustomDate.kalender)[newDate.month() - 2]][1]
            newDate = CustomDate("%d.%d.%d" % ((daysInMonth)+newDate.day(), (newDate.month() - 1), newDate.year()))
            newDate=newDate.date_validation()

        elif newDate.day() == 0:
            daysInMonth = CustomDate.kalender[list(CustomDate.kalender)[newDate.month()-2]][1]
            newDate = CustomDate("%d.%d.%d" % ((daysInMonth), (newDate.month() - 1), newDate.year()))
            newDate=newDate.date_validation()


        if not checkOnly:
            return newDate

        if newDate is self:
            return True
        else:
            return False

    def __str__(self):
        """ defines string representation of the object

        :return: ->str
        """
        add=" "
        if CustomDate.Helper:
            add=" (%s) " % (CustomDate.kalender [list(CustomDate.kalender) [self.month()-1]][0])
        return "%d.%s%s%d" % (self.day(), list(CustomDate.kalender)[self.month()-1], add, self.year())

    def __repr__(self):
        """ defines console representation of the object

        :return: ->str
        """
        return str(self.date)


def randomChar():
    """returns a random local first and lastname

    :return: ->dict
    """
    conn = sqlite3.connect(DataStore.Settingpath)
    c = conn.cursor()
    sex = randint(0,1)
    sex_list=["male","female"]
    sex=sex_list[sex]
    fname = randint(1, 46)
    family = randint(2, 27)

    c.execute("SELECT name FROM Forname_Kosch_%s WHERE rowid = ?" %(sex), (fname,))
    fName = c.fetchone()[0]

    c.execute("SELECT name FROM Lastname_Kosch WHERE rowid = ?", (family,))
    family_Name = c.fetchone()[0]

    conn.close()

    charDict={}
    charDict['indiv_fName']=fName
    charDict['family_Name']=family_Name
    charDict['indiv_sex']=[sex]

    return charDict

#endregion


#region Database Factories, access and manipulation

def searchFactory(text:str,library:str,innerJoin:str ="",output:str =None,  shortOut:bool= False ,
                  attributes:list=None ,Filter:dict={},OrderBy = None, searchFulltext:bool =False,
                  dictOut=False,uniqueID=True):
    """returns the sqlite database datasets

        :param text: str,
            the value/text to search for in database
        :param library: str
            the table to search in
        :param innerJoin: str, optional, sqlite syntax
        :param output: str, optional, sqlite syntax
        :param shortOut: bool, optional
            returns the saved profile matching the library
        :param attributes: list, optional
            specifies the list of column names to search the text in
        :param Filter: dict, optional
            specifies additional search parameter
        :param OrderBy: str, optional, sqlite syntax
        :param searchFulltext: bool, optional
            if yes searches as well if the given search-text is a substring of the data items
        :param dictOut: bool, optional
            if yes returns the data as dict with the column names as keys
        :param uniqueID: bool, optional
            if no returns items several times, if searched in multiple attributes
        :return: ->list|dict , all datasets resembling the specified parameters
        """


    conn=sqlite3.connect(DataStore.path)
    c=conn.cursor()


    if type(text)!=str:
        text=str(text)

    if OrderBy == None:
        OrderBy= library+'.rowid'

    if searchFulltext:
        text = "%"+text+"%"


    if shortOut:

        shortOutputDict= {"Individuals":['individual_ID, indiv_fName, family_Name',
                                         'INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID'],
                          "Sessions":["Sessions.session_ID, session_Name",
                                      "LEFT JOIN Session_Individual_jnt on Sessions.session_ID= Session_Individual_jnt.fKey_session_ID "
                                      "LEFT JOIN Individuals on Individuals.individual_ID = Session_Individual_jnt.fKey_individual_ID"],
                          "Event_Individuals_jnt":["Individuals.individual_ID,Individuals.indiv_fName, Families.family_Name",
                                              """INNER JOIN Events on Events.event_ID = Event_Individuals_jnt.fKey_event_ID
                                              LEFT JOIN Sessions on Events.fKey_Session_ID = Sessions.session_ID
                                            RIGHT JOIN Individuals on Individuals.individual_ID = Event_Individuals_jnt.fKey_individual_ID
                                            LEFT JOIN Families on Individuals.fKey_family_ID= Families.family_ID"""],
                          "Session_Individual_jnt": ["Sessions.session_ID,session_Name",
                                                """INNER JOIN Sessions on Session_Individual_jnt.fKey_session_ID = Sessions.session_ID 
                                             INNER JOIN Individuals on Individuals.individual_ID = Session_Individual_jnt.fKey_individual_ID
                                             INNER JOIN Families on Individuals.fKey_family_ID= Families.family_ID"""],
                          "Events":["Events.event_ID,Events.event_Title",""],
                          "Notes":["Notes.note_ID,Notes.note_Content",""]}


        if not output:
            output=shortOutputDict[library][0]
        if not innerJoin:
            innerJoin= shortOutputDict[library][1]

    if not output:
        output = '*'
        if library.endswith("_Pathlib"):
            output = library+'.rowid,*'


    if not attributes:
        c.execute("""SELECT *  
                        FROM %s %s""" % ( library, innerJoin))
        attributes = [x[0] for x in c.description]

    elif type(attributes)==str:
        attributes=list(attributes)

    filterstring = ""
    filterTextList = []
    if Filter:
        for item in Filter:
            filterstring += " AND %s like ?" % (item)
            if Filter[item][1]:
                filterTextList.append("%"+Filter[item][0]+"%")
            else:
                filterTextList.append(Filter[item][0])
        if text=="" or None or '' or len(text)==0:
            filterstring=" WHERE "+filterstring[4:]



    a=1
    searchResult = []
    searchIndex = []

    for column in attributes:

        if text=="" or text==None or text=='' or len(text)==0:


            c.execute("""SELECT %s  FROM %s %s %s ORDER BY %s""" % (
            output, library, innerJoin, filterstring, OrderBy),
                      (*[*filterTextList],))
            data = c.fetchall()
            name = [x[0] for x in c.description]



            if uniqueID:
                data_collection = []
                Id_collection = []
                for index,datum in enumerate(data):
                    if datum[0] in Id_collection:
                        continue

                    data_collection.append(datum)
                    Id_collection.append(datum[0])
                data=data_collection

            if dictOut:
                searchResult={}
                for index,item in enumerate(name):
                    searchResult[item]=data[index]
            else:
                searchResult=data

            break

        if column== 'indiv_fName' and not searchFulltext:
            c.execute("""SELECT %s
                        FROM %s %s
                        WHERE %s like ?
                         or % s like ?
                         or % s like ?
                         or % s like ?
                         ORDER BY %s""" % (output, library, innerJoin, column, column, column, column, OrderBy),
                      (text,"% "+text,text+" %","% "+text+" %"))
            data = c.fetchall()

        else:

            c.execute("""SELECT %s  FROM %s %s WHERE %s like ? %s ORDER BY %s""" % (output, library, innerJoin, column, filterstring, OrderBy),
                (text,*[*filterTextList]))
            name=[x[0] for x in c.description]
            data = c.fetchall()


        for indexA,item in enumerate(data):
            if not dictOut:
                if item[0] not in searchIndex:
                    searchIndex.append(item[0])
                    searchResult.append(item)

            else:

                if item[0] not in searchIndex:
                    searchIndex.append(item[0])
                    searchResult.append({})
                    for indexB, Value in enumerate(item):
                        searchResult[indexA][name[indexB]] = Value





    conn.close()
    return searchResult


#TODO check searchFactory2, search in all tables, currently not implemented
def searchFactory2(text:str,library:list=None,innerJoin:str ="",output:str =None,  shortOut:bool= False ,
                   attributes:list=None ,OrderBy = None, searchFulltext:bool =False):

    """WIP searches in all tables of a database

    :param text:
    :param library:
    :param innerJoin:
    :param output:
    :param shortOut:
    :param attributes:
    :param OrderBy:
    :param searchFulltext:
    :return:
    """
    conn=sqlite3.connect(DataStore.path)
    c=conn.cursor()

    searchResult= []
    searchIndex= []


    #region defaultsearch parameter

    if library==None:
        c.execute("""SELECT name FROM sqlite_master 
                        WHERE type = 'table';""")
        list = [c.fetchall()]


    elif type(library)== str:
        library = [library]

    if not output:
        outputmarker=True

    if not attributes:
        attributesmarker=True

    if not OrderBy:
        OrderByMarker=True

    if searchFulltext:
        text = "%"+text+"%"

    if shortOut:

        shortOutputDict= {"Individuals":["Individuals.rowid, fName, family_Name","INNER JOIN Families on Families.rowid = Individuals.family_Id"],
                          "Sessions":["Sessions.rowid, session_Name",""]}
        output=shortOutputDict[library][0]
        innerJoin= shortOutputDict[library][1]

    elif type(attributes)==str:
        attributes=list(attributes)

    #endregion

    for table in library:

        #region defaultsearchparams
        if  outputmarker:
            output = table + '.rowid,*'

        if  attributesmarker:
            c.execute("""SELECT *  
                            FROM %s %s""" % (table, innerJoin))
            attributes = [x[0] for x in c.description]

        if OrderByMarker:
            OrderBy = table +'.rowid'

        for column in attributes:

            if column== 'fName' and not searchFulltext:
                c.execute("""SELECT %s  
                            FROM %s %s 
                            WHERE %s like ? 
                             or % s like ?
                             or % s like ?
                             or % s like ?
                             ORDER BY ?""" % (output, table, innerJoin, column, column, column, column),
                          (text,"% "+text,text+" %","% "+text+" %", OrderBy))
                data = c.fetchall()

            else:

                c.execute("""SELECT %s.rowid,*  FROM %s %s WHERE %s like ? ORDER BY ?""" % (table, table, innerJoin, column),
                    (text,OrderBy))
                data = c.fetchall()

            for item in data:
                if table+" "+str(item[0]) not in searchIndex:
                    searchIndex.append(table+" "+str(item[0]))
                    searchResult.append(item)


    conn.close()
    return searchResult

def getFactory(id:int,library:str,output:str='*',defaultOutput:bool=False,shortOutput=False, dictOut=False, path=None):
    """returns the sqlite datum with matching id

    :param id: int
        id of searched datum
    :param library: str
        table name
    :param output: str, optional, sqlitesyntax
    :param defaultOutput: bool, optional
        returns the saved profile matching the library
    :param shortOutput: bool, optional
        returns the saved profile matching the library
    :param dictOut: bool, optional
        if yes returns the data as dict with the column names as keys
    :param path: str, optional
    :return: -> list|dict
    """
    defaultOutDict= {'Families':['*',''],
                        'Individuals':['*, family_Name','INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID']}

    shortOutDict = {'Families': ['family_ID,family_Name', ''],
                      'Individuals': ['Individuals.individual_ID, indiv_fName, family_Name',
                                      'INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID']}

    innerJoin=''
    if shortOutput and library in shortOutDict:
        output = shortOutDict[library][0]
        innerJoin = shortOutDict[library][1]

    if defaultOutput and library in defaultOutDict:
        output=defaultOutDict[library][0]
        innerJoin=defaultOutDict[library][1]

    if path==None:
        path=DataStore.path

    conn = sqlite3.connect(path)
    c=conn.cursor()

    c.execute("""SELECT %s FROM %s %s WHERE %s.rowid=(?)"""%(output,library,innerJoin,library),(id,))
    column = [x[0] for x in c.description]
    data=c.fetchone()

    conn.close()

    if dictOut:
        dataDict = {}
        for index,item in enumerate(data):
            dataDict[column[index]]=item

        return dataDict
    else:
        return data

def updateFactory(id, texts:list,library:str,attributes:list, path=None):
    """updates the specified datasets attributes with given values

    :param id: str
        sqlite id of dataset
    :param texts: list
        list of values to update with
    :param library: str
        table name
    :param attributes:  list
        list of columns to update
    :param path: str, optional
        path of database
    :return:
    """
    if path==None:
        path=DataStore.path

    conn = sqlite3.connect(path)
    c = conn.cursor()
    str= ("""UPDATE %s 
          SET """)
    for index,attribute in enumerate(attributes):
        str+= " %s = (?) "
        if not index >= len(attributes)-1:
            str+=", "
        str+="""
        """
    str+= "WHERE rowid = (?) "

    c.execute(str %(library,*attributes),(*texts,id))
    conn.commit()
    conn.close()

def deleteFactory(id:int,library:str):

    conn=sqlite3.connect(DataStore.path)
    c=conn.cursor()
    c.execute("""PRAGMA foreign_keys=ON""")
    c.execute("""DELETE FROM %s 
                    WHERE rowid= (?)""" %(library),(id,))

    conn.commit()
    conn.close()

    return

def newFactory(library: str, data: dict={}):
    """creates new entries with given data in given table within the library at DataStore.Path

    :param library: str
        name of table
    :param data: dict
        dictionary with columns as keys
    :return: ->int, the id of the newly created entry
    """
    conn = sqlite3.connect(DataStore.path)
    c = conn.cursor()
    c.execute("SELECT * FROM %s" % (library,))
    existing_col = [x[0] for x in c.description]

    listed_values = []
    len_list = ""
    for column in existing_col:
        if column in data:
            listed_values.append(data[column])
        else:
            listed_values.append(None)

        len_list += "?,"

    len_list=len_list.rstrip(',')
    c.execute("INSERT INTO %s VALUES (%s)" % (library, len_list), (*listed_values,))
    id = c.lastrowid
    conn.commit()
    conn.close()

    return id

#endregion Factories


#region tools

def get_table_Prop(library:str):
    """returns the properties of a certain table

    :param library: str, the library that should be observed
    :return: ->dict, with the keys 'lastItem_ID','colName','length_row','length_col','data'
    """
    conn=sqlite3.connect(DataStore.path)
    c=conn.cursor()

    propDict={}
    c.execute("""SELECT rowid,* FROM %s""" %(library))

    data=c.fetchall()
    propDict['lastItem_ID'] = data[-1][0]
    propDict['colName'] = [x[0] for x in c.description]
    propDict['length_row']= len(data)
    propDict['length_col']= len(propDict['colName'])
    propDict['data']={}

    for item in data:
        propDict['data'][item[0]]={}
        for col_index,col in enumerate(propDict['colName']):
            propDict['data'][item[0]][col]=item[col_index]

    conn.close()

    return propDict

def checkLibrary(path, setting):
    """checks if a library has a matching table set and therefore is a compatible library

    :param path: str, the path for the checked library
    :param setting: bool, if true checked library is handled as setting library elseway as campaign library
    :return: list, the missing tables
    """
    baselibrary = ['Families', 'Event_Individuals_jnt', 'Locations', 'Session_Individual_jnt', 'Events', 'Individuals', 'Timelines', 'Sessions', 'Timelines_Events_jnt', 'DB_Properties', 'Notes', 'Note_Note_Pathlib', 'LastSessionData', 'Draftbooks', 'Notes_Draftbook_jnt']
    if setting:
        baselibrary = ['Lastname_Kosch', 'Forname_Kosch_male', 'Frühling', 'Herbst', 'Sommer', 'Winter', 'Wind', 'Temp', 'Kalender_Zwölfgötter', 'Forname_Kosch_female']

    missing = []
    for item in baselibrary:

        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (item,))
        if len(c.fetchall()) == 0:
            missing.append(item)
        conn.close()

    return missing

def getAllAtr(classes, varOnly=False):
    """returns all not inherited defined functions and variables for any object

    :param classes: cls,
    :param varOnly: bool, optional, if true returns only class variables
    :return: ->dict
    """
    newDict = {}
    for i in list(classes.__dict__):
        if not(i[0]=="_" and i[1] =="_" and i[-1]=="_" and i[-2]=="_"):
            if not varOnly:
                newDict[i] = classes.__dict__[i]
            elif not callable(classes.__dict__[i]):
                newDict[i]=classes.__dict__[i]
    return newDict

def getTableNames(path):
    """returns all tables in database as list of strings

    :param path: str, path of the library
    :return: ->List of strings
    """
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
    tables= c.fetchall()
    conn.close()

    return [x[0] for x in tables]

#endregion
