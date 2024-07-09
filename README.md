# Discord Music Bot

A simple and feature-rich Discord music bot that can play music from YouTube in your Discord server.

## Description

This bot allows users to join a voice channel and play music from YouTube. The bot supports various commands to control music playback, including play, pause, resume, stop, skip, and queue management. It uses `yt_dlp` for downloading and extracting audio, and `FFmpeg` for audio processing.

## Requirements

- Python 3.7+
- `discord.py` library
- `yt_dlp` library
- `FFmpeg` (installed and accessible from the script)

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/discord-music-bot.git
    cd discord-music-bot
    ```

2. **Install dependencies:**
    ```sh
    pip install discord.py yt-dlp
    ```

3. **Install FFmpeg:**
    - Windows: [Download FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.
    - macOS: Install using Homebrew: `brew install ffmpeg`
    - Linux: Install using your package manager, e.g., `sudo apt install ffmpeg`

4. **Set up the bot token:**
    - Create a file named `.env` in the project root directory and add your bot token:
      ```env
      DISCORD_BOT_TOKEN=your_bot_token_here
      ```

## Usage

1. **Run the bot:**
    ```sh
    python bot.py
    ```

2. **Invite the bot to your server:**
    - Use the OAuth2 URL Generator in the Discord Developer Portal to generate an invite link with the `bot` and `applications.commands` scopes.

## Commands

| Command       | Alias | Description                                           | Usage                 |
|---------------|-------|-------------------------------------------------------|-----------------------|
| `!join`       |       | Tells the bot to join the voice channel               | `!join`               |
| `!leave`      |       | Makes the bot leave the voice channel                 | `!leave`              |
| `!play`       | `!p`  | Plays a song from a given URL                         | `!play <url>`         |
| `!pause`      |       | Pauses the currently playing song                     | `!pause`              |
| `!resume`     |       | Resumes the paused song                               | `!resume`             |
| `!stop`       |       | Stops the currently playing song and clears the queue | `!stop`               |
| `!skip`       | `!s`  | Skips the currently playing song                      | `!skip`               |
| `!nowplaying` | `!np` | Shows information about the currently playing song    | `!nowplaying`         |
| `!queue`      | `!q`  | Shows the current song queue                          | `!queue`              |
| `!remove`     |       | Removes a specific song from the queue                | `!remove <index>`     |
| `!shuffle`    |       | Shuffles the queue                                    | `!shuffle`            |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
