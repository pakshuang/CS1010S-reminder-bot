# CS1010S Reminder Bot
![GitHub release (latest by date)](https://img.shields.io/github/v/release/pakshuang/CS1010S-Reminder-Bot) ![AWS CodeBuild](https://codebuild.ap-southeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiTDN1NjRCTDQySk8yNnVvUzhkWWszWENmRmkxK0VPcm03QWNEd0lzVkhmRmFIL3k0bFVXdmxid0tEeDJnTmNSdGwwWUdFM2kxQ0ZVT25KOUZYRTN6TVBJPSIsIml2UGFyYW1ldGVyU3BlYyI6Imc1UnEvRklJWFVPbHVPbHEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main) 

Telegram bot that reminds students about deadlines, exams, and more for the NUS module CS1010S Programming Methodology
[Telegram Channel](https://t.me/CS1010S_reminders)

## Project Status
- I intend to deploy this bot for all subsequent semesters of CS1010S for the foreseeable future
- v3.0 is meant to be the final major release, but any new plans will be documented in [Issues](https://github.com/pakshuang/CS1010S-reminder-bot/issues)
- v3.1 ports the Bot into a form that can be deployed on AWS Lambda

## Sample
<img src="https://user-images.githubusercontent.com/81917538/144759067-78c65e57-6256-4703-bc52-17d6747afd1b.png" width="300"/>

## Impact
<img src="https://user-images.githubusercontent.com/81917538/143457371-5f6621b2-9bfa-43d3-a44c-edd745e3b0bb.png" alt="Sample" width="200"/>

## Bot Features
### Frontend
- Everyday, reminders for the day and the next 2 days are compiled into a single message
- This message is nicely formatted with direct hyperlinks for assignments, emojis, font styles, and also uses Inline Keyboard Markup for links to the learning portal Coursemology and to subscribe to the Channel.
- This message is broadcast on the [Telegram Channel](https://t.me/CS1010S_reminders) and the Channel automatically pushes to the Telegram Supergroup for the semester
- Some tasks have multiple deadlines, only the relevant dates (and respective EXP values) are shown.
- The components of the reminder message are:
  - Academic task reminders
  - COVID test reminders
  - Level progress tracking
  - Exam countdowns
### Backend
- CI/CD pipeline: Pushing to the private repository sends a webhook to AWS CodeBuild which pulls from the public and private repositories and triggers a new AWS Lambda build
- GitHub Webhooks for triggering AWS CodeBuild
- AWS CodeBuild for building
- AWS Simple Notification Service to notify me about the AWS CodeBuild build state
- AWS Lambda for hosting
- AWS EventBridge for scheduling the AWS Lambda function
- Beautiful Soup 4 for the web scraping of Coursemology for deadline data
- Primarly Pandas for the generation of reminder messages
- Telegram Bot API for broadcasting reminders

## How the Progress Tracker is designed:
### Disclaimer
This progress tracker is unofficial. It is an interpretation of the data in an attempt to provide realistic expectations for students to benchmark themselves, YMMV. Special thanks to [@wjiayis](https://github.com/wjiayis) for helping me design the tracker's models
### Concept
- The idea is to provide a reference for what level students should reach that week in order to be on track to reach level 50 by a certain target week (e.g. reach level 50 in Week 10 of the semester)
- It is not sufficient to provide a linearly extrapolated projection from Week 1 to the target week as the workload of assignments and thus available EXP will vary throughout the semester
### Data Analysis and Modelling
- Real-world student EXP data was taken from the AY21/22 Sem 1 lecture slides and superimposed onto a graph (left).
- The 3 lines were fitted to the data such that it provided a good range of progressions towards level 50, the "hardest" green line finishing the fastest but with a greater increase in level each week, the "easiest" orange line having the least increase in level each week but still finishing before the cutoff. Data from Coursemology indicates that 60% of the AY21/22 Sem 1 cohort reached level 50 by the cutoff date, meaning the orange line roughly projects the progression of the 40th percentile, so projections that fail to reach level 50 will not be shown by the Progress Tracker
- The fitted lines are discretized by week so that the Tracker shows the target level to reach by the end of the week, which allows students more leeway as well as a greater capacity to plan for the week (right)

<p float="left">
  <img src="https://github.com/pakshuang/CS1010S-reminder-bot/blob/b987814d24c62235e9e89404bd8fa27edbe345ee/images/progress_tracker_model.png" width="400"/>
  <img src="https://github.com/pakshuang/CS1010S-reminder-bot/blob/b987814d24c62235e9e89404bd8fa27edbe345ee/images/progress_tracker_model_floored.png" width="400"/> 
</p>
<img src="https://user-images.githubusercontent.com/81917538/144758516-6cee1b1a-2e14-4834-b9e1-56d4df8ae656.png" alt="Sample" width="300"/>
