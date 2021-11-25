# CS1010S-Reminder-Bot
![GitHub release (latest by date)](https://img.shields.io/github/v/release/pakshuang/CS1010S-Reminder-Bot)

Telegram bot that reminds students about deadlines, exams, and more for the NUS module CS1010S Programming Methodology.
[Telegram Channel where Bot is deployed](https://t.me/CS1010S_reminders)

## Improvement ideas that I'll eventually implement:
- Not urgent but how can I improve the bot to be more flexible? I've made the lead time customisable, so in general the compilation of messages into a single reminder is quite flexible. However, generating the messages themselves rely on a hard-coded control flow. The generation of messages in v2.0 is much more versatile than v1.0 as it can automatically recognise which information is available and how to present the information. There are still cases that are hard-coded like how "exam" type events are treated differently so that their "deadline" doesn't get called a deadline because that wouldn't sound right. What should the more elegant solution be? Create a new column just for exam dates (3 exams in total) and add another layer to the control flow? Or maybe this hardcoding is actually good because it's considering the event type before it generates the message. It just doesn't seem very elegant (though much more elegant than before) but it does the job. If I want to build upon this code for a different mod in the future, I will probably have to re-hard-code the message function because deadlines work very differently in different mods.
- Issue: These deadlines are only for those who have been keeping up with their assignments. If you submit some tasks late enough, all subsequent deadlines are delayed, meaning the reminders will not be entirely accurate for those individuals.

## Example
![image](https://user-images.githubusercontent.com/81917538/135656906-f279b696-0d8b-4af8-ab1b-1cefb9e4b6b5.png)
![image](https://user-images.githubusercontent.com/81917538/135706115-d104e4a0-26cc-458a-8f86-237ea4a3e722.png)

## Impact
![image](https://user-images.githubusercontent.com/81917538/143457371-5f6621b2-9bfa-43d3-a44c-edd745e3b0bb.png)
