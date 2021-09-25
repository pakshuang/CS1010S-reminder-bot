from telegram import *
from telegram.ext import *
from datetime import *
from pytz import *
import pandas as pd

### Load data ###

deadlines = pd.read_csv("deadlines.csv")
deadlines['deadline'] = pd.to_datetime(deadlines['deadline'],
                                       format = '%Y-%m-%d')
deadlines['bonus cut off'] = pd.to_datetime(deadlines['bonus cut off'],
                                            format = '%Y-%m-%d')
deadlines['attempt by'] = pd.to_datetime(deadlines['attempt by'],
                                         format = '%Y-%m-%d')

### Establish the current date ###

today = datetime.now(timezone('Asia/Singapore')).date()

### Define Telegram variables and start bot ###

API_Key = #"REDACTED"
Chat_ID = "@CS1010S_Reminders"

bot = Bot(API_Key)
updater = Updater(API_Key, use_context = True)
updater.start_polling()

### Generates and broadcasts message ###

def generate_msg(i, deadline_type):
    name = deadlines['name'][i]
    action_type = deadlines['type'][i]
    msg = f'<u>Reminder:</u>\n<i>{name}</i>'
    if action_type == 'exam':
        msg += '\nThere is an exam tomorrow!\nWishing you all the best!'
    if action_type != 'exam' and action_type != 'exam practice':
        exp = int(deadlines['exp'][i])
        msg += f"\nEXP: {exp}"
    if deadline_type == 'deadline' and action_type != 'exam':
        dl = deadlines['deadline'][i].strftime('%a, %d %B')
        msg += f"\nDeadline: {dl}"
    if deadline_type == 'bonus' or deadline_type == 'attempt':
        bonus_exp = int(deadlines['bonus exp'][i])
        bco = deadlines['bonus cut off'][i].strftime('%a, %d %B')
        msg += f"\nBonus EXP: {bonus_exp}\nBonus cutoff: {bco}"
    if deadline_type == 'attempt':
        ab = deadlines['attempt by'][i].strftime('%a, %d %B')
        msg += f"\nAttempt questions by {ab} for Tutorial EXP"
    bot.send_message(chat_id = Chat_ID,
                     text = msg,
                     parse_mode = 'html')
    return msg

### Checks for today's deadlines ###

for i in range(len(deadlines)):
    if deadlines['deadline'][i] == today:
        print(generate_msg(i, 'deadline'))
    if deadlines['bonus cut off'][i] == today:
        print(generate_msg(i, 'bonus'))
    if deadlines['attempt by'][i] == today:
        print(generate_msg(i, 'attempt'))

updater.stop()
