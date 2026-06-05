import discord
from discord.ext import commands

class Tawtheeq(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="توثيق")
    async def tawtheeq(self, ctx, member: discord.Member):
        allowed_role = ctx.guild.get_role(1475214728061128874)
        
        if allowed_role not in ctx.author.roles:
            await ctx.send("🪽 ما عندك صلاحية استخدام هذا الأمر!")
            return
        
        role_to_remove = ctx.guild.get_role(1469317253689249994)
        role_to_give = ctx.guild.get_role(1462252055107338282)
        
        await member.remove_roles(role_to_remove)
        await member.add_roles(role_to_give)
        await ctx.send(f"🪽 تم توثيق {member.mention} بنجاح!")

async def setup(bot):
    await bot.add_cog(Tawtheeq(bot))
