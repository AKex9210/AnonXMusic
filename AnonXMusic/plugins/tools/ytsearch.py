import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Initialize Pyrogram Client
app = Client("my_bot")

@app.on_message(filters.command(["search"]))
async def ytsearch(client: Client, message: Message):
    try:
        # Check if the search query is provided
        if len(message.command) < 2:
            await message.reply_text("Usage: /search <query>")
            return
        
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("ꜱᴇᴀʀᴄʜɪɴɢ...")
        
        # Perform YouTube search
        results = YoutubeSearch(query, max_results=4).to_dict()
        
        # Prepare the response text
        text = "\n\n".join(
            f"**ᴛɪᴛʟᴇ:** {result['title']}\n"
            f"**ᴅᴜʀᴀᴛɪᴏɴ:** {result['duration']}\n"
            f"**ᴠɪᴇᴡꜱ:** {result['views']}\n"
            f"**ᴄʜᴀɴɴᴇʟ:** {result['channel']}\n"
            f"https://youtube.com{result['url_suffix']}"
            for result in results
        )
        
        # Send the search results
        await m.edit(text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ ʏᴛꜱᴇᴀʀᴄʜ: {e}")
        await message.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ꜱᴇᴀʀᴄʜɪɴɢ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
