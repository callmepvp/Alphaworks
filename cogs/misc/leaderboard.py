import string
from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

general = cluster['discord']['general']
collections = cluster['discord']['collections']
server = cluster['discord']['server']

class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['l', 'li', 'lb', 'leaderboards'])
    async def leaderboard(self, ctx, lb = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            
            text = []
            #* General Info on Leaderboards/Updates
            if lb == None: 

                text.append("**Leaderboards**" "\n")
                text.append("*Do f!lb <leaderboard name> for specifics!*" "\n" "\n")

                text.append("Current Leaderboards:" "\n")
                text.append("⤳ **Collections** ⬿" "\n"
                            "⇒ Wood" "\n"
                            "⇒ Ore" "\n")

                text.append("\n" "⤳ **Seasonal** ⬿" "\n"
                            "⇒ ..." "\n")

            #* Collection Leaderboards
            else:
                statsServer = server.find_one({'serverID' : 1})
                d1 = statsServer[str(lb.lower()) + 'amounts']
                d2 = statsServer[str(lb.lower()) + 'ids']
                text.append(f"Leaderboard for **{string.capwords(lb)}:**" "\n" "*Showing the best 10!*" "\n" "\n")

                #Set the amount of times its shown
                if len(d2) <= 10:
                    val = len(d2)
                else:
                    val = 10

                for i in range(val):
                    stats = general.find_one({'id' : d2[i]})
                    name = stats['name']

                    if i == 0:
                        text.append(f"**{i+1}.** **{name}** with **{d1[i]}** Collection :crown:" "\n")
                    else:
                        text.append(f"**{i+1}.** **{name}** with **{d1[i]}** Collection" "\n")
                    
            
            await ctx.send(''.join(text))
        else:
            await ctx.send('You do not have a profile setup. Please do the setup command to make your profile!')

    @commands.command()
    async def lbupdate(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:

            #* Collection LB Update
            #* Wood, Ore
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

            await ctx.send("Leaderboards Updated Manually.")
        else:
            await ctx.send('You do not have a profile setup. Please do the setup command to make your profile!')

def setup(client):
    client.add_cog(Leaderboard(client))