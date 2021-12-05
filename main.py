from telegram import *
from telegram.ext import *
from datetime import *
from pytz import *
from os.path import abspath, dirname, join
import pandas as pd
from emoji import emojize
from num2words import num2words

#################
#  Load config  #
#################

from config import *
if test_mode:
    today = pd.Timestamp('2021-09-15').date()
    chat_id = "337648992"
else:
    today = datetime.now(timezone('Asia/Singapore')).date()
sem_start_date = date(*week_1)

###############
#  Load data  #
###############

deadlines_path = abspath(join(dirname(__file__), 'web scraping/deadlines.csv'))
deadlines = pd.read_csv(deadlines_path,
                        dtype={'Experience Points': 'Int64',
                               'Bonus Experience Points': 'Int64'})

time_cols = ['Attempt By', 'End At', 'Bonus Cut Off', 'Start At']
deadlines[time_cols] = deadlines[time_cols].apply(pd.to_datetime,
                                                  format='%Y-%m-%d',
                                                  errors='ignore')
for col in time_cols:
    deadlines[col] = deadlines[col].apply(lambda ts: ts.date())
#print(deadlines.info())

###########################
#  Calculate week number  #
###########################

week_format = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6',
               'Recess Week',
               'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12', 'Week 13',
               'Reading Week', 'Examination Weeks', 'Examination Weeks', 'Vacation']
# ^because of recess week, it helps to not think of the actual week numbers, but the indices instead
week_delta = max(-1, min(17,
                         today.isocalendar()[1] - sem_start_date.isocalendar()[1]))
# ^this is just error trapping, week_delta should never go beyond it's boundaries if deployed at the correct time
nus_week = week_format[week_delta]

######################
#  Define functions  #
######################

def get_events(df, lead_time):
    dates = pd.date_range(today, periods=lead_time, closed='right').date
    today_cols = ['Attempt By', 'End At', 'Bonus Cut Off', 'Start At']
    future_cols = ['Attempt By', 'End At', 'Bonus Cut Off']
    today_events = df[df[today_cols].eq(today).any(axis=1)]#.reset_index(drop=True)
    future_events = df[df[future_cols].isin(dates).any(axis=1)]
    future_events = future_events.drop(today_events.index.to_list(), errors='ignore').reset_index(drop=True)
    today_events = today_events.reset_index(drop=True)
    return today_events, future_events

def generate_msg(row):
    date_format = '%a, %d %b'

    # Header
    if pd.notna(row['Link']):
        msg = f"\n\n<b>{emojis.get(row['Type'], '')}  <a href='{row['Link']}'>{row['Title']}</a></b>"
    else:
        msg = f"\n\n<b>{emojis.get(row['Type'], '')}  {row['Title']}</b>"
    
    # End At
    if pd.notna(row['End At']) and row['Type']!='Exam':
        dl = row['End At'].strftime(date_format)
        msg += f'\nDeadline: <u>{dl}</u>'

    # Exam
    elif pd.notna(row['End At']) and row['Type']=='Exam':
        dl = row['End At'].strftime(date_format)
        msg += f'\nExam date: <u>{dl}</u>'
        msg += '\nAll the best!'

    # attempt tutorial
    if pd.notna(row['Attempt By']) and row['Attempt By']>=today and row['Type']=='Tutorial':
        ab = row['Attempt By'].strftime(date_format)
        msg += f'\n<i>Attempt by <u>{ab}</u> to earn Participation EXP</i>'

    # Experience Points
    if pd.notna(row['Experience Points']):
        msg += f'\nEXP: {int(row["Experience Points"])}'

    # forum weekly
    if pd.notna(row['Attempt By']) and row['Type']=='Forum':
        ab = row['Attempt By'].strftime(date_format)
        msg += f'\n<i>Contribute to the forums by <u>{ab}</u> to earn Participation EXP for {week_format[week_delta-1]}</i>'

    # Bonus Cut Off
    if pd.notna(row['Bonus Cut Off']):
        bco = row['Bonus Cut Off'].strftime(date_format)
        msg += f'\nBonus Cutoff: <u>{bco}</u>'

    # Bonus Experience Points
    if pd.notna(row['Bonus Experience Points']):
        msg += f'\nBonus EXP: {int(row["Bonus Experience Points"])}'

    # Reflections
    if row['Type']=='Reflections':
        msg += f"\n<i>There's a lecture today!\nShare your lecture reflections on the forum thread to earn Participation EXP</i>"
    
    # FET tuts
    if "Tutorial" in row['Title'] and row['Type']=='FET' and FET_tuts:
        msg += '\n<i>Remember to take your FET before going to school</i>'

    # FET recs
    if "Recitation" in row['Title'] and row['Type']=='FET' and FET_recs:
        msg += '\n<i>Remember to take your FET before going to school</i>'
    
    return msg


