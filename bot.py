import asyncio
from pydoc import describe
from turtle import title
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button, ButtonStyle
import sqlite3
from discord.utils import get
import datetime
# from disco.types.message import MessageEmbed



db = sqlite3.connect("bot_database.db")
cr = db.cursor()
EmojiLink = "0"


def read_token():
		with open("token.txt","r") as f:
				token = f.readline()
				return token
intents = discord.Intents.all()
client = commands.Bot(command_prefix = "!" ,intents=intents)
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

#Delete Bad Words#
@client.listen('on_message')
async def BadWords(message):
	if message.content.startswith('hug'):
		await message.channel.send(f"hugs {message.author.mention}")
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
			if new_xp >= tg_XP and "BOT" not in str(message.author.roles):
				lvl +=1
				cr.execute(f"UPDATE ranks SET XP = '0', lvl = {lvl} WHERE id = '{id}'")
				await message.channel.send(f"Good Job {username.mention} for advancing to level: {lvl}")
			else:
				cr.execute(f"UPDATE ranks SET XP = '{new_xp}' WHERE id = '{id}'")
			db.commit()
	elif id not in users and "BOT" not in str(message.author.roles):
		cr.execute(f"INSERT INTO users (user_name,id,no_of_BD) VALUES ('{username}','{id}','0')")
		db.commit()
		cr.execute(f"INSERT INTO ranks (id,XP,lvl) VALUES ('{id}','{int(0)}','{int(0)}')")
		db.commit()

	for txt in Blocked_Words:
		if id in users and "Admin" not in str(message.author.roles) and txt in str(message.content.lower()) and "BOT" not in str(message.author.roles):
			cr.execute(f"SELECT no_of_BD FROM users where id = '{id}'")
			BD = cr.fetchone()
			new_BD = int(BD[0])+1
			cr.execute(f"UPDATE users SET no_of_BD = '{new_BD}' WHERE id = '{id}'")
			db.commit()
			await message.channel.purge(limit=1)
			await message.channel.send("Bad Word :shushing_face:")

@client.event
async def on_member_join(member):
	print("member joined")
	emb=discord.Embed(title="NEW MEMBER",description=f"Thanks {member.name} for joining!")
	await client.get_channel(839671710856773632).send(embed=emb)
	await member.add_roles("Bystaders")

@client.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, user: discord.Member,role:discord.Role):
	if role in user.roles:
		await ctx.send("The user has this role already")
	else:
		await user.add_roles(role)

@client.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, user: discord.Member,role:discord.Role):
	if role not in user.roles:
		await ctx.send("The user dont have this role already")
	else:
		await user.remove_roles(role)



@client.command()
async def rank(message):
	cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{message.author.id}'")
	r = cr.fetchone()
	emb =  discord.Embed(title="",description=f"XP : {r[0]} / {int(r[1])*100} , LVL : {r[1]}")
	await message.channel.send(embed=emb)

@client.command()
async def top(message):
	cr.execute(f"SELECT XP,lvl,id FROM ranks ORDER BY lvl DESC ")
	r = cr.fetchall()
	ha = []
	for i in range(len(r)):
		ha.append(f"#{i+1} | [{get_user_name(r[i][2])}] | [lvl : {r[i][1]}]")
	emb = discord.Embed(title="Top-Ranks",description="\n".join(ha),color=0x00FF00)
	await message.channel.send(embed=emb)

@client.command()
async def add_bad_word(message):
	ind = str(message.message.content.find(" "))
	msg = message.message.content[int(ind)+1:]
	if msg in Blocked_Words:
		await message.channel.send(f"Already Exists")
	else:
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
	await message.channel.send("ميتين دي اصطباحه قوم ذاكر يلا")

# Audit Log (any message edit)
@client.event
async def on_message_edit(before, after):
	if "BOT" not in str(before.author.roles):
		await client.get_channel(958072130598219847).send(
			f'{before.author} edited a message in <#{before.channel.id}> \n'
			f'Before: {before.content}\n'
			f'After: {after.content}\n'
			'==============================================================='
		)

	if "BOT"in str(before.author.roles):
		pass

# Audit Log (any delete of edit)
# @client.event
# async def on_message_edit(before, after):
# 	if "BOT" not in str(before.author.roles):
# 		await client.get_channel(958072130598219847).send(
# 			f'{before.author} edited a message in <#{before.channel.id}> \n'
# 			f'Before: {before.content}\n'
# 			f'After: {after.content}\n'
# 			'==============================================================='
# 		)

# 	if "BOT"in str(before.author.roles):
# 		pass

# # Audit Log (any delete of Message)
# @client.event
# async def on_message_delete(before):
# 	async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.message_delete):
# 		deleter = entry.user
# 		print(f"{deleter.name} deleted message by {before.author.name}")

# 		await client.get_channel(958072130598219847).send(
# 		f"I've deleted a message in <#{before.channel.id}> \n"
# 		f'Message: {before.content}\n'
# 		f'Author: {before.author}'
# 		# f'Message id: {before.Message.id}'
# 		'==============================================================='
# 	)

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
async def info(ctx, member:discord.Member=None):
	if member == None:
		emb = discord.Embed(title = (f"Welcome {ctx.author}"),description = "Test",color = 0x6B5B95)
		emb.add_field(name = "Account Level",inline = True,value="Your level in db")
		emb.add_field(name = "Roles",inline = True,value= "Your roles in db")
		dateY = ctx.message.author.created_at.strftime("%Y")
		dateM = ctx.message.author.created_at.strftime("%m")
		dateD = ctx.message.author.created_at.strftime("%d")
		date2 = datetime.datetime.today().strftime("%Y/%m/%d")
		d2 = datetime.datetime(int(dateY), int(dateM), int(dateD))
		x = d2.strftime("%Y/%m/%d")
		dt1 = datetime.datetime.strptime(x,"%Y/%m/%d")
		dt2 = datetime.datetime.strptime(date2,"%Y/%m/%d")
		d = dt2 - dt1
		ind = str(d).find(",")
		emb.add_field(name = "Account Age",inline = True,value=str(d)[:ind])
		await ctx.send(embed=emb)

	elif member != None :
		user = client.get_user(member.id)
		emb = discord.Embed(title = (f"Welcome {ctx.author}, This is informations of\n{member}"),description = "Test",color = 0x6B5B95)
		emb.add_field(name = "Account Level",inline = True,value="His level in db")
		emb.add_field(name = "Roles",inline = True,value= "His roles in db")
		dateY = user.created_at.strftime("%Y")
		dateM = user.created_at.strftime("%m")
		dateD = user.created_at.strftime("%d")
		date2 = datetime.datetime.today().strftime("%Y/%m/%d")
		d2 = datetime.datetime(int(dateY), int(dateM), int(dateD))
		x = d2.strftime("%Y/%m/%d")
		dt1 = datetime.datetime.strptime(x,"%Y/%m/%d")
		dt2 = datetime.datetime.strptime(date2,"%Y/%m/%d")
		d = dt2 - dt1
		ind = str(d).find(",")
		emb.add_field(name = "Account Age",inline = True,value=str(d)[:ind])
		await ctx.send(embed=emb)


# keep_alive()
client.run(read_token())
