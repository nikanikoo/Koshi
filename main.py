import json
import discord
import asyncio
import requests
import wikipedia
import os
import base64
import shutil
from io import BytesIO
from PIL import Image
from discord.ext import commands
import datetime, time
import platform, psutil
import random

## api.openweathermap.org
api_openw = "API TOKEN"

def get_prefix(client, message):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)

    guild_id = str(message.guild.id)
    if guild_id in prefixes:
        return prefixes[guild_id]
    else:
        prefixes[guild_id] = 'k!'  # Установка префикса по умолчанию для сервера
        with open("db/prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)  # Запись измененного словаря в JSON-файл
        return prefixes[guild_id]

client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
client.remove_command("help")

with open("db/counts.json", 'r') as f:
    command_counts = json.load(f)


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

start_time = datetime.datetime.utcnow()

async def get_time():
    loop = asyncio.get_running_loop()
    cde = await loop.run_in_executor(None, datetime.datetime.now)
    if cde.minute < 10:
        ts = f"{cde.day}.{cde.month}.{cde.year} {cde.hour}:0{cde.minute}"
        return ts
    ts = f"{cde.day}.{cde.month}.{cde.year} {cde.hour}:{cde.minute}"
    return ts

def get_uptime():
    delta_uptime = datetime.datetime.utcnow() - start_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptime = f"{days}d, {hours}h, {minutes}m, {seconds}s"
    return uptime

@client.event 
async def on_guild_join(guild):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)] = "k!"

    with open("db/prefixes.json", "w") as f:
        json.dump(prefixes, f)

@client.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, prefix='k!'):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("db/prefixes.json", "w") as f:
        json.dump(prefixes, f)

    await ctx.send(f"The prefix was changed to {prefix}")

@setprefix.error
async def setprefix_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

@client.event
async def on_message(msg):
    await client.process_commands(msg)

@client.event
async def on_ready():
    activity = discord.Game(name="Coming soon...", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)
    print("Koshi: I am ready!!")

@client.command()
async def ping(ctx):
    latency = round(client.latency * 1000)
    embed=discord.Embed(title="🏓 Pong!")
    embed.add_field(name="Client", value=f"{latency}ms")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def botinfo(ctx):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)
    pre = prefixes[str(ctx.guild.id)]

    embed=discord.Embed(title="🤖 Koshi information")
    embed.add_field(name="Prefix", value=pre)
    embed.add_field(name="Developer", value="nikor1")
    embed.add_field(name="Version", value="v0.1 08.07.23")
    embed.add_field(name="Discord.py", value="2.3.0")
    embed.add_field(name="Python", value="3.10.8")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def prefix(ctx):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    
    embed=discord.Embed(title="⚙️ Koshi Prefix")
    embed.add_field(name="Server Prefix", value=f'```{pre}```')
    embed.add_field(name="Default Prefix", value="```k!```")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def host(ctx):
    total_channels = 0
    for guild in client.guilds:
        total_channels += len(guild.channels)
    uname = platform.uname()
    startTime = time.time()
    uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
    svmem = psutil.virtual_memory()
    clientStats = f"```Servers    {len(client.guilds)}\nUsers      {len(client.users)}\nChannels   {total_channels}\nPing       {round(client.latency * 1000)}\nUptime     {get_uptime()}```"
    hostStats = f"```OS         {uname.system} {uname.version}\nCPU        {uname.processor}\nCores      {psutil.cpu_count(logical=True)}\nCPU Usage  {psutil.cpu_percent()}%\nRAM        {get_size(svmem.total)}\nRAM Usage  {get_size(svmem.used)}```"
    embed=discord.Embed(title="🖥 Koshi Statistics")
    embed.add_field(name="Client", value=clientStats)
    embed.add_field(name="Host", value=hostStats)
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@client.command()
async def cringe(ctx):
    shutil.copy2('db/counts.json', 'db/backups/counts_backup.json')
    user_id = str(ctx.author.id)
    if user_id not in command_counts:
        command_counts[user_id] = {'cringe': 0}

    if 'cringe' not in command_counts[user_id]:
        command_counts[user_id]['cringe'] = 0

    command_counts[user_id]['cringe'] += 1

    with open('db/counts.json', 'w') as f:
        json.dump(command_counts, f, indent=4)
    embed=discord.Embed(title="🤢 Cringe", description=f"{ctx.author.display_name} cringed 🤮")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def flip(ctx):
    result = random.choice(['🌕 ', '🌑 '])
    embed=discord.Embed(title=f"{result} Coinflip", description=f"The coin landed on **{result}**!")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    embed=discord.Embed(title=f"🎲 Roll Dice ({sides})", description=f"The dice rolled **{result}**!")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        result = random.randint(1, 6)
        embed=discord.Embed(title=f"🎲 Roll Dice (6)", description=f"The dice rolled **{result}**!")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

