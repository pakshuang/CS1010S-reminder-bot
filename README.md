# CS1010S Reminder Bot
![GitHub release (latest by date)](https://img.shields.io/github/v/release/pakshuang/CS1010S-Reminder-Bot)

Telegram bot that reminds students about deadlines, exams, and more for the NUS module CS1010S Programming Methodology.
[Telegram Channel where bot is deployed](https://t.me/CS1010S_reminders)

## Project Status:
- v3.0 is in progress, plans are documented in [Issues](https://github.com/pakshuang/CS1010S-reminder-bot/issues)

## Project Summary:
- This Telegram bot sends students reminders through a public Telegram channel which also pushes reminders to a supergroup.
- Each morning, the bot determines which deadlines/reminders are due for that day, as well as the following 2 days (this lead time is customizable).
- Some tasks have multiple deadlines, such as Tutorials which have different dates to attempt by and for the bonus cutoff, only the relevant dates (and respective EXP values) are shown.
- The reminders for the day are compiled into a single reminder message that is nicely formatted with different emojis, font styles, and also uses Inline Keyboard Markup for links to the learning portal Coursemology and to subscribe to the channel
- The bot utilizes the Telegram Bot API

## Sample of the bot at work:
<img src="https://user-images.githubusercontent.com/81917538/137580522-f1e34e43-36ec-4f3d-bbe6-634a963d8d14.png" alt="Sample" width="400"/>

## Impact:
<img src="https://user-images.githubusercontent.com/81917538/143457371-5f6621b2-9bfa-43d3-a44c-edd745e3b0bb.png" alt="Sample" width="400"/>