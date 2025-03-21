from django.core.management.base import BaseCommand
from django.conf import settings
import discord
import os
from discord import app_commands
from discord.ext import commands
from BotTest.services.ptt_beauty import get_beauty_imgs, dc_beauty_message
from BotTest.services.open_ai import call_completions
from BotTest.services.gemini_service import create_image, edit_image

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '！'), intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('目前登入身份：', bot.user)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.hybrid_command(name="正妹")
async def 正妹(ctx):
    embeds = dc_beauty_message(*get_beauty_imgs(1))
    await ctx.send(embeds=embeds)

@bot.hybrid_command(name="十連抽")
async def 十連抽(ctx):
    embeds = dc_beauty_message(*get_beauty_imgs(10))
    await ctx.send(embeds=embeds)

@bot.hybrid_command(name="ai")
@app_commands.describe(question = "問題")
async def ai(ctx, question):
    # 超過3秒未回覆會報錯，需先用ctx.defer()延遲回覆
    await ctx.defer()
    message = call_completions(question)
    await ctx.send(message)

@bot.hybrid_command(name="生圖")
@app_commands.describe(prompt="提示詞")
async def create_photo(ctx, prompt: str):
    await ctx.defer()
    processing_msg = await ctx.send(f"正在生圖: {prompt}")

    image_path = await create_image(prompt, str(ctx.author.id))
    await processing_msg.delete()
    if image_path:
        await ctx.send(prompt, file=discord.File(image_path))
        # 刪除臨時檔案
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"刪除臨時檔案失敗：{str(e)}")
    else:
        await ctx.send("圖片生成失敗，請稍後再試。")

@bot.hybrid_command(name="修圖")
@app_commands.describe(prompt="修改提示詞")
async def edit_photo(ctx, prompt: str):
    await ctx.defer()
    attachment = None
    original_msg = None

    # 檢查當前訊息是否有圖片附件
    if hasattr(ctx.message, 'attachments') and ctx.message.attachments:
        attachment = next((att for att in ctx.message.attachments
                            if att.content_type and att.content_type.startswith('image/')), None)

    # 如果當前訊息沒有圖片，從歷史記錄尋找
    if not attachment:
        messages = [msg async for msg in ctx.channel.history(limit=10)]
        for msg in messages:
            if msg.attachments:
                img_att = next((att for att in msg.attachments
                                if att.content_type and att.content_type.startswith('image/')), None)
                if img_att:
                    attachment = img_att
                    original_msg = msg
                    break

    if not attachment:
        await ctx.send("找不到最近上傳的圖片，請先上傳一張圖片！")
        return

    if original_msg:
        await ctx.send(f"原始圖片: {original_msg.jump_url}\n")

    processing_msg = await ctx.send(f"正在修圖: {prompt}")

    # 讀取圖片數據
    image_bytes = await attachment.read()

    # 使用Gemini API處理圖片
    image_path = await edit_image(image_bytes, prompt, str(ctx.author.id))

    await processing_msg.delete()
    if image_path:
        await ctx.send(prompt, file=discord.File(image_path))
        # 刪除臨時檔案
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"刪除臨時檔案失敗：{str(e)}")
    else:
        await ctx.send("圖片處理失敗，請稍後再試。")

class Command(BaseCommand):
    help = "Run a discord bot"

    def handle(self, *args, **options):
        bot.run(settings.DISCORD_TOKEN)
