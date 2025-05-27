import json

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
    campaignAppLayout={1: {"type": "Draftbook", "data": [None], "id": None, "origin": None},
                         2: {"type": "Browser", "data": [None], "id": None, "origin": None}}


class AppData:
    """manages internal variables

    """
    current_ID=None
    current_Flag=None
    current_Data=None
    current_origin=None
    mainWin=None
    AppDataPath = "./Libraries/ProgrammData/ProgrammData.db"
    DBVersion = "0.1"

    @classmethod
    def setCurrInfo(cls,Id=None,Flag=None,Data=None, origin=None):
        cls.current_ID=Id
        cls.current_Data=Data
        cls.current_Flag=Flag
        cls.current_origin=origin
        return

def decode(text):
    sub=""
    for char in text:
        if char==":":
            key=sub
            sub=""

        sub+=char





data="{1: {'type': 'Draftbook', 'data': [None], 'id': None, 'origin': None}, 2: {'type': 'Browser', 'data': [None], 'id': None, 'origin': None}}"

decode(data)