from discord.ext import commands
import string

import json
from json import loads
from pathlib import Path

data = loads(Path("cogs/data/other/items.json").read_text())

class Item(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['i'])
    async def item(self, ctx, *, arg1 = None):
        #Usage: f!item > Shows usage and categories
        #f!item ITEM_NAME > Shows item info
        #f!item CATEGORY > Shows all items in that category (?)

        if arg1 == None:
            await ctx.send(f"This command shows info about every item in the bot. Currently there are **{len(data)}** items!" "\n" "*f!item ITEM_NAME for specifics!*")
        else:
            counter = 0
            for i in data:
                if arg1 == i:
                    counter += 1
                    message = []
                    
                    emoji = data[arg1][0]['emoji']
                    desc = data[arg1][0]['description']
                    location = data[arg1][0]['location']

                    itemType = data[arg1][0]['type']
                    rarity = data[arg1][0]['rarity']

                    message.append(f"Information about **{string.capwords(arg1)}** {emoji}" "\n")
                    message.append(f"{rarity} {itemType}" "\n" "\n")

                    message.append("⇒ *Description:*" "\n")
                    message.append(f"{desc}" "\n \n")

                    message.append("⇒ *Acquiring:*" "\n")
                    message.append(f"{location}")

                    await ctx.send(''.join(message))

                    #? Add statistics for each item at the bottom
                    #? Amount that has been foraged/farmed etc
                    #? Add amount of XP it gives, if its a forageable
                    
            if counter == 0:
                await ctx.send("Item not found!")

def setup(client):
    client.add_cog(Item(client))