#-------------------------------------------------------------------------------------------------------#
#--------------------------------------Library Imports--------------------------------------------------#


import os          # To Fetch Environment Variables
from os import system
import sqlite3
from turtle import title          # SQLite DataBase
my_secret = os.environ['BotToken']      # Environment Variable
import time     # Time Library
import discord      # Discord library
from discord.ext import commands,tasks      # Commands for discord bot
from discord.ext.commands import Bot,has_permissions        # Bot Access from discord
from webserver import keep_alive      # Flask Hosting To keep server running
import datetime     # Date and Time library
from datetime import date       # Date library
from dateutil.tz import gettz       # To get specific location for date and time
import asyncio      # Asynchronous generators, and closing the threadpool
import requests     # Webserver page request in JSON
import paginator        # Discord Embed Tabular Form


#-------------------------------------------------------------------------------------------------------#
#-------------------------------------SQLite Tables-----------------------------------------------------#


# Create Required Tables In SQLite Database
def create():
    con=sqlite3.connect('sql.db')
    cur=con.cursor()

    # Activating Foreign Key Connectivity ON
    cur.execute('''PRAGMA foreign_keys = ON;''')
    con.commit()

    # Table For Regular Week Classes
    cur.execute('''CREATE TABLE IF NOT EXISTS CLASSES(
        SUBJECT TEXT NOT NULL,
        DAY INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        SKIP INTEGER DEFAULT 0,
        REASON TEXT);''')
    con.commit()

    # Table For Assignment Reminds
    cur.execute('''CREATE TABLE IF NOT EXISTS ASSIGNMENTS(
        SUBJECT TEXT NOT NULL,
        DATE INTEGER NOT NULL,
        MONTH INTEGER NOT NULL,
        YEAR INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        DESCRIPTION TEXT);''')
    con.commit()

    # Table For Events Or Other Misc Schedules
    cur.execute('''CREATE TABLE IF NOT EXISTS EVENTS(
        EVENT TEXT NOT NULL,
        ETYPE TEXT NOT NULL,
        DATE INTEGER NOT NULL,
        MONTH INTEGER NOT NULL,
        YEAR INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        DESCRIPTION TEXT);''')
    con.commit()

    # Table For User Data & Storing Solved Question Points
    cur.execute('''CREATE TABLE IF NOT EXISTS POINTS(
        DISCORDID TEXT PRIMARY KEY,
        NAME TEXT NOT NULL,
        CFHANDLE TEXT NOT NULL,
        POINTS INTEGER DEFAULT 0);''')
    con.commit()

    # Table For Storing Daily Practice Questions
    cur.execute('''CREATE TABLE IF NOT EXISTS QUESTIONS(
        CONID TEXT NOT NULL,
        PINDEX TEXT NOT NULL,
        DATE INTEGER NOT NULL,
        MONTH INTEGER NOT NULL,
        YEAR INTEGER NOT NULL,
        LINK TEXT NOT NULL,
        POINT INTEGER DEFAULT 0);''')
    con.commit()

    # Table For List Of Solved Questions With Link To Points Table
    cur.execute('''CREATE TABLE IF NOT EXISTS SOLVED(
        USERID TEXT,
        QNSID INTEGER,
        FOREIGN KEY(USERID) REFERENCES POINTS(DISCORDID));''')
    con.commit()

    cur.execute('''CREATE TABLE IF NOT EXISTS MODS(
        USERID TEXT NOT NULL);''')
    con.commit()

    con.close()
    return


#-------------------------------------------------------------------------------------------------------#
#---------------------------------------Bot Init & Params-----------------------------------------------#


# Discord Bot Or Client Initialization
bot = commands.Bot(command_prefix='!',allowed_mentions = discord.AllowedMentions(everyone = True))
client = discord.Client()


# Getting Some Important Parameters
current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dch=""
# targetchannel = bot.get_channel(928234877898350612)

