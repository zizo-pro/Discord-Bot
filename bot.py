from ast import alias
import discord
from discord.ext import commands
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

@client.event
async def on_ready():
		print(f"Bot logged in as {client.user}")
		DiscordComponents(client)

Blocked_Words = ["1st", "2nd", "3rd"]
@client.command()
async def ping(ctx):
	await ctx.send('pong!')

@client.command()
async def button(ctx):
	await ctx.send(
			"this is a button test :smile:"
			,components=[
				Button(style=ButtonStyle.blue, label="Button 1"),
				Button(style=ButtonStyle.red, label="Button 2"),
				Button(style=ButtonStyle.URL, label="This is a Picture!", url=EmojiLink)])

	res = await client.wait_for("button_click")
	if res.channel == ctx.channel :
		await res.respond(
			type=4,content= "test"
		)

@client.event
async def on_message(msg):
		for text in Blocked_Words:
				if "Admin" not in str(msg.author.roles) and text in str(msg.content.lower()):
					await msg.delete()
				else:
					@client.command()
					async def ping(ctx):
						await ctx.send('pong!')



# keep_alive()
client.run(read_token())