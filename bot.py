import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button, ButtonStyle
import sqlite3
from discord.utils import get
import datetime
import DiscordUtils
from youtubesearchpython import VideosSearch
# import discord_slash
# from disco.types.message import MessageEmbed



db = sqlite3.connect("bot_database.db")
cr = db.cursor()
EmojiLink = "0"
music = DiscordUtils.Music()

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = "!" ,intents=intents)
cog = commands.Cog

def read_token():
		with open("token.txt","r") as f:
				token = f.readline()
				return token

def get_bad_words():
	global Blocked_Words
	cr.execute("SELECT bad_word FROM bad_words")
	data = cr.fetchall()
	Blocked_Words = []
	for i in range(len(data)):
		Blocked_Words.append(data[i][0])
get_bad_words()

def get_id(user_name):
	cr.execute(f"SELECT id FROM users WHERE user_name = '{user_name}'")
	it = cr.fetchone()
	id = it[0]
	return id

def get_user_name(id):
	cr.execute(f"SELECT user_name FROM users WHERE id = '{id}'")
	user_ame = cr.fetchone()
	user_name = user_ame[0]
	return user_name

def fill():
	cr.execute("SELECT id FROM users")
	ID = cr.fetchall()
	return ID

@client.command()
async def lol(ctx):
	for i in range(len(fill())):
		l = fill()[i][0]

@client.event
async def on_ready():
		print(f"Bot logged in as {client.user}")
		DiscordComponents(client)

@client.command()
async def ping(ctx):
	await ctx.send((f'Pong! In {round(client.latency * 1000)}ms'))

@client.command()
async def button(ctx):
	await ctx.send(
			"this is a button test :smile:"
			,components=[[
				Button(style=ButtonStyle.blue,
				label="Button 1"),
				Button(style=ButtonStyle.red,
				label="Button 2")]])


	res = await client.wait_for("button_click")

	if res.channel == ctx.channel :
		await res.message.channel.send(EmojiLink)

def get_users_from_db():
	global users
	cr.execute("SELECT id FROM users")
	lol = cr.fetchall()
	users = []
	for i in range(len(lol)):
		users.append(lol[i][0])
get_users_from_db()

def get_user_XP_LVL(ig):
	cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{ig}'")
	xpdata = cr.fetchone()
	return xpdata

bad_commands = commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError, commands.CommandNotFound
@client.event
async def on_command_error(ctx, error):
	if isinstance(error,bad_commands):
		await ctx.channel.send(f'Command Not found')

@client.command(pass_context = True)
async def join(ctx):
	#if author is in channel
	if (ctx.author.voice):
		#if bot isnt in ANY channels
		voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
		if voice_client == None :
			channel = ctx.message.author.voice.channel
			await channel.connect()
		#if bot in channel
		else :
			#if in the SAME channel
			if (ctx.voice_client.channel.id) == (ctx.message.author.voice.channel.id) :
				await ctx.send("I am in the same voice channel")
			#if in ANOTHER channel
			elif (ctx.voice_client.channel.id) != (ctx.message.author.voice.channel.id) :
				await ctx.guild.voice_client.disconnect()
				channel = ctx.message.author.voice.channel
				await channel.connect()
	#if author isnt in ANY channels
	else :
		await ctx.send("You are not in a voice channel, you must be in a voice channnel to run this command!")
@client.command(pass_context = True)
async def leave(ctx) :
	if (ctx.voice_client) :
		await ctx.guild.voice_client.disconnect()
		await ctx.send("I left the voice channel")
	else :
		await ctx.send("I am not in a voice channel")

@client.command()
async def play(ctx,*,url):
	if not (ctx.voice_client):
		voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
		if voice_client == None :
			channel = ctx.message.author.voice.channel
			await channel.connect()
	player = music.get_player(guild_id = ctx.guild.id)
	if "https:" in url:
		url = url
	else:
		l = url
		video = VideosSearch(l,limit = 1)
		url = video.result()['result'][0]['link']
		
	if not player:
		player = music.create_player(ctx,fmmpeg_error_betterfix=True)
	if not ctx.voice_client.is_playing():
		await player.queue(url , search=True)
		song = await player.play()
		await ctx.send(f"Playing: {song.name}")
	else:
		song = await player.queue(url,search=True)
		await ctx.send(f"Queud: {song.name}")

