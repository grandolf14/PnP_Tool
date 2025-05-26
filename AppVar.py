class UserData:
    """dataclass to centrally store data

    """
    today=None
    now=None
    weather=None
    weatherNext=None
    location=None
    path='./Libraries/Campaign/ExampleCampaign.db'
    Settingpath='./Libraries/Setting/Setting Aventurien.db'
    defaultFamily=None


class AppData:
    """manages internal variables

    """
    current_ID=None
    current_Flag=None
    current_Data=None
    mainWin=None
    AppDataPath = "./Libraries/ProgrammData/ProgrammData.db"
    DBVersion = "0.0"

    @classmethod
    def setCurrInfo(cls,Id=None,Flag=None,Data=None):
        cls.current_ID=Id
        cls.current_Data=Data
        cls.current_Flag=Flag
        return


