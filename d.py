import discord
from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal
from discord import Interaction
import json

KLUP_DOSYASI = 'klupler.json'
intents = discord.Intents.all()
CHANNEL_ID = 1219298594604056648  

bot = commands.Bot(command_prefix='/', intents=intents)

async def send_club_message(channel):
    button = Button(label="Klüp Kurmak İçin Tıkla", style=discord.ButtonStyle.green)

    async def button_callback(interaction):
        await interaction.response.defer()
        await create_club_channels(interaction.guild, interaction.user)
        await interaction.followup.send("Klüp başarıyla kuruldu ve rol atanmıştır!", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await channel.send("Klüp kurmak için aşağıdaki butona tıklayın:", view=view)

@bot.event
async def on_ready():
    print(f'{bot.user} adıyla giriş yapıldı!')
    await bot.tree.sync()  
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await send_club_message(channel)
    else:
        print(f"Kanal bulunamadı: {CHANNEL_ID}")

async def create_club_channels(guild, member):
    klup_adi = "Klüp Adı"  
    klup_rengi = "#7289DA"  
    # Klüp adını ve rengini kullanarak bir rol oluştur
    color = discord.Colour(int(klup_rengi[1:], 16))
    club_role = await guild.create_role(name=klup_adi, colour=color, mentionable=True)

    # Üyeye klüp rolünü ata
    await member.add_roles(club_role)

    # Kategori oluştur ve rol izinlerini ayarla
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        club_role: discord.PermissionOverwrite(read_messages=True)
    }
    category = await guild.create_category(klup_adi, overwrites=overwrites)

    # Kategori altında kanallar oluştur
    await guild.create_text_channel("sohbet", category=category)
    await guild.create_voice_channel("sesli-sohbet", category=category)

    # Kullanıcıya bilgilendirme mesajı gönder
    text_channel = discord.utils.get(guild.text_channels, name="sohbet", category_id=category.id)
    await text_channel.send(f"{member.mention}, klübünüz açıldı! Hoş geldiniz.")

    print(f"{klup_adi} klübü ve ilgili kanallar başarıyla oluşturuldu.")


@bot.tree.command(name="kurulumt", description="Klübünüz için kurulum yapın.")
async def kurulum(interaction: Interaction):
    modal = KlupKurulumModal()
    await interaction.response.send_modal(modal)

class KlupKurulumModal(Modal, title="Klüp Kurulumu"):
    klup_adi = TextInput(label="Klüp Adı", placeholder="Klübünüzün adını girin")
    klup_rengi = TextInput(label="Klüp Rengi", placeholder="#RRGGBB şeklinde renk kodunu girin (Ör: #FF0000)")

    async def on_submit(self, interaction: Interaction):
        try:
            with open(KLUP_DOSYASI, 'r') as f:
                klupler = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            klupler = {}

        if self.klup_adi.value in klupler:
            await interaction.response.send_message("Bu klüp adı zaten alınmış. Lütfen başka bir isim deneyin.", ephemeral=True)
            return

        if not self.klup_rengi.value.startswith('#') or len(self.klup_rengi.value) != 7:
            await interaction.response.send_message("Renk, #RRGGBB formatında olmalıdır.", ephemeral=True)
            return
        color = discord.Colour(int(self.klup_rengi.value[1:], 16))

        klupler[self.klup_adi.value] = {"renk": self.klup_rengi.value}
        with open(KLUP_DOSYASI, 'w') as f:
            json.dump(klupler, f, indent=4)
        
        club_role = await interaction.guild.create_role(name=self.klup_adi.value, colour=color, mentionable=True)

        await interaction.response.send_message(f"Klübünüz başarıyla kuruldu! Adı: {self.klup_adi.value}, Renk: {self.klup_rengi.value}", ephemeral=True)

TOKEN = 'x'

bot.run(TOKEN)



