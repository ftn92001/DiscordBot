import discord
from discord import ButtonStyle
from discord.ui import View, Button

class RetryView(View):
    def __init__(self, ctx, **kwargs):
        super().__init__(timeout=180)  # 設定按鈕會在 3 分鐘後失效
        self.ctx = ctx
        self.kwargs = kwargs
        self.command = ctx.command  # 保存整個指令物件

    @discord.ui.button(label="再試一次", style=ButtonStyle.primary, emoji="🔄")
    async def retry_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        # 更新原始訊息，移除按鈕
        await interaction.message.edit(view=None)
        # 創建新的 context 並設定指令
        new_ctx = await self.ctx.bot.get_context(interaction.message)
        new_ctx.command = self.command  # 設定指令
        await self.command(new_ctx, **self.kwargs)
