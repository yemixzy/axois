import discord, subprocess, sys, time, os, colorama, base64, codecs, datetime, io, random, numpy, datetime, smtplib, string, ctypes, youtube_dl, typing, re, httpx
import urllib.parse, urllib.request, re, json, requests,aiohttp, asyncio, functools, logging
from datetime import date
from multiprocessing import Process
from discord.ext import commands
from discord.utils import get
from urllib.parse import urlencode
from colorama import Fore
from sty import RgbFg, Style, bg, ef, fg, rs
if sys.platform == "win32":
    from win10toast import ToastNotifier

data = json.load(open('config.json', encoding='utf-8'))

usertoken = data['bottoken']
alttoken = data['alttoken']
maintoken = data['token']
discord_password = data['password']
BOT_PREFIX = data['prefix']
stream_url = data['stream_url']
start_time = datetime.datetime.utcnow()
bot = commands.Bot(command_prefix=BOT_PREFIX)
bitly_key = ''
nitro_sniper = None
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
ns_url = data['nitro_webhook_url']
giveaway_entries = []
giveaway_msg_id = None

nitroRegex = re.compile('(discord.com/gifts/|discordapp.com/gifts/|discord.gift/)([a-zA-Z0-9]+)')
cc_digits = {
    'american express': '3',
    'visa': '4',
    'mastercard': '5'
}

def embed_timestamp():
    if data['footer_timestamp']:
        return date.datetime.utcfromtimestamp(time.time())
    else:
        return discord.embeds.EmptyEmbed

async def is_owner(ctx):
    return ctx.author.id == 699407455926485064

def drone_startup(pos, alttoken):
    drone = discord.Client()
    time.sleep(2)
    print(f'NitroSniper: {pos + 1}')

    def wsend(paylod):
        requests.post(ns_url, json=paylod)
        
    @drone.event
    async def on_ready():
        print("Sniper: " + drone.user.name + "#" + drone.user.discriminator + "\n")


    @drone.event
    async def on_message(msg):
        try:
            if json.load(open('config.json', encoding='utf-8'))['nitro_sniper'] == True and nitroRegex.search(msg.content):
                code = nitroRegex.search(msg.content).group(2)
                if len(code) >= 16:
                    async with httpx.AsyncClient() as client:    
                        start_time = time.time()
                        result = await client.post(f'https://canary.discordapp.com/api/v8/entitlements/gift-codes/{code}/redeem', json={'channel_id': msg.channel.id}, headers={'authorization': json.load(open('config.json', encoding='utf-8'))['bottoken'], 'user-agent': user_agent})
                        elapsed = '%.3fs' % (time.time() - start_time)
                    if 'This gift has been redeemed already' in str(result.content):
                        print('[!] Already redeemed | ' + elapsed)
                        paylod = {'content': 'Code Already redeemed | ' + elapsed}
                        wsend(paylod)
                    elif 'nitro' in str(result.content):
                        print('[+] Successfully redeemed | ' + elapsed)
                        paylod = {'content': 'Successfully redeemed | ' + elapsed}
                        wsend(paylod)
                    elif 'Unknown Gift Code' in str(result.content):
                        print('[-] Unknown/Invalid | ' + elapsed)
                        paylod = {'content': 'Unknown/Invalid | ' + elapsed}
                        wsend(paylod)
                else:
                    pass
        except Exception:
            print("something went wrong")
            pass

    drone.run(alttoken)

@bot.event
async def on_ready(self):
    os.system('')
    print("Logged in as: " + self.user + "\n")

@bot.command()
async def about(ctx):
    embed = discord.Embed(title="About the bot", description="Its a little Selfbot", color=0x00ffff)
    embed.add_field(name="Created with:", value="discord.py-self", inline=False)
    embed.add_field(name="Created by:", value="axois#0001", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def memberboost(ctx):
    await ctx.send('https://discord.gg/3Ynqwcanjr')

@bot.command(pass_context=True, aliases=['j', 'joi'])
@commands.check(is_owner)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Successfully joined {channel}")


@bot.command(pass_context=True, aliases=['l', 'lea'])
@commands.check(is_owner)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Successfully leaved {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")


@bot.command(pass_context=True, aliases=['p', 'pla'])
@commands.check(is_owner)
async def play(ctx, *, url: str):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send("Loading...")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'auto',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.50

    nname = name.rsplit("-", 2)
    #await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")
    
@bot.command(pass_context=True, aliases=['tc'])
@commands.check(is_owner)
async def create_tc(ctx, message):
    guild = ctx.message.guild
    await guild.create_text_channel(message)
    print("Successfully text channel created!")

@bot.command(pass_context=True, aliases=['vc'])
@commands.check(is_owner)
async def create_vc(ctx, message):
    guild = ctx.message.guild
    await guild.create_voice_channel(message)
    print("Successfully voice channel created!")
    
@bot.command(pass_context=True)
@commands.check(is_owner)
async def stream(ctx, *, message):
    stream = discord.Streaming(
        name=message,
        url=stream_url, 
    )
    await bot.change_presence(activity=stream)
    print("Activity successfully set to stream")
    
@bot.command(pass_context=True)
@commands.check(is_owner)
async def game(ctx, *, message):
    game = discord.Game(
        name=message
    )
    await bot.change_presence(activity=game)
    print("Activity successfully set to playing")
    
@bot.command(pass_context=True)
@commands.check(is_owner)
async def listening(ctx, *, message):
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=message, 
        ))
    print("Activity successfully set to listening")
       