def checkm(ctxi):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT * FROM MODS''')
    data = cur.fetchall()
    data1=[str(x[0]) for x in data]
    con.commit()
    con.close()
    if ctxi==759036446224154684 or str(ctxi) in data1:
        return True
    else:
        return False


# Bot Successful Start Event
@bot.event
async def on_ready():
    dch=bot.get_channel(969659476632277053)
    await dch.send(f'Server Restarted At {current.hour}:{current.minute}')
    print('Bot is ready')


#-------------------------------------------------------------------------------------------------------#
#----------------------------------------Regular Classes------------------------------------------------#


# To Skip Some Class Not Going To Held
@bot.command()
async def skip(ctx):
    if checkm(ctx.author.id)==False:        # Mod Check
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):       # Check if it is the same author or not
        return m.author.id==ctx.author.id
    skipp=0
    reasons=["MASS BUNK","CANCELLATION OF CLASS","HOLIDAY"]         # Reason to skip class
    reason=""
    try:
        con=sqlite3.connect('sql.db')
        cur=con.cursor()
        cur.execute('''SELECT rowid,* FROM CLASSES''')
        output = cur.fetchall()
        await ctx.channel.send("Select The Class To Skip")
        for row in output:
            await ctx.channel.send(f'{row[0]} : {row[1]} at {row[3]} and Status is {row[4]}')
        con.commit()
        assgi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        rowi=int(assgi.content)
        await ctx.channel.send("Select The Reason To Skip\n1:Mass Bunk\n2:Class Cancelled\n3:Holiday")
        reas = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        reason=reasons[int(reas)-1]
        cur.execute('''UPDATE CLASSES set SKIP = 1, REASON=? where rowid = ?''',(reason,rowi))
        await ctx.channel.send("Class has been Skipped")
        con.commit()
        con.close()
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None

@bot.command()
async def delc(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    skipp=0
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM CLASSES ORDER BY DAY ASC,TIME ASC;''')
    data = cur.fetchall()
    data = [[x[0],x[1],weekdays[int(x[2])],str(x[3])] for x in data]
    await ctx.channel.send("Select The Class To Delete")
    con.commit()
    await paginator.Paginator(data, ["Row","Subject","Day","Time"], f"B6 Class Schedule", 15).paginate(ctx, bot)
    assgi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
    rowi=int(assgi.content)
    cur.execute('''DELETE from CLASSES where rowid = ?''',(rowi,))
    await ctx.channel.send("Class Has Been Permanently Removed")
    con.commit()
    con.close()

