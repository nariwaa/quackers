import os
from datetime import datetime, timedelta
import sqlite3
from sqlite3 import Error
import json
import time
import random

scrpt_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = 'db/quackers.db'
database_path = os.path.join(scrpt_dir, folder_name)

import qlogs

CONNECTION = sqlite3.connect(database_path)
CURSOR = CONNECTION.cursor()
CURSOR.execute('CREATE TABLE IF NOT EXISTS "members" ("id" INTEGER UNIQUE, "name" TEXT, "coins" INTEGER, "daily" TEXT, "quackers" INTEGER, "mess" INTEGER, "created" TEXT, "streak" INTEGER DEFAULT 0, "epvoicet" INTEGER DEFAULT 0, "voiceh" INTEGER DEFAULT 0, "luck" INTEGER DEFAULT 0, "cryptoq" INTEGER DEFAULT 0, PRIMARY KEY("id" AUTOINCREMENT));')

def add(name, amount):
    CURSOR.execute("SELECT coins FROM members WHERE name = ?",(name,))
    rows = CURSOR.fetchall()
    data = rows[0]
    coins = data[0]

    coins += amount

    CURSOR.execute("UPDATE members SET coins = ? WHERE name = ?", (coins, name))
    CONNECTION.commit()

def luck(name, amount):
    CURSOR.execute("SELECT luck FROM members WHERE name = ?",(name,))
    rows = CURSOR.fetchall()
    data = rows[0]
    luck = data[0]

    luck += amount

    CURSOR.execute("UPDATE members SET luck = ? WHERE name = ?", (luck, name))
    CONNECTION.commit()

