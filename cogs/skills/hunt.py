import string
import random

from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

mobs = loads(Path("cogs/data/mobs/mobsDefault.json").read_text())
mobsData = loads(Path("cogs/data/mobs/mobsDefaultData.json").read_text())

#Collections
general = cluster['discord']['general']
mobloot = cluster['discord']['mobloot']

skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']
bonuses = cluster['discord']['bonuses']
bestiary = cluster['discord']['bestiary']

"""
Goblin: 1-2 dph - Goblin ear ; Goblin gold
Zombie: 1-2 dph - Zombie flesh ; Zombie brain
Skeleton: 0-4 dph - Bone ; Crystal Skull ; Archery potion
Ogre: 1-3 dph - Ogre thumb ; Ogre skin ; Health potion

Ghost: 0-5 dph - Sorrow ; Ectoplasm
"""

class Hunt(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command()
    async def hunt(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsMobLoot = mobloot.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})
            statsBonuses = bonuses.find_one({'id' : ctx.author.id})
            statsBestiary = bestiary.find_one({'id' : ctx.author.id})

            #Choose the mob and drop
            mobType = random.choice(list(mobs))
            print(mobType)
            lootType = random.choice(list(mobs[mobType].items()))
            print(lootType)
            lootType = lootType[1]
            print(lootType)
            lootAmount = random.randint(1, 2)

            #Get the stats
            defense = statsGeneral['defense']
            hp = statsGeneral['hp']
            maxhp = statsGeneral['maxhp']
            mobDamage = random.randint(1, int(list(mobsData[mobType].items())[0][1]))
            
            #Get the loot chance
            chance = random.randint(1, 100)
            lootChance = (chance >= 1 and chance <= 75) #75%

            #Find the bonuses
            #Applicable Bonuses: Well-Fed
            if bonuses.find_one({'id' : ctx.author.id, 'well-fed' : {'$exists': True}}) is not None:
                #Well-fed bonus > 5%
                wellfedbonus = True
                bonusLast = statsBonuses['well-fed']
                if bonusLast - 1 != 0:
                    bonuses.update_one({'id' : ctx.author.id}, {"$set":{'well-fed' : bonusLast - 1}})
                else:
                    bonuses.update_one({'id' : ctx.author.id}, {"$unset":{'well-fed' : ''}})
                
                dodgeChance = 5 + statsSkills['scavengingAttribute']
            else:
                wellfedbonus = False
                dodgeChance = statsSkills['scavengingAttribute']

            #Give the damage
            dodgeCalculated = random.randint(1, 100)
            if dodgeCalculated >= 1 and dodgeCalculated <= 100 - dodgeChance:                
                #Dodge wont happen
                dodge = False

                #Calculate the health
                hpAfter = (hp-mobDamage) + (defense*0.5*mobDamage)/100
                hpAfter = (int(hpAfter))
                if hpAfter >= maxhp:
                    hpAfter = maxhp
                
            else:
                #Dodge will happen
                dodge = True

                #Calculate the health
                hpAfter = hp

            #Send the messages
            if hpAfter == 0:
                general.update_one({'id' : ctx.author.id}, {"$set":{'hp' : hpAfter}})
                await ctx.send(f'**[*]** You went hunting and found a **{mobType}**.' '\n' f'**[*]** You have {hpAfter}/{maxhp} HP!')
                await ctx.send('**[DEATH]** You died! You are now on cooldown before you can do any actions again.')
            else:
                general.update_one({'id' : ctx.author.id}, {"$set":{'hp' : hpAfter}})

                #Update the bestiary
                if bestiary.find_one({'id' : ctx.author.id, mobType : {'$exists': True}}) is None:
                    mobData = {
                        'id' : ctx.author.id,
                        mobType : 1 
                    }

                    if statsBestiary is None:
                        bestiary.insert_one(mobData)
                    else:
                        bestiary.update_one({'id' : ctx.author.id}, {"$set":{mobType : 1}})
                else:
                    bestiary.update_one({'id' : ctx.author.id}, {"$set":{mobType : statsBestiary[mobType] + 1}})

                #Change the message depending on the dodge chance
                message = []
                if dodge == False and lootChance == True:
                    message.append(f'**[*]** You went hunting and found a **{string.capwords(mobType)}**.' '\n'
                                    f'**[*]** You now have **{hpAfter}/{maxhp} HP** left!' '\n'
                                    f'**[*]** While hunting you found **{lootAmount}** x **{string.capwords(lootType)}**.' '\n')

                elif dodge == True and lootChance == True:
                    message.append(f'**[*]** You went hunting and found a **{string.capwords(mobType)}**.' '\n'
                                    f'**[*]** You evaded all damage because of your evasion stat!' '\n'
                                    f'**[*]** While hunting you found **{lootAmount}** x **{string.capwords(lootType)}**.' '\n')

                elif dodge == False and lootChance == False:
                    message.append(f'**[*]** You went hunting and found a **{string.capwords(mobType)}**.' '\n' 
                    f'**[*]** You now have **{hpAfter}/{maxhp} HP** left!' '\n')

                elif dodge == True and lootChance == False:
                    message.append(f'**[*]** You went hunting and found a **{string.capwords(mobType)}**.' '\n' 
                    f'**[*]** You evaded all damage because of your evasion stat!' '\n')

                if wellfedbonus == True:
                    if bonusLast - 1 != 0: 
                        message.append(f'**[BONUS]** Your `well-fed` bonus will last for **{bonusLast - 1}** more hunts! Do the bonus command (f!bonus) to learn about your bonuses.')
                else:
                    pass
                
                #Give the loot
                if lootChance == True:
 
                    if mobloot.find_one({'id' : ctx.author.id, lootType : {'$exists': True}}) is None:
                        #Form the data file
                        lootData = {
                            'id' : ctx.author.id,
                            lootType : lootAmount
                        }

                        if statsMobLoot is None:
                            mobloot.insert_one(lootData)
                        else:
                            mobloot.update_one({'id' : ctx.author.id}, {"$set":{lootType : lootAmount}})
                    else:
                        mobloot.update_one({'id' : ctx.author.id}, {"$set":{lootType : statsMobLoot[lootType] + lootAmount}})

                messageValue = ''.join(message)
                await ctx.send(messageValue)

                #Calculate and give the skill XP
                existingXP = statsSkills['combatXP']
                existingLevel = statsSkills['combatLevel']

                xp = 7
                combatXP = existingXP + xp

                if combatXP >= 50*existingLevel + 10:
                    skills.update_one({'id' : ctx.author.id}, {"$set":{'combatXP' : 0, 'combatLevel' : existingLevel + 1}})
                    await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Combat** level **{existingLevel + 1}**!')

                else:
                    skills.update_one({'id' : ctx.author.id}, {"$set":{'combatXP' : combatXP}})
                    await ctx.send(f'**[*]** You gained +**{xp} Combat** XP!')
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Hunt(client))