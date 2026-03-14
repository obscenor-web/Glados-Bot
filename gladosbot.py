import discord
from discord.ext import commands
import asyncio
import re
from datetime import datetime, timedelta, timezone
import platform
from keep_alive import keep_alive

# ===== CONFIGURAÇÕES =====
COMMAND_PREFIX = "!"
LOG_CHANNEL_NAME = "logs"
REACTION_EMOJI = "👁"
BOT_VERSION = "1.1.0"

BAD_WORDS = [
    "nigger","niga","puta","pqp","merda","bosta","porra","caralho",
    "foda","cacete","fodase","fdp","vagabundo","idiota","burro",
    "otário","retardado","escroto","babaca","cabrão","arrombado",
    "desgraçado","maldito","filho da puta","safado","canalha",
    "palhaço","doente","nojento","imbecil","cretino","fodido",
    "malandro","corno","otária","puta que pariu","cu","cusão",
    "porcaria","boçal","viado","bicha","buceta","bunda",
    "pau no cu","pau no rabo","safada","bumbum","porra","caralho","puta","bosta","merda","cacete","fodase","foda-se",
    "pqp","fdp","arrombado","desgraçado","maldito","inferno","idiota",
    "burro","otario","otário","retardado","imbecil","babaca","escroto",
    "cretino","nojento","doente","lixo","verme","boçal","palhaço",
    "canalha","safado","safada","vagabundo","vagabunda","corno","corna","buceta","pau","pinto","rola","cu","cú","cusao","cusão","bunda",
    "rabeta","piroca","xoxota","grelo","chupeta","punheta","siririca",
    "gozada","gozar","meter","transar","foder","fudendo","estupro","estuprador","estuprada","violacao","violação","abuso sexual",
    "assedio","assédio","pedofilia","pedofilo","pedófilo","pedofila",
    "exploracao sexual","exploração sexual","nigger","niga","negro imundo","macaco","preto imundo",
    "viado","bicha","traveco","sapatão","gay lixo",
    "judeu imundo","nazista","hitler","judeu","gay","trans","foda","fuder","fodido","fudido","fodeu","fudeu","matar","morte","morrer","assassinar","assassinato","tiro","bala",
    "arma","fuzil","ak47","pistola","revólver","facada","bomba",
    "explodir","genocidio","genocídio","massacre","chacina","suicidio","suicídio","se matar","me matar","morrer logo",
    "me cortar","auto mutilacao","automutilação","smt","pornografia infantil","cp","zoofilia","necrofila","necrofília",
    "canibal","canibalismo","epstein","diddy","jeffrey","raulzito","capitão hunter","hitler","nigga","carai"

]

# ===== BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
bot.launch_time = datetime.now(timezone.utc)

# ===== FUNÇÃO DE LOG =====
async def send_log(guild: discord.Guild, embed: discord.Embed):
    channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if channel:
        await channel.send(embed=embed)

# ===== EVENTOS =====
@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 🥚 Easter Egg GLaDOS
    if re.search(r"\bglados\b", message.content, re.IGNORECASE):
        await message.channel.send("**I'm always watching! 👁️**")

    # 🚫 Filtro de badwords
    for word in BAD_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
            try:
                await message.add_reaction(REACTION_EMOJI)
            except:
                pass

            embed = discord.Embed(
                title="🚨 Badword detectada",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Usuário", value=message.author.mention, inline=False)
            embed.add_field(name="Canal", value=message.channel.mention, inline=False)
            embed.add_field(name="Palavra", value=word, inline=False)
            embed.add_field(name="Mensagem", value=message.content[:1000], inline=False)

            await send_log(message.guild, embed)

            async def delete_later(msg):
                await asyncio.sleep(900)
                try:
                    await msg.delete()
                except:
                    pass

            bot.loop.create_task(delete_later(message))
            break

    await bot.process_commands(message)

# ===== COMANDOS =====
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    uptime = datetime.now(timezone.utc) - bot.launch_time

    embed = discord.Embed(
        title="📊 Status do Bot",
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Status", value="Online ✅", inline=True)
    embed.add_field(name="Latência", value=f"{latency}ms", inline=True)
    embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=False)
    embed.add_field(name="Sistema", value=f"{platform.system()} {platform.release()}", inline=False)
    embed.add_field(name="Versão", value=BOT_VERSION, inline=True)

    await ctx.send(embed=embed)

# ===== LIMPAR =====
@bot.command(aliases=["limpar"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"🧹 **{len(deleted) - 1} mensagens apagadas com sucesso**")

    # apaga a mensagem de confirmação depois de 5 segundos (opcional)
    await asyncio.sleep(5)
    await msg.delete()

    embed = discord.Embed(
        title="🧹 Mensagens apagadas",
        color=discord.Color.orange(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
    embed.add_field(name="Canal", value=ctx.channel.mention, inline=False)
    embed.add_field(name="Quantidade", value=len(deleted) - 1, inline=False)

    await send_log(ctx.guild, embed)

# ===== TIMEOUT =====
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="Não especificado"):
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)

    await ctx.send(f"⏳ {member.mention} recebeu timeout de {minutes} minutos.")

# ===== BAN =====
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Não especificado"):
    await member.ban(reason=reason)

    await ctx.send(f"🔨 {member} foi banido.")

    embed = discord.Embed(
        title="⛔ Ban aplicado",
        color=discord.Color.dark_red(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Usuário", value=str(member), inline=False)
    embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
    embed.add_field(name="Motivo", value=reason, inline=False)

    await send_log(ctx.guild, embed)

# ===== RODA O BOT =====
keep_alive()
import os
bot.run(os.getenv("DISCORD_TOKEN"))
