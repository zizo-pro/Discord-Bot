from ast import alias
from codecs import ignore_errors
from pickle import TRUE
from tokenize import Ignore
from click import pass_obj
import discord
from discord.ext import commands
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button, ButtonStyle
import sqlite3

db = sqlite3.connect("bot_database.db")
cr = db.cursor()
EmojiLink = "https://www.youtube.com/watch?v=iik25wqIuFo"


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
				label="Button 2"),
				Button(style=ButtonStyle.URL,
				label="This is a Picture!",
				url=EmojiLink)]])

	res = await client.wait_for("button_click")
	if res.channel == ctx.channel :
		await res.message.channel.send(EmojiLink)

#Delete Bad Words#
@client.listen('on_message')
async def BadWords(message):
	for txt in Blocked_Words:
		if "Admin" not in str(message.author.roles) and txt in str(message.content.lower()) and "BOT" not in str(message.author.roles):
			await message.channel.purge(limit=1)



@client.event
async def on_member_join(member):
	print("member joined")
	emb=discord.Embed(title="NEW MEMBER",description=f"Thanks {member.name} for joining!")
	await client.get_channel(839671710856773632).send(embed=emb)

# @client.command
# async def join(ctx):
# 	channel = ctx.author.voice.channel
# 	await channel.connect()

@client.command()
async def mention(message):
	await message.channel.send(f"{message.author.mention} done")

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
		await message.channel.send(f"Word added ||{msg}||")



# keep_alive()
client.run(read_token())