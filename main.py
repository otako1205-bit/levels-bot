import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"enabled": False, "channel_id": None, "level_message": "🪽 {user} وصلتِ للفل {level}!", "users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_xp_needed(level):
    return level * 100

data = load_data()

@bot.tree.command(name="setup", description="اختاري الشات اللي يرسل فيه رسائل اللفل")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    data["channel_id"] = channel.id
    save_data(data)
    await interaction.response.send_message(f"🪽 تم! رسائل اللفل راح تجي في {channel.mention}")

@bot.tree.command(name="enable-levels", description="تفعيل نظام اللفلات")
@app_commands.checks.has_permissions(administrator=True)
async def enable_levels(interaction: discord.Interaction):
    data["enabled"] = True
    save_data(data)
    await interaction.response.send_message("🪽 تم تفعيل نظام اللفلات!")

@bot.tree.command(name="disable-levels", description="إيقاف نظام اللفلات")
@app_commands.checks.has_permissions(administrator=True)
async def disable_levels(interaction: discord.Interaction):
    data["enabled"] = False
    save_data(data)
    await interaction.response.send_message("🪽 تم إيقاف نظام اللفلات!")

@bot.tree.command(name="reset-levels", description="تصفير كل اللفلات")
@app_commands.checks.has_permissions(administrator=True)
async def reset_levels(interaction: discord.Interaction):
    data["users"] = {}
    save_data(data)
    await interaction.response.send_message("🪽 تم تصفير كل اللفلات!")

@bot.tree.command(name="set-message", description="تغيير رسالة اللفل")
@app_commands.checks.has_permissions(administrator=True)
async def set_message(interaction: discord.Interaction, message: str):
    data["level_message"] = message
    save_data(data)
    await interaction.response.send_message(f"🪽 تم تغيير الرسالة!\nمثال: {message.replace('{user}', interaction.user.mention).replace('{level}', '5')}")

@bot.tree.command(name="give-xp", description="أعطي XP لعضو")
@app_commands.checks.has_permissions(administrator=True)
async def give_xp(interaction: discord.Interaction, member: discord.Member, amount: int):
    uid = str(member.id)
    if uid not in data["users"]:
        data["users"][uid] = {"xp": 0, "level": 1, "messages": 0}
    data["users"][uid]["xp"] += amount
    save_data(data)
    await interaction.response.send_message(f"🪽 تم إعطاء {amount} XP لـ {member.mention}")

@bot.tree.command(name="remove-xp", description="اسحبي XP من عضو")
@app_commands.checks.has_permissions(administrator=True)
async def remove_xp(interaction: discord.Interaction, member: discord.Member, amount: int):
    uid = str(member.id)
    if uid not in data["users"]:
        data["users"][uid] = {"xp": 0, "level": 1, "messages": 0}
    data["users"][uid]["xp"] = max(0, data["users"][uid]["xp"] - amount)
    save_data(data)
    await interaction.response.send_message(f"🪽 تم سحب {amount} XP من {member.mention}")

@bot.command(name="level")
async def level(ctx):
    uid = str(ctx.author.id)
    if uid not in data["users"]:
        await ctx.send("🪽 ما عندك XP بعد، ابدي تكلمين!")
        return
    user_data = data["users"][uid]
    xp = user_data["xp"]
    lvl = user_data["level"]
    messages = user_data["messages"]
    needed = get_xp_needed(lvl)
    embed = discord.Embed(title=f"لفل {ctx.author.display_name}", color=0xffb6c1)
    embed.add_field(name="🏆 اللفل", value=str(lvl), inline=True)
    embed.add_field(name="✨ XP", value=f"{xp}/{needed}", inline=True)
    embed.add_field(name="💬 الرسايل", value=str(messages), inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="top")
async def top(ctx):
    if not data["users"]:
        await ctx.send("🪽 ما في بيانات بعد!")
        return
    sorted_users = sorted(data["users"].items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    embed = discord.Embed(title="🏆 ليدربورد اللفلات", color=0xffb6c1)
    description = ""
    for i, (uid, udata) in enumerate(sorted_users, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else "عضو مغادر"
        description += f"**{i}.** {name} — لفل {udata['level']} | {udata['xp']} XP\n"
    embed.description = description
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot or not data["enabled"]:
        return

    uid = str(message.author.id)
    if uid not in data["users"]:
        data["users"][uid] = {"xp": 0, "level": 1, "messages": 0}

    xp_gain = random.randint(6, 8)
    data["users"][uid]["xp"] += xp_gain
    data["users"][uid]["messages"] += 1

    current_level = data["users"][uid]["level"]
    needed = get_xp_needed(current_level)

    if data["users"][uid]["xp"] >= needed:
        data["users"][uid]["level"] += 1
        data["users"][uid]["xp"] = 0
        new_level = data["users"][uid]["level"]

        if data["channel_id"]:
            channel = bot.get_channel(data["channel_id"])
            if channel:
                msg = data["level_message"].replace("{user}", message.author.mention).replace("{level}", str(new_level))
                await channel.send(msg)

    save_data(data)
    await bot.process_commands(message)

@bot.event
async def on_ready():
    try:
        await bot.load_extension("extras")
        await bot.load_extension("tawtheeq")
        await bot.tree.sync()
        print(f"✅ البوت شغالة: {bot.user}")
    except Exception as e:
        print(f"❌ خطأ في التحميل: {e}")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)

