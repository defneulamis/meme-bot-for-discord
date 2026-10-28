# Meme Bot for Discord

A Discord bot where **every server has its own collection of inside jokes**.
Save a text, GIF, or image link under a name, then call it whenever you want.
Memes saved in one server never show up in another.

## Commands

| Command | What it does |
|---|---|
| `/meme add name content` | Save a new meme |
| `/meme call name` | Post a saved meme (names autocomplete as you type) |
| `/meme random` | Post a random meme from this server |
| `/meme list` | Show all memes and how many times each was used |
| `/meme remove name` | Delete a meme (only the author or a mod with Manage Messages) |

## How it works

Memes are stored in a local SQLite database (`memes.db`). Each meme is saved
together with the server ID, which keeps every server's collection separate.

## Setup

**1. Clone the repo**
```
git clone https://github.com/defneulamis/meme-bot-for-discord.git
cd meme-bot-for-discord
```

**2. Install the requirements** (Python 3.10 or newer)
```
python -m pip install -r requirements.txt
```

**3. Create your bot**
- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create an application, open the **Bot** tab, and copy the token

**4. Add your token**
Create a file named `.env` in the project folder:
```
DISCORD_TOKEN=your_token_here
```

**5. Invite the bot to your server**
In the Developer Portal go to **OAuth2 → URL Generator**, tick the scopes
`bot` and `applications.commands`, and open the generated link.

**6. Run it**
```
python bot.py
```

The bot is only online while this command is running.

## Notes

- Never share or commit your `.env` file. It holds your bot's token.
- `memes.db` is created automatically the first time the bot runs.
- If a token is ever leaked, reset it right away in the Developer Portal.

## Built with

- [discord.py](https://github.com/Rapptz/discord.py)
- SQLite
- Python