@bot.command(pass_context=True)
@commands.check(is_owner)
async def watching(ctx, *, message):
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=message
        ))
    print("Activity successfully set to watching")
    
@bot.command()
@commands.check(is_owner)
async def status(ctx):
    await ctx.send('Alles läuft gut und ich bin einsatzbereit!')

@bot.command()
@commands.check(is_owner)
async def lesbian(ctx):
    r = requests.get("https://nekos.life/api/v2/img/les")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['url'])
    await ctx.send(embed=em)

@bot.command()
@commands.check(is_owner)
async def cum(ctx):
    r = requests.get("https://nekos.life/api/v2/img/cum")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['url'])
    await ctx.send(embed=em) 

@bot.command()
@commands.check(is_owner)
async def anal(ctx):
    r = requests.get("https://nekos.life/api/v2/img/anal")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['url'])
    await ctx.send(embed=em) 
    
@bot.command()
@commands.check(is_owner)
async def boobs(ctx):
    r = requests.get("https://nekos.life/api/v2/img/boobs")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['url'])
    await ctx.send(embed=em) 

@bot.command()
@commands.check(is_owner)
async def wallpaper(ctx):
    r = requests.get("https://nekos.life/api/v2/img/wallpaper")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['url'])
    await ctx.send(embed=em)   
    
@bot.command()
@commands.check(is_owner)
async def uptime(ctx):
    uptime = datetime.datetime.utcnow() - start_time
    uptime = str(uptime).split('.')[0]
    await ctx.send(f'`'+uptime+'`') 
    
@bot.command()
@commands.check(is_owner)
async def spam(ctx, amount: int, *, message):   
    for _i in range(amount):
        await ctx.send(message)

@bot.command(aliases=['shorteen'])
@commands.check(is_owner)
async def bitly(ctx, *, link):
    if bitly_key == '':
        print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}Bitly API key has not been set"+Fore.RESET)
    else:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api-ssl.bitly.com/v3/shorten?longUrl={link}&domain=bit.ly&format=json&access_token={bitly_key}') as req:
                    r = await req.read()
                    r = json.loads(r) 
            new = r['data']['url']
            em = discord.Embed()
            em.add_field(name='Shortened link', value=new, inline=False)
            await ctx.send(embed=em)
        except Exception as e:
            print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}"+Fore.RESET)
        else:
            print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{req.text}"+Fore.RESET)
    
