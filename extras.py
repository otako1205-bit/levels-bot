import discord
from discord.ext import commands
from discord import app_commands

class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="broadcast", description="ارسلي رسالة للخاص لكل الأعضاء")
    @app_commands.checks.has_permissions(administrator=True)
    async def broadcast(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("🪽 بدأت إرسال الرسائل...", ephemeral=True)
        
        success = 0
        failed = 0
        
        for member in interaction.guild.members:
            if member.bot:
                continue
            try:
                await member.send(f"🪽 {message}")
                success += 1
            except:
                failed += 1
        
        await interaction.followup.send(
            f"🪽 تم الإرسال!\n✅ وصل لـ {success} عضو\n❌ ما وصل لـ {failed} عضو",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Extras(bot))
