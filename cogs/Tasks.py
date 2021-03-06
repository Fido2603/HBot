import datetime
import random
import discord
from discord.ext import tasks, commands
import PrunusDB
from Util import logger


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.treelanderOfTheDay.start()

    def cog_unload(self):
        self.treelanderOfTheDay.cancel()

    @tasks.loop(seconds=60.0)
    async def treelanderOfTheDay(self):
        logger.logDebug("Treelander of the day Task")
        totD_id = PrunusDB.get_currentTreelanderOfTheDay()
        logger.logDebug("totD_id: " + totD_id)
        dt = datetime.datetime.now()
        logger.logDebug("dt: " + str(dt))
        if totD_id == "" or len(totD_id) == 0:
            logger.logDebug("no treelander of the day found")
            await self.newTreelanderOfTheDay(totD_id)
        elif dt.time() > datetime.time(12):
            logger.logDebug("it is over 12:00. Time now is: " + str(datetime.datetime.now().time()))
            treelanderOfTheDayTime = PrunusDB.get_currentTreelanderOfTheDayTime()
            logger.logDebug(treelanderOfTheDayTime)
            current_treelanderOfTheDay_TimeStamp = datetime.datetime.strptime(str(treelanderOfTheDayTime),
                                                                              "%Y-%m-%d %H:%M:%S.%f")
            logger.logDebug("Breakpoint 1")
            logger.logDebug(str(current_treelanderOfTheDay_TimeStamp))

            #timeElapsed = dt - current_treelanderOfTheDay_TimeStamp
            #logging.logDebug(timeElapsed)
            #timeElapsed_seconds = timeElapsed.total_seconds()
            #logging.logDebug(timeElapsed_seconds)
            #timeElapsed_hours = divmod(timeElapsed.total_seconds(), 3600)[0]
            #logging.logDebug(timeElapsed_hours)
            #if timeElapsed_hours > 20:
                #logging.logDebug("it was now over 20 hours ago")
            logger.logDebug(str(dt.date()) + " - " + str(current_treelanderOfTheDay_TimeStamp.date()))
            if dt.date() != current_treelanderOfTheDay_TimeStamp.date():
                logger.logDebug("It happened yesterday haha")
                await self.newTreelanderOfTheDay(totD_id)

    @treelanderOfTheDay.before_loop
    async def before_loop(self):
        logger.logDebug('waiting...')
        await self.bot.wait_until_ready()

    async def newTreelanderOfTheDay(self, totD_id=""):
        # guild: 221996778092888065
        # role: 638480387403677727
        # channel: 221998962247204864
        # emote: 584529307402240000
        guild_id = 221996778092888065
        role_id = 638480387403677727
        risings_role_id = 530778945105428501
        channel_id = 665922203686273054
        emote_id = 584529307402240000

        logger.logDebug('newtreelanderoftheday')
        logger.logDebug("nice totD_id: " + totD_id)
        treeland = await self.bot.fetch_guild(guild_id)
        logger.logDebug('got treeland')
        treelanderoftheday_role = treeland.get_role(role_id)
        logger.logDebug('got role')
        treelanders = []
        async for member in treeland.fetch_members(limit=None):
            if risings_role_id in [role.id for role in member.roles]:
                treelanders.append(member)
        logger.logDebug('got members of rising role')

        # Do random seed with date and time
        random.seed(int(datetime.datetime.now().strftime("%d%m%Y%H%M%S%f")))

        while True:
            logger.logDebug('while loop')
            user = random.choice(treelanders)
            logger.logDebug('got random user: ' + user.name)
            if user.bot:
                logger.logDebug("user is a bot")
            elif totD_id == "" or len(totD_id) == 0:
                logger.logDebug('todays treelander id is 0, found new treelander of the day')
                break
            elif totD_id == str(user.id):
                logger.logDebug("User is already treelander of the day")
            else:
                logger.logDebug('new treelander of the day found!')
                break
            logger.logDebug("help")
        logger.logDebug('out of while loop')
        try:
            await user.add_roles(treelanderoftheday_role, reason="Treelander of the Day!")
        except Exception as e:
            await logger.log("Error trying to add the treelander of the day role: " + str(e), self.bot)
            return
        logger.logDebug('added role')
        await PrunusDB.add_TreelanderOfTheDay(user.id, user.name + user.discriminator, self.bot)
        if totD_id != "" and len(totD_id) != 0:
            logger.logDebug("totD_id is not empty, removing role")
            totD = await treeland.fetch_member(int(totD_id))
            if totD is not None:
                logger.logDebug("user is not null")
                logger.logDebug("got user: " + totD.name)
                try:
                    await totD.remove_roles(treelanderoftheday_role, reason="No longer the Treelander of the Day!")
                except Exception as e:
                    await logger.log("Error trying to remove the treelander of the day role: " + str(e), self.bot)
                    return
                logger.logDebug('removed role')
            else:
                logger.logDebug("Member is null")
            PrunusDB.remove_TreelanderOfTheDay(user.id, True) # Removes Treelander of the Day status from everyone
                                                              # BUT the user who got it today!
        logger.logDebug("sending embed")

        channel = self.bot.get_channel(channel_id)

        emojis = self.bot.emojis
        emote = u"\U0001F333"
        for emoji in emojis:
            if emoji.id == emote_id:
                emote = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                break

        embed = discord.Embed(title="New Treelander of the Day!",
                              color=discord.Color.from_rgb(22, 198, 12), timestamp=datetime.datetime.utcnow(),
                              description=emote + " " + user.name + " is now the Treelander of the Day! Congrats!")
        embed.set_footer(text="New Treelander of the Day",
                         icon_url="https://cdn.discordapp.com/attachments/513770658589704204/588464009217310771/Treeland2.gif")
        embed.set_thumbnail(url=user.avatar_url)
        await channel.send(content="Congratulations, <@" + str(
                                  user.id) + ">!", embed=embed)
        await logger.log(
            "A member just became Treelander of the Day... %s#%s" % (user.name, user.discriminator),
            self.bot, "INFO")


def setup(bot):
    bot.add_cog(Tasks(bot))
