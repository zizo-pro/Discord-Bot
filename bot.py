from ast import alias
from codecs import ignore_errors
from pickle import TRUE
from tokenize import Ignore
from click import pass_obj
import discord
from discord.ext import commands, join
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button, ButtonStyle
import sqlite3

db = sqlite3.connect("bot_database.db")
cr = db.cursor()
EmojiLink = "https://cdn.discordapp.com/emojis/733293111228366871.gif"


def read_token():
		with open("token.txt","r") as f:
				token = f.readline()
				return token

client = commands.Bot(command_prefix = "!" )
Blocked_Words = ["1st", "2nd", "3rd"]

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
	if message.content in Blocked_Words :
		await message.channel.purge(limit=1)
		await message.channel.send("Bad Word :shushing_face:")


# intents = discord.Intents.default()
# intents.members = True
# client = commands.Bot(command_prefix=',', intents=intents)

# @client.event 
# async def on_member_join(member):
# 	emb=discord.Embed(title="NEW MEMBER",description=f"Thanks {member.name} for joining!")
#     await channel.send(embed=emb)


@client.command
async def join(context):
	channel = context.author.voice.channel
	await channel.connect()





# @client.event
# async def on_message(msg):
# 		for text in Blocked_Words:
# 				if "Admin" not in str(msg.author.roles) and text in str(msg.content.lower()):
# 					await msg.delete()



# keep_alive()
client.run(read_token())