@bot.command(name='view', aliases=['view-bot', 'viewbot'])
@commands.check(is_owner)
async def _ebay_view(ctx, url, views: int):
    start_time = datetime.datetime.now()
    def EbayViewer(url, views):
        headers = {
           "User-Agent": user_agent,
           "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }        
        for _i in range(views):
            requests.get(url, headers=headers)
    EbayViewer(url, views)
    elapsed_time = datetime.datetime.now() - start_time
    em = discord.Embed(title='ViewBot')
    em.add_field(name='Views sent', value=views, inline=False)
    em.add_field(name='Elapsed time', value=elapsed_time, inline=False)
    await ctx.send(embed=em)
    
@bot.command(aliases=['pfp', 'avatar'])
@commands.check(is_owner)
async def av(ctx, *, user: discord.Member=None):
    format = "gif"
    user = user or ctx.author
    if user.is_avatar_animated() != True:
        format = "png"
    avatar = user.avatar_url_as(format = format if format != "gif" else None)
    async with aiohttp.ClientSession() as session:
        async with session.get(str(avatar)) as resp:
            image = await resp.read()
    with io.BytesIO(image) as file:
        await ctx.send(file = discord.File(file, f"Avatar.{format}"))
        
@bot.command(aliases=['ri', 'role'])
@commands.check(is_owner)
async def roleinfo(ctx, *, role: discord.Role): # b'\xfc'
    await ctx.message.delete()
    guild = ctx.guild
    since_created = (ctx.message.created_at - role.created_at).days
    role_created = role.created_at.strftime("%d %b %Y %H:%M")
    created_on = "{} ({} days ago)".format(role_created, since_created)
    users = len([x for x in guild.members if role in x.roles])
    if str(role.colour) == "#000000":
        colour = "default"
        color = ("#%06x" % random.randint(0, 0xFFFFFF))
        color = int(colour[1:], 16)
    else:
        colour = str(role.colour).upper()
        color = role.colour
    em = discord.Embed(colour=color)
    em.set_author(name=f"Name: {role.name}"
    f"\nRole ID: {role.id}")
    em.add_field(name="Users", value=users)
    em.add_field(name="Mentionable", value=role.mentionable)
    em.add_field(name="Hoist", value=role.hoist)
    em.add_field(name="Position", value=role.position)
    em.add_field(name="Managed", value=role.managed)
    em.add_field(name="Colour", value=colour)
    em.add_field(name='Creation Date', value=created_on)
    await ctx.send(embed=em)
    
@bot.command(aliases=['changehypesquad'])
@commands.check(is_owner)
async def hypesquad(ctx, house): # b'\xfc'
    await ctx.message.delete()
    request = requests.Session()
    headers = {
      'Authorization': usertoken,
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36'
    }    
    if house == "bravery":
      payload = {'house_id': 1}
    elif house == "brilliance":
      payload = {'house_id': 2}
    elif house == "balance":
      payload = {'house_id': 3}
    elif house == "random":
        houses = [1, 2, 3]
        payload = {'house_id': random.choice(houses)}
    try:
        request.post('https://discordapp.com/api/v6/hypesquad/online', headers=headers, json=payload, timeout=10)
    except Exception as e:
        print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}"+Fore.RESET)
        
@bot.command()
@commands.check(is_owner)
async def dm(ctx, user : discord.Member, *, message):
    user = bot.get_user(user.id)
    if ctx.author.id == bot.user.id:
        return
    else:
        try:
            await user.send(message) 
        except:
            pass
            
@bot.command()
@commands.check(is_owner)
async def purge(ctx, amount: int):
    async for message in ctx.message.channel.history(limit=amount).filter(lambda m: m.author == bot.user).map(lambda m: m):
        try:
           await message.delete()
        except:
            pass
            
@bot.command()
@commands.check(is_owner)
async def purgeall(ctx, amount: int):
    async for message in ctx.message.channel.history(limit=amount):
        try:
           await message.delete()
        except:
            pass

@bot.command()
@commands.check(is_owner)
async def server(ctx):
    print('Servers connected to:')
    await ctx.send('Servers connected to: ')
    for server in bot.guilds:
        print(server.name)
        await ctx.send(server.name)

@bot.command()
@commands.check(is_owner)
async def ascii(ctx, *, text):
    r = requests.get(f'http://artii.herokuapp.com/make?text={urllib.parse.quote_plus(text)}').text
    if len('```'+r+'```') > 2000:
        return
    await ctx.send(f"```{r}```")

@bot.command(aliases=['bitcoin'])
@commands.check(is_owner)
async def btc(ctx):
    r = requests.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR')
    r = r.json()
    usd = r['USD']
    eur = r['EUR']
    em = discord.Embed(description=f'USD: `{str(usd)}$`\nEUR: `{str(eur)}€`')
    em.set_author(name='Bitcoin', icon_url='https://cdn.pixabay.com/photo/2013/12/08/12/12/bitcoin-225079_960_720.png')
    await ctx.send(embed=em)
    
@bot.command(name='first-message', aliases=['firstmsg', 'fm', 'firstmessage'])
@commands.check(is_owner)
async def _first_message(ctx, channel: discord.TextChannel = None): 
    if channel is None:
        channel = ctx.channel
    first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]
    embed = discord.Embed(description=first_message.content)
    embed.add_field(name="First Message", value=f"[Jump]({first_message.jump_url})")
    await ctx.send(embed=embed)

@bot.command(aliases=['js'])
@commands.check(is_owner)
async def joinserver(ctx, invite_url):
    code = re.findall(r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)(/?[a-zA-Z0-9]+/?)", invite_url)
    if not code:
        return await ctx.send("Invalid invite url")
    headers = { 'authorization': usertoken }
    code = code[0].strip('/')
    join = requests.post('https://discord.com/api/v6/invites/%s' % (code), headers = headers)
    if not join.status_code == 200:
        return await ctx.send("Could not join server")
    else:
        return await ctx.send("Succesfully joined server!")

