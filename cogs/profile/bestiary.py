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
bestiary = cluster['discord']['bestiary']

mobs = loads(Path("cogs/data/mobs/mobsDefault.json").read_text())
mobsData = loads(Path("cogs/data/mobs/mobsDefaultData.json").read_text())

class Bestiary(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['beastdiary', 'bd', 'b'])
    async def bestiary(self, ctx, mob = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsBestiary = bestiary.find_one({'id' : ctx.author.id})
            
            text = []
            if statsBestiary is not None:
            
                #If no argument is provided
                if mob == None:
                
                    text.append("**Your Bestiary:**" "\n" "*Do f!bd <mob> for specifics!*" "\n" "\n")

                    document = bestiary.find_one({'id' : ctx.author.id})
                    for res in document:
                        val = document[res]
                        if res != 'id' and res != '_id':

                            text.append(string.capwords(res) + " ⇒ " + f"**{str(val)}**" + "\n")

                            #? Total XP from x mob
                            #? Total deaths from x mob
                            #? Other misc info

                #Search up provided mob
                else:

                    if mob in mobsData and mob in mobs:
                        if mob in statsBestiary is not None:
                            text.append(f"Beastiary entry on **{string.capwords(mob)}:**" "\n" "\n")

                            #* Description
                            text.append("⇒ **Description**:" "\n" f"{list(mobsData[mob].items())[1][1]}" "\n")
                            
                            #** Damage
                            text.append(f"*Damage Per Hit*: `1-{list(mobsData[mob].items())[0][1]}`" "\n" "\n")

                            #* Mob Drops
                            #? Only show the drops you've gotten from battling them
                            text.append("⇒ **Drops**:" "\n")
                            for i in range(int(len(list(mobs[mob].items())))):
                                text.append(f"{string.capwords(list(mobs[mob].items())[i][1])}" "\n")

                            #* Misc Information
                            text.append("\n" "⇒ **Added in**:" f" {list(mobsData[mob].items())[2][1]}" "\n")
                            text.append("⇒ **Found in**:" f" {list(mobsData[mob].items())[3][1]}")

                        else:
                            text.append("You don't know anything about this mob.")

                    else:
                        text.append("There is no data on this mob.")

                await ctx.send(''.join(text))
        else:
            await ctx.send('You do not have a profile setup. Please do the setup command to make your profile!')

def setup(client):
    client.add_cog(Bestiary(client))