@client.command()
async def avatar(ctx, member: discord.Member=None):
    if not member:
        member = ctx.message.author
    userAvatar = member.avatar.url
    embed=discord.Embed(title=f"{member.display_name}`s avatar")
    embed.set_image(url=userAvatar)
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@avatar.error
async def avatar_error(ctx, error):
    if isinstance(error, commands.errors.MemberNotFound):
        member = ctx.message.author
        userAvatar = member.avatar.url
        embed=discord.Embed(title=f"{member.display_name}`s avatar")
        embed.set_image(url=userAvatar)
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

@client.command()
async def fap(ctx, member: discord.Member=None):
    shutil.copy2('db/counts.json', 'db/backups/counts_backup.json')
    user_id = str(ctx.author.id)
    if user_id not in command_counts:
        command_counts[user_id] = {'fap': 0}

    if 'fap' not in command_counts[user_id]:
        command_counts[user_id]['fap'] = 0

    command_counts[user_id]['fap'] += 1

    with open('db/counts.json', 'w') as f:
        json.dump(command_counts, f, indent=4)

    if not member:
        member = ctx.message.author
        embed = discord.Embed(title=f"🍆 {member.display_name} fapping")
        embed.set_image(url="https://images-ext-1.discordapp.net/external/CJL4dZW3Ot195PHmYw1KC5QkLvRQ2B58UcGlelZWgsc/https/i.gifer.com/7DnT.gif")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return
    if member:
        embed = discord.Embed(title=f"🍆 {ctx.author.display_name} fapping to {member.display_name}")
        embed.set_image(url="https://images-ext-1.discordapp.net/external/CJL4dZW3Ot195PHmYw1KC5QkLvRQ2B58UcGlelZWgsc/https/i.gifer.com/7DnT.gif")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return
@fap.error
async def fap_error(ctx, error):
    if isinstance(error, commands.errors.MemberNotFound):
        content = error.argument
        embed = discord.Embed(title=f"🍆 {ctx.author.display_name} fapping to {content}")
        embed.set_image(url="https://images-ext-1.discordapp.net/external/CJL4dZW3Ot195PHmYw1KC5QkLvRQ2B58UcGlelZWgsc/https/i.gifer.com/7DnT.gif")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return


@client.command()
async def profile(ctx, member: discord.Member=None):
    shutil.copy2('db/bios.json', 'db/backups/bios_backup.json')
    shutil.copy2('db/counts.json', 'db/backups/counts_backup.json')
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    if not member:
        user_id = str(ctx.author.id)
        if user_id not in command_counts:
            command_counts[user_id] = {'fap': 0, 'cringe': 0}
            
        if 'fap' not in command_counts[user_id]:
            command_counts[user_id]['fap'] = 0

        if 'cringe' not in command_counts[user_id]:
            command_counts[user_id]['cringe'] = 0

        with open('db/counts.json', 'w') as f:
            json.dump(command_counts, f, indent=4)

        with open('db/bios.json', 'r') as f:
            bios = json.load(f)
        if str(user_id) in bios:
            biography = bios[str(user_id)]
        else:
            biography = f"To add your bio, use {pre}bio"

        embed = discord.Embed(title=f"{ctx.message.author.display_name} Statistic", description=f"```{biography}```")
        embed.add_field(name="Commands Counts", value=f"🍆 Fap: {command_counts[user_id]['fap']}\n🤮 Cringe: {command_counts[user_id]['cringe']}")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return
        
    if member:
        user_id = str(member.id)
        if user_id not in command_counts:
            command_counts[user_id] = {'fap': 0, 'cringe': 0}

        if 'fap' not in command_counts[user_id] and 'cringe' not in command_counts[user_id]:
            command_counts[user_id]['fap'] = 0
            command_counts[user_id]['cringe'] = 0

        with open('db/counts.json', 'w') as f:
            json.dump(command_counts, f, indent=4)
        with open('db/bios.json', 'r') as f:
            bios = json.load(f)
        if str(user_id) in bios:
            biography = bios[str(user_id)]
        else:
            biography = f"To add your bio, use {pre}bio"

        embed = discord.Embed(title=f"{member.display_name} Statistic", description=f"{biography}")
        embed.add_field(name="Commands Counts", value=f"🍆 Fap: {command_counts[user_id]['fap']}\n🤮 Cringe: {command_counts[user_id]['cringe']}")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return

