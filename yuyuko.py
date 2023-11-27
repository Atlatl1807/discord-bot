import discord
import random
import io
import aiohttp
from discord.ext import commands
from discord.commands import Option
from datetime import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv
import shlex
import subprocess


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="'", intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.event
async def on_ready():
    print("logged in")                      #prints message if bot is online
    try:
        await bot.sync_commands()
        print("synced commands")            #send message if commands are synced with the bot
    except Exception as e:
        print(e)                            #sends error message if commands are not being synced

@bot.slash_command(name="hello", description="checks if the slash command is working")   
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("working slash command")                    

@bot.slash_command(name="tiktok_archiver", description="archive tiktok")
@commands.has_permissions(manage_messages=True)
async def tiktok_archiver(interaction: discord.Interaction, username: Option(str, "tiktok username", required = False, default = ''), userid: Option(str, "manually enter tiktok userID, for deleted users", required = False, default = ''), year: Option(str, "year of tiktok", required = False, default = '')):               
    
    #7165852795429323777

    if username:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.tik.fail/v2/search/user?q=' + username) as r:
                if r.status == 200:
                    json_data = await r.json()
                    if json_data['success'] == False:
                        await interaction.response.send_message("ERROR: Unable to find id of " + username)
                        return
                    json_data = await r.json()
                    userid = json_data['data'][0]['uid']

    if userid: #probably a better way to do this lol
        await interaction.response.send_message("Archiving userID: " + userid)
    else:
        await interaction.response.send_message("ERROR: You didn't enter a username or userID, dumbass")
        return


    all_videoData = []
    #0 is videourl
    #1 is time
    #2 is title
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.tik.fail/v2/search?sortBy=date&userID=' + userid + '&count=10000') as r:
            if r.status == 200:
                json_data = await r.json()
                videoList = json_data['itemList']
                for iterator in reversed(range(len(json_data['itemList']))):
                    videoData = ['https://v2-videos-tiktok.files.fail/a1aeef7eeb52f2c9ce9c475ff95b94cf.mp4', 1534449033, 'hard times']
                    videoData[0] = videoList[iterator]['_tik']['video']
                    videoData[1] = videoList[iterator]['metadata']['create_time']
                    videoData[2] = videoList[iterator]['metadata']['desc']
                    all_videoData.append(videoData)
                    iterator += 1

    if len(all_videoData) == 0:
        await interaction.followup.send("ERROR: No videos found.")
        return

    for videoData in all_videoData:
        async for message in interaction.channel.history(limit=None):
            if message.attachments:
                if str(videoData[1]) + '.mp4' == message.attachments[0].filename:
                    if videoData[2]:
                        title = videoData[2]
                    else:
                        title = "[No title, ID: " + videoData[1] + "]"
                    print(title + " already in channel, not sending")
                    break
            if year:
                if datetime.utcfromtimestamp(videoData[1]).strftime('%Y') != year:
                    print(videoData[2] + " wrong year, not sending")   
                    break
        else:
            print("sending video " + videoData[2])   
            async with aiohttp.ClientSession() as session:
                async with session.get(videoData[0]) as resp:
                    data = io.BytesIO(await resp.read())
                    await interaction.channel.send(content=videoData[2] + "\n" + datetime.utcfromtimestamp(videoData[1]).strftime('%Y/%m/%d %H:%M:%S'), file=discord.File(data, str(videoData[1]) + '.mp4'))
    await interaction.channel.send('Cooking complete.')
                
@bot.command()
async def canthinkygif(ctx, cosplay=""):
    
    gifs = []
    gifs.append([bot.get_channel(1168547925564072017), "zero_two"])
    gifs.append([bot.get_channel(1168988603142131764), "ellie"])

    all_messages = []
    for channel in gifs:
        if channel[1] == cosplay:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)
            break
    else:
        for channel in gifs:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)
            
    message_to_send = random.choice(all_messages)

    await ctx.send(message_to_send.system_content)

@bot.slash_command(name="canthinkyvideo", description="send a video")
async def canthinkyvideo(ctx: discord.ApplicationContext, year: Option(str, "2022, 2023", required = False, default = ''), keyword: Option(str, "tag in description", required = False, default = '')):
    gifs = []
    gifs.append([bot.get_channel(1169328746763931658), "2023"])
    gifs.append([bot.get_channel(1169327829679357992), "2022"])

    all_messages = []
    for channel in gifs:
        if channel[1] == year:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)
            break
    else:
        for channel in gifs:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)

    filtered_messages = []
    for message in all_messages:
        if keyword in message.system_content:
            filtered_messages.append(message)

    if len(filtered_messages) == 0:
        filtered_messages = all_messages

    message_to_send = random.choice(filtered_messages) 
    max_tries = 10
    times = 1
    while(len(message_to_send.attachments) == 0):
        message_to_send = random.choice(filtered_messages)
        times += 1
        if (times > max_tries):
            ctx.response.send_message("ERROR: Unable to find any message with attachment (within " + str(max_tries) + " tries)!")
            return

    attachment = random.choice(message_to_send.attachments)
    
    await ctx.response.send_message(content=attachment.url)  

@bot.command()
async def canthinkyvideo(ctx):
    
    gifs = []
    gifs.append([bot.get_channel(1169328746763931658), "2023"])
    gifs.append([bot.get_channel(1169327829679357992), "2022"])

    all_messages = []
    for channel in gifs:
        async for message in channel[0].history(limit=None):
            all_messages.append(message)

    message_to_send = random.choice(all_messages) 
    max_tries = 10
    times = 1
    while(len(message_to_send.attachments) == 0):
        message_to_send = random.choice(all_messages)
        times += 1
        if (times > max_tries):
            ctx.send("ERROR: Unable to find any message with attachment (within " + str(max_tries) + " tries)!")
            return

    attachment = random.choice(message_to_send.attachments)
    message = attachment.url

    await ctx.send(message)

@bot.command()
async def canthinky(ctx):
    all_messages = []
    channel = bot.get_channel(1168236054168473702)
    async for message in channel.history(limit=None):
        all_messages.append(message)

    if (len(all_messages) == 0):
        ctx.send("ERROR: Unable to find any messages!")
        return

    message_to_send = random.choice(all_messages)
    max_tries = 10
    times = 1
    while(len(message_to_send.attachments) == 0):
        message_to_send = random.choice(all_messages)
        times += 1
        if (times > max_tries):
            ctx.send("ERROR: Unable to find any message with attachment (within " + str(max_tries) + " tries)!")
            return

    attachment = random.choice(message_to_send.attachments)

    await ctx.send(attachment.url)


@bot.slash_command(name="shutdown", description="restart the bot")
@commands.is_owner()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message(content="Shutting Down..", ephemeral=True)               
    exit()

@bot.slash_command(name="console", description="do a command")
@commands.is_owner()
async def console(ctx: discord.ApplicationContext, command: str):
    command=shlex.split(command)
    output = subprocess.Popen( command, stdout=subprocess.PIPE ).communicate()[0]
    await ctx.response.send_message(content=output, ephemeral=True)               

bot.run(TOKEN)   #replace TOKEN with your bots token if you are not working with a seperate file to protect the token put the token in quotation marks.
