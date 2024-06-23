import asyncio
import os
import time
import wget
import yt_dlp as youtube_dl
from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import SearchVideos

is_downloading = False
DURATION_LIMIT = 99999  # Example duration limit in minutes

def get_text(message):
    # Assuming the function extracts the command argument from the message
    return message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""

def progress(current, total, pablo, c_time, status_message, file_stark):
    # Assuming a progress function for uploading progress
    time_now = time.time()
    if time_now - c_time >= 5:
        percentage = current * 100 / total
        speed = current / (time_now - c_time)
        eta = (total - current) / speed
        try:
            pablo.edit_text(
                f"{status_message}\n"
                f"Progress: {percentage:.2f}%\n"
                f"Speed: {speed:.2f} KB/s\n"
                f"ETA: {eta:.2f} seconds"
            )
        except Exception as e:
            pass

@Client.on_message(filters.command(["vsong", "video"]))
async def ytmusic(client, message: Message):
    global is_downloading

    if is_downloading:
        await message.reply_text("Another download is in progress, try again after sometime.")
        return

    urlissed = get_text(message)
    if not urlissed:
        await message.reply_text("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return

    pablo = await client.send_message(message.chat.id, f"`Getting {urlissed} from YouTube servers. Please wait.`")

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    results = search.result().get("search_result", [])

    if not results:
        await pablo.edit("No results found.")
        return

    video_info = results[0]
    video_link = video_info["link"]
    video_title = video_info["title"]
    video_id = video_info["id"]
    channel_name = video_info["channel"]
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    try:
        thumbnail = wget.download(thumbnail_url)
    except Exception as e:
        await pablo.edit(f"Failed to download thumbnail: {e}")
        return

    ydl_opts = {
        "format": "best",
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "quiet": True,
    }

    try:
        is_downloading = True
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_link, download=False)
            video_duration = round(video_info["duration"] / 60)

            if video_duration > DURATION_LIMIT:
                await pablo.edit(f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {video_duration} minute(s).")
                is_downloading = False
                return

            ydl.download([video_link])
            downloaded_file = f"{video_info['id']}.mp4"

    except Exception as e:
        await pablo.edit(f"Failed to download video: {e}")
        is_downloading = False
        return

    try:
        c_time = time.time()
        caption = (f"**Video Name:** `{video_title}`\n"
                   f"**Requested For:** `{urlissed}`\n"
                   f"**Channel:** `{channel_name}`\n"
                   f"**Link:** `{video_link}`")

        await client.send_video(
            message.chat.id,
            video=downloaded_file,
            duration=int(video_info["duration"]),
            file_name=video_info["title"],
            thumb=thumbnail,
            caption=caption,
            supports_streaming=True,
            progress=progress,
            progress_args=(pablo, c_time, f"`Uploading {urlissed} video from YouTube!`", downloaded_file),
        )
    except Exception as e:
        await pablo.edit(f"Failed to send video: {e}")
    finally:
        is_downloading = False
        await pablo.delete()
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if os.path.exists(thumbnail):
            os.remove(thumbnail)