def compile_reminder(today_events, future_events):
    # title
    reminder = f'<b>Reminder{"s" if len(future_events)+len(today_events) > 1 else ""} for {today.strftime("%A, %d %b")} ({nus_week})</b>'

    # today
    reminder += f'\n\n<b>:rotating_light:  Today  :rotating_light:</b>'
    if len(today_events) == 0:
        reminder += f'\n\n<i>:grin:  There are no deadlines today</i>'
    else:
        reminder += today_events.apply(generate_msg, axis=1).str.cat()

    # next lead_time days
    reminder += f'\n\n<b>:{num2words(lead_time - 1)}:  Next {lead_time - 1} Days  :{num2words(lead_time - 1)}:</b>'
    if len(future_events) == 0:
        reminder += f'\n\n<i>:grin:  There are no upcoming deadlines in the following {lead_time-1} days</i>'
    else:
        reminder += future_events.apply(generate_msg, axis=1).str.cat()
    return reminder

def progression(week_delta):
    msg = '<b>\n\n:chart_increasing:  Progress Tracker  :chart_increasing:</b>'
    #msg += '\n<i>Projected week to reach level 50</i>'
    #msg += '\n<i>Your level this week  :right_arrow:  Level 50 Week</i>'
    for i in range(len(target_weeks)):
        if target_weeks[i] > week_delta:
            target_level = round(50 * ((week_delta - target_intercepts[i] + 1) / (target_weeks[i] - target_intercepts[i] + 1)))
            #msg += f'\nLevel {target_level}  :right_arrow:  {week_format[target_week]}'
            msg += f'\nLevel {target_level} this week :right_arrow: Level 50 in {week_format[target_weeks[i]]}'
            #msg += f'\nLvl {target_level} this week :right_arrow: Lvl 50 in {week_format[target_week]}'
    return msg

def countdown(row):
    return f'\n{row["Title"]}: {row["End At"].strftime("%d %b")} ({row["Countdown"]} day{"s" if row["Countdown"] > 1 else ""})'

####################
#  Telegram stuff  #
####################

# initialise bot
bot = Bot(api_key)
updater = Updater(api_key, use_context = True)
updater.start_polling()

# get relevant events
today_events, future_events = get_events(deadlines, lead_time)

# compile and send reminder if there are any relevant events
if len(today_events)>0 or len(future_events)>0:
    # main reminders
    msg = compile_reminder(today_events, future_events)

    # level progression tracker
    if tracker_start <= week_delta < max(target_weeks):
        msg += progression(week_delta)

    # exam countdown
    exams = deadlines[(deadlines['Type'] == 'Exam') & ((deadlines['End At'] - today).dt.days <= countdown_threshold) & (1 <= (deadlines['End At'] - today).dt.days)]
    exams = exams[['Title', 'End At']].sort_values(['End At'])
    if len(exams) > 0:
        exams['Countdown'] = (exams['End At'] - today).dt.days
        msg += f'\n\n<b>:hourglass_not_done:  Upcoming Exams  :hourglass_not_done:</b>'
        msg += exams.apply(countdown, axis=1).str.cat()

    # buttons
    coursemology_button = InlineKeyboardButton(text = emojize(':rocket:  Coursemology', use_aliases=True),
                                               url = "https://coursemology.org/courses/2104")
    channel_button = InlineKeyboardButton(text = emojize(':bell:  Join Channel', use_aliases=True),
                                          url = "https://t.me/CS1010S_reminders")
    keyboard = [[coursemology_button, channel_button]]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    # broadcast message
    msg = emojize(msg, use_aliases=True)
    print(msg)
    bot.send_message(chat_id = chat_id,
                     text = msg,
                     parse_mode = 'html',
                     disable_web_page_preview = True,
                     reply_markup = keyboard_markup)
else:
    print(f'No reminders today ({today})')
updater.stop()
