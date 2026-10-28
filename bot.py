import os
from dotenv import load_dotenv
load_dotenv()
import discord
import requests
import json
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

# --- database ---
db = sqlite3.connect("memes.db")
db.execute("""
CREATE TABLE IF NOT EXISTS memes (
    guild_id INTEGER,
    name TEXT,
    content TEXT,
    author_id INTEGER,
    uses INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, name)
)
""")
db.commit()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
meme = app_commands.Group(name="meme", description="Server inside-joke memes",
                          guild_only=True)

# --- autocomplete: suggests this server's meme names while typing ---
async def name_autocomplete(interaction: discord.Interaction, current: str):
    rows = db.execute(
        "SELECT name FROM memes WHERE guild_id=? AND name LIKE ? LIMIT 25",
        (interaction.guild_id, f"%{current.lower()}%"),
    ).fetchall()
    return [app_commands.Choice(name=r[0], value=r[0]) for r in rows]

@meme.command(name="add", description="Add a new inside joke")
async def add(interaction: discord.Interaction, name: str, content: str):
    name = name.lower().strip()
    try:
        db.execute("INSERT INTO memes (guild_id, name, content, author_id) VALUES (?,?,?,?)",
                   (interaction.guild_id, name, content, interaction.user.id))
        db.commit()
        await interaction.response.send_message(f"Added **{name}** 🎉")
    except sqlite3.IntegrityError:
        await interaction.response.send_message(
            f"**{name}** already exists in this server.", ephemeral=True)

@meme.command(name="call", description="Call an inside joke")
@app_commands.autocomplete(name=name_autocomplete)
async def call(interaction: discord.Interaction, name: str):
    row = db.execute("SELECT content FROM memes WHERE guild_id=? AND name=?",
                     (interaction.guild_id, name.lower())).fetchone()
    if row is None:
        await interaction.response.send_message("No such meme here.", ephemeral=True)
        return
    db.execute("UPDATE memes SET uses = uses + 1 WHERE guild_id=? AND name=?",
               (interaction.guild_id, name.lower()))
    db.commit()
    await interaction.response.send_message(row[0])  # links auto-embed

@meme.command(name="random", description="Post a random inside joke")
async def random_meme(interaction: discord.Interaction):
    row = db.execute("SELECT content FROM memes WHERE guild_id=? ORDER BY RANDOM() LIMIT 1",
                     (interaction.guild_id,)).fetchone()
    await interaction.response.send_message(row[0] if row else "No memes yet! Use /meme add")

@meme.command(name="list", description="List this server's memes")
async def list_memes(interaction: discord.Interaction):
    rows = db.execute("SELECT name, uses FROM memes WHERE guild_id=? ORDER BY uses DESC",
                      (interaction.guild_id,)).fetchall()
    text = "\n".join(f"**{n}** ({u} uses)" for n, u in rows) or "Nothing yet."
    await interaction.response.send_message(text[:2000])

@meme.command(name="remove", description="Remove a meme (author or mods only)")
@app_commands.autocomplete(name=name_autocomplete)
async def remove(interaction: discord.Interaction, name: str):
    row = db.execute("SELECT author_id FROM memes WHERE guild_id=? AND name=?",
                     (interaction.guild_id, name.lower())).fetchone()
    if row is None:
        await interaction.response.send_message("No such meme.", ephemeral=True)
        return
    is_mod = interaction.user.guild_permissions.manage_messages
    if interaction.user.id != row[0] and not is_mod:
        await interaction.response.send_message("Only the author or a mod can remove it.",
                                                ephemeral=True)
        return
    db.execute("DELETE FROM memes WHERE guild_id=? AND name=?",
               (interaction.guild_id, name.lower()))
    db.commit()
    await interaction.response.send_message(f"Removed **{name}**.")

bot.tree.add_command(meme)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])