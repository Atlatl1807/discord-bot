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

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

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
async def tiktok_archiver(interaction: discord.Interaction, tiktoker: str):               
    userID = 7165852795429323777
    

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.tik.fail/v2/search/user?q=' + tiktoker) as r:
            if r.status == 200:
                json_data = await r.json()
                if json_data['success'] == False:
                    await interaction.response.send_message("Unable to find " + tiktoker)
                    return
                json_data = await r.json()
                userID = json_data['data'][0]['uid']


    all_videoData = []
    #0 is videourl
    #1 is time
    #2 is title
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.tik.fail/v2/search?sortBy=date&userID=' + userID + '&count=10000') as r:
            if r.status == 200:
                json_data = await r.json()
                iterator = 0
                for key in json_data['itemList']:
                    videoData = ['https://v2-videos-tiktok.files.fail/a1aeef7eeb52f2c9ce9c475ff95b94cf.mp4', 1534449033, 'hard times']
                    videoData[0] = json_data['itemList'][iterator]['_tik']['video']
                    videoData[1] = json_data['itemList'][iterator]['metadata']['create_time']
                    videoData[2] = json_data['itemList'][iterator]['metadata']['desc']
                    all_videoData.append(videoData)
                    iterator += 1

    await interaction.response.send_message("Jesse, Time to cook.")

    for videoData in all_videoData:
        print("testing video " + videoData[2])   
        async for message in interaction.channel.history(limit=None):
            if message.attachments:
                if str(videoData[1]) + '.mp4' == message.attachments[0].filename:
                    print(videoData[2] + " already in channel, not sending")
                    break
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(videoData[0]) as resp:
                    data = io.BytesIO(await resp.read())
                    await interaction.channel.send(content=videoData[2] + "\n" + datetime.utcfromtimestamp(videoData[1]).strftime('%Y-%m-%d %H:%M:%S'), file=discord.File(data, str(videoData[1]) + '.mp4'))
    await interaction.channel.send('Cooking complete.')
                



@bot.slash_command(name="canthinky_gif", description="return a random gif")
async def canthinky_gif(interaction, cosplay: Option(str, "zero_two, ellie", required = False, default = '')):
    
    gifs = []
    gifs.append([bot.get_channel(1168547925564072017), "zero_two"])
    gifs.append([bot.get_channel(1168988603142131764), "ellie"])

    one_channel = False

    all_messages = []
    for channel in gifs:
        if channel[1] == cosplay:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)
            one_channel = True
            break

    if one_channel == False:
        for channel in gifs:
            async for message in channel[0].history(limit=None):
                all_messages.append(message)
            



    message_to_send = random.choice(all_messages)
    await interaction.response.send_message(message_to_send.system_content)

bot.run(TOKEN)   #replace TOKEN with your bots token if you are not working with a seperate file to protect the token put the token in quotation marks.