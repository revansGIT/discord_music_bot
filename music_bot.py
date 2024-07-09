import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
import datetime
from collections import deque

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

# Ensure FFmpeg is accessible
ffmpeg_path = 'C:/Users/Sindar/Desktop/Python Bot/ffmpeg/bin/ffmpeg.exe'
if os.path.isfile(ffmpeg_path):
    ffmpeg_options['executable'] = ffmpeg_path
else:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        ffmpeg_options['executable'] = ffmpeg_path
    else:
        raise RuntimeError("FFmpeg is not accessible from this script")

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        except youtube_dl.DownloadError as e:
            print(f"Error downloading video: {e}")
            raise e

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
queue = deque()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send(f'{ctx.author.name} is not connected to a voice channel')
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        queue.clear()

@bot.command(name='play', aliases=['p'], help='To play a song from a given URL')
async def play(ctx, *, url=None):
    if url is None:
        await ctx.send("You need to provide a URL to play a song.")
        return

    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    # Check if the bot is already connected to a voice channel
    if voice_client:
        if voice_client.channel != channel:
            # Move the bot to the new channel and handle reconnection
            await voice_client.move_to(channel)
            await ctx.send(f'Moved to {channel}')
    else:
        # Connect the bot to the voice channel
        voice_client = await channel.connect()

    try:
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        return

    queue.append(player)

    if not voice_client.is_playing():
        await start_playing(ctx)

async def start_playing(ctx):
    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("Bot is not connected to a voice channel.")
        return

    if queue:
        player = queue.popleft()
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(handle_next(ctx), bot.loop))
        await ctx.send(f'**Now playing:** {player.title} ({str(datetime.timedelta(seconds=player.duration))})\nUploader: {player.uploader}')

async def handle_next(ctx):
    if queue:
        await start_playing(ctx)
    else:
        await ctx.send("Queue is empty. Use !play to add songs.")

@bot.command(name='pause', help='Pauses the currently playing song')
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused the song")
    else:
        await ctx.send("No song is currently playing")

@bot.command(name='resume', help='Resumes the paused song')
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed the song")
    else:
        await ctx.send("No song is paused")

@bot.command(name='stop', help='Stops the currently playing song')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        queue.clear()
        await ctx.send("Stopped the song and cleared the queue")
    else:
        await ctx.send("No song is currently playing")

@bot.command(name='skip', aliases=['s'], help='Skips the currently playing song')
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await start_playing(ctx)
    else:
        await ctx.send("No song is currently playing")

@bot.command(name='nowplaying', aliases=['np'], help='Shows information about the currently playing song')
async def nowplaying(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        player = voice_client.source
        embed = discord.Embed(title=player.title, url=player.url, color=discord.Color.green())
        embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=player.duration)), inline=True)
        embed.add_field(name="Uploader", value=player.uploader, inline=True)
        embed.set_thumbnail(url=player.thumbnail)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='queue', aliases=['q'], help='Shows the current song queue')
async def show_queue(ctx):
    if queue:
        embed = discord.Embed(title="Song Queue", color=discord.Color.blue())
        queue_list = [f"{idx+1}. {song.title} ({str(datetime.timedelta(seconds=song.duration))})" for idx, song in enumerate(queue)]
        embed.description = "\n".join(queue_list)
        await ctx.send(embed=embed)
    else:
        await ctx.send("The queue is currently empty.")

@bot.command(name='remove', help='Removes a specific song from the queue')
async def remove(ctx, index: int):
    if 0 < index <= len(queue):
        removed = queue[index - 1]
        del queue[index - 1]
        await ctx.send(f"Removed {removed.title} from the queue.")
    else:
        await ctx.send("Invalid index.")

@bot.command(name='shuffle', help='Shuffles the queue')
async def shuffle(ctx):
    if queue:
        random.shuffle(queue)
        await ctx.send("Shuffled the queue.")
    else:
        await ctx.send("The queue is currently empty.")

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        if before.channel is None and after.channel is not None:
            # Joined a voice channel
            return
        if before.channel is not None and after.channel is None:
            # Disconnected from a voice channel
            if member.guild.voice_client is not None:
                await member.guild.voice_client.disconnect()
                queue.clear()
        elif before.channel != after.channel:
            # Moved to a different voice channel
            voice_client = after.channel.guild.voice_client
            if voice_client:
                voice_client.stop()
                await voice_client.move_to(after.channel)
                if queue:
                    await start_playing(await bot.get_context(await bot.get_channel(after.channel.id).history(limit=1).flatten()[0]))

bot.run('your_discord_bot_token_here')
