# Pantry Raid
Pantry Raid is a matchmaker for your pantry and your next meal. Find recipes that use only ingredients you have on hand. Save money by shopping your freezer and shelves, not the supermarket's.

Developed using [Flask](http://flask.pocoo.org/) for UNO's Introduction to Software Engineering course (CSCI 4830).

Visit the project on Heroku: https://pantryraids.herokuapp.com/

Travis CI: ![travis](https://travis-ci.com/jepeffer/Pantry-Raid.svg?token=rgvxzfsBUHqkuKBE9AuA&branch=master)

[Python API Documentation](https://jepeffer.github.io/Pantry-Raid/pantry_raid/)

[JavaScript Documentation](https://jepeffer.github.io/Pantry-Raid/jsdocs/)

## The Raiders
- Claire O. (@claire0): project manager
- Julian P. (@jepeffer): team tech support
- David R. (@dreamuno): software architect
- Tiff H. (@pagewin): scribe and Git POC

[Google Drive](https://drive.google.com/drive/folders/1QhSI7IcAfUReih-JnEPyzf5wukSTto59?usp=sharing)

[Project Tracker](https://github.com/jepeffer/Pantry-Raid/projects/1)
- [Milestone 1](https://github.com/jepeffer/Pantry-Raid/projects/1?card_filter_query=milestone%3A%22milestone+1%22)
- [Milestone 2](https://github.com/jepeffer/Pantry-Raid/projects/1?card_filter_query=milestone%3A%22milestone+2%22)
- [Milestone 3](https://github.com/jepeffer/Pantry-Raid/projects/1?card_filter_query=milestone%3A%22milestone+3%22)

[Slack](https://pantry-raid.slack.com)

## Getting Started
### Launch from the Command Line
Follow the instructions on setting up the virtual environment in `CONTRIBUTING.md`.
```bash
# Bash (recommended)
source .venv/bin/activate
FLASK_APP=pantry_raid/raid.py flask run

# Windows cmd
.venv\Scripts\activate
set FLASK_APP=pantry_raid\raid.py
flask run

# Windows PowerShell
.venv\Scripts\activate
$env:FLASK_APP = "pantry_raid\raid.py"
flask run
```

### Launch from VS Code
Using the default keybinds, you can press `F5` (debug mode) or `Ctrl+F5` (no debug) to launch the Flask application. VS Code's integrated terminal will show the running status of the server and any requests made to the server. To kill the server, you can press `Ctrl+C` within the terminal, or stop the process using the playback GUI (click or `Shift+F5`) that appears at the top of the VS Code window.
