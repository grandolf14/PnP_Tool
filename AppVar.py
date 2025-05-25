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
    dataBaseVersion_intern= "0.0"
    defaultFamily=None
    win_intern=None
