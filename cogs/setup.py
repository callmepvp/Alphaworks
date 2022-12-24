import time
import discord
import random
from discord.ext import commands
from discord.ext.commands.help import Paginator
from pymongo import MongoClient
import DiscordUtils
import string

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

badges = []
footers = []

#Database initializing
cluster = MongoClient(dbtoken)
general = cluster['discord']['general']
recipes = cluster['discord']['recipes']
skills = cluster['discord']['skills']
items = cluster['discord']['items']
tools = cluster['discord']['tools']
collections = cluster['discord']['collections']
areas = cluster['discord']['areas']
quests = cluster['discord']['quest']
misc = cluster['discord']['stats']

server = cluster['discord']['server']

class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases=['stp', 's'])
    async def setup(self, ctx):
        stats = general.find_one({'id' : ctx.author.id})
        statsServer = server.find_one({'serverID' : 0})
        if not ctx.author.bot:
            try:
                if stats is None:
                    newuserGeneral = {
                        'id' : ctx.author.id, 'name' : ctx.author.name,
                        'coins' : 0, 'bank' : 0, 'hp' : 100, 'maxhp' : 100, 'mana' : 150, 'energy' : 300, 'defense' : 0,
                        'axepower' : 1, 'pickpower' : 1, 'fishingrodpower' : 1,
                        'creation' : time.time(),

                        'leaderboards' : [0, 0] #! Update with amount of LBs in game right now // Make a global variable later
                    }

                    newuserSkills = {
                        'id' : ctx.author.id,
                        'foragingLevel' : 0, 'foragingXP' : 0, 'foragingAttribute' : 0,
                        'miningLevel' : 0, 'miningXP' : 0, 'miningAttribute' : 0,
                        'scavengingLevel' : 0, 'scavengingXP' : 0, 'scavengingAttribute' : 0,
                        'farmingLevel' : 0, 'farmingXP' : 0, 'farmingAttribute' : 0,
                        'fishingLevel' : 0, 'fishingXP' : 0, 'fishingAttribute' : 0,

                        'craftingLevel' : 0, 'craftingXP' : 0, 'craftingAttribute' : 0,
                        'brewingLevel' : 0, 'brewingXP' : 0, 'brewingAttribute' : 0,
                        'cookingLevel' : 0, 'cookingXP' : 0, 'cookingAttribute' : 0,
                        
                        'combatLevel' : 0, 'combatXP' : 0, 'combatAttribute' : 0
                    }

                    newuserCollections = { #! HAS 2 LEADERBOARDS
                        'id' : ctx.author.id,
                        'wood' : 0, 'woodmilestone' : 0, 'woodtemp' : 0,
                        'ore' : 0, 'oremilestone' : 0, 'oretemp' : 0
                        #Scavenge Collection
                        #Farming Collection (idle?)
                    }
                    
                    newuserRecipes = {
                        'id' : ctx.author.id,
                        'healthpotion' : True, 'bread' : True
                    }

                    newuserAreas = {
                        'id' : ctx.author.id,
                        'currentarea' : 'plains', 'currentlocation' : 'pond'
                    }

                    general.insert_one(newuserGeneral)
                    skills.insert_one(newuserSkills)
                    collections.insert_one(newuserCollections)
                    recipes.insert_one(newuserRecipes)
                    areas.insert_one(newuserAreas)

                    server.update_one({'serverID' : 0}, {"$set":{'registeredusers': statsServer['registeredusers'] + 1}})
                    await ctx.send('Your profile has been sucessfully setup. Happy playing!')
                else:
                    await ctx.send('You have already setup your character. You can use the profile command (f!profile) to view your profile.')
            except:
                await ctx.send('An error occured. Please try again later.')
                
    @commands.command(aliases=['prf', 'p'])
    async def profile(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsItems = items.find_one({'id' : ctx.author.id})
            
            currentAxe = statsGeneral['currentaxe']
            currentPick = statsGeneral['currentpick']
            currentRod = statsGeneral['currentrod']

            creation = statsGeneral['creation']
            
            #Tools Page
            descriptionValue = []
            document = tools.find_one({'id' : ctx.author.id})
            for res in document:
                val = document[res]
                if res != 'id' and res != '_id':
                    if res == currentAxe:
                        descriptionValue.append(f'{string.capwords(res)}' f' | ID: (`{val}`) **[EQUIPPED]**' '\n')
                    elif res == currentPick:
                        descriptionValue.append(f'{string.capwords(res)}' f' | ID: (`{val}`) **[EQUIPPED]**' '\n')
                    elif res == currentRod:
                        descriptionValue.append(f'{string.capwords(res)}' f' | ID: (`{val}`) **[EQUIPPED]**' '\n')
                    else:
                        descriptionValue.append(f'{string.capwords(res)}' f' | ID: (`{val}`)' '\n')
            
            #Items Page
            ItemsDescriptionValue = []
            if statsItems is not None:
                document = items.find_one({'id' : ctx.author.id})
                for res in document:
                    val = document[res]
                    if res != 'id' and res != '_id':
                            if statsItems is not None:
                                ItemsDescriptionValue.append(f'{val} x {string.capwords(res)}' '\n')
            else:
                ItemsDescriptionValue.append('This inventory is empty!')
            
            itemsDesc = ''.join(ItemsDescriptionValue)
            toolsDesc = ''.join(descriptionValue)

            profile1 = discord.Embed(title = 'Page 1/3: Main Stats', description = '', color=0x049a2a)
            profile2 = discord.Embed(title = 'Page 2/3: Tools & Armor', description = toolsDesc, color=0x049a2a)
            profile3 = discord.Embed(title = 'Page 3/3: Items', description = itemsDesc, color=0x049a2a)
            embeds = [profile1, profile2, profile3]
            footerEmbeds = [profile2, profile3] #Embeds that will have a default footer

            #Set footers and authors (idk how to do it better)
            for x in footerEmbeds:
                x.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
                x.set_footer(text = random.choice(footers))

            profile1.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)

            #Calculate character score WIP
            hp = statsGeneral['hp']
            maxhp = statsGeneral['maxhp']
            mana = statsGeneral['mana']
            defense = statsGeneral['defense']

            formula = ((maxhp + hp) / 6) + ((defense + mana) / 4)
            general.update_one({'id' : ctx.author.id}, {"$set":{'charscore' : int(formula)}})

            profile1.set_footer(text = 'Overall rank: ...')

            #Add the STATS page fields
            profile1.add_field(name = "MAIN", value = f"**HP** - {statsGeneral['hp']}" "\n" f"**Max HP** - {statsGeneral['maxhp']}" "\n" f"**Mana** - {statsGeneral['mana']}" "\n", inline = True)
            profile1.add_field(name = 'OTHER', value = f"**Defense** - {statsGeneral['defense']}" "\n" f"**Energy** - {statsGeneral['energy']}" "\n" f"**Coins** - {statsGeneral['coins']}", inline = True)
            profile1.add_field(name = 'MISC', value = f"**Reputation** - {statsGeneral['reputation']}" "\n" "**Achievement Points** - ...", inline=False)
            profile1.add_field(name = 'CLASS', value = '**Class** - ...' "\n" f'**Creation Date** - {creation}', inline=False)

            #Add the badges section

            #Badges:
            #NR 1 Leaderboard player
            #NR 1 AP player
            #Event badges

            badgeInfo = []
            if len(statsGeneral['badges']) > 1:
                for x in statsGeneral['badges']:
                    if x != '0':
                        badge = badges.get(x)
                        if len(statsGeneral['badges']) - 1 == (statsGeneral['badges'].index(x)):
                            badgeInfo.append(badge)
                        else:
                            badgeInfo.append(badge + " ; ")

                profile1.add_field(name = 'BADGES', value = ''.join(badgeInfo), inline=False)

            #Setup the paginated embed
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")
            paginator.add_reaction('⏭️', "last")

            await paginator.run(embeds)
        else:
            await ctx.send('You do not have a profile setup. Please do the setup command to make your profile!')

def setup(client):
    client.add_cog(Setup(client))