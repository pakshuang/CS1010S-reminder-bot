from os.path import abspath, realpath, dirname, join
import sys
import datetime
import json

import pandas as pd
from bs4 import BeautifulSoup

private_path = realpath(abspath(join(dirname(__file__), '..', 'private')))
sys.path.insert(1, private_path)
import scraping_config


###########
#  Login  #
###########

import requests
from lxml import html

session_requests = requests.session()
result = session_requests.get(scraping_config.login_url)

tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='csrf-token']/@value")))

result = session_requests.post(
    scraping_config.login_url,
    data = scraping_config.payload,
)


##########
#  Load  #
##########

missions_json = session_requests.get(scraping_config.missions_link).text
missions_dict = json.loads(missions_json)["assessments"]
missions_dict_normalized = pd.json_normalize(missions_dict)
missions = pd.DataFrame.from_dict(missions_dict_normalized)
missions.drop(missions[missions["published"] == False].index, inplace=True)

trainings_json = session_requests.get(scraping_config.trainings_link).text
trainings_dict = json.loads(trainings_json)["assessments"]
trainings_dict_normalized = pd.json_normalize(trainings_dict)
trainings = pd.DataFrame.from_dict(trainings_dict_normalized)
trainings.drop(trainings[trainings["published"] == False].index, inplace=True)

tutorials_json = session_requests.get(scraping_config.tutorials_link).text
tutorials_dict = json.loads(tutorials_json)["assessments"]
tutorials_dict_normalized = pd.json_normalize(tutorials_dict)
tutorials = pd.DataFrame.from_dict(tutorials_dict_normalized)
tutorials.drop(tutorials[tutorials["published"] == False].index, inplace=True)


##############
#  Missions  #
##############

missions = missions[missions['title'].str.contains(
    r'Mission|Side Quest|Contest', na=False)]

def mission_cat(title):
    if 'Mission' in title:
        return 'Mission'
    if 'Side Quest' in title:
        return 'Side Quest'
    if 'Contest' in title:
        return 'Contest'

missions['type'] = missions['title'].apply(mission_cat)

###############
#  Trainings  #
###############

def training_cat(title):
    if 'Lecture' in title:
        return 'Lecture Training'
    if 'Debugging' in title:
        return 'Debugging'
    if 'Midterm' in title or 'Final' in title:
        return 'Exam Practice'

trainings['type'] = trainings['title'].apply(training_cat)


###############
#  Tutorials  #
###############

tutorials['type'] = 'Tutorial'

# calculate tutorial attempt cutoff for participation EXP
first_monday = datetime.date(*scraping_config.week_1)
tut_attempts = pd.date_range(start=first_monday,
                             periods=len(tutorials) + len(scraping_config.no_tuts),
                             freq=scraping_config.tut_cutoff_day)
tut_attempts = tut_attempts.to_frame(index=False, name='attemptBy').drop(scraping_config.no_tuts).reset_index(drop=True)
tutorials = pd.concat([tutorials, tut_attempts], axis=1)


#########################################
#  Join Missions, Trainings, Tutorials  #
#########################################

deadlines = pd.concat([missions, trainings, tutorials], ignore_index=True)

# Correct deadlines with times early in the day
# E.g., A 2023-02-28 00:00:00 deadline has an effective deadline of 2023-02-27
time_cols = ['bonusEndAt.referenceTime', 'endAt.referenceTime']
deadlines[time_cols] = deadlines[time_cols].apply(pd.to_datetime, errors='ignore')

def correct_deadline_date(timestamp):
    if timestamp.hour >= 9:
        return timestamp
    else:
        return timestamp - pd.Timedelta(days=1)

for col in time_cols:
    deadlines[col] = deadlines[col].apply(correct_deadline_date)
    deadlines[col] = deadlines[col].apply(lambda ts: ts.date().isoformat())

deadlines['url'] = scraping_config.coursemology_link + deadlines['url'].astype(str)


###########
#  Exams  #
###########

exams = pd.DataFrame.from_dict(scraping_config.exam_dates)
exams['type'] = 'Exam'


########################
#  Lecture Reflection  #
########################

# generate reflection titles
reflection_titles = []
for i in range(1, scraping_config.lecture_count + 1):
    reflection_titles.append(f'Reflections: Lecture {i}')

# generate reflection dates
reflection_dates = []
lectures = pd.date_range(start=first_monday,
                         periods=scraping_config.lecture_count + len(scraping_config.no_lecture_weeks),
                         freq=scraping_config.lecture_day)
lectures = lectures.to_frame(index=False, name='startAt').drop(
    scraping_config.no_lecture_weeks).reset_index(drop=True)
lectures['title'] = reflection_titles
lectures['type'] = 'Reflections'
lectures['url'] = scraping_config.reflections_link


###########
#  Forum  #
###########

# generate forum titles
week_format = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6',
               'Recess Week',
               'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12', 'Week 13']
forum_titles = []
for i in range(len(week_format)):
    forum_titles.append(f'Forum Participation: {week_format[i]}')

# generate forum dates
forum_dates = []
forums = pd.date_range(start=first_monday, periods=15,
                       freq=scraping_config.lecture_day)
forums = forums.to_frame(index=False, name='attemptBy').drop(
    [0]).reset_index(drop=True)
forums['title'] = forum_titles
forums['type'] = 'Forum'
forums['url'] = scraping_config.forum_link


#########
#  CSV  #
#########

deadlines = pd.concat([exams, lectures, deadlines, forums], ignore_index=True)
cols = ['title', 'type', 'attemptBy', 'endAt.referenceTime', 'baseExp',
        'bonusEndAt.referenceTime', 'timeBonusExp', 'startAt', 'url']
deadlines = deadlines[cols]
sorter = ['Exam', 'Reflections', 'Mission', 'Side Quest', 'Contest',
          'Lecture Training', 'Tutorial', 'Exam Practice', 'Forum', 'Debugging']
deadlines['type'] = deadlines['type'].astype('category')
deadlines['type'] = deadlines['type'].cat.set_categories(sorter, ordered=True)
deadlines = deadlines.sort_values(['type', 'title']).reset_index(drop=True)
deadlines.columns = ['Title', 'Type', 'Attempt By', 'End At', 'Experience Points', 'Bonus Cut Off', 'Bonus Experience Points', 'Start At', 'Link']
print(deadlines)

if not scraping_config.test_mode:
    deadlines_path = abspath(join(private_path, 'deadlines.csv'))
    deadlines.to_csv(deadlines_path, index=False)
