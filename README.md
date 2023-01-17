# CS1010S Reminder Bot

![GitHub release (latest by date)](https://img.shields.io/github/v/release/pakshuang/CS1010S-Reminder-Bot) ![AWS CodeBuild](https://codebuild.ap-southeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiTDN1NjRCTDQySk8yNnVvUzhkWWszWENmRmkxK0VPcm03QWNEd0lzVkhmRmFIL3k0bFVXdmxid0tEeDJnTmNSdGwwWUdFM2kxQ0ZVT25KOUZYRTN6TVBJPSIsIml2UGFyYW1ldGVyU3BlYyI6Imc1UnEvRklJWFVPbHVPbHEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main)

Telegram bot that reminds students about deadlines, exams, and more for the NUS module CS1010S Programming Methodology
[Telegram Channel](https://t.me/CS1010S_reminders)

## Project Status

- I intend to deploy this bot for all subsequent semesters of CS1010S for the foreseeable future
- Any new plans will be documented in [Issues](https://github.com/pakshuang/CS1010S-reminder-bot/issues)

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
