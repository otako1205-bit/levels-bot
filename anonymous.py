async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        username = self.target.value.strip().lstrip("@")
        member = discord.utils.find(
            lambda m: m.name.lower() == username.lower() or m.display_name.lower() == username.lower(),
            interaction.guild.members
        )

        if not member:
            await interaction.followup.send("🪽 ما لقيت العضو، تأكدي من اليوزرنيم!", ephemeral=True)
            return

        if member == interaction.user:
            await interaction.followup.send("🪽 ما تقدرين ترسلين لنفسك!", ephemeral=True)
            return

        # إيمبد الرسالة المجهولة
        embed = discord.Embed(
            title=config["message_embed"]["title"],
            description=config["message_embed"]["description"],
            color=config["message_embed"]["color"]
        )
        embed.add_field(name="الرسالة", value=self.message.value, inline=False)
        embed.set_footer(text="Dev by adrianos")
        if config["message_embed"].get("image"):
            embed.set_image(url=config["message_embed"]["image"])

        try:
            await member.send(embed=embed, view=ReplyButton(interaction.user.id))
            await interaction.followup.send("🪽 تم إرسال رسالتك!", ephemeral=True)

            # لوق الرسالة في الروم السري
            log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(title="🪽 رسالة مجهولة جديدة", color=0xc9b1ff)
                log_embed.add_field(name="المرسل", value=f"{interaction.user} ({interaction.user.id})", inline=False)
                log_embed.add_field(name="المرسل إليه", value=f"{member} ({member.id})", inline=False)
                log_embed.add_field(name="الرسالة", value=self.message.value, inline=False)
                log_embed.add_field(name="الوقت", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
                log_embed.set_footer(text="Dev by adrianos")
                await log_channel.send(embed=log_embed)
        except:
            await interaction.followup.send("🪽 ما قدرت أرسل، العضو مغلق خاصه!", ephemeral=True)

# =====================
# زر الإرسال
# =====================
class AnonButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🪽رسـالة", style=discord.ButtonStyle.secondary, custom_id="anon_button")
    async def anon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AnonModal())

# =====================
# أوامر الأدمن
# =====================
class Anonymous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(AnonButton())

    @app_commands.command(name="setup-anonymous", description="أرسلي الإيمبد مع زر الرسالة المجهولة")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_anonymous(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title=config["button_embed"]["title"],
            description=config["button_embed"]["description"],
            color=config["button_embed"]["color"]
        )
        embed.set_footer(text="Dev by adrianos")
        if config["button_embed"].get("image"):
            embed.set_image(url=config["button_embed"]["image"])
        await channel.send(embed=embed, view=AnonButton())
        await interaction.response.send_message("🪽 تم!", ephemeral=True)

    @app_commands.command(name="set-button-embed", description="عدلي على إيمبد الزر")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_button_embed(self, interaction: discord.Interaction, title: str = None, description: str = None, color: str = None, image: str = None):
        if title:
            config["button_embed"]["title"] = title
        if description:
            config["button_embed"]["description"] = description
        if color:config["button_embed"]["color"] = int(color.strip("#"), 16)
        if image:
            config["button_embed"]["image"] = image
        save_config(config)
        await interaction.response.send_message("🪽 تم تعديل إيمبد الزر!", ephemeral=True)

    @app_commands.command(name="set-message-embed", description="عدلي على إيمبد الرسالة")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_message_embed(self, interaction: discord.Interaction, title: str = None, description: str = None, color: str = None, image: str = None):
        if title:
            config["message_embed"]["title"] = title
        if description:
            config["message_embed"]["description"] = description
        if color:
            config["message_embed"]["color"] = int(color.strip("#"), 16)
        if image:
            config["message_embed"]["image"] = image
        save_config(config)
        await interaction.response.send_message("🪽 تم تعديل إيمبد الرسالة!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Anonymous(bot))
