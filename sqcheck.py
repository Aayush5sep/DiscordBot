import sqlite3
import requests

def create():
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS CLASSES(
        SUBJECT TEXT NOT NULL,
        DAY INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        SKIP INTEGER DEFAULT 0,
        REASON TEXT);''')
    con.commit()

    cur.execute('''CREATE TABLE IF NOT EXISTS ASSIGNMENTS(
        SUBJECT TEXT NOT NULL,
        DATE INTEGER NOT NULL,
        MONTH INTEGER NOT NULL,
        YEAR INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        DESCRIPTION TEXT);''')
    con.commit()

    cur.execute('''CREATE TABLE IF NOT EXISTS EVENTS(
        EVENT TEXT NOT NULL,
        ETYPE TEXT NOT NULL,
        DATE INTEGER NOT NULL,
        MONTH INTEGER NOT NULL,
        YEAR INTEGER NOT NULL,
        TIME INTEGER NOT NULL,
        DESCRIPTION TEXT);''')
    con.commit()

    con.close()
    return


def skip():
    skipp=0
    reasons=["MASS BUNK","CANCELLATION OF CLASS","HOLIDAY"]
    reason=""
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM CLASSES''')
    output = cur.fetchall()
    for row in output:
        print(f'{row[0]} : {row[1]} at {row[3]} and Status is {row[4]}')
    con.commit()
    assgi = input("Select The Class To Skip ") # 30 seconds to reply
    rowi=int(assgi)
    reas = input("Select The Reason To Skip ") # 30 seconds to reply
    reason=reasons[int(reas)]
    cur.execute('''UPDATE CLASSES set SKIP = 1, REASON=? where rowid = ?''',(reason,rowi))
    con.commit()
    con.close()
    

def delc():
    skipp=0
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM CLASSES''')
    output = cur.fetchall()
    for row in output:
        print(f'{row[0]} : {row[1]} at {row[3]} and Status is {row[4]}')
    con.commit()
    assgi = input("Select The Class To Delete ") # 30 seconds to reply
    rowi=int(assgi)
    cur.execute('''DELETE FROM CLASSES WHERE rowid = ?''',(rowi,))
    con.commit()
    con.close()

def addc():
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    subject=""
    day=""
    time=""
    subjecti = input("Enter the Subject ") # 30 seconds to reply
    subject=subjecti

    dayi = input("What is the Day? ") # 30 seconds to reply
    day=int(dayi)

    timei = input("What is the Time(HH) ? ") # 30 seconds to reply
    time=int(timei)
    
    
    cur.execute('''INSERT INTO CLASSES(SUBJECT,DAY,TIME) VALUES(
        ?,?,?)''',(subject,day,time))
    con.commit()
    con.close()

def classes():
    con=sqlite3.connect('sql.db')
    cur=con.cursor()
    cur.execute('''SELECT rowid,* FROM CLASSES''')
    output = cur.fetchall()
    for row in output:
        print(f'{row[0]} : {row[1]} at {row[3]} and Status is {row[4]}')
    con.commit()
    con.close()


# def webscrape():
#     baseurl="https://codeforces.com/api/user.status?handle="
#     handle="Aayush5sep"
#     count=25
#     finalurl=baseurl+handle+"&count="+str(count)
#     print(finalurl)
#     response = requests.get(finalurl)
#     data = response.json()
#     print(data)

# webscrape()

# assig_loop.start()
# classes.start()
# keep_alive()
