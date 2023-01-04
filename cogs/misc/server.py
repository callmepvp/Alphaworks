#Server File
#Handles all server-sided data management and/or other calls - anything server related put here
#! Not operational

import string

from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

totalItems = 9 #Update this with the amount of items in the game
#* This is hard-coded in so there's something to check against in case the bot doesn't load all items correctly

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
itemData = loads(Path("cogs/data/other/items.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

general = cluster['discord']['general']
collections = cluster['discord']['collections']
server = cluster['discord']['server']


class Server(commands.Cog):
    def __init__(self, client):
        self.client = client

        #* Leaderboard Refresh
        counter = 0
        categories = ['wood', 'ore']
        for category in categories:

            first = []
            ids = []
            
            #Find all the data
            for i in collections.find({},{"id" : 1, category : 1}): 
                amount = i[category]
                id = i['id']

                if int(amount) < 1: #Scores under 1 arent counted
                    pass
                else:
                    first.append(amount)
                    ids.append(id)

            first2 = first.copy()
            sorted = first.copy()
            sorted.sort(reverse=True)

            withoutdupes = []
            dupes = []

            withoutiddupes = []
            iddupes = []

            #Check for duplicates
            for x in sorted:
                cursor = first2.index(x)
                if x in withoutdupes:
                    dupes.append(x)
                    iddupes.append(ids[cursor])

                else:
                    withoutdupes.append(x)
                    withoutiddupes.append(ids[cursor])

                first2.pop(cursor)
                first2.insert(cursor, 'x')

            final = []
            idsfinal = []

            for x in range(len(first)):
                final.append('x')
                idsfinal.append('x')

            for i in range(len(first)):
                ogitem = first[i]
                ogid = ids[i]
                posnew = sorted.index(ogitem)

                if ogitem in withoutdupes: #Every unique value gets added straight away
                    withoutdupes.remove(ogitem)

                    final.pop(posnew)
                    final.insert(posnew, ogitem)

                    idsfinal.pop(posnew)
                    idsfinal.insert(posnew, ids[i])

                else: #Has to be a duplicate
                    itempos = final.index(ogitem)
                    
                    val = dupes.count(ogitem)
                    dupes.remove(ogitem)
                    iddupes.remove(ogid)

                    for j in range(val):
                        final.pop(itempos + val)
                        final.insert(itempos + val, ogitem)

                        idsfinal.pop(itempos + val)
                        idsfinal.insert(itempos + val, ids[i])  

            server.update_one({'serverID' : 1}, {"$set":{str(category) + 'amounts': final}})
            server.update_one({'serverID' : 1}, {"$set":{str(category) + 'ids': idsfinal}})

            #Update leaderboard data for every player
            for x in idsfinal:
                spot = idsfinal.index(x) + 1

                statsGeneral = general.find_one({'id' : x})
                personalLB = statsGeneral['leaderboards']
                personalLB[counter] = spot
                general.update_one({'id' : x}, {"$set":{'leaderboards' : personalLB}})

            counter += 1
        
        message = []
        message.append("[SERVER] ")

        for k in range(len(categories)):
            message.append(string.capwords(categories[k]))
            message.append(" | ")

        message.append('leaderboards updated succesfully!')
        print(''.join(message))
        
        #* Item Counter (To check if every item description in f!item was loaded properly)
        if len(itemData) == totalItems:
            print(f"[SERVER] All {len(itemData)} items loaded succesfully!")
        else:
            print("[SERVER] Something went wrong with item data loading. Check your totalItems variable.")

        #* Data Collection

def setup(client):
    client.add_cog(Server(client))