@client.command()
async def pause(ctx):
	player = music.get_player(guild_id=ctx.guild.id)
	song = await player.pause()
	await ctx.send("Paused")

@client.command()
async def resume(ctx):
	player = music.get_player(guild_id=ctx.guild.id)
	song = await player.resume()
	await ctx.send("Resumed")

@client.command()
async def stop(ctx):
	if (ctx.voice_client) :
		player = music.get_player(guild_id=ctx.guild.id)
		await ctx.guild.voice_client.disconnect()
		await player.stop()
		await ctx.send("Stopped")
	else :
		await ctx.send("I am not Playing")


@client.command()
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{' ,'.join([song.name for song in player.current_queue()])}")

@client.command()
async def np(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    await ctx.send(song.name)

@client.command()
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    playr = player.current_queue()
    await ctx.send(f"Skipped from {playr[0].name} to {playr[1].name}")

@client.command()
async def volume(ctx, vol):
    player = music.get_player(guild_id=ctx.guild.id)
    song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
    await ctx.send(f"Changed volume for {song.name} to {int(volume*100)}%")
    
@client.command()
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f"Removed {song.name} from queue")


#Delete Bad Words
@client.listen('on_message')
async def BadWords(message):
	if "BOT" not in str(message.author.roles):
		cr.execute("SELECT value FROM STATS WHERE item = 'messages'")
		mes = cr.fetchone()
		new_mes = int(mes[0])+1
		cr.execute(f"UPDATE STATS SET value ='{new_mes}' WHERE item = 'messages'")
		db.commit()
	id = message.author.id
	username = message.author
	get_users_from_db()
	if id in users:
		cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{id}'")
		DBxp = cr.fetchone()
		XP = DBxp[0]
		lvl = DBxp[1]
		new_xp = int(XP) + 10
		tg_XP = int(lvl)*100
		if new_xp >= tg_XP and "BOT" not in str(message.author.roles) and tg_XP != 0:
			lvl +=1
			cr.execute(f"UPDATE ranks SET XP = '0', lvl = {lvl} WHERE id = '{id}'")
			emb=discord.Embed(title="Congrats",description=f"Good Job {username.mention} for advancing to level: {lvl}")
			await message.channel.send(embed=emb)
		else:
			cr.execute(f"UPDATE ranks SET XP = '{new_xp}' WHERE id = '{id}'")
			db.commit()
	elif id not in users and "BOT" not in str(message.author.roles):
		cr.execute(f"INSERT INTO users (user_name,id,no_of_BD) VALUES ('{username}','{id}','0')")
		db.commit()
		cr.execute(f"INSERT INTO ranks (id,XP,lvl) VALUES ('{id}','{int(0)}','{int(0)}')")
		db.commit()
	for txt in Blocked_Words:
		if txt in str(message.content.lower()) and "Admin" not in str(message.author.roles):
				cr.execute(f"SELECT no_of_BD FROM users where id = '{id}'")
				BD = cr.fetchone()
				new_BD = int(BD[0])+1
				cr.execute(f"UPDATE users SET no_of_BD = '{new_BD}' WHERE id = '{id}'")
				db.commit()
				await message.delete()
				# await message.channel.send("Bad Word :shushing_face:")
				await message.channel.send("اخلاقك يا برو ")
				cr.execute("SELECT value FROM STATS WHERE item = 'no_bad_words'")
				badwrd = cr.fetchone()
				new_badwrd = int(badwrd[0])+1
				cr.execute(f"UPDATE STATS SET value ='{new_badwrd}' WHERE item = 'no_bad_words'")
				db.commit()
@client.command()
async def STATS(ctx):
	cr.execute("SELECT value FROM STATS WHERE item = 'no_bad_words'")
	nobd = cr.fetchone()
	cr.execute("SELECT value FROM STATS WHERE item = 'messages'")
	msg = cr.fetchone()
	cr.execute("SELECT value FROM STATS WHERE item = 'no_users'")
	nousr = cr.fetchone()
	await ctx.channel.send(f"no. of bad words : {nobd[0]} , no. msg : {msg[0]} , usr : {nousr[0]}")

