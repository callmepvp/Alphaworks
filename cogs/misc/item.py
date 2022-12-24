from discord.ext import commands

class Item(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['i'])
    async def item(self, ctx):
        await ctx.send("Lets you look up every item in the future!")

def setup(client):
    client.add_cog(Item(client))