@bot.command(aliases=['ls'])
@commands.check(is_owner)
async def leaveserver(ctx, guild: typing.Union[int, str]=None):
    if guild is None: # Leave guild the command was used in
        await ctx.guild.leave()
    elif isinstance(guild, int):
        guild = bot.get_guild(guild)
        await guild.leave()
    elif isinstance(guild, str):
        guild = discord.utils.find(lambda g: g.name.lower() == guild.lower(), bot.guilds)
        if guild is None:
            return await ctx.send("No guild found by that name")
        await guild.leave()
    return await ctx.author.send(f"Successfully left guild **{ctx.guild.name}**")

@bot.command(name="stealpfp")
async def stealpfp(ctx, user: discord.User):
        await bot.user.edit(avatar = bytes(requests.get(user.avatar_url).content), password = discord_password)
        await ctx.send('Profile Picture was set.')

@bot.command(name="tokeninfo")
async def tokeninfo(ctx, token):   
    try:
        await ctx.message.delete
    except:
        pass
    try:
        headers = {
                'Authorization': token,
                'Content-Type': 'application/json',
                'User-Agent': user_agent
        }

        res = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)

        if res.status_code == 200: # code 200 if valid

                # user info
                res_json = res.json()

                user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
                user_id = res_json['id']
                avatar_id = res_json['avatar']
                avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.gif'
                phone_number = res_json['phone']
                email = res_json['email']
                mfa_enabled = res_json['mfa_enabled']
                flags = res_json['flags']
                verified = res_json['verified']

                creation_date = datetime.utcfromtimestamp(((int(user_id) >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')

                has_nitro = False
                res = requests.get('https://discordapp.com/api/v9/users/@me/billing/subscriptions', headers=headers)
                nitro_data = res.json()
                has_nitro = bool(len(nitro_data) > 0)
                if has_nitro:
                    d1 = datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    d2 = datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    days_left = abs((d2 - d1).days)

                # billing info
                billing_info = []
                for x in requests.get('https://discordapp.com/api/v9/users/@me/billing/payment-sources', headers=headers).json():
                    y = x['billing_address']
                    name = y['name']
                    address_1 = y['line_1']
                    address_2 = y['line_2']
                    city = y['city']
                    postal_code = y['postal_code']
                    state = y['state']
                    country = y['country']

                    if x['type'] == 1:
                        cc_brand = x['brand']
                        cc_first = cc_digits.get(cc_brand)
                        cc_last = x['last_4']
                        cc_month = str(x['expires_month'])
                        cc_year = str(x['expires_year'])
                        
                        data = {
                            'Payment Type': 'Credit Card',
                            'Valid': not x['invalid'],
                            'CC Holder Name': name,
                            'CC Brand': cc_brand.title(),
                            'CC Number': ''.join(z if (i + 1) % 2 else z + ' ' for i, z in enumerate((cc_first if cc_first else '*') + ('*' * 11) + cc_last)),
                            'CC Exp. Date': ('0' + cc_month if len(cc_month) < 2 else cc_month) + '/' + cc_year[2:4],
                            'Address 1': address_1,
                            'Address 2': address_2 if address_2 else '',
                            'City': city,
                            'Postal Code': postal_code,
                            'State': state if state else '',
                            'Country': country,
                            'Default Payment Method': x['default']
                        }

                    elif x['type'] == 2:
                        data = {
                            'Payment Type': 'PayPal',
                            'Valid': not x['invalid'],
                            'PayPal Name': name,
                            'PayPal Email': x['email'],
                            'Address 1': address_1,
                            'Address 2': address_2 if address_2 else '',
                            'City': city,
                            'Postal Code': postal_code,
                            'State': state if state else '',
                            'Country': country,
                            'Default Payment Method': x['default']
                        }

                    billing_info.append(data)

                print('Basic Information')
                print('-----------------')
                print(f'    {Fore.RESET}Username               {Fore.GREEN}{user_name}')
                print(f'    {Fore.RESET}User ID                {Fore.GREEN}{user_id}')
                print(f'    {Fore.RESET}Creation Date          {Fore.GREEN}{creation_date}')
                print(f'    {Fore.RESET}Avatar URL             {Fore.GREEN}{avatar_url if avatar_id else ""}')
                print(f'    {Fore.RESET}Token                  {Fore.GREEN}{token}')
                print(f'{Fore.RESET}\n')
                
                print('Nitro Information')
                print('-----------------')
                print(f'    {Fore.RESET}Nitro Status           {Fore.MAGENTA}{has_nitro}')
                if has_nitro:
                    print(f'    {Fore.RESET}Expires in             {Fore.MAGENTA}{days_left} day(s)')
                print(f'{Fore.RESET}\n')


                print('Contact Information')
                print('-------------------')
                print(f'    {Fore.RESET}Phone Number           {Fore.YELLOW}{phone_number if phone_number else ""}')
                print(f'    {Fore.RESET}Email                  {Fore.YELLOW}{email if email else ""}')
                print(f'{Fore.RESET}\n')

                if len(billing_info) > 0:
                    print('Billing Information')
                    print('-------------------')
                    if len(billing_info) == 1:
                        for x in billing_info:
                            for key, val in x.items():
                                if not val:
                                    continue
                                print(Fore.RESET + '    {:<23}{}{}'.format(key, Fore.CYAN, val))
                    else:
                        for i, x in enumerate(billing_info):
                            title = f'Payment Method #{i + 1} ({x["Payment Type"]})'
                            print('    ' + title)
                            print('    ' + ('=' * len(title)))
                            for j, (key, val) in enumerate(x.items()):
                                if not val or j == 0:
                                    continue
                                print(Fore.RESET + '        {:<23}{}{}'.format(key, Fore.CYAN, val))
                            if i < len(billing_info) - 1:
                                print(f'{Fore.RESET}\n')
                    print(f'{Fore.RESET}\n')

                print('Account Security')
                print('----------------')
                print(f'    {Fore.RESET}2FA/MFA Enabled        {Fore.BLUE}{mfa_enabled}')
                print(f'    {Fore.RESET}Flags                  {Fore.BLUE}{flags}')
                print(f'{Fore.RESET}\n')

                print('Other')
                print('-----')
                print(f'    {Fore.RESET}Email Verified         {Fore.RED}{verified}')

        elif res.status_code == 401: # code 401 if invalid
                print(f'{Fore.RED}[-] {Fore.RESET}Invalid token')

        else:
                print(f'{Fore.RED}[-] {Fore.RESET}An error occurred while sending request')
    except:
            print(f'{Fore.RED}[-] {Fore.RESET}An error occurred while getting request')
    else:
        print(f'Usage: python {sys.argv[0]} [token]')

@bot.command(name="giveaway")
async def giveaway(ctx, time: int, winners: int, *, prize: str):
        global giveaway_msg_id
        try:
            embed = discord.Embed()
            embed.add_field(name=f'__🎉 Prize__', value=f'{prize}', inline=False)
            embed.add_field(name=f'__⏱ Time in Seconds__', value=f'{time}s', inline=False)
            embed.add_field(name=f'__🎁 Winners__', value=f'{winners}', inline=False)
            embed.set_thumbnail(url='')
            embed.set_footer(text='axois Test Client', icon_url='')
            embed.set_author(name='axois#0001', icon_url='', url='')
            msg = await ctx.send(embed=embed)
            giveaway_msg_id = msg.id
            await msg.add_reaction('🎉')
            await asyncio.sleep(time)
            giveaway_entries.pop(giveaway_entries.index(bot.user.id))
            try:
                if winners == 1:
                    winner = random.choice(giveaway_entries)
                    await ctx.send(f"<@{winner}> has won the giveaway for **{prize}**! {msg.jump_url}")
                else:
                    users_who_won = []
                    if len(giveaway_entries) < winners:
                        await ctx.send(f"Could not determine winners for **{prize}**! {msg.jump_url}")
                        return
                    for j in range(0, winners):
                        def determine_winner():
                            new_winner = giveaway_entries[random.randint(0, len(giveaway_entries))]
                            if new_winner not in users_who_won:
                                users_who_won.append(new_winner)
                            else:
                                determine_winner()
                        
                        determine_winner()
                                
                    await ctx.send(f", ".join([f"<@{user_id}>" for user_id in users_who_won]) + f" have won the giveaway for **{prize}**! {msg.jump_url}")
                            
            except Exception:
                print("something went wrong")
                pass
                await ctx.send(f"Could not determine winner for **{prize}**! {msg.jump_url}")
            giveaway_msg_id = None
            giveaway_entries.clear()
        except Exception:
            print("something went wrong")
            pass

def selfbot(test, maintoken):
    bot.run(maintoken)

if __name__ == '__main__':
    if sys.platform == "win32":
        toaster = ToastNotifier()
        os.system('color')
    if data['nitro_sniper'] == True:
        nitro_sniper_thread = Process(target=drone_startup, args=(0, alttoken,))
        nitro_sniper_thread.start()
    elif data['nitro_sniper'] == False:
        pass
    main_thread = Process(target=selfbot, args=(0, maintoken,))
    main_thread.start()