@client.command()
async def zizo(ctx):
	cr.execute("SELECT id FROM users")
	lll = cr.fetchall()
	# ctx.send(user)
	guild = client.get_guild(839639743771836456)
	
	for i in range(len(lll)):
		userid = lll[i][0]
		member = guild.get_member(userid)
		# await ctx.send(member.mention)
		for x in range(len(member.roles)):
			cr.execute(f"SELECT roles FROM users WHERE id = '{userid}'")
			g = cr.fetchone()[0]
			if g == "" or g == None:
				if member.roles[x] != "@everyone":
					cr.execute(f"UPDATE users SET roles = '{member.roles[x]}' WHERE id = '{userid}'")
			else:
				if  member.roles[x] != "@everyone":
					new = f"{g},{member.roles[x]}"
					cr.execute(f"UPDATE users SET roles = '{new}' WHERE id = '{userid}'")
@client.command()
async def warn(message, member : discord.Member=None) :
	if "Admin" in str(message.author.roles) :
		await message.send(
			f'"{member}" has been warned\n'
			# f'Reason : {Reason}'
			'Now he has # warns'     # replace (#) with db warns
		)

	else :
		await message.send("Waiting Admins aproval")
		await client.get_channel(839642523722055691).send(f"Author : {message.author.mention} \nWant's to warn {member.mention}")

@client.event
async def on_member_remove(member):
	emb = discord.Embed(title="Member Left",description=f"{member.mention} left the server")
	await client.get_channel(958072130598219847).send(embed=emb)

@client.event
async def on_member_join(member):
	if member.id in users:
		pass
	else:
		cr.execute(f"INSERT INTO users (user_name,id,no_of_BD,roles) VALUES ('{member}','{member.id}','0','Bystanders')")
		db.commit()
		cr.execute(f"INSERT INTO ranks (id,XP,lvl) VALUES ('{member.id}','{int(0)}','{int(0)}')")
		db.commit()
	emb=discord.Embed(title="NEW MEMBER",description=f"Thanks {member.name} for joining!")
	role = get(member.guild.roles, id=958038471656763422)
	await client.get_channel(839671710856773632).send(embed=emb)
	await member.add_roles(role)


@client.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, user: discord.Member,role:discord.Role):
	if role in user.roles:
		await ctx.send("The user has this role already")
	else:
		cr.execute(f"SELECT roles FROM users WHERE user_name = '{user}'")
		rls = cr.fetchone()[0]
		if rls == None or rls == '':
			cr.execute(f"UPDATE users SET roles ='{role}' WHERE user_name = '{user}'")
		else:
			new_rls = f"{rls},{role}"
			cr.execute(f"UPDATE users SET roles ='{new_rls}' WHERE user_name = '{user}'")
		db.commit()
		await user.add_roles(role)
		await client.get_channel(958072130598219847).send(f"{user} has been given {role} Role")

@client.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, user: discord.Member,role:discord.Role):
	if role not in user.roles:
		await ctx.send("The user dont have this role already")
	else:
		cr.execute(f"SELECT roles FROM users WHERE user_name = '{user}'")
		roles = cr.fetchone()[0]
		new_roles = roles.replace(f"{role}",'')
		llrls = new_roles.replace(',,',',')
		if llrls[0] == ",":
			llrls = llrls[1:]
		elif llrls[-1] == ",":
			llrls = llrls[:-1]
		cr.execute(f"UPDATE users SET roles = '{llrls}' WHERE id = '{user.id}'")
		db.commit()
		await user.remove_roles(role)

@client.command(pass_context=True)
async def rank(message, user: discord.Member=None):
	if user == None:
		cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{message.author.id}'")
		r = cr.fetchone()
		emb =  discord.Embed(title="",description=f"XP : {r[0]} / {int(r[1])*100} , LVL : {r[1]}")
		await message.channel.send(embed=emb)
	else:
		cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{user.id}'")
		r = cr.fetchone()
		emb =  discord.Embed(title="",description=f"XP : {r[0]} / {int(r[1])*100} , LVL : {r[1]}")
		await message.channel.send(embed=emb)
