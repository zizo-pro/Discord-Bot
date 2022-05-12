from colorama import Style
import discord
from discord_ui import Button, components, ButtonStyle, SelectMenu, SelectOption
import discord_ui
from discord_components import *
from yarl import URL
from keep_alive import keep_alive

client = discord.Client()
DisBut= DiscordComponents(client)

print(discord.__version__)
def read_token():
	with open("token.txt","r") as f:
		tok = f.readlines()
		return tok

@client.event
async def on_ready():
		print("we have logged in as {0.user}".format(client))
		DiscordComponents(client)

@client.event
async def on_message(message):
		def server():
			global server_id
			server_id = client.get_guild(839639743771836456)
		
		if message.author == client.user:
			return

		if message.content.startswith('$hello'):
			await message.channel.send("مساء الخرة")

		if message.content.startswith('$صباحو'):
			await message.channel.send("صبح اعمنا ✋")

		if message.content.startswith('$بحبك'):
			await message.channel.send("حبك برص")

		if message.content.startswith('$help'):
			await message.channel.send('اتصرف انا عبيط')

		if message.content == "users":
			server()
			await message.channel.send(f"members count: {server_id.member_count}")

		if message.content.startswith('$test'):
			await message.channel.send("this is a button!",components = [Button(label="دوس",style=ButtonStyle.blue), Button(label="Am SeXy AnD i KnOw It",style=ButtonStyle.red)])
			interaction = await client.wait_for(("button_click"))
			await interaction.respond(content="طيزك فيها دبوس")

@client.event
async def button(ctx):
	BCommand= await ctx.send(
		"Button Command Ran!",
		components=[
			Button(Style=ButtonStyle.blue, label="Click Me!"),
			Button(Style=ButtonStyle.URL, label="Important Video!", url="https://www.youtube.com/watch?v=QB7ACr7pUuE"),
			Button(Style=ButtonStyle.URL, label="ِAnother Important Video!", url="https://www.youtube.com/watch?v=8G0omjVSh_U"),
		],
	)

	res = await DisBut.wait_for_button_click(BCommand)
	await res.respond(
		type=InteractionEventType.ChannelMessageWithSource,
		content=f'{res.button.lable} has been Clicked!!!'
	)


@client.event
async def on_member_join(member):
		print("joined")
		await client.send_message(member,"Welcome!")

keep_alive()
client.run(read_token()[0])