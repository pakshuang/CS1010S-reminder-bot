from os.path import abspath, realpath, dirname, join
from os import environ
import sys
import datetime

import pytz
import pandas as pd
import telegram
from emoji import emojize
from num2words import num2words

#################
#  Load config  #
#################

private_path = realpath(abspath(join(dirname(__file__), '..', 'private')))
sys.path.insert(1, private_path)
import config

###############
#  Load data  #
###############

deadlines_path = abspath(join(private_path, 'deadlines.csv'))
deadlines = pd.read_csv(deadlines_path,
                        dtype={'Experience Points': 'Int64',
                               'Bonus Experience Points': 'Int64'})

time_cols = ['Attempt By', 'End At', 'Bonus Cut Off', 'Start At']
deadlines[time_cols] = deadlines[time_cols].apply(pd.to_datetime,
                                                  format='%Y-%m-%d',
                                                  errors='ignore')
for col in time_cols:
    deadlines[col] = deadlines[col].apply(lambda ts: ts.date())
# print(deadlines.info())

######################
#  Define functions  #
######################

def get_events(df, lead_time):
    dates = pd.date_range(today, periods=lead_time, closed='right').date
    today_cols = ['Attempt By', 'End At', 'Bonus Cut Off', 'Start At']
    future_cols = ['Attempt By', 'End At', 'Bonus Cut Off']
    today_events = df[df[today_cols].eq(today).any(
        axis=1)]  # .reset_index(drop=True)
    future_events = df[df[future_cols].isin(dates).any(axis=1)]
    future_events = future_events.drop(
        today_events.index.to_list(), errors='ignore').reset_index(drop=True)
    today_events = today_events.reset_index(drop=True)
    return today_events, future_events


def generate_msg(row):
    date_format = '%a, %d %b'

    # Header
    if pd.notna(row['Link']):
        msg = f"\n\n<b>{config.emojis.get(row['Type'], '')}  <a href='{row['Link']}'>{row['Title']}</a></b>"
    else:
        msg = f"\n\n<b>{config.emojis.get(row['Type'], '')}  {row['Title']}</b>"

    # End At
    if pd.notna(row['End At']) and row['Type'] != 'Exam':
        dl = row['End At'].strftime(date_format)
        msg += f'\nDeadline: <u>{dl}</u>'

    # Exam
    elif pd.notna(row['End At']) and row['Type'] == 'Exam':
        dl = row['End At'].strftime(date_format)
        msg += f'\nExam date: <u>{dl}</u>'
        msg += '\nAll the best!'

    # attempt tutorial
    if pd.notna(row['Attempt By']) and row['Attempt By'] >= today and row['Type'] == 'Tutorial':
        ab = row['Attempt By'].strftime(date_format)
        msg += f'\n<i>Attempt by <u>{ab}</u> to earn Participation EXP</i>'

    # Experience Points
    if pd.notna(row['Experience Points']):
        msg += f'\nEXP: {int(row["Experience Points"])}'

    # forum weekly
    if pd.notna(row['Attempt By']) and row['Type'] == 'Forum':
        ab = row['Attempt By'].strftime(date_format)
        msg += f'\n<i>Contribute to the forums by <u>{ab}</u> to earn Participation EXP for {config.week_format[week_delta-1]}</i>'

    # Bonus Cut Off
    if pd.notna(row['Bonus Cut Off']):
        bco = row['Bonus Cut Off'].strftime(date_format)
        msg += f'\nBonus Cutoff: <u>{bco}</u>'

    # Bonus Experience Points
    if pd.notna(row['Bonus Experience Points']):
        msg += f'\nBonus EXP: {int(row["Bonus Experience Points"])}'

    # Reflections
    if row['Type'] == 'Reflections':
        msg += f"\n<i>There's a lecture today!\nShare your lecture reflections on the forum thread to earn Participation EXP</i>"

    # FET tuts
    if "Tutorial" in row['Title'] and row['Type'] == 'FET' and config.FET_tuts:
        msg += '\n<i>Remember to take your FET before going to school</i>'

    # FET recs
    if "Recitation" in row['Title'] and row['Type'] == 'FET' and config.FET_recs:
        msg += '\n<i>Remember to take your FET before going to school</i>'

    return msg


