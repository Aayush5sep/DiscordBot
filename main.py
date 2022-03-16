import os
my_secret = os.environ['BotToken']
import discord
import time
from discord.ext import commands,tasks
from discord.ext.commands import Bot,has_permissions
from webserver import keep_alive
from replit import db
import datetime
from datetime import date
from dateutil.tz import gettz
import asyncio
import requests

bot = commands.Bot(command_prefix='!',allowed_mentions = discord.AllowedMentions(everyone = True))
client = discord.Client()

current = datetime.datetime.now()
# use db['all_assig']=[] for the first time only

@bot.event
async def on_ready():
  print('Bot is ready')
  
  
@bot.command()
async def add(ctx):
	if ctx.author.id!=759036446224154684 and ctx.author.id!=922091085340237834:
		return None
	def check(m):
		return m.author.id==ctx.author.id
	assg=""
	subject=""
	day=""
	month=""
	year=""
	desc=""
	try:
		await ctx.channel.send('Type the Title of assignment')
		assgi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
		assg=assgi.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	try:
		await ctx.channel.send('Enter the Subject of assigned assignment')
		subjecti = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
		subject=subjecti.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	try:
		await ctx.channel.send('What is the day(DD) ?')
		dayi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
		day=dayi.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	try:
		await ctx.channel.send('What is the month(MM) ?')
		monthi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
		month=monthi.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	try:
		await ctx.channel.send('What is the Year(YYYY) ?')
		yeari = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
		year=yeari.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	try:
		await ctx.channel.send('Give a small brief Description of the assignment')
		desci = await bot.wait_for("message", check=check, timeout=60.0) # 60 seconds to reply
		desc=desci.content
	except asyncio.TimeoutError:
		await ctx.channel.send("Sorry, you didn't reply in time!")
		return None
	db[assg]={}
	temp=db[assg]
	temp['assg']=assg
	temp['subject']=subject
	temp['day']=day
	temp['month']=month
	temp['year']=year
	temp['description']=desc
	db[assg]=temp
	db['all_assig'].append(assg)
	await ctx.channel.send(f'Assignment added: \n {assg} of {subject} wil be last submitted on {day}/{month}/{year} \n Description: {desc}')
	
@bot.command()
async def contests(ctx):
	contestapi = requests.get("https://codeforces.com/api/contest.list")
	cdata = contestapi.json()
	if cdata['status']=='OK':
		for contests in cdata['result']:
			if contests['phase']=='BEFORE':
				ctime=contests['relativeTimeSeconds']*(-1)
				clist=discord.Embed(title="Future Contests",color=0xf1c40f)
				clist.add_field(name="Contest Name",value=contests['name'])
				clist.add_field(name="Starting after",value=str((ctime//3600)//24) + " Days " + str((ctime//3600)%24) + " Hours " + str((ctime%3600)//60) + " Minutes")
				await ctx.channel.send(embed=clist)
			else:
				print('No more future contests to add')
				break
			


@bot.command()
async def assignments(ctx):
    if ctx.channel.id==928234877898350612:
        for assigs in db['all_assig']:
            assigs_list = discord.Embed(title="Assignment",color=0x2ecc71)
            assigs_list.add_field(name="Subject",value=db[assigs]['subject'])
            assigs_list.add_field(name="Assignment",value=db[assigs]['assg'])
            assigs_list.add_field(name="Description",value=db[assigs]['description'])
            assigs_list.add_field(name="Date",value=( db[assigs]['day'] + "/" + db[assigs]['month']+"/"+db[assigs]['year'] ) )
            await ctx.channel.send(embed=assigs_list)
    else:
        await ctx.channel.send('This command is available on Assignment channel only')
  	  	

@tasks.loop(hours=1)
async def assig_loop():
	await bot.wait_until_ready()
	current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
	cday = current.day
	cmonth = current.month
	chour = current.hour
	cyear=current.year
	for assigs in db['all_assig']:
			date1=date(cyear,cmonth,cday)
			date2=date(int(db[assigs]['year']),int(db[assigs]['month']),int(db[assigs]['day']))
			diff=date2-date1
			if(diff.days==1) and (chour==8 or chour==20) :
				clist = discord.Embed(title="Assignment Submission Alert",color=0x992d22)
				clist.add_field(name="Subject",value=db[assigs]['subject'])
				clist.add_field(name="Assignment Name",value=db[assigs]['assg'])
				clist.add_field(name="Description",value=db[assigs]['description'])
				clist.add_field(name="Date",value=( db[assigs]['day'] + "/" + db[assigs]['month'] ) )
				clist.set_image(url="https://media.giphy.com/media/Rhr6OQDIoUOtDCcxD2/giphy.gif")
				targetchannel = bot.get_channel(928234877898350612)
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
				
			elif(cday==int(db[assigs]['day'])) and (cmonth==int(db[assigs]['month'])):
				del db[assigs]
				db['all_assig'].remove(assigs)


monday={'9':'Computer Lab','11':'Computer Practical','14':'Electrical Lab'}
tuesday={'11':'Physics Lab','13':'Computer Lab'}
wednesday={'10':'Electrical Practical','12':'Engineering Graphics','16':'Physics Practical'}
thursday={'13':'Physics Lab','14':'Mathematics Lab'}
friday={'9':'Electrical','10':'Mathematics Lab'}
saturday={}
sunday={}

@tasks.loop(minutes=10)
async def classes():
	await bot.wait_until_ready()
	current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
	chour=current.hour
	cminute=current.minute
	day=datetime.datetime.today().weekday()
	if cminute>=50:
		targetchannel=bot.get_channel(928266236910010378)
		try:
			if day==0:
				classes=monday[str(chour+1)]
				clist = discord.Embed(title="Class Alert",color=0x992d22)
				clist.add_field(name="Subject",value=f'{classes}')
				clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
				clist.set_image(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
			elif day==1:
				classes=tuesday[str(chour+1)]
				clist = discord.Embed(title="Class Alert",color=0x992d22)
				clist.add_field(name="Subject",value=f'{classes}')
				clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
				clist.set_image(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
			elif day==2:
				classes=wednesday[str(chour+1)]
				clist = discord.Embed(title="Class Alert",color=0x992d22)
				clist.add_field(name="Subject",value=f'{classes}')
				clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
				clist.set_image(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
			elif day==3:
				classes=thursday[str(chour+1)]
				clist = discord.Embed(title="Class Alert",color=0x992d22)
				clist.add_field(name="Subject",value=f'{classes}')
				clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
				clist.set_image(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
			elif day==4:
				classes=friday[str(chour+1)]
				clist = discord.Embed(title="Class Alert",color=0x992d22)
				clist.add_field(name="Subject",value=f'{classes}')
				clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
				clist.set_image(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
				await targetchannel.send('@everyone')
				await targetchannel.send(embed=clist)
		except KeyError:
			print('No classes for now')



@bot.command()
async def commands(ctx):
	helpl = discord.Embed(title="Commands",color=0x95a5a6)
	helpl.add_field(name="!assignments",value="Prints the list of all Pending Assignments")
	helpl.add_field(name="!contests",value="Prints all future Codeforces contests")
	helpl.add_field(name="!commands",value="Specifies all the commands")
	helpl.add_field(name="!add {Subject} {Day} {Month} {Year} {Assignment} {Description}",value="Administrator Command Only")
	await ctx.channel.send(embed=helpl)


assig_loop.start()
classes.start()
keep_alive()

bot.run(my_secret)