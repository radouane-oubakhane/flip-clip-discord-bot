import discord
import sqlite3
import random
import re
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

# Connect to SQLite database
conn = sqlite3.connect('videos.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS videos
             (id INTEGER PRIMARY KEY, user_id TEXT, link TEXT)''')
conn.commit()

# Supported platforms regex
supported_platforms = re.compile(
    r'(https?://)?(www\.)?(instagram\.com/reel/|facebook\.com/reel/|tiktok\.com/|youtube\.com/shorts/)'
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command(name='submit')
async def submit(ctx, link: str):
    if not supported_platforms.match(link):
        await ctx.send('🚫 That link doesn\'t look right! Make sure it\'s from Instagram Reels, Facebook Reels, TikTok, or YouTube Shorts.')
        return

    # Check if the link already exists in the database
    c.execute('SELECT * FROM videos WHERE link = ?', (link,))
    if c.fetchone():
        await ctx.send('⚠️ This link has already been submitted! Try submitting a different one.')
        return

    c.execute('INSERT INTO videos (user_id, link) VALUES (?, ?)', (str(ctx.author.id), link))
    conn.commit()
    await ctx.send(f'🎉 Thanks for the link, {ctx.author.mention}! I\'ll keep it safe and sound.')

@bot.command(name='random')
async def random_video(ctx):
    c.execute('SELECT link FROM videos WHERE user_id != ?', (str(ctx.author.id),))
    videos = c.fetchall()
    if not videos:
        await ctx.send('😢 No videos found! Be the first to submit one using `!submit <link>`.')
        return

    link = random.choice(videos)[0]
    await ctx.author.send(f'🎬 Here\'s a surprise video for you: {link}')
    await ctx.send(f'🎬 I\'ve sent you a surprise video in your DMs, {ctx.author.mention}! Make sure to check your messages from {bot.user.mention}.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('⚠️ Oops! You forgot to include a link. Try again with `!submit <link>`.')
    else:
        await ctx.send('❌ Something went wrong! Please try again.')

# Run the bot
bot.run(TOKEN)