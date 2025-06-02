import sqlite3
import json

from datetime import datetime
from random import randint


import DB_Access as ex

from AppVar import UserData, AppData


class custDateTime(datetime):
    """class datetime from datetime module reimplementation, added dump function to retrieve date as listed values to
    have an easier application initialisation

    """

    def dump(self)->list:
        """returns year, month, day and hour so it can be used with an unpack operator "*" for datetime initialisation

        :return: list, [year,month,day,hour]"""
        return [self.year,self.month,self.day,self.hour]

class ApplicationValues():
    """saves and loads Datavalues

    :cvar new: Bool, True if the application first load was executed with creating a new Campaign
    """
    newFlag=False

    @classmethod
    def load(cls):
        """loads the database values at program start

        :return: ->None
        """
        if UserData.path==None:
            UserData.path = ex.getFactory(1, "Properties", path=AppData.AppDataPath, dictOut=True)['last_Campaign_path']
        try:
            f=open(UserData.path,"r")
            f.close()
        except:
            path = './Libraries/ProgrammData/NewCampaign.db'
            UserData.path = path
            cls.newFlag=True

        UserData.Settingpath= ex.getFactory(1, "DB_Properties",path=UserData.path, dictOut=True)["setting_Path"]
        data= ex.getFactory(1,"LastSessionData",dictOut=True, path=UserData.path)

        data = {k: json.loads(v) for (k, v) in data.items() if v is not None}
        data.update({k:v for (k, v) in data.items() if v is None})

        UserData.today = CustomDate(data["today"])
        UserData.now = custDateTime(*data["now"])
        UserData.weather = Weather(*data["weather"])
        UserData.weatherNext = Weather(*data["weatherNext"])
        UserData.location = data["location"]
        UserData.defaultFamily = data["defaultfamily"]
        UserData.campaignAppLayout = data["campaignAppLayout"]
        return

    @classmethod
    def save(cls):
        """saves the session data on program close

        :return: ->None
        """
        AppData.mainWin.ses_Main_wid.saveValues()
        for var in ex.getAllAtr(UserData, varOnly=True):
            data = UserData.__dict__[var]

            if type(data) == Weather or type(data) == CustomDate or type(data) == custDateTime:
                data = data.dump()

            if var == "path":
                ex.updateFactory(1, [data], "Properties", ["last_Campaign_path"], path=AppData.AppDataPath)

            elif var == "Settingpath":
                ex.updateFactory(1, [data], "DB_Properties", ["setting_Path"])

            else:
                data = json.dumps(data)
                ex.updateFactory(1, [data], "LastSessionData", [var])

        return



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
        self.month = UserData.today.month()

    def next(self):
        """generates a season appropriate random weather development

        :return: ->weather object, the next weather
        """

        month = self.month
        weather =self.weather[0]
        wind= self.weather[1]
        temp= self.weather[2]

        conn = sqlite3.connect(UserData.Settingpath)
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

    def dump(self)->list:
        """returns the weather values as list so it can be used with an ostrich operator for Weather init

        :return: self.weather: list, [weather,wind,temp] """
        return self.weather
    def __str__(self):
        """translates a weather object into readable data

        :return: ->Str
        """

        month = self.month
        weather = self.weather[0]
        wind = self.weather[1]
        temp = self.weather[2]

        conn = sqlite3.connect(UserData.Settingpath)
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


    def dump(self)->str:
        """returns the date ready for CustomDate init
        :return: self.date, str 'day.month.year'"""
        return self.date

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

    def __eq__(self, other):
        if self.day()==other.day() and self.month()==other.month() and self.year()==other.year():
            return True
        return False

    def __gt__(self, other):

        if self.year()>other.year():
            return True

        if self.year()==other.year() and self.month()>other.month():
            return True

        if self.year()==other.year() and self.month()==other.month() and self.day()>other.day():
            return True

        return False
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
    conn = sqlite3.connect(UserData.Settingpath)
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
