from pickle import TRUE
from turtle import title
import discord
from discord.ext import commands
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button, ButtonStyle
import sqlite3

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
	await ctx.send('pong!')

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

@client.command()
async def rank(message):
	cr.execute(f"SELECT XP,lvl FROM ranks WHERE id = '{message.author.id}'")
	r = cr.fetchone()
	await message.channel.send(f"XP : {r[0]}/{int(r[1]*100)} , LEVEL : {r[1]}")

@client.command()
async def top(message):
	cr.execute(f"SELECT XP,lvl,id FROM ranks ORDER BY XP DESC")
	r = cr.fetchall()
	ha = []
	for i in range(len(r)):
		ha.append(f"#{i+1} | [{get_user_name(r[i][2])}] | [lvl : {r[i][1]}]")
	print(ha)
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
async def on_message_edit(before, after, message):
	if "BOT" not in str(message.author.roles):
		await client.get_channel(958072130598219847).send(
			f'{before.author} edited a message in <#{before.channel.id}> \n'
			f'Before: {before.content}\n'
			f'After: {after.content}\n'
			'==============================================================='
		)

@client.command()
async def بعبص(message, member:discord.Member):
	author = message.author
	await message.channel.send(f"{author.mention} بعبص {member.mention} \n https://tenor.com/view/%D8%AE%D8%AF-%D8%A8%D8%B9%D8%A8%D9%88%D8%B5-raise-the-roof-dance-gif-12930921")

@client.command()
async def avatar(ctx, *, member:discord.Member=None):
	if member == None :
		member = ctx.author
		UserAvatar = member.avatar_url
		emb = discord.Embed(title = f"{member.name}'s Avatar", description="Look , He's so SEXY")
		emb.set_image(url = UserAvatar)
		await ctx.send(embed = emb)

	elif member != None :
		UserAvatar = member.avatar_url
		emb = discord.Embed(title = f"{member.name}'s Avatar", description="Look , He's so SEXY")
		emb.set_image(url = UserAvatar)
		await ctx.send(embed = emb)

# keep_alive()
client.run(read_token())