@bot.command()
async def addc(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    subject=""
    day=""
    time=""
    try:
        await ctx.channel.send('Enter the Subject')
        subjecti = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        subject=subjecti.content
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Day?')
        dayi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        day=int(dayi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Time(HH) ?')
        timei = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        time=int(timei.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    
    cur.execute('''INSERT INTO CLASSES(SUBJECT,DAY,TIME) VALUES(
        ?,?,?)''',(subject,day,time))
    con.commit()
    await ctx.channel.send("Class Is Successfully Added")
    con.close()

@bot.command()
async def classes(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT * FROM CLASSES ORDER BY DAY ASC,TIME ASC;''')
    data = cur.fetchall()
    data = [[x[0],weekdays[int(x[1])],str(x[2]),str(x[3])] for x in data]
    con.commit()
    con.close()
    await paginator.Paginator(data, ["Subject","Day","Time","Skip"], f"B6 Class Schedule", 15).paginate(ctx, bot)


#-------------------------------------------------------------------------------------------------------#
#-------------------------------------Assignment/Project Reminder---------------------------------------#


@bot.command()
async def add(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    subject=""
    day=0
    month=0
    year=0
    time=0
    desc=""
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
        day=int(dayi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the month(MM) ?')
        monthi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        month=int(monthi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Year(YYYY) ?')
        yeari = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        year=int(yeari.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Time(HH) ?')
        timei = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        time=int(timei.content)
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
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''INSERT INTO ASSIGNMENTS(SUBJECT,DATE,MONTH,YEAR,TIME,DESCRIPTION) VALUES(
        ?,?,?,?,?,?)''',(subject,day,month,year,time,desc))
    con.commit()
    con.close()
    await ctx.channel.send(f'Assignment added: \n Assignment of {subject} wil be last submitted on {day}/{month}/{year} \n Description: {desc}')
	

@bot.command()
async def delete(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    skipp=0
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM ASSIGNMENTS''')
    output = cur.fetchall()
    await ctx.channel.send("Select The Assignment To Delete")
    for row in output:
        await ctx.channel.send(f'{row[0]} : {row[1]} at {row[2]} {row[3]} {row[4]} {row[5]} ')
    con.commit()
    assgi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
    rowi=int(assgi.content)
    cur.execute('''DELETE from ASSIGNMENTS where rowid = ?''',(rowi,))
    con.commit()
    await ctx.channel.send("Assignment Removed From Database")
    con.close()

@bot.command()
async def assig(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM ASSIGNMENTS''')
    data = cur.fetchall()
    con.commit()
    con.close()
    data1 = [[str(x[0]),x[1], (str(x[2])+"/"+str(x[3])+"/"+str(x[4])),str(x[5])] for x in data]
    await paginator.Paginator(data1, ["S.No.","Subject", "Date", "Time"], f"Pending Assignments/Projects", 5).paginate(ctx, bot)
    data = [[str(x[0]),x[6]] for x in data]
    await paginator.Paginator(data, ["S.No.","Description"], f"Pending Assignments/Projects", 4).paginate(ctx, bot)


#-------------------------------------------------------------------------------------------------------#
#----------------------------------------Scheduled Events-----------------------------------------------#


@bot.command()
async def adde(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    evnt=""
    evtype=""
    day=0
    month=0
    year=0
    time=0
    desc=""
    try:
        await ctx.channel.send('Enter the name of Event')
        subjecti = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        evnt=subjecti.content
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('Enter the Event type')
        evtypei = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        evtype=evtypei.content
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the day(DD) ?')
        dayi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        day=int(dayi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the month(MM) ?')
        monthi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        month=int(monthi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Year(YYYY) ?')
        yeari = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        year=int(yeari.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('What is the Time(HH) ?')
        timei = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
        time=int(timei.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send('Give a small brief Description of the evemt')
        desci = await bot.wait_for("message", check=check, timeout=60.0) # 60 seconds to reply
        desc=desci.content
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''INSERT INTO EVENTS(EVENT,ETYPE,DATE,MONTH,YEAR,TIME,DESCRIPTION) VALUES(
        ?,?,?,?,?,?,?)''',(evnt,evtype,day,month,year,time,desc))
    con.commit()
    con.close()
    await ctx.channel.send(f'Event added: \n{evnt} wil be held on {day}/{month}/{year} \n Description: {desc}')
	
@bot.command()
async def dele(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    skipp=0
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM EVENTS''')
    output = cur.fetchall()
    await ctx.channel.send("Select The Event To Delete")
    for row in output:
        await ctx.channel.send(f'{row[0]} : {row[1]} type {row[2]} at {row[3]} {row[4]} {row[5]} {row[6]} ')
    con.commit()
    assgi = await bot.wait_for("message",check=check, timeout=30.0) # 30 seconds to reply
    rowi=int(assgi.content)
    cur.execute('''DELETE from EVENTS where rowid = ?''',(rowi,))
    con.commit()
    await ctx.channel.send("The Event Has Been Deleted")
    con.close()

@bot.command()
async def show(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT * FROM EVENTS''')
    data = cur.fetchall()
    con.commit()
    con.close()
    data = [[x[0],x[1],(str(x[2])+"/"+str(x[3])+"/"+str(x[4])),str(x[5])] for x in data]
    await paginator.Paginator(data, ["Event","Type","Date","Time"], f"Upcoming Events", 5).paginate(ctx, bot)


#-------------------------------------------------------------------------------------------------------#
#----------------------------------------Codeforces Handles---------------------------------------------#


@bot.command(pass_context=True)
async def new(ctx,cfhandle,user:discord.User):
    if ctx.author.id!=759036446224154684 and ctx.author.id!=user.id:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''INSERT INTO POINTS(DISCORDID,NAME,CFHANDLE) VALUES(
        ?,?,?)''',(user.id,user.name,cfhandle))
    con.commit()
    con.close()

#Print all saved codeforce handles in the database
@bot.command()
async def handles(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM POINTS''')
    data = cur.fetchall()
    data = [[str(x[0]), x[2],x[3]] for x in data]
    con.commit()
    con.close()
    await paginator.Paginator(data, ["S.No.","User", "Handle"], f"Codeforce Handles", 5).paginate(ctx, bot)


#-------------------------------------------------------------------------------------------------------#
#--------------------------------------Daily Practice Questions-----------------------------------------#


@bot.command()
async def addqn(ctx):
    if checkm(ctx.author.id)==False:
        await ctx.channel.send("You Should Be A Moderator To Use This Command !")
        return None
    def check(m):
        return m.author.id==ctx.author.id
    response=""
    point=0
    try:
        await ctx.channel.send(f'Enter The Link For Daily Practice Question')
        resi = await bot.wait_for("message", check=check, timeout=60.0) # 60 seconds to reply
        response=resi.content
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    try:
        await ctx.channel.send(f'Enter The Number Of Points')
        resi = await bot.wait_for("message", check=check, timeout=60.0) # 60 seconds to reply
        point=int(resi.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return None
    vars = response.split("/")[-3:]
    contid=vars[1]
    pindex=vars[2]
    current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    cdate=current.day
    cmonth=current.month
    cyear=current.year
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM QUESTIONS''')
    output = cur.fetchall()
    rowids=[]
    for row in output:
        if int(row[3])!=int(cdate) or int(row[4])!=int(cmonth) or int(row[5])!=int(cyear):
            rowids.append(row[1])
    con.commit()
    for rows in rowids:
        cur.execute('''DELETE from EVENTS where rowid = ?''',(rows,))
        con.commit()
    cur.execute('''INSERT INTO QUESTIONS(CONID,PINDEX,DATE,MONTH,YEAR,LINK,POINT) VALUES(
        ?,?,?,?,?,?,?)''',(contid,pindex,cdate,cmonth,cyear,response,point))
    con.commit()
    await ctx.channel.send("New Practice Question Added For Today")
    con.close()

@bot.command()
async def qns(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM QUESTIONS''')
    output = cur.fetchall()
    for row in output:
        await ctx.channel.send(f'{row[0]} : Problem {row[1]} {row[2]} due on {row[3]}/{row[4]}/{row[5]} \nLink : {row[6]}')
    con.commit()
    con.close()

@bot.command()
async def solved(ctx,rowi):
    if rowi==None:
        await ctx.channel.send("Kindly Enter the ID of Question as well\n       !solved ID")
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    userid=str(ctx.author.id)
    cur.execute('''SELECT CFHANDLE FROM POINTS WHERE DISCORDID = ?''',(userid,))
    handles=cur.fetchall()
    handl=str(handles[0][0])
    contestID=""
    index=""
    points=0
    cur.execute('''SELECT rowid,* FROM QUESTIONS''')
    output = cur.fetchall()
    for row in output:
        if int(row[0])==int(rowi):
            contestID=str(row[1])
            index=row[2]
            points=row[7]
            break
    con.commit()
    baseurl="https://codeforces.com/api/user.status?handle="
    count=10
    finalurl=baseurl+handl+"&count="+str(count)
    response = requests.get(finalurl)
    data = response.json()
    flag=0
    for probs in data["result"]:
        conti=str(probs["problem"]["contestId"])
        ind=str(probs["problem"]["index"])
        verd=probs["verdict"]
        if conti==contestID and ind==index and verd=="OK":
            cur.execute('''SELECT * FROM SOLVED WHERE USERID = ?''',(userid,))
            problems=cur.fetchall()
            for prob in problems:
                if int(prob[1])==int(rowi):
                    con.commit()
                    await ctx.channel.send("Points Have Been Already Added For This Question")
                    return None
            con.commit()
            cur.execute('''INSERT INTO SOLVED(USERID,QNSID) VALUES(
                ?,?)''',(userid,rowi))
            con.commit()
            cur.execute('''UPDATE POINTS SET POINTS = POINTS+? WHERE DISCORDID = ?''',(points,userid))
            con.commit()
            await ctx.channel.send("Your Points Have Been Updated Successfully")
            flag=1
            break
    if flag==0:
        await ctx.channel.send("Kindly Solve The Question To claim Points")
    con.close()

# Print user gained points by solving CF qns
@bot.command()
async def points(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM POINTS''')
    data = cur.fetchall()
    data = [[str(x[0]), x[2],x[3],str(x[4])] for x in data]
    con.commit()
    con.close()
    await paginator.Paginator(data, ["S.No.","User", "Handle", "Points"], f"Handles And Points", 5).paginate(ctx, bot)


#-------------------------------------------------------------------------------------------------------#
#----------------------------------------Moderation-----------------------------------------------------#


def checkmod(uid):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT USERID FROM MODS WHERE USERID=?''',(uid,))
    data = cur.fetchall()
    con.commit()
    con.close()
    if data is not None:
        return True
    else:
        return False


@bot.command(pass_context=True)
async def mod(ctx,user:discord.User):
    if ctx.author.id!=759036446224154684:
        return None
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''INSERT INTO MODS(USERID) VALUES(
        ?);''',(str(user.id),))
    con.commit()
    await ctx.channel.send("New Mod Added For Bot")
    con.close()


@bot.command(pass_context=True)
async def demod(ctx,user:discord.User):
    if ctx.author.id!=759036446224154684:
        return None
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''DELETE FROM MODS WHERE USERID=?''',(str(user.id),))
    con.commit()
    await ctx.channel.send("Specified Mod Deleted From Bot")
    con.close()


@bot.command()
async def mods(ctx):
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT * FROM MODS''')
    data = cur.fetchall()
    data1=[]
    for x in data:
        user=await bot.fetch_user(int(x[0]))
        uname=user.name
        data1.append([str(uname)])
    data1.insert(0,["Admin-Aayush"])
    con.commit()
    con.close()
    await paginator.Paginator(data1, ["User"], f"Bot Moderators", 5).paginate(ctx, bot)
  

#-------------------------------------------------------------------------------------------------------#
#--------------------------------------Continuous Loops-------------------------------------------------#


@tasks.loop(hours=1)
async def assig_loop():
    await bot.wait_until_ready()
    current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    chour=current.hour
    cdate=current.day
    cmonth=current.month
    cyear=current.year
    if chour==10 or chour==20:
        date1=date(cyear,cmonth,cdate)
        con=sqlite3.connect('sql.db')
        cur=con.cursor()
        cur.execute('''SELECT rowid,* FROM ASSIGNMENTS''')
        data = cur.fetchall()
        con.commit()
        con.close()
        for assgs in data:
            date2=(assgs[4],assgs[3],assgs[2])
            diff=date2-date1
            if diff.days==1:
                clist = discord.Embed(title="Assignment Submission Alert",description="@everyone",color=0x992d22)
                clist.set_thumbnail(url="https://media.giphy.com/media/Rhr6OQDIoUOtDCcxD2/giphy.gif")
                clist.add_field(name="Subject",value=assgs[1])
                clist.add_field(name="Description",value=assgs[6])
                clist.add_field(name="Date",value=(assgs[2] + "/" + assgs[3] + "/" + assgs[4]))
                targetchannel = bot.get_channel(928234877898350612)
                await targetchannel.send(embed=clist)
            elif diff.days==0:
                con=sqlite3.connect('sql.db')
                cur=con.cursor()
                cur.execute('''DELETE FROM ASSIGNMENTS WHERE rowid=?''',(assgs[0],))
                con.commit()
                con.close()



@tasks.loop(minutes=10)
async def classes():
    await bot.wait_until_ready()
    dcl=bot.get_channel(969659476632277053)
    current = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    chour=current.hour
    cminute=current.minute
    crday=datetime.datetime.today().weekday()
    if cminute>=50:
        con=sqlite3.connect('sql.db')
        cur=con.cursor()
        cur.execute('''SELECT rowid,* FROM CLASSES''')
        data = cur.fetchall()
        con.commit()
        targetchannel=bot.get_channel(928266236910010378) #928266236910010378
        for classes in data:
            if crday==classes[2] and chour==(classes[3]-1):
                if classes[4]==0:
                    clist = discord.Embed(title="Class Alert",description="@everyone",color=0x992d22)
                    clist.set_thumbnail(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
                    clist.add_field(name="Subject",value=f'{classes[1]}')
                    clist.add_field(name="Time",value=f'Next class starting at {chour+1}')
                    await targetchannel.send(embed=clist)
                else:
                    clist = discord.Embed(title="Class Alert",description="@everyone",color=0x992d22)
                    clist.set_thumbnail(url="https://media.giphy.com/media/9Qr5qhREdWzuSFp9ti/giphy.gif")
                    clist.add_field(name="Subject",value=f'{classes[1]}')
                    clist.add_field(name="Class Status",value=f'Not Held Due To {classes[5]}')
                    await targetchannel.send(embed=clist)
                    cur.execute('''UPDATE CLASSES SET SKIP=0 WHERE rowid=?''',(classes[0]))
                con.close()
                break


#-------------------------------------------------------------------------------------------------------#
#-------------------------------------Help Commands And Inits-------------------------------------------#


# Help Command - List Of Functions
@bot.command()
async def fns(ctx):
    helpl = discord.Embed(title="Moderators Only",color=0x95a5a6)
    helpl.add_field(name="!addc",value="Add Class",inline=True)
    helpl.add_field(name="!delc",value="Delete Class",inline=True)
    helpl.add_field(name="!skip",value="Skip Class",inline=True)
    helpl.add_field(name="!add",value="Adding New Assignment",inline=True)
    helpl.add_field(name="!delete",value="Delete Assignment",inline=True)
    helpl.add_field(name="!adde",value="Add Some Event",inline=True)
    helpl.add_field(name="!dele",value="Delete Scheduled Event",inline=True)
    helpl.add_field(name="!addqn",value="New Question for Coding Practice",inline=True)
    await ctx.channel.send(embed=helpl)
    helpl = discord.Embed(title="General Commands",color=0x95a5a6)
    helpl.add_field(name="!classes",value="List of all Classes",inline=True)
    helpl.add_field(name="!assig",value="List of all Assignments",inline=True)
    helpl.add_field(name="!show",value="Show upcoming Events",inline=True)
    helpl.add_field(name="!new",value="Add new CF Handle",inline=True)
    helpl.add_field(name="!handles",value="View Registered Handles",inline=True)
    helpl.add_field(name="!qns",value="Print DPP",inline=True)
    helpl.add_field(name="!solved [id]",value="Evaluate points after Question is solved",inline=True)
    helpl.add_field(name="!points",value="User and Points",inline=True)
    await ctx.channel.send(embed=helpl)




# To Run Create Function Initially
create()
# Run Loops
assig_loop.start()
classes.start()
# Flask Hosting
keep_alive()
# Bot Run
try:
    bot.run(my_secret)
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system("python newip.py")
    system('kill 1')


#-------------------------------------------------------------------------------------------------------#
#-------------------------------------Extra Comments----------------------------------------------------#


# Codeforces User Solved Problems JSON
# https://codeforces.com/api/user.status?handle=Aayush5sep&count=25
# list["result"][]     ["id"]    ["verdict"]    ["problem"]["contestId"]/["index"]
# "TIME_LIMIT_EXCEEDED"       "WRONG_ANSWER"          "OK"
# codeforces.com/contest/1579/problem/D
# url = "http://www.example.com/site/section1/VAR1/VAR2"
# url.split("/")[-2:]
# ['VAR1', 'VAR2']
