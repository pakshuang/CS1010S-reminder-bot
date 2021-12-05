# CS1010S Reminder Bot
![GitHub release (latest by date)](https://img.shields.io/github/v/release/pakshuang/CS1010S-Reminder-Bot)

Telegram bot that reminds students about deadlines, exams, and more for the NUS module CS1010S Programming Methodology.
[Telegram Channel where bot is deployed](https://t.me/CS1010S_reminders)

## Project Status:
- v3.0 has been released.
- I intend to deploy this bot for all subsequent semesters of CS1010S for the foreseeable future and possibly port the bot for other modules in the future
- v3.0 is meant to be the final major release, but any plans will be documented in [Issues](https://github.com/pakshuang/CS1010S-reminder-bot/issues)

## Project Summary:
- This Telegram bot sends students reminders through a public Telegram channel which also pushes reminders to a supergroup.
- Each morning, the bot determines which deadlines/reminders are due for that day, as well as the following 2 days (this lead time is customizable).
- Some tasks have multiple deadlines, such as Tutorials which have different dates to attempt by and for the bonus cutoff, only the relevant dates (and respective EXP values) are shown.
- The reminders for the day are compiled into a single reminder message that is nicely formatted with direct hyperlinks for assignments, emojis, font styles, and also uses Inline Keyboard Markup for links to the learning portal Coursemology and to subscribe to the channel.
- The bot utilizes the Telegram Bot API for broadcasting reminders, Beautiful Soup 4 for the web scraping of Coursemology for the deadlines data, and primarly Pandas for the generation of reminder messages.
- Features of the reminder messages are: Academic tasks reminders, Covid test reminders, Progress tracking, and exam countdowns.

## How the Progress Tracker works:
- The idea is to provide a reference for what level students should reach that week in order to be on track to reach level 50 by a certain target week (e.g. reach level 50 in Week 10 of the semester).
- It is not sufficient to provide a linearly extrapolated projection from Week 1 to the target week as the workload of assignments and thus available EXP will vary throughout the semester.
- Real-world student EXP data was taken from the AY21/22 Sem 1 lecture slides and superimposed onto a graph (left).
- The 3 lines were fitted to the data such that it provided a good range of progressions towards level 50, the "hardest" green line finishing the fastest but with a greater increase in level each week, the "easiest" orange line having the least increase in level each week but still finishing before the cutoff. Data from Coursemology indicates that 60% of the AY21/22 Sem 1 cohort reached level 50 by the cutoff date, meaning the orange line roughly projects the progression of the 40th percentile, so projections that fail to reach level 50 will not be shown by the Progress Tracker.
- The fitted lines are discretized by week so that the Tracker shows the target level to reach by the end of the week, which allows students more leeway as well as a greater capacity to plan for the week (right)

<p float="left">
  <img src="https://github.com/pakshuang/CS1010S-reminder-bot/blob/b987814d24c62235e9e89404bd8fa27edbe345ee/images/progress_tracker_model.png" width="400"/>
  <img src="https://github.com/pakshuang/CS1010S-reminder-bot/blob/b987814d24c62235e9e89404bd8fa27edbe345ee/images/progress_tracker_model_floored.png" width="400"/> 
</p>

![image](https://user-images.githubusercontent.com/81917538/144758516-6cee1b1a-2e14-4834-b9e1-56d4df8ae656.png)

## Sample of the bot at work:
<img src="https://user-images.githubusercontent.com/81917538/137580522-f1e34e43-36ec-4f3d-bbe6-634a963d8d14.png" alt="Sample" width="400"/>

## Impact:
<img src="https://user-images.githubusercontent.com/81917538/143457371-5f6621b2-9bfa-43d3-a44c-edd745e3b0bb.png" alt="Sample" width="400"/>