@client.command()
async def top(message):
	cr.execute(f"SELECT XP,lvl,id FROM ranks ORDER BY lvl DESC LIMIT 10")
	r = cr.fetchall()
	ha = []
	for i in range(len(r)):
		if r[i][1] > 0:
			ha.append(f"#{i+1} | [{get_user_name(r[i][2])}] | [lvl : {r[i][1]}]")
	emb = discord.Embed(title="Top-10-Ranks",description="\n".join(ha),color=0x00FF00)
	await message.channel.send(embed=emb)

@client.command()
async def addbdword(message):
	ind = str(message.message.content.find(" "))
	msg = message.message.content[int(ind)+1:]
	if msg in Blocked_Words:
		await message.channel.send(f"Already Exists")
	else:
		xp = get_user_XP_LVL(message.author.id)[0]
		lvl = get_user_XP_LVL(message.author.id)[1]
		newxp = int(xp)+5
		tg_XP = int(lvl)*100
		if newxp >= tg_XP and "BOT" not in str(message.author.roles):
			lvl +=1
			cr.execute(f"UPDATE ranks SET XP = '0', lvl = {lvl} WHERE id = '{message.author.id}'")
			await message.channel.send(f"Good Job {message.author.mention} for advancing to level: {lvl}")
		else:
			cr.execute(f"UPDATE ranks SET XP = '{newxp}' WHERE id = '{message.author.id}'")
		cr.execute(f"INSERT INTO bad_words (bad_word) VALUES ('{msg}')")
		db.commit()
		get_bad_words()
		await message.channel.send(f"Word add ||{msg}||")

@client.command()
async def id(message):
	print(message.author.id)
	print(message.author)

@client.command()
async def صباحو(message):
	await message.channel.send("ميتين دي اصطباحه قوم نام يلا")

# Audit Log (any delete of Message)
@client.event
async def on_message_delete(message): #.replace(tzinfo=timezone('UTC+2'))
	date = message.created_at.strftime("%Y/%m/%d, %I:%M:%S")
	date_now = datetime.datetime.today().strftime("%Y/%m/%d, %I:%M:%S")
	emb = discord.Embed(title = (f"Message deletion"),description = f"A message was deleted in <#{message.channel.id}>",color = 0x6B5B95)
	emb.add_field(name = "Message Content", inline = False, value = message.content)
	emb.add_field(name = "Message Author", inline = False, value = message.author)
	emb.add_field(name = "Sent at", inline = False, value = date)
	emb.add_field(name = "Deleted at", inline = False, value = date_now)
	emb.set_footer(text=" ================\n🔥SECRET 101⚡SCR🔥")
	await client.get_channel(958072130598219847).send(embed=emb)
	await client.get_channel(958072130598219847).send('===============================================================')

@client.command()
async def بعبص(message, member:discord.Member):
	author = message.author
	await message.channel.send(f"البيه ده{author.mention} بعبص الشخص ده {member.mention} \n https://tenor.com/view/%D8%AE%D8%AF-%D8%A8%D8%B9%D8%A8%D9%88%D8%B5-raise-the-roof-dance-gif-12930921")

@client.command()
async def avatar(ctx, *, member:discord.Member=None):
	if member == None :
		member = ctx.author
		UserAvatar = member.avatar_url_as(size=4096)
		emb = discord.Embed(title = f"{member.name}'s Avatar", description="Look , He's so SEXY")
		emb.set_image(url = UserAvatar)
		await ctx.send(embed = emb)

	elif member != None :
		UserAvatar = member.avatar_url_as(size=4096)
		emb = discord.Embed(title = f"{member.name}'s Avatar", description="Look , He's so SEXY")
		emb.set_image(url = UserAvatar)
		await ctx.send(embed = emb)


@client.command()
async def spam(message, member:discord.Member=None):
	count = 5
	if member != None :
		while count > 0 :
			await message.channel.send(member.mention)
			count = count - 1

	elif member == None :
		while count > 0 :
			await message.channel.send(count)
			count = count - 1


