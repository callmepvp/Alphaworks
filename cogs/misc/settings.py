from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['setting'])
    async def settings(self, ctx, process = None, arg = None, toggle = None):
        #Process - None or "Change"
        #Arg - None or the setting to change
        #Toggle - The state of the setting

        #Settings - 
        #Public Profile (Anyone can view your equipment and inventory)
        #Language (Change the local language)
        #Trading (switch trading requests on or off)
        #Pmarket notifs (switch dm notifs on or off)
        #LB notifs

        #Maybe -
        #Guild (switch guild invites on or off)
        
        #Server Admin Commands -
        #Prefix (Change the server-wide prefix for the bot)

        pass

def setup(client):
    client.add_cog(Settings(client))