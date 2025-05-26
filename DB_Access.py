
import shutil
import os
import sqlite3

from datetime import datetime

from AppVar import UserData, AppData

#region Database Factories, access and manipulation

#ToDo update doc
def searchFactory(text:str,library:str,innerJoin:str ="",output:str =None,  shortOut:bool= False ,
                  attributes:list=None ,Filter:list=[],OrderBy = None, searchFulltext:bool =False,
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


    conn=sqlite3.connect(UserData.path)
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
    if Filter!=[]:
        for index, filterDict in enumerate(Filter):
            filterstring += " AND %s like ?" % (filterDict["key"])

            if filterDict["fullTextSearch"]:
                filterTextList.append("%"+filterDict["text"]+"%")
            else:
                filterTextList.append(filterDict["text"])

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
    conn=sqlite3.connect(UserData.path)
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
        path=UserData.path

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
        path=UserData.path

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

    conn=sqlite3.connect(UserData.path)
    c=conn.cursor()
    c.execute("""PRAGMA foreign_keys=ON""")
    c.execute("""DELETE FROM %s 
                    WHERE rowid= (?)""" %(library),(id,))

    conn.commit()
    conn.close()

    return

def newFactory(library: str, data: dict={}):
    """creates new entries with given data in given table within the library at UserData.Path

    :param library: str
        name of table
    :param data: dict
        dictionary with columns as keys
    :return: ->int, the id of the newly created entry
    """
    conn = sqlite3.connect(UserData.path)
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
    conn=sqlite3.connect(UserData.path)
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

def updateLibraryVersion(updatePath:str):
    """copies all data from the updatePaths database to the structure of the applications NewCampaign.db

    :param updatePath: str, specifies the origin path of the database to update

    :return: True|str, returns True if the operation was successful or the origin of the produced backup database

    """
    basePath = "./Libraries/ProgrammData/NewCampaign.db"
    updatePath = updatePath
    backupPath = updatePath.rsplit(".", maxsplit=1)[0] + "_backup_" + datetime.now().strftime("%Y-%m-%d") + (".db")
    if os.path.exists(backupPath):
        backupPath = updatePath.rsplit(".", maxsplit=1)[0] + "_backup_" + datetime.now().strftime("%Y-%m-%d-%H%M%S") + (
            ".db")

    shutil.copy(updatePath, backupPath)

    try:

        shutil.copy(basePath, updatePath)

        conn=sqlite3.connect(updatePath)
        c=conn.cursor()
        c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        tables = [x[0] for x in c.fetchall()]
        tablesDict = {}

        for table in tables:
            c.execute("""SELECT * FROM %s""" %(table))
            tablesDict[table] = [x[0] for x in c.description]

        c.execute("""SELECT Database_Version FROM DB_Properties""")
        version=c.fetchone()[0]
        conn.close()

        conn = sqlite3.connect(backupPath)
        c = conn.cursor()
        c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        tables = [x[0] for x in c.fetchall()]

        dataInsert= {}
        for table in tables:
            c.execute("""SELECT * FROM %s"""%(table))

            columns=[x[0] for x in c.description]
            insertionIndexes=[]
            for index,column in enumerate(tablesDict[table]):
                if column not in columns:
                    insertionIndexes.append(index)

            dataset=c.fetchall()
            newDataset=[]
            for set in dataset:
                listed=[x for x in set]
                for index in insertionIndexes:
                    listed.insert(index,None)
                newDataset.append(listed)

            dataInsert[table] = newDataset

        conn.close()

        conn = sqlite3.connect(updatePath)
        c = conn.cursor()

        for table in tables:


            c.execute("DELETE FROM %s" % (table))

            for dataset in dataInsert[table]:
                c.execute("""INSERT INTO %s VALUES (%s)""" % (table, (len(dataset) * "?,").rstrip(",")),
                          (*dataset,))

        c.execute("""UPDATE DB_Properties SET Database_Version = (?) """ ,(version,))

        conn.commit()
        conn.close()
    except:
        return backupPath
    return True

def checkLibrary(path, campaign=True):
    """checks if a library has a matching table set and therefore is a compatible library

    :param path: str, the path for the checked library
    :param campaign: bool, optional, specifies if the checked library version should be handled as Campaign Database
    :return: bool, True if the checked Database Version ist compatible with the reqúired Database Version
    """
    app_DBVersion_requirement=AppData.DBVersion
    if campaign:

        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("""SELECT Database_Version FROM DB_Properties""")
        campaign_DB_version=c.fetchone()[0]
        conn.close()
        if campaign_DB_version==app_DBVersion_requirement:
            return True

        return False

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