@profile.error
async def profile_error(ctx, error):
    if isinstance(error, commands.errors.MemberNotFound):
        with open("db/prefixes.json", "r") as f:
            prefixes = json.load(f)

        pre = prefixes[str(ctx.guild.id)]
        user_id = str(ctx.author.id)
        if user_id not in command_counts:
            command_counts[user_id] = {'fap': 0, 'cringe': 0}
            
        if 'fap' not in command_counts[user_id]:
            command_counts[user_id]['fap'] = 0

        if 'cringe' not in command_counts[user_id]:
            command_counts[user_id]['cringe'] = 0

        with open('db/counts.json', 'w') as f:
            json.dump(command_counts, f, indent=4)

        with open('db/bios.json', 'r') as f:
            bios = json.load(f)
        if str(user_id) in bios:
            biography = bios[str(user_id)]
        else:
            biography = f"To add your bio, use {pre}bio"

        embed = discord.Embed(title=f"{ctx.message.author.display_name} Statistic", description=f"```{biography}```")
        embed.add_field(name="Commands Counts", value=f"🍆 Fap: {command_counts[user_id]['fap']}\n🤮 Cringe: {command_counts[user_id]['cringe']}")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        return



# @client.command()
# async def demo(ctx, *, message=''):
#     parts = message.split('/', 1)

#     if len(parts) == 2:
#         args1, args2 = parts
#     else:
#         args1 = parts[0]
#         args2 = ''

#     member = ctx.message.author.display_name
#     image = ctx.message
#     dem = Demotivator(args1, args2)
#     image_repl = None
#     if ctx.message.reference:
#         image_repl = await ctx.channel.fetch_message(ctx.message.reference.message_id)

#     if len(image.attachments) > 0:
#         p = requests.get(image.attachments[0].url)
#         out = open(rf'db/images/attachment_{member}.jpg', "wb")
#         out.write(p.content)
#         out.close()
#     elif image_repl:
#         p = requests.get(image_repl.attachments[0].url)
#         out = open(rf'db/images/attachment_{member}.jpg', "wb")
#         out.write(p.content)
#         out.close()
#     else:
#         await ctx.send("Please attach an image to the message or reply to a message with an image.")
#         return
#     dem.create(f'db/images/attachment_{member}.jpg', watermark='Koshi', use_url=False, arrange=False, result_filename=f'db/images/result_{member}.jpg', delete_file=False)
#     with open(f'db/images/result_{member}.jpg', 'rb') as f:
#         file = discord.File(f, filename=f'db/images/result_{member}.jpg')
#         await ctx.send(file=file)

@client.command()
async def weather(ctx, message=''):
    try:
        if len(message) == 0:
            await ctx.send("Enter a city")
            return

        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={message}&appid={api_openw}&units=metric')
        weather_data = response.json()
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description'].capitalize()
        wind_speed = weather_data['wind']['speed']
        embed = discord.Embed(title=f"☁ Weather in {message}", description=description)
        embed.add_field(name="Temperature", value=f"```{temp}°C```")
        embed.add_field(name="Feels like", value=f"```{feels_like} °C```")
        embed.add_field(name="Wind Speed", value=f"```{wind_speed} m/s```")
        embed.add_field(name="Humidity", value=f"```{humidity} %```")
        embed.add_field(name="\u200b", value=f"\u200b")
        embed.add_field(name="\u200b", value=f"\u200b")
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    except:
        await ctx.send(f"Error occurred while fetching weather data for {message}")
