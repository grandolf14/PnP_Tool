import Executable as ex
from datetime import datetime
import shutil, os

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
        ex.DataStore.path = ex.getFactory(1, "Properties", path=ex.DataStore.prop_path_intern)[0]
        try:
            f=open(ex.DataStore.path,"r")
            f.close()
        except:
            path = './Libraries/ProgrammData/NewCampaign.db'
            ex.DataStore.path = path
            cls.newFlag=True

        ex.DataStore.Settingpath= ex.getFactory(1, "DB_Properties",path=ex.DataStore.path, dictOut=True)["setting_Path"]
        data= ex.getFactory(1,"LastSessionData",dictOut=True, path=ex.DataStore.path)

        ex.DataStore.today=ex.CustomDate(data["today"])
        ex.DataStore.now = datetime(*[int(x) for x in data["now"].split(",")])
        ex.DataStore.weather = ex.Weather(*[int(x) for x in data["weather"].split(",")])
        ex.DataStore.weatherNext= ex.Weather(*[int(x) for x in data["weatherNext"].split(",")])
        ex.DataStore.location=[data["location"]]
        ex.DataStore.defaultFamily=data["defaultfamily"]

    @classmethod
    def save(cls):
        """saves the session data on program close

        :return: ->None
        """

        for var in ex.getAllAtr(ex.DataStore, varOnly=True):
            new = ""

            data = ex.DataStore.__dict__[var]
            if type(data) == list:
                marker = False
                for dataOb in data:
                    if marker:
                        new += ","
                    if type(dataOb) != str:
                        new += str(dataOb)
                    else:
                        new += dataOb
                    marker = True

            elif type(data) == datetime:
                new += data.strftime("%Y,%m,%d,%H")

            elif type(data) == ex.Weather:
                new += str(data.weather[0]) + "," + str(data.weather[1]) + "," + str(data.weather[2])

            elif type(data) == ex.CustomDate:
                new += str(data.date)

            elif type(data) != str:
                new += str(data)

            else:
                new += data

            if var=="path":
                ex.updateFactory(1, [new], "Properties", ["last_Campaign_path"], path=ex.DataStore.prop_path_intern)
            elif var=="Settingpath":
                ex.updateFactory(1, [new], "DB_Properties", ["setting_Path"])
            elif not var.endswith("intern") and not var.endswith("ily"):
                ex.updateFactory(1,[new],"LastSessionData", [var])

        return


