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
    # generate the dates of the next X days
    dates = pd.date_range(today, periods=lead_time, closed='right').date

    today_cols = ['Attempt By', 'End At', 'Bonus Cut Off', 'Start At']
    future_cols = ['Attempt By', 'End At', 'Bonus Cut Off']
    today_events = df[df[today_cols].eq(today).any(axis=1)]

    # remove duplicates from tasks with multiple dates
    future_events = df[df[future_cols].isin(dates).any(axis=1)]
    future_events = future_events.drop(today_events.index.to_list(), errors='ignore').reset_index(drop=True)

    today_events = today_events.reset_index(drop=True)
    return today_events, future_events


def generate_msg(row):
    date_format = '%a, %d %b'

    # Header
    if pd.notna(row['Link']):
        msg = f"\n\n{config.emojis.get(row['Type'], '')}  <a href='{row['Link']}'>{row['Title']}</a>"
    else:
        msg = f"\n\n{config.emojis.get(row['Type'], '')}  {row['Title']}"

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
        msg += f'\n<i>Attempt by <u>{ab}</u> to earn EXP</i>'

    # Experience Points
    if pd.notna(row['Experience Points']) and row['Experience Points'] > 0:
        msg += f'\nEXP: {int(row["Experience Points"])}'

    # forum weekly
    if pd.notna(row['Attempt By']) and row['Type'] == 'Forum':
        ab = row['Attempt By'].strftime(date_format)
        msg += f'\n<i>Contribute to the forums by <u>{ab}</u> 10:00 to earn EXP for {config.week_format[week_delta-1]}</i>'

    # Bonus Cut Off
    if pd.notna(row['Bonus Cut Off']):
        bco = row['Bonus Cut Off'].strftime(date_format)
        msg += f'\nBonus Cutoff: <u>{bco}</u>'

    # Bonus Experience Points
    if pd.notna(row['Bonus Experience Points']):
        msg += f'\nBonus EXP: {int(row["Bonus Experience Points"])}'

    # Reflections
    if row['Type'] == 'Reflections':
        msg += f"\n<i>There's a lecture today!\nAfter the lecture, share your reflections on the forum thread to earn EXP</i>"

    return msg


def compile_reminder(today_events, future_events):
    # title
    reminder = f'<b>Reminder{"s" if len(future_events)+len(today_events) > 1 else ""} for {today.strftime("%A, %d %b")} ({nus_week})</b>'

    # today
    reminder += f'\n\n<b>:rotating_light:  TODAY  :rotating_light:</b>'
    if len(today_events) == 0:
        reminder += f'\n\n<i>:relaxed: There are no deadlines today!</i>'
    else:
        reminder += today_events.apply(generate_msg, axis=1).str.cat()

    # next lead_time days
    reminder += f'\n\n<b>:{num2words(config.lead_time - 1)}:  NEXT {config.lead_time - 1} DAYS  :{num2words(config.lead_time - 1)}:</b>'
    if len(future_events) == 0:
        reminder += f'\n\n<i>:relaxed: There are no upcoming deadlines for the following {config.lead_time-1} days!</i>'
    else:
        reminder += future_events.apply(generate_msg, axis=1).str.cat()
    return reminder


def progression(week_delta):
    msg = '<b>\n\n:chart_increasing:  PROGRESS TRACKER  :chart_increasing:</b>'
    msg += '\n<i>For reference only:</i>'
    for i in range(len(config.target_weeks)):
        if config.target_weeks[i] > week_delta:
            target_level = round(50 * ((week_delta - config.target_intercepts[i] + 1) / (
                config.target_weeks[i] - config.target_intercepts[i] + 1)))
            if week_delta == 5:
                target_level += 3
            elif week_delta == 7:
                target_level -= 2
            elif week_delta == 11:
                target_level += 2
            msg += f'\nLevel {target_level} this week :right_arrow: Level 50 in {config.week_format[config.target_weeks[i]]}'
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
            msg += f'\n\n<b>:hourglass_not_done:  UPCOMING EXAMS  :hourglass_not_done:</b>'
            msg += exams.apply(countdown, axis=1).str.cat()

        # disclaimer
        msg += f'\n\n<i>{config.disclaimer} <a href="{config.disclaimer_link}">Disclaimer</a></i>'

        # buttons
        coursemology_button = telegram.InlineKeyboardButton(text=emojize(':rocket:  Coursemology', language='alias'),
                                                            url=config.coursemology_link)
        channel_button = telegram.InlineKeyboardButton(text=emojize(':bell:  Join Channel', language='alias'),
                                                    url=config.channel_link)
        buttons = [[coursemology_button, channel_button]]
        keyboard = telegram.InlineKeyboardMarkup(buttons)

        # broadcast message
        msg = emojize(msg, language='alias')
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
# event = {'test': 'True', 'date': '2022-09-13', 'api_key': config.api_key}
# execute(event, None)