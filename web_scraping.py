from os.path import abspath, realpath, dirname, join
import sys
import datetime

import pandas as pd
from bs4 import BeautifulSoup

private_path = realpath(abspath(join(dirname(__file__), '..', 'private')))
sys.path.insert(1, private_path)
import scraping_config

##############
#  Missions  #
##############

# parsing HTML file
missions_path = abspath(join(private_path, 'Missions.html'))
with open(missions_path, 'r') as missions_file:
    missions_html = missions_file.read()
    missions = pd.read_html(missions_html,
                            na_values=['-'],
                            converters={'Experience Points': int,
                                        'Bonus Experience Points': int})[0]
    missions_soup = BeautifulSoup(missions_html, 'html.parser')

# parsing links
missions_table = missions_soup.find('table')
missions_links = []
for tr in missions_table.find_all("tr"):
    th = tr.find("th")
    try:
        link = th.find('a')['href']
        missions_links.append(link)
    except:
        pass
missions['Link'] = missions_links
#print(missions.columns)

# sorting out the df
missions = missions[['Title', 'Experience Points', 'Bonus Experience Points',
                     'Bonus Cut Off', 'End At', 'Link']]

missions = missions[missions['Title'].str.contains(
    r'Mission|Side Quest|Contest', na=False)]

def mission_cat(title):
    if 'Mission' in title:
        return 'Mission'
    if 'Side Quest' in title:
        return 'Side Quest'
    if 'Contest' in title:
        return 'Contest'

missions['Type'] = missions['Title'].apply(mission_cat)
# print(missions)

###############
#  Tutorials  #
###############

# parsing HTML file
tutorials_path = abspath(join(private_path, 'Tutorial.html'))
with open(tutorials_path, 'r') as tutorials_file:
    tutorials_html = tutorials_file.read()
    tutorials = pd.read_html(tutorials_html,
                             na_values=['-'],
                             converters={
                                 'Experience Points': int,
                                 'Bonus Experience Points': int
                             })[0]
    tutorials_soup = BeautifulSoup(tutorials_html, 'html.parser')

# parsing links
tutorials_table = tutorials_soup.find('table')
tutorials_links = []
for tr in tutorials_table.find_all("tr"):
    th = tr.find("th")
    try:
        link = th.find('a')['href']
        tutorials_links.append(link)
    except:
        pass
tutorials['Link'] = tutorials_links
#print(tutorials.columns)

# sorting out the df
tutorials = tutorials[['Title', 'Experience Points', 'Bonus Experience Points',
                       'Bonus Cut Off', 'Link']]

tutorials['Type'] = 'Tutorial'

# tutorial attempt cutoff for participation EXP
first_monday = datetime.date(*scraping_config.week_1)
tut_attempts = pd.date_range(start=first_monday,
                             periods=len(tutorials) + len(scraping_config.no_tuts),
                             freq=scraping_config.tut_cutoff_day)
tut_attempts = tut_attempts.to_frame(index=False, name='Attempt By').drop(scraping_config.no_tuts).reset_index(drop=True)
#print(tut_attempts)
tutorials = pd.concat([tutorials, tut_attempts], axis=1)
#print(tutorials)

###############
#  Trainings  #
###############

# parsing HTML file
trainings_path = abspath(join(private_path, 'Trainings.html'))
with open(trainings_path, 'r') as trainings_file:
    trainings_html = trainings_file.read()
    trainings = pd.read_html(trainings_html,
                             na_values=['-'],
                             converters={
                                 'Experience Points': int,
                                 'Bonus Experience Points': int
                             })[0]
    trainings_soup = BeautifulSoup(trainings_html, 'html.parser')

# parsing links
trainings_table = trainings_soup.find('table')
trainings_links = []
for tr in trainings_table.find_all("tr"):
    th = tr.find("th")
    try:
        link = th.find('a')['href']
        trainings_links.append(link)
    except:
        pass
trainings['Link'] = trainings_links
#print(trainings.info())

# sorting out the df
trainings = trainings[['Title', 'Experience Points', 'Bonus Experience Points',
                       'Bonus Cut Off', 'Link']]

def training_cat(title):
    if 'Lecture' in title:
        return 'Lecture Training'
    if 'Debugging' in title:
        return 'Debugging'
    if 'Midterm' in title or 'Final' in title:
        return 'Exam Practice'

trainings['Type'] = trainings['Title'].apply(training_cat)
# print(trainings)

#########################################
#  Join Missions, Tutorials, Trainings  #
#########################################

deadlines = pd.concat([missions, tutorials, trainings], ignore_index=True)
time_cols = ['Bonus Cut Off', 'End At']
deadlines[time_cols] = deadlines[time_cols].apply(pd.to_datetime,
                                                                                      format='%d %b %H:%M',
                                                                                      errors='ignore')
for col in time_cols:
    deadlines[col] = deadlines[col].apply(lambda ts: ts.replace(year=scraping_config.year))
    deadlines[col] = deadlines[col].apply(lambda ts: ts.date())
#print(deadlines)

###########
#  Exams  #
###########

exams = pd.DataFrame.from_dict(scraping_config.exam_dates)
exams['Type'] = 'Exam'
#print(exams)

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
lectures = lectures.to_frame(index=False, name='Start At').drop(
    scraping_config.no_lecture_weeks).reset_index(drop=True)
lectures['Title'] = reflection_titles
lectures['Type'] = 'Reflections'
lectures['Link'] = scraping_config.reflections_link
#print(lectures)

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
#print(forum_titles)

# generate forum dates
forum_dates = []
forums = pd.date_range(start=first_monday, periods=15,
                       freq=scraping_config.lecture_day)
forums = forums.to_frame(index=False, name='Attempt By').drop(
    [0]).reset_index(drop=True)
forums['Title'] = forum_titles
forums['Type'] = 'Forum'
forums['Link'] = scraping_config.forum_link
# print(forums)

#########
#  CSV  #
#########

deadlines = pd.concat([exams, lectures, deadlines, forums], ignore_index=True)
cols = ['Title', 'Type', 'Attempt By', 'End At', 'Experience Points',
        'Bonus Cut Off', 'Bonus Experience Points', 'Start At', 'Link']
deadlines = deadlines[cols]
sorter = ['Exam', 'Reflections', 'Mission', 'Side Quest', 'Contest',
          'Lecture Training', 'Tutorial', 'Exam Practice', 'Forum', 'Debugging']
deadlines['Type'] = deadlines['Type'].astype('category')
deadlines['Type'].cat.set_categories(sorter, inplace=True)
deadlines = deadlines.sort_values(['Type', 'Title']).reset_index(drop=True)
print(deadlines)

if not scraping_config.test_mode:
    deadlines_path = abspath(join(private_path, 'deadlines.csv'))
    deadlines.to_csv(deadlines_path, index=False)