@client.command()
async def info(ctx, member:discord.Member=None):
	if member == None:
		cr.execute(f"SELECT roles FROM users WHERE id = '{ctx.message.author.id}'")
		r = cr.fetchone()[0]

		emb = discord.Embed(title = (f"Welcome {ctx.author}"),description = "This is your Information",color = 0x6B5B95)
		emb.add_field(name = "Account Level",inline = True,value=get_user_XP_LVL(ctx.author.id)[1])
		emb.add_field(name = "Roles",inline = True,value=r.replace("@everyone,",""))
		dateY = ctx.message.author.created_at.strftime("%Y")
		dateM = ctx.message.author.created_at.strftime("%m")
		dateD = ctx.message.author.created_at.strftime("%d")
		date2 = datetime.datetime.today().strftime("%Y/%m/%d")
		d2 = datetime.datetime(int(dateY), int(dateM), int(dateD))
		x = d2.strftime("%Y/%m/%d")
		dt1 = datetime.datetime.strptime(x,"%Y/%m/%d")
		dt2 = datetime.datetime.strptime(date2,"%Y/%m/%d")
		d = dt2 - dt1
		ind = str(d).find("d")
		years = int(str(d)[:ind])/365
		ins = str(years).find(".")
		days = int(str(years)[ins+1:])
		hi = len(str(days)) 
		n ="1"
		new = days/int(n.ljust(hi + len(str(n)),'0'))
		emb.add_field(name = "Account Age",inline = True,value=f"{str(years)[:ins]} year {int(new*365)} day")
		await ctx.send(embed=emb)

	elif member != None :
		cr.execute(f"SELECT roles FROM users WHERE id = '{member.id}'")
		r = cr.fetchone()[0]
		user = client.get_user(member.id)
		emb = discord.Embed(title = (f"Welcome {ctx.author}"),description = f"This is informations of\n{member}",color = 0x6B5B95)
		emb.add_field(name = "Account Level",inline = True,value=get_user_XP_LVL(member.id)[1])
		emb.add_field(name = "Roles",inline = True,value=r.replace("@everyone,",""))
		dateY = user.created_at.strftime("%Y")
		dateM = user.created_at.strftime("%m")
		dateD = user.created_at.strftime("%d")
		date2 = datetime.datetime.today().strftime("%Y/%m/%d")
		d2 = datetime.datetime(int(dateY), int(dateM), int(dateD))
		x = d2.strftime("%Y/%m/%d")
		dt1 = datetime.datetime.strptime(x,"%Y/%m/%d")
		dt2 = datetime.datetime.strptime(date2,"%Y/%m/%d")
		d = dt2 - dt1
		ind = str(d).find("d")
		years = int(str(d)[:ind])/365
		ins = str(years).find(".")
		days = int(str(years)[ins+1:])
		hi = len(str(days)) 
		n ="1"
		new = days/int(n.ljust(hi + len(str(n)),'0'))
		emb.add_field(name = "Account Age",inline = True,value=f"{str(years)[:ins]} year {int(new*365)} day")
		await ctx.send(embed=emb)

@client.command()
async def about(ctx):
	total_text_channels = len(ctx.guild.text_channels)
	total_voice_channels = len(ctx.guild.voice_channels)
	emb = discord.Embed(title =f"{ctx.guild.name} Info",description="Information about the server",color=discord.Color.blue())
	emb.add_field(name="🆔server ID",value=ctx.guild.id,inline = True)
	emb.add_field(name="📆Created On",value=ctx.guild.created_at.strftime("%d/%m/%Y"),inline=True)
	emb.add_field(name="👑owner",value=ctx.guild.owner,inline=True)
	emb.add_field(name="👥Member",value=f"{ctx.guild.member_count} Members",inline=True)
	emb.add_field(name="💬Channels", value = f'{total_text_channels} Text | {total_voice_channels} Voice', inline = True)
	emb.add_field(name="🌎Region",value="Middle East",inline=True)
	await ctx.send(embed=emb)

@client.command()
async def status(ctx, member:discord.Member=None) :
	if member == None :
		if str(ctx.author.status) == "online" :
			await ctx.send(f"{ctx.author.mention} is online")

		elif str(ctx.author.status) == "offline" :
			await ctx.send(f"{ctx.author.mention} if offline")

	elif member != None :
		if str(member.status) == "online" :
			await ctx.send(f"{member.mention} is online")

		elif str(member.status) == "offline" :
			await ctx.send(f"{member.mention} is offline")

		elif str(member.status) == "idle" :
			await ctx.send(f"{member.mention} is idle")

		else :
			await ctx.send(f"{member.mention} dont want to get disturbed")



# keep_alive()
client.run(read_token())