from telegram import *
from telegram.ext import *
from datetime import *
from pytz import *
import pandas as pd
from emoji import emojize
from num2words import num2words
#api file
import config



### Load data ###

deadlines = pd.read_csv("deadlines.csv")
deadlines['deadline'] = pd.to_datetime(deadlines['deadline'],
                                       format = '%Y-%m-%d').dt.date
deadlines['bonus cut off'] = pd.to_datetime(deadlines['bonus cut off'],
                                            format = '%Y-%m-%d').dt.date
deadlines['attempt by'] = pd.to_datetime(deadlines['attempt by'],
                                         format = '%Y-%m-%d').dt.date
deadlines['start'] = pd.to_datetime(deadlines['start'],
                                         format = '%Y-%m-%d').dt.date



### Establish the current date and desired lead time for reminders###

today = datetime.now(timezone('Asia/Singapore')).date()
##today = pd.Timestamp('2021-10-02').date()
lead_time = 3



### Define functions ###

def get_events(df, period):
    dates = pd.date_range(today,
                          periods=period).tolist()
    today_cols = ['start',
                  'deadline',
                  'bonus cut off',
                  'attempt by']
    future_cols = ['deadline',
                   'bonus cut off',
                   'attempt by']
    today_remind = []
    future_remind = []
    for i, row in deadlines.iterrows():
        if dates[0] in row[today_cols].values:
            today_remind.append(i)
    for date in dates:
        for i, row in deadlines.iterrows():
            if date in row[future_cols].values and i not in today_remind and i not in future_remind:
                future_remind.append(i)
    today_events = df.iloc[today_remind].reset_index(drop = True)
    future_events = df.iloc[future_remind].reset_index(drop = True)
    return today_events, future_events


def generate_msg(row):
    emojis = {'mission': ':airplane:',
              'side quest': ':small_airplane:',
              'contest': ':magic_wand:',
              'exam': ':people_hugging:',
              'lecture training': ':video_game:',
              'tutorial training': ':joystick:',
              'exam practice': ':book:',
              'forum': ':speech_balloon:',
              'lecture reflection': ':thought_balloon:'}
    
    msg = f"<b>{emojis[row['type']]}  {row['name']}</b>"
    
    # deadline
    if pd.notna(row['deadline']) and row['type']!='exam':
        dl = row['deadline'].strftime('%a, %d %b')
        msg += f'\nDeadline: <u>{dl}</u>'

    # exam
    elif pd.notna(row['deadline']) and row['type']=='exam':
        dl = row['deadline'].strftime('%a, %d %b')
        msg += f'\nExam date: <u>{dl}</u>'

    # attempt tutorial
    if pd.notna(row['attempt by']) and row['attempt by']>=today and row['type']=='tutorial training':
        ab = row['attempt by'].strftime('%a, %d %b')
        msg += f'\n<i>Attempt questions by <u>{ab}</u> to earn extra EXP</i>'

    # exp
    if pd.notna(row['exp']):
        msg += f'\nEXP: {int(row["exp"])}'

    # forum weekly
    if pd.notna(row['attempt by']) and row['type']=='forum':
        ab = row['attempt by'].strftime('%a, %d %b')
        msg += f'\n<i>Post on the forums by <u>{ab}</u> to earn forum EXP for the week</i>'

    # bonus cut off
    if pd.notna(row['bonus cut off']):
        bco = row['bonus cut off'].strftime('%a, %d %b')
        msg += f'\nBonus Cutoff: <u>{bco}</u>'

    # bonus exp
    if pd.notna(row['bonus exp']):
        msg += f'\nBonus EXP: {int(row["bonus exp"])}'

    # lecture reflections
    if pd.notna(row['start']) and row['type']=='lecture reflection':
        msg += f'\n<i>There is a lecture today!\nAfter the lecture, remember to post your reflections to earn forum EXP</i>'
    return msg


def compile_reminder(today_events, future_events):
    # title
    reminder = f'<u>Reminder{"s" if len(future_events)+len(today_events) > 1 else ""} for {today.strftime("%A, %d %b")}:</u>'

    # today
    reminder += f'\n\n<b>:rotating_light:  Today  :rotating_light:</b>'
    if len(today_events)==0:
        reminder += f'\n\n<i>:grin:  There are no deadlines today</i>'
    for i, row in today_events.iterrows():
        reminder += '\n\n' + generate_msg(row)

    # next lead_time days
    reminder += f'\n\n<b>:{num2words(lead_time-1)}:  Next {lead_time-1} Days  :{num2words(lead_time-1)}:</b>'
    if len(future_events)==0:
        reminder += f'\n\n<i>:grin:  There are no upcoming deadlines in the following {lead_time-1} days</i>'
    for i, row in future_events.iterrows():
        reminder += '\n\n' + generate_msg(row)
    # coursemology
    # reminder += '\n\n:rocket:  <a href="https://coursemology.org/courses/2104/assessments?category=2568&tab=4374">Coursemology</a>  :rocket:'
    # emojize
    reminder = emojize(reminder, use_aliases=True)
    return reminder



### Telegram stuff and sending reminders ###

API_Key = config.api_key
Chat_ID = "@CS1010S_Reminders"
#Chat_ID = "337648992"

bot = Bot(API_Key)
updater = Updater(API_Key, use_context = True)
updater.start_polling()

today_events, future_events = get_events(deadlines, lead_time)

if len(today_events)>0 or len(future_events)>0:
    msg = compile_reminder(today_events, future_events)
    coursemology_button = InlineKeyboardButton(text = emojize(':rocket:  Coursemology', use_aliases=True),
                                               url = "https://coursemology.org/courses/2104")
    channel_button = InlineKeyboardButton(text = emojize(':bell:  Join Channel', use_aliases=True),
                                          url = "https://t.me/CS1010S_reminders")
    keyboard = [[coursemology_button, channel_button]]
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    print(msg)
    bot.send_message(chat_id = Chat_ID,
                     text = msg,
                     parse_mode = 'html',
                     disable_web_page_preview = True,
                     reply_markup = keyboard_markup)

updater.stop()
