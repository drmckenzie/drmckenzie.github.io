# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:28:31 2021

"""

def runAllTypesTopX(calcyFilename,gamepressFilename,topX):
    """ 
    Inputs: filenames of calcyIV and gamepress csv files. Select top X results 
    Method: goes through the calcy database and matches any from the gampress
    database that has the best attacking moves (defined by DPS^3*TDO)
    Output: For each type, returns ratio of pokemon with best moves.
    """    
    
    typeList = ["Normal", "Fire", "Water", "Grass", "Flying", "Fighting", "Poison", "Electric", "Ground", "Rock", "Psychic", "Ice", "Bug", "Ghost", "Steel", "Dragon", "Dark", "Fairy"]
    
    import pandas as pd
    
    allData = pd.DataFrame(columns=["Pokemon","#","Type","Count","Caught","DPS^3*TDO"])
    
    for typeFilter in typeList:
        Result,topResult = calculatePokemonWithBestMoves(calcyFilename,gamepressFilename,typeFilter,topX)

        # get the data we're interested in. Name and score
        ResultTopX = Result[["Pokemon","#","Fast move","Special move","DPS^3*TDO"]].copy()
          
        # NOTE: this controls whether we see the same pokemon with different moves in the result
        #TODO make this a flag
        # ResultTopX.drop_duplicates(subset=['Pokemon','#'], inplace=True)  
                                           
        if len(ResultTopX)==0:
            ResultTopX = pd.DataFrame(columns=["Pokemon","#","Type","Fast move","Special move","Count","Caught","DPS^3*TDO"])
            ResultTopX.loc[0] = ['',0,typeFilter,"","",0,'No',1]
        else:
            ResultTopX["Count"] = 1
                                           
        ResultTopX["Type"] = typeFilter
        ResultTopX["Caught"] = "Yes"
        
        # get the difference, what we have not caught:
        notCaught = topResult[topResult.Pokemon.isin(Result.Pokemon) == False]
        notCaughtTopX = notCaught[["Pokemon","#","Fast move","Special move","DPS^3*TDO"]].copy()
        notCaughtTopX["Type"] = typeFilter
        notCaughtTopX["Caught"] = "No"
        notCaughtTopX["Count"] = "1"
        
        allData = pd.concat([allData,ResultTopX,notCaughtTopX],sort=False)
              
        foundTypeTopX = "You have the top "+str(len(ResultTopX))+" of the "+str(topX)+" most powerful "+typeFilter+" type Pokemon"                                   
        print(foundTypeTopX)
        
    return allData

def getGamepressData(gamepressFilename,typeFilter,topX):
    """ 
    Inputs: filenames of gamepress csv files 
    Method: goes through the gamepress database and loads. Filters by type.
    Output: Results dataframe of pokemon sorted by "DPS^3*TDO" and filtered by type.
    """    
    
    if (topX==[]):
        topX = 999999999
    
    # import csv sheet
    import pandas as pd
    
    # read the csv files into dataframes
    gamepressData = pd.read_csv(gamepressFilename, encoding='utf8')
    
    # get the data we're interested in. Name and score
    gamepress = gamepressData[["Pokemon","Fast Move","Charged Move","DPS","TDO","DPS^3*TDO"]]
    
    #TODO do something with Geodude Normal etc.
       
    # rename columns                                 
    gamepress = gamepress.rename(columns={'Charged Move': 'Special move'})
    gamepress = gamepress.rename(columns={'Fast Move': 'Fast move'})
    
    # Duplicate the special move column for later on
    gamepress['Special move 2'] = gamepress['Special move']
    
    # get the number, type and name from the lookup:
    PokemonNoType =  getPokemonNumberType()

    # match pokemon to type:
    gamepressType = gamepress.merge(PokemonNoType,how='inner', on=['Pokemon'])
     
    if typeFilter==[]:
        gpResultBoth = gamepressType.copy()
    else:
        # filter by type. Careful, there's two columns.
        gpResult1 = gamepressType[gamepressType["Type1"]==typeFilter]
        gpResult2 = gamepressType[gamepressType["Type2"]==typeFilter]
           
        gpResultBoth = pd.concat([gpResult1,gpResult2],sort=False)
        
        # NOTE: this controls whether we see the same pokemon with different moves in the result
        #TODO make this a flag
        #gpResultBoth.drop_duplicates(subset=['Pokemon','#'], inplace=True)
        
    # sort by ..
    gpResultBoth.sort_values(by=["DPS^3*TDO",'#'], inplace=True, ascending=False)

    # extract topX if required:
    if (topX>0)&( topX<=len(gpResultBoth) ):
            gpResult = gpResultBoth.head(topX)
    else:
        gpResult = gpResultBoth.copy()
                                 
    return gpResult


def getPvpPokeData(pvpPokeFilename,typeFilter,topX):
    """ 
    Inputs: filenames of gamepress csv files 
    Inputs column: Pokemon	Score	Type 1	Type 2	Attack	Defense	Stamina	Stat Product	Level	Fast Move	Charged Move 1	Charged Move 2
    Method: goes through the gamepress database and loads. Filters by type (of pokemon).
    Output: Results dataframe of pokemon sorted by "DPS^3*TDO" and filtered by type.
    """    
    
    if (topX==[]):
        topX = 999999999
    
    # import csv sheet
    import pandas as pd
    
    # read the csv files into dataframes
    pvpPokeData = pd.read_csv(pvpPokeFilename, encoding='utf8')
    
    # get the data we're interested in. Name and score
    pvpPoke = pvpPokeData[["Pokemon","Fast Move","Charged Move 1","Charged Move 2","Score","Level"]]
    
    #TODO do something with Geodude Normal etc.
       
    # rename columns                                 
    # pvpPoke = pvpPoke.rename(columns={'Charged Move 1': 'Special move'})
    #pvpPoke = pvpPoke.rename(columns={'Fast Move': 'Fast move'})
    
    # get the number, type and name from the lookup:
    PokemonNoType =  getPokemonNumberType()

    # match pokemon to type:
    pvpPokeType = pvpPoke.merge(PokemonNoType,how='inner', on=['Pokemon'])
     
    if typeFilter==[]:
        pvpResultBoth = pvpPokeType.copy()
    else:
        # filter by type. Careful, there's two columns.
        pvpResult1 = pvpPokeType[pvpPokeType["Type1"]==typeFilter]
        pvpResult2 = pvpPokeType[pvpPokeType["Type2"]==typeFilter]
           
        pvpResultBoth = pd.concat([pvpResult1,pvpResult2],sort=False)
        
        # NOTE: this controls whether we see the same pokemon with different moves in the result
        #TODO make this a flag
        #gpResultBoth.drop_duplicates(subset=['Pokemon','#'], inplace=True)
        
    # sort by ..
    pvpResultBoth.sort_values(by=["Score",'Pokemon'], inplace=True, ascending=False)

    # extract topX if required:
    if (topX>0)&( topX<=len(pvpResultBoth) ):
            pvpResult = pvpResultBoth.head(topX)
    else:
        pvpResult = pvpResultBoth.copy()
                                 
    return pvpResult


def calculatePokemonWithBestMoves(calcyFilename,gamepressFilename,typeFilter,topX):
    """ 
    Inputs: filenames of calcyIV and gamepress csv files 
    Method: goes through the calcy database and matches any from the gampress
    database that has the best attacking moves (defined by DPS^3*TDO)
    Output: Results dataframe of matched pokemon with best moves.
    """    
    
    # import csv sheet
    import pandas as pd
    
    gamepress = getGamepressData(gamepressFilename,typeFilter,topX)
    
    # read the csv files into dataframes
    calcyData = pd.read_csv(calcyFilename, encoding='utf8')
    
    # get the data we're interested in. Name and score
    calcy = calcyData[["Name","Nr","Fast move","Special move","Special move 2","CP","Saved","Lucky","ShadowForm"]]
    
    # drop those that are not saved:
    calcy = calcy[calcy["Saved"]==1]
    
    #TODO do something with Geodude Normal etc.
       
    # rename shadow and XL to remove the quotation marks
    #calcy['Shadow'] = calcy['Shadow'].str.replace(r'"', '')
    
    # rename columns                                 
    calcy = calcy.rename(columns={'Name': 'Pokemon'})
    calcy = calcy.rename(columns={'Nr': '#'})
    
    # drop any blank fast/special moves:
    calcy = calcy[~calcy["Fast move"].str.startswith('-')]
    calcy = calcy[~calcy["Fast move"].str.startswith(" -")]
    calcy = calcy[~calcy["Special move"].str.startswith("-")]
    calcy = calcy[~calcy["Special move"].str.startswith(' -')]
    
    # rename - whitespace. Infuriating
    calcy['Fast move'] = calcy['Fast move'].str.replace(r'-', ' ')
    calcy['Special move'] = calcy['Special move'].str.replace(r'-', ' ')
    calcy['Special move 2'] = calcy['Special move 2'].str.replace(r'-', ' ')
    
    # move the "shadow" tag to the front rather than the back
    calcyShadowFound = calcy['Pokemon'].str.endswith('Shadow').copy()
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Shadow', '')
    calcy.loc[calcyShadowFound,'Pokemon'] = 'str' + calcy.loc[calcyShadowFound,'Pokemon'].astype(str)
    
    # filter for testing:
    # calcy = calcy[calcy["Pokemon"].str.startswith('Rhyp')]
    
    # merge : this needs to be a 2 step process
    Result1 = calcy.merge(gamepress,how='inner', on=['Pokemon',"#",'Fast move','Special move'])
    
    Result2 = calcy.merge(gamepress,how='inner', on=['Pokemon',"#",'Fast move','Special move 2'])
    
    # rename columns
    Result1 = Result1.rename(columns={'Special move 2_x': 'Special move 2'})
    Result1 = Result1.rename(columns={'Special move 2_y': 'Temp'})
    Result2 = Result2.rename(columns={'Special move_x': 'Special move'})
    Result2 = Result2.rename(columns={'Special move_y': 'Temp'})
    
    Result = pd.concat([Result1,Result2],sort=False)
    
    # drop the column
    Result.drop(columns=['Temp'], inplace=True)
    
    # drop duplicates - WARNING, may drop some pokemon with second special moves
    #TODO - maybe do this better??
    Result.drop_duplicates(subset=['Pokemon','CP'], inplace=True)
    
    # print(Result)
    
    # sort by ..
    Result.sort_values(by=['#', 'CP'], inplace=True)
                           
    # get the number, type and name from the lookup:
    #PokemonNoType =  getPokemonNumberType()

    # match pokemon to type:
    #ResultType = Result.merge(PokemonNoType,how='inner', on=['Pokemon',"#"])
                                        
    return Result,gamepress



def getNoCpFromResults(Result):
    """ 
    Input: Result dataframe 
    Method: spit out the list of all pokemon that have the best moves in the
    format number and CP for entering into the Pokemon Go search bar.
    e.g. 1,2,3,50&CP20,CP40,CP50,CP60
    Output: CSV file (all results) and text file (above string).
    """    
        
    # filtering to get the # an CP
    ResultsCP = Result[["Pokemon","#","CP"]]
    # get a unique list of pokemon:
    ResultsPokemon = list(Result.Pokemon.unique())

    # print the # and CP list to file:
    keepFileNoCP = 'results_pokemon_No_CP_best_moves.txt'
    with open(keepFileNoCP, 'w') as file:
        file.write('')
        #file.write(ResultsPokemonCPBestMoves)
    
    #iterate to get CP values:
    iter = 0
    strNo = ''
    strCP = ''
    ResultsPokemonCPBestMoves = ''
    
    # how many chunks do we want?
    splitEvery = 7
    
    for pokemon in ResultsPokemon:
        iter = iter + 1
        
        if iter >= (splitEvery+1):
            with open(keepFileNoCP, 'a') as file:
                file.write(ResultsPokemonCPBestMoves)
                file.write('\n')
                file.write('\n')
            strNo = ''
            strCP = ''
            iter = 0
        
        getNo = ResultsCP[ResultsCP["Pokemon"]==pokemon]["#"].unique() 
        getCP = ResultsCP[ResultsCP["Pokemon"]==pokemon]["CP"].unique()
        strNo = str(strNo)+str(*getNo)+','
        for cp in getCP:
            strCP = strCP+'CP'+str(cp)+','
            
        ResultsPokemonCPBestMoves = strNo[:-1] + "&" + strCP[:-1]

    return
    
def getPokemonNumberType():
    """ 
    Input: none 
    Method: inputs database of pokemon information.
    Output: lookup table of pokemon and type.
    """    

    # import csv sheet
    import pandas as pd
    
    # filenames
    #csvFilename = 'great_overall.csv'
    lookupFilename = 'Pokemon_Lookup.csv'
    
    # read the csv files into dataframes
    # rawData = pd.read_csv(csvFilename, encoding='utf8')
    lookupData = pd.read_csv(lookupFilename, encoding='utf8')
    
    # drop nan s from these columns
    lookupData = lookupData.dropna(subset=['#'])
    # the lookup data should be integers
    lookupData.astype({'#': 'int32'}).dtypes
    
    lookupNameNumber = lookupData[["Name","#","Type 1","Type 2","Released_2021_03_13"]]
                                   
    # drop those that are not released yet:
    lookupNameNumber = lookupNameNumber[lookupNameNumber["Released_2021_03_13"]==True]
    
    # rename for better handling of spaces:
    lookupNameNumber.rename(columns={"Type 1": "Type1"}, inplace=True)
    lookupNameNumber.rename(columns={"Type 2": "Type2"}, inplace=True)
                                   
    # duplicate this list because of the way Gamepress do the shadow names
    lookupNameNumberShadow = lookupNameNumber.copy()
    lookupNameNumberShadow['Name'] = 'Shadow ' + lookupNameNumberShadow['Name'].astype(str)
    
    # duplicate this list because of the way Gamepress do the shadow names
    lookupNameNumberShadowPVP = lookupNameNumber.copy()
    lookupNameNumberShadowPVP['Name'] = lookupNameNumberShadowPVP['Name'].astype(str)+' (Shadow)'
    
    lookupNameNumberBoth = pd.concat([lookupNameNumber,lookupNameNumberShadow,lookupNameNumberShadowPVP])
    
    lookupNameNumberBoth.drop_duplicates(subset=['Name','#'], inplace=True)
                                                 
    lookupNameNumberBoth.rename(columns={'Name': 'Pokemon'}, inplace=True)
                                   
    return lookupNameNumberBoth

def getListOfPokemonNotCaught(calcyFilename,gamepressFilename):
    
    # import csv sheet
    import pandas as pd
    
    # switch off copy warning
    pd.set_option("mode.chained_assignment",None)
    
    # read the csv files into dataframes
    calcyData = pd.read_csv(calcyFilename, encoding='utf8')
    
    # read the csv files into dataframes
    gamepressData = pd.read_csv(gamepressFilename, encoding='utf8')
    
    # get the data we're interested in. Name and score
    gamepress = gamepressData[["Pokemon","Fast Move","Charged Move","DPS","TDO","DPS^3*TDO"]]
    # drop duplicates - 
    gamepress.drop_duplicates(subset=['Pokemon'], inplace=True)
    
    # get the data we're interested in. Name and score
    #calcy = calcyData[["Name","Nr","Fast move","Special move","Special move 2","CP","Saved","Lucky","ShadowForm"]]
    calcy = calcyData[["Name","Nr"]].copy()
    

       
    # rename shadow and XL to remove the quotation marks
    #calcy['Shadow'] = calcy['Shadow'].str.replace(r'"', '')
    
    # rename columns                                 
    calcy = calcy.rename(columns={'Name': 'Pokemon'})
    calcy = calcy.rename(columns={'Nr': '#'})    
                                  
    # drop duplicates - WARNING, may drop some pokemon with second special moves
    calcy.drop_duplicates(subset=['Pokemon','#'], inplace=True)
                                  
    #TODO do something with Geodude Normal etc.
    # rename - whitespace. Infuriating
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Normal', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Alolan', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Spring', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Winter', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Summer', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Autumn', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Plant', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Sandy', '')                              
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Trash', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Purified', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Shadow', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'(Rainy)', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'(Snowy)', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'(Sunny)', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'Castform (Rainy)', 'Castform')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'Castform (Snowy)', 'Castform')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r'Castform (Sunny)', 'Castform')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Blue Striped', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Red Striped', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' West Sea', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' East Sea', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Overcast', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Sunshine', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Galarian', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Incarnate', '')
    calcy['Pokemon'] = calcy['Pokemon'].str.replace(r' Therian', '')
    
           

    # make a column with "caught"
    calcy['Caught'] = True                                  
                                  
    # get the number, type and name from the lookup:
    PokemonNoTypeAll =  getPokemonNumberType()
    PokemonNoType = PokemonNoTypeAll[["Pokemon","#","Released_2021_03_13"]].copy()
        
    # merge 
    Result1 = gamepress.merge(PokemonNoType,how='inner', on=['Pokemon'])
    
    # This should be the list of released pokemon so far.
    releasedPokemon = Result1[["Pokemon"]].copy()
    releasedPokemon.drop_duplicates(subset=['Pokemon'], inplace=True)

    # a list of pokemon /we/ have is:
    caughtPokemon = calcy[["Pokemon"]].copy()
    caughtPokemon.drop_duplicates(subset=['Pokemon'], inplace=True)
    
    #what we have /not' caught is:
    notCaught = releasedPokemon[releasedPokemon.Pokemon.isin(calcy.Pokemon) == False]
    # sort by ..
    notCaught.sort_values(by=['Pokemon'], inplace=True)
        
    # drop the column
    #Result.drop(columns=['Temp'], inplace=True)
    
    # drop duplicates - WARNING, may drop some pokemon with second special moves
    #TODO - maybe do this better??
    #Result.drop_duplicates(subset=['Pokemon','CP'], inplace=True)
    
    # print(Result)
    
    # sort by ..
    #Result.sort_values(by=['#'], inplace=True)
                           
    return releasedPokemon,caughtPokemon,notCaught

def replaceNameStrings(smallData):
    # making sure we can do something with variants of pokemon with special text
    smallData["PokemonBase"] = smallData["Pokemon"].copy()
    # mostly PVPpoke data
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Shadow)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Shadow XL)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Galarian)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Galarian XL)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Alolan)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Alolan XL)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Rainy)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Snowy)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Sunny)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Overcast)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Sunshine)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Standard)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Defense)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Speed)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Standard)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (East)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (West)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Male)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Female)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Wash)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Trash)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Sandy)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Plant)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Burn)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Origin)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Altered)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Incarnate)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Therian)', ''))
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace(' (Armoured)', ''))
  
    # mostly gamepress data
    smallData['PokemonBase'] = smallData['PokemonBase'].apply(lambda x: x.replace('Shadow ', ''))

    return smallData

def replaceBaseNameStrings(strName,strNameBase):
    # do some filtering and replacing
    if strName.endswith(" (Shadow)"):
        strNameSearch = strNameBase + "&shadow"
    elif strName.startswith("Shadow "):
        strNameSearch = strNameBase + "&shadow"
    elif strName.endswith(" (Shadow XL)"):
        strNameSearch = strNameBase + "&shadow"
    elif strName.endswith(" (Galarian)"):
        strNameSearch = strNameBase + "&galar"
    elif strName.endswith(" (Galarian XL)"):
        strNameSearch = strNameBase + "&galar"
    elif strName.endswith(" (Alolan)"):
        strNameSearch = strNameBase + "&alola"
    elif strName.endswith(" (Alolan XL)"):
        strNameSearch = strNameBase + "&alola"
    elif strName.endswith(" (Standard)"):
        strNameSearch = strNameBase
    elif strName.startswith("Castform"):
        strNameSearch = strNameBase
    elif strName.startswith("Cherrim"):
        strNameSearch = strNameBase
    elif strName.startswith("Gastrodon"):
        strNameSearch = strNameBase
    elif strName.startswith("Deoxys"):
        strNameSearch = strNameBase
    elif strName.startswith("Meowstic"):
        strNameSearch = strNameBase
    elif strName.startswith("Rotom"):
        strNameSearch = strNameBase
    elif strName.startswith("Shellos"):
        strNameSearch = strNameBase
    elif strName.startswith("Wormadam"):
        strNameSearch = strNameBase
    elif strName.startswith("Genesect"):
        strNameSearch = strNameBase
    elif strName.startswith("Giratina"):
        strNameSearch = strNameBase
    elif strName.startswith("Landorus"):
        strNameSearch = strNameBase
    elif strName.startswith("Thundurus"):
        strNameSearch = strNameBase
    elif strName.startswith("Tornadus "):
        strNameSearch = strNameBase
    elif strName.startswith("Mewtwo (Armored)"):
        strNameSearch = strNameBase
    else:
        strNameSearch = strName
            
    return strNameSearch

def makeNicePvpPokeString(stringIn):
    
    strMiddle = stringIn
    
    # mostly PvPPoke data
    strMiddle = strMiddle.replace(' (','_')
    strMiddle = strMiddle.replace(')', '')
    
    strOut = strMiddle.lower()

    return strOut

def makeNiceGamepressString(stringIn,strNumber):
    
    strName = stringIn
    
    # do some filtering and replacing
    if strName.endswith(" (Shadow)"):
        strNameSearch = strNumber + "-shadow"
    elif strName.startswith("Shadow "):
        strNameSearch = strNumber + "-shadow"
    elif strName.endswith(" (Shadow XL)"):
        strNameSearch = strNumber + "-shadow"
    elif strName.endswith(" (Galarian)"):
        strNameSearch = strNumber + "-galarian"
    elif strName.endswith(" (Galarian XL)"):
        strNameSearch = strNumber + "-galarian"
    elif strName.endswith(" (Alolan)"):
        strNameSearch = strNumber + "-alolan"
    elif strName.endswith(" (Alolan XL)"):
        strNameSearch = strNumber + "-alolan"
    elif strName.endswith(" (Standard)"):
        strNameSearch = strNumber
    else:
        strNameSearch = strNumber
        
    #TODO: something with the other variants, such as castform, deoxy etc.

    strOut = strNameSearch.lower()

    return strOut