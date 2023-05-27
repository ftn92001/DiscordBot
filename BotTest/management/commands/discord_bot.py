from django.core.management.base import BaseCommand
from django.conf import settings
from BotTest.services.ptt_beauty import get_beauty_imgs, dc_beauty_message
from BotTest.services.open_ai import call_completions
import discord
from discord import app_commands
from discord.ext import commands

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
    imgs, texts, urls = get_beauty_imgs(1)
    await ctx.send(dc_beauty_message(imgs, texts, urls))

@bot.hybrid_command(name="十連抽")
async def 十連抽(ctx):
    for _ in range(10):
        imgs, texts, urls = get_beauty_imgs(1)
        await ctx.send(dc_beauty_message(imgs, texts, urls))

@bot.hybrid_command(name="ai")
@app_commands.describe(question = "問題")
async def ai(ctx, question):
    await ctx.send(call_completions(question))

class Command(BaseCommand):
    help = "Run a discord bot"

    def handle(self, *args, **options):
        bot.run(settings.DISCORD_TOKEN)