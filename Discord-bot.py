import discord

def read_token():
  with open("token.txt","r") as f:
    lines = f.readlines()
    return lines[0].strip()

client = discord.Client()
@client.event
async def on_message(message):
  server_id = client.get_guild(839639743771836456)
  if message.content.find("!hello") != -1:
    await message.channel.send("hi")

  elif message.content == "!users":
    await message.channel.send(f"NO. of Members: {server_id.member_count}")

@client.event
async def on_member_join(member):
  for channel in member.guild.channels:
    if str(channel) == "general":
      await channel.send('Private message')

token = read_token()
client.run(token)