def export():
    global scrpt_dir
    export_path = os.path.join(scrpt_dir, "txt/database.json")

    CURSOR.execute('SELECT * FROM members')
    data = CURSOR.fetchall()

    # Convert data to a list of dictionaries
    column_names = [desc[0] for desc in CURSOR.description]
    json_data = []
    for row in data:
        json_data.append(dict(zip(column_names, row)))
    
    # Write JSON data to the output file
    with open(export_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def export_to_jsonl():
    global scrpt_dir
    export_path = os.path.join(scrpt_dir, "txt", "training_data.jsonl")

    CURSOR.execute('SELECT * FROM members')
    data = CURSOR.fetchall()

    # Convert data to a list of dictionaries
    column_names = [desc[0] for desc in CURSOR.description]
    json_data = []
    for row in data:
        json_data.append(dict(zip(column_names, row)))

    # Write data to a .jsonl file in the required format
    with open(export_path, 'w') as jsonl_file:
        for entry in json_data:
            # Construct the messages list based on your data
            messages = []

            # Optional: Add a system prompt if needed
            # messages.append({"role": "system", "content": "Your system prompt here."})

            # Assuming your database has 'user_input' and 'assistant_response' fields
            if 'user_input' in entry and 'assistant_response' in entry:
                messages.append({"role": "user", "content": entry['user_input']})
                messages.append({"role": "assistant", "content": entry['assistant_response']})
            else:
                # Skip entries without required fields
                continue

            # Create the JSON object
            json_line = {"messages": messages}

            # Write the JSON object as a line in the .jsonl file
            jsonl_file.write(json.dumps(json_line) + '\n')
            

def user_in_db(name):
    CURSOR.execute("SELECT COUNT(*) FROM members WHERE name = ?",(name,))
    data = CURSOR.fetchall()
    return(data[0][0])

def add_user(name):
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    CURSOR.execute('INSERT INTO members (name, coins, daily, quackers, mess, created, streak, epvoicet, voiceh, luck, cryptoq) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (name, 0, "", 0, 0, date, 0, 0, 0, 0, 0))
    CONNECTION.commit()
    qlogs.info(f'--QDB // ADDED USER : {name}')

def qcheck(name, amount):
    CURSOR.execute("SELECT coins FROM members WHERE name = ?",(name,))
    data = CURSOR.fetchall()
    coins = data[0][0]

    if coins >= amount:
        return(0)
    else:
        return(1)

def add_mess(name):
    CURSOR.execute("SELECT coins, mess FROM members WHERE name = ?",(name,))
    rows = CURSOR.fetchall()
    data = rows[0]
    coins = data[0]
    mess = data[1]

    coins += 1
    mess += 1

    CURSOR.execute("UPDATE members SET coins = ?, mess = ? WHERE name = ?", (coins, mess, name))
    CONNECTION.commit()

def add_quackers(name):
    CURSOR.execute("SELECT coins, quackers FROM members WHERE name = ?",(name,))
    rows = CURSOR.fetchall()
    data = rows[0]
    coins = data[0]
    quackers = data[1]

    coins += 9  #9 + 1coin from message => 10
    quackers += 1

    CURSOR.execute("UPDATE members SET coins = ?, quackers = ? WHERE name = ?", (coins, quackers, name))
    CONNECTION.commit()

def daily(name):
    date = datetime.now().strftime('%Y-%m-%d')
    CURSOR.execute("SELECT coins, daily, streak FROM members WHERE name = ?",(name,))
    rows = CURSOR.fetchall()
    data = rows[0]
    coins = data[0]
    daily = data[1]
    streak = data[2]

    if daily != date:
        amount = 100
        if daily == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'):
            streak += 1
            if streak > 20:
                amount = random.randint(250, 350)
            else:
                mult = 1 + (streak - 1) * (2.5 - 1) / (20 - 1)
                amount *= mult
            
        else:
            streak = 0

        coins += int((amount))

        CURSOR.execute("UPDATE members SET coins = ?, daily = ?, streak = ? WHERE name = ?", (coins, date, streak, name))
        CONNECTION.commit()
        qlogs.info(f'--QDB // DAILY : {name} : {coins}')
        if streak == 0:
            return(f'Successfully added {int((amount))} <:quackCoin:1124255606782578698> to {name} balance, total : {coins} QuackCoins')
        else:
            return(f'Successfully added {int((amount))} <:quackCoin:1124255606782578698> to {name} balance, total : {coins} QuackCoins // STREAK : {streak}')
    else:
        return(f'Daily QuackCoins have already been collected today for {name}')

def send(fname, dname, amount):
    if amount<0:
        return('The amount must be higher than 1 <:quackCoin:1124255606782578698>.')
    CURSOR.execute("SELECT coins FROM members WHERE name = ?",(fname,))
    data = CURSOR.fetchall()
    fcoin = data[0][0]
    if fcoin < amount:
        return("INSUFICIENT FUNDS")
    
    CURSOR.execute("UPDATE members SET coins = ? WHERE name = ?", (fcoin-amount, fname))
    CONNECTION.commit()
    CURSOR.execute("SELECT coins FROM members WHERE name = ?",(dname,))
    data = CURSOR.fetchall()
    dcoin = data[0][0]
    CURSOR.execute("UPDATE members SET coins = ? WHERE name = ?", (dcoin+amount, dname))
    CONNECTION.commit()
    qlogs.info(f'--QDB // SENT : {amount} // FROM : {fname} / TO : {dname}')
    return(f"{fname.capitalize()} sent {amount} <:quackCoin:1124255606782578698> to {dname.capitalize()}")

def coins(name):
    CURSOR.execute("SELECT coins FROM members WHERE name = ?", (name,))
    data = CURSOR.fetchall()
    return(f'{name.capitalize()} possède {data[0][0]} <:quackCoin:1124255606782578698>.')

def info(name):
    CURSOR.execute("SELECT coins, mess, created, epvoicet, voiceh, luck FROM members WHERE name = ?", (name,))
    data = CURSOR.fetchall()

    coins = data[0][0]
    CURSOR.execute("SELECT COUNT(*) FROM members WHERE coins > ?",(coins,))
    cdata = CURSOR.fetchall()
    rank = cdata[0][0] + 1
    return(data[0], rank)

def leaderboard():
    CURSOR.execute("SELECT * FROM members ORDER BY coins DESC LIMIT 10")
    data = CURSOR.fetchall()
    result = []
    emoji = ["🥇","🥈","🥉",""]
    for i in range(len(data)):
        emo = i
        if i >= 3:
            emo = 3
        bold = ""
        if i <= 2:
            bold = "**"
        result.append(f'{emoji[emo]} N.{i+1} :: {bold}{data[i][1].capitalize()}{bold} :: {data[i][2]} <:quackCoin:1124255606782578698>')
    return(result)

def voiceactive(name):
    timenow = int(time.time())
    CURSOR.execute("UPDATE members SET epvoicet = ? WHERE name = ?",(timenow, name))
    CONNECTION.commit()

def voicestalled(name):
    timenow = int(time.time())
    CURSOR.execute("SELECT epvoicet FROM members WHERE name = ?",(name,))
    data = CURSOR.fetchall()
    past = data[0][0]

    if past != 0 and past < timenow:
        secelapsed = timenow - past
        if secelapsed > 3600:
            hours = divmod(secelapsed, 3600)[0]
            amount = 50 * hours
            if amount > 500:
                amount = 500
            add(name, amount)
            #ADD HOURS TO DB
            CURSOR.execute("SELECT voiceh FROM members WHERE name = ?",(name,))
            raw = CURSOR.fetchall()
            data = raw[0][0]

            data += hours

            CURSOR.execute("UPDATE members SET voiceh = ? WHERE name = ?", (data, name))
            CONNECTION.commit()
            #LOGS
            qlogs.info(f"-- QDB // Added {amount} to {name} for being active in Voice Channel.")

    CURSOR.execute("UPDATE members SET epvoicet = ? WHERE name = ?",(0, name))
    CONNECTION.commit()