def compile_reminder(today_events, future_events):
    # title
    reminder = f'<b>Reminder{"s" if len(future_events)+len(today_events) > 1 else ""} for {today.strftime("%A, %d %b")} ({nus_week})</b>'

    # today
    reminder += f'\n\n<b>:rotating_light:  TODAY  :rotating_light:</b>'
    if len(today_events) == 0:
        reminder += f'\n\n<i>:grin:  There are no deadlines today</i>'
    else:
        reminder += today_events.apply(generate_msg, axis=1).str.cat()

    # next lead_time days
    reminder += f'\n\n<b>:{num2words(config.lead_time - 1)}:  NEXT {config.lead_time - 1} DAYS  :{num2words(config.lead_time - 1)}:</b>'
    if len(future_events) == 0:
        reminder += f'\n\n<i>:grin:  There are no upcoming deadlines in the following {config.lead_time-1} days</i>'
    else:
        reminder += future_events.apply(generate_msg, axis=1).str.cat()
    return reminder


def progression(week_delta):
    msg = '<b>\n\n:chart_increasing:  Progress Tracker  :chart_increasing:</b>'
    #msg += '\n<i>Projected week to reach level 50</i>'
    #msg += '\n<i>Your level this week  :right_arrow:  Level 50 Week</i>'
    for i in range(len(config.target_weeks)):
        if config.target_weeks[i] > week_delta:
            target_level = round(50 * ((week_delta - config.target_intercepts[i] + 1) / (
                config.target_weeks[i] - config.target_intercepts[i] + 1)))
            #msg += f'\nLevel {target_level}  :right_arrow:  {week_format[target_week]}'
            msg += f'\nLevel {target_level} this week :right_arrow: Level 50 in {config.week_format[config.target_weeks[i]]}'
            #msg += f'\nLvl {target_level} this week :right_arrow: Lvl 50 in {week_format[target_week]}'
    return msg


def countdown(row):
    return f'\n{row["Title"]}: {row["End At"].strftime("%A, %d %b")} ({row["Countdown"]} day{"s" if row["Countdown"] > 1 else ""})'

####################
#  Telegram stuff  #
####################

def execute(event, context):
    global today, week_delta, nus_week

    # parse test_mode
    test_mode = bool(event['test'] != 'False')
    if test_mode:
        test_date = event['date']
        today = pd.Timestamp(test_date).date()
        chat_id = config.dev_id
    else:
        today = datetime.datetime.now(pytz.timezone('Asia/Singapore')).date()
        chat_id = config.channel_id

    # define week data
    sem_start_date = datetime.date(*config.week_1)
    week_delta = max(-1, min(17,
                            today.isocalendar()[1] - sem_start_date.isocalendar()[1]))
    # ^this is just error trapping, week_delta should never go beyond it's boundaries if deployed at the correct time
    nus_week = config.week_format[week_delta]
    
    # initialise bot
    bot = telegram.Bot(event['api_key'])

    # get relevant events
    today_events, future_events = get_events(deadlines, config.lead_time)

    # compile and send reminder if there are any relevant events
    if len(today_events) > 0 or len(future_events) > 0:
        # main reminders
        msg = compile_reminder(today_events, future_events)

        # level progression tracker
        if config.tracker_start <= week_delta < max(config.target_weeks):
            msg += progression(week_delta)

        # exam countdown
        exams = deadlines[(deadlines['Type'] == 'Exam') & ((deadlines['End At'] - today).dt.days <=
                                                        config.countdown_threshold) & (1 <= (deadlines['End At'] - today).dt.days)]
        exams = exams[['Title', 'End At']].sort_values(['End At'])
        if len(exams) > 0:
            exams['Countdown'] = (exams['End At'] - today).dt.days
            msg += f'\n\n<b>:hourglass_not_done:  Upcoming Exams  :hourglass_not_done:</b>'
            msg += exams.apply(countdown, axis=1).str.cat()

        # buttons
        coursemology_button = telegram.InlineKeyboardButton(text=emojize(':rocket:  Coursemology', use_aliases=True),
                                                            url="https://coursemology.org/courses/2104")
        channel_button = telegram.InlineKeyboardButton(text=emojize(':bell:  Join Channel', use_aliases=True),
                                                    url="https://t.me/CS1010S_reminders")
        buttons = [[coursemology_button, channel_button]]
        keyboard = telegram.InlineKeyboardMarkup(buttons)

        # broadcast message
        msg = emojize(msg, use_aliases=True)
        print(msg)
        bot.send_message(chat_id=chat_id,
                        text=msg,
                        parse_mode='html',
                        disable_web_page_preview=True,
                        reply_markup=keyboard)
    else:
        msg = f'No reminders today ({today})'
        print(msg)
        bot.send_message(
            text=msg, chat_id=config.dev_id)

# for testing locally
# event = {'test': 'True', 'date': '2021-09-15', 'api_key': config.api_key}
# execute(event, None)