@client.command()
async def whois(ctx, message=''):
    if len(message) == 0:
        await ctx.send("Enter a IP")
        return
    response = requests.get(f'http://ip-api.com/json/{message}')
    json_data = json.loads(response.text)
    if json_data['status'] == 'fail':
        await ctx.send(f"Failed to retrieve IP address information")
    if json_data['status'] == 'success':

        embed = discord.Embed(title=f"📃 Information about Ip: *{json_data['query']}*")
        embed.add_field(name="County", value=f"```{json_data['country']}```")
        embed.add_field(name="City", value=f"```{json_data['city']}```")
        embed.add_field(name="ISP", value=f"```{json_data['isp']}```")
        
        embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

@client.command()
async def mping(ctx, message=''):
    parts = message.split(':', 1)
    if message == '':
        await ctx.send("Enter a IP")
        return
    if len(parts) == 2:
        args1, args2 = parts
    else:
        args1 = parts[0]
        args2 = '25565'
    response = requests.get(f'https://mcapi.us/server/status?ip={args1}&port={args2}')

    json_data = json.loads(response.text)
    error1 = json_data['error']

    if json_data['status'] == "error":
        embed = discord.Embed(title=f'🔴 *{message}* information:', description=f'{error1}')
        await ctx.send(embed=embed)
        return

    favicon_base64 = json_data['favicon']
    if json_data['motd']:
        embed = discord.Embed(title=f'🟢 *{message}* information:', description=f"```{json_data['motd']}```")
    if not json_data['motd']:
        embed = discord.Embed(title=f'🟢 *{message}* information:', description=f"```{json_data['motd_json']}```")
    duration_json = int(json_data['duration'])
    duration = duration_json / 1000000
    # Очищаем префикс "data:image/png;base64,"
    if favicon_base64:
        
        favicon_base64 = favicon_base64.replace('data:image/png;base64,', '')
        favicon_bytes = base64.b64decode(favicon_base64)
        favicon_image = Image.open(BytesIO(favicon_bytes))
        favicon_image.save(f'favicon{ctx.author.display_name}.png')
        with open(f"favicon{ctx.author.display_name}.png", "rb") as f:
            file = discord.File(f"favicon{ctx.author.display_name}.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")       

    embed.add_field(name=f"Players", value=f"```{json_data['players']['now']}/{json_data['players']['max']}```")
    embed.add_field(name=f"Version", value=f"```{json_data['server']['name']}```")
    embed.add_field(name="Duration", value=f"```{int(duration)} ms```")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    if not favicon_base64:
        await ctx.send(embed=embed)
        return
    await ctx.send(file=file, embed=embed)
    os.remove(f'favicon{ctx.author.display_name}.png')

@client.command()
async def help(ctx):
    with open("db/prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    embed = discord.Embed(title="📃 All Koshi commands", description=f"```{pre}help - Shows all bot commands\n{pre}avatar - Sends your or the mentioned user's avatar\n{pre}bio - Decorate your profile with a description\n{pre}botinfo - Koshi information (library, python version)\n{pre}cringe - Show everyone that you're a cringing\n{pre}demo - Demotivator generator\n{pre}flip - Heads and Tails\n{pre}fap - there will be no description\n{pre}host - Koshi server information\n{pre}mping - Ping of the Minecraft servers\n{pre}prefix - Shows what the current prefix and default is\n{pre}profile - Getting your own or another person's statistics\n{pre}roll - Random Random numbers (the default number is 6)\n{pre}setprefix - Change the prefix for this server (Available only to administrators)\n{pre}weather - Find out what the weather will be like in the city you want\n{pre}whois - Find out information about IP address```")
    embed.set_footer(text=f"{ctx.author.display_name} || {await get_time()}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@client.command()
async def bio(ctx, *, content=None):
    shutil.copy2('db/bios.json', 'db/backups/bios_backup.json')
    user = ctx.author
    with open('db/bios.json', 'r') as f:
        bios = json.load(f)
    bios[str(user.id)] = content
    if len(content) > 364:
        await ctx.send('The description has more than 364 characters!')
        return
    with open('db/bios.json', 'w') as f:
        json.dump(bios, f)
    await ctx.send('The biography has been set successfully')

client.run("DISCORD TOKEN")