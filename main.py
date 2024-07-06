import discord
import sqlite3
import asyncio
import pytz
import os
import datetime as dt
from discord.ui import View, Button
from discord import ButtonStyle
from datetime import datetime, timezone
from discord.ext import commands
from discord.ext import tasks
from discord import Embed, Reaction, User
from gtts import gTTS


BOT_OWNER = [BOT_OWNER]

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), intents=intents, case_insensitive=True)

@bot.command(name='join')
async def join(ctx):
    await ctx.message.delete()
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Bin dem Voice-Channel {channel} beigetreten!')
    else:
        await ctx.send('Du bist in keinem Voice-Channel!')

@bot.command(name='leave')
async def leave(ctx):
    await ctx.message.delete()
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Habe den Voice-Channel verlassen!')
    else:
        await ctx.send('Ich bin in keinem Voice-Channel!')

@bot.command(name='play')
async def play(ctx):
    if ctx.voice_client:
        voice_client = ctx.voice_client

        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.filename.endswith('.mp3'):
                file_path = os.path.join(os.getcwd(), attachment.filename)
                await attachment.save(file_path)
                voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: print('done', e))
                await ctx.send(f'Abspielen von {attachment.filename} gestartet.')
            else:
                await ctx.send('Nur MP3-Dateien können abgespielt werden.')
        else:
            await ctx.send('Keine MP3-Datei angehängt.')
    else:
        await ctx.send('Ich bin in keinem Voice-Channel!')


@bot.event
async def on_guild_join(guild):
    category_name = "Log"
    channel_names = ["log", "log-messages"]
    
    category = await guild.create_category(category_name)
    
    for name in channel_names:
        channel = await guild.create_text_channel(name, category=category)
        
        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(guild.me, read_messages=True)  
        
        for role in guild.roles:
            if role.permissions.administrator:
                await channel.set_permissions(role, read_messages=True)

        await channel.set_permissions(guild.default_role, send_messages=False)
        await channel.set_permissions(guild.me, send_messages=True) 


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Security"))
    channel = bot.get_channel(1231533299361517568)
    if channel:
        await channel.send("Ich bin Gestartet ✔️")
    print("Ich bin Gestartet ✔️")
          
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    embed = discord.Embed(
        title="Gelöschte Nachricht",
        description=f"Die Nachricht von {message.author.mention} wurde im Kanal {message.channel.mention} gelöscht",
        color=discord.Color.red()
    )
    embed.add_field(name="Inhalt", value=message.content, inline=False)
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.set_footer(text=f"{message.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(message.guild.channels, name="log-messages")
    await log_channel.send(embed=embed)

    
@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user or before.author.bot:
        return 

    embed = discord.Embed(
        title="Bearbeitete Nachricht",
        description=f"Die Nachricht von {before.author.mention} im Kanal {before.channel.mention} wurde bearbeitet",
        color=discord.Color.orange()
    )
    embed.add_field(name="Vorher", value=before.content, inline=False)
    embed.add_field(name="Nachher", value=after.content, inline=False)
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_thumbnail(url=before.author.avatar.url) 
    embed.set_footer(text=f"{before.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(before.guild.channels, name="log-messages")
    await log_channel.send(embed=embed)



@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title="Neues Mitglied",
        description=f"{member.mention} ist dem Server beigetreten",
        color=discord.Color.green()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"{member.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(member.guild.channels, name="log")
    await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(
        title="Mitglied hat den Server verlassen",
        description=f"{member.mention} hat den Server verlassen",
        color=discord.Color.red()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"{member.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(member.guild.channels, name="log")
    await log_channel.send(embed=embed)
    
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"{member.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(member.guild.channels, name="log")
    await log_channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
            if entry.target == after and entry.before.nick != entry.after.nick:
                changed_by = entry.user
                break
        else:
            changed_by = "Unbekannt"

        embed = discord.Embed(
            title="Nickname geändert",
            description=f"Der Nickname von {before.mention} wurde geändert.\nGeändert von {changed_by.mention if isinstance(changed_by, discord.Member) else changed_by}",
            color=discord.Color.purple()
        )
        embed.add_field(name="Vorher", value=before.nick, inline=False)
        embed.add_field(name="Nachher", value=after.nick, inline=False)
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{before.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(before.guild.channels, name="log")
        await log_channel.send(embed=embed)

    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]

    for role in added_roles:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.target == after:
                added_by = entry.user
                break
        else:
            added_by = "Unbekannt"

        embed = discord.Embed(
            title="Rolle hinzugefügt",
            description=f"Die Rolle `{role.name}` wurde dem Mitglied {after.mention} hinzugefügt.\nHinzugefügt von {added_by.mention if isinstance(added_by, discord.Member) else added_by}",
            color=discord.Color.green()
        )
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{before.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(before.guild.channels, name="log")
        await log_channel.send(embed=embed)

    for role in removed_roles:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.target == after:
                removed_by = entry.user
                break
        else:
            removed_by = "Unbekannt"

        embed = discord.Embed(
            title="Rolle entfernt",
            description=f"Die Rolle `{role.name}` wurde dem Mitglied {after.mention} entfernt.\nEntfernt von {removed_by.mention if isinstance(removed_by, discord.Member) else removed_by}",
            color=discord.Color.red()
        )
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{before.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(before.guild.channels, name="log")
        await log_channel.send(embed=embed)



@bot.event
async def on_guild_role_create(role):
    creator = role.guild.owner
    embed = discord.Embed(
        title="Rolle erstellt",
        description=f"Die Rolle `{role.name}` wurde von {creator.mention} erstellt.",
        color=discord.Color.green()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{role.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(role.guild.channels, name="log")
    await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_create(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
        creator = entry.user
        break
    else:
        creator = "Unbekannt"

    embed = discord.Embed(
        title="Neuer Kanal erstellt",
        description=f"Ein neuer Kanal mit dem Namen `{channel.name}` wurde erstellt.\nKanal erstellt von {creator.mention}",
        color=discord.Color.green()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{channel.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(channel.guild.channels, name="log")
    await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    if channel.name == "log":
        for _ in range(5):
            for owner_id in BOT_OWNER:
                owner = bot.get_user(owner_id)
                if owner:
                    warn_embed = discord.Embed(
                        title="Warnung",
                        description="Der Kanal 'log' wurde gelöscht!",
                        color=discord.Color.red()
                    )
                    await owner.send(embed=warn_embed)
                else:
                    print(f"User with ID {owner_id} not found.")

    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        deleter = entry.user
        break
    else:
        deleter = "Unbekannt"

    embed = discord.Embed(
        title="Kanal gelöscht",
        description=f"Der Kanal `{channel.name}` wurde von {deleter.mention} gelöscht.",
        color=discord.Color.red()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{channel.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(channel.guild.channels, name="log")
    await log_channel.send(embed=embed)



@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
        if entry.target == user:
            banner = entry.user
            reason = entry.reason if entry.reason else "Kein Grund angegeben"
            break
    else:
        banner = "Unbekannt"
        reason = "Kein Grund angegeben"

    embed = discord.Embed(
        title="Mitglied gebannt",
        description=f"Das Mitglied `{user.mention}` wurde vom Server gebannt.\nGebannt von: {banner.mention}\nGrund: {reason}",
        color=discord.Color.red()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(guild.channels, name="log")
    await log_channel.send(embed=embed)
    
@bot.event
async def on_member_unban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
        if entry.target == user:
            unbanner = entry.user
            reason = entry.reason if entry.reason else "Kein Grund angegeben"
            break
    else:
        unbanner = "Unbekannt"
        reason = "Kein Grund angegeben"

    embed = discord.Embed(
        title="Mitglied entbannt",
        description=f"Das Mitglied {user.mention} wurde vom Server entbannt.\nEntbannt von: {unbanner.mention}\nGrund: {reason}",
        color=discord.Color.green()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(guild.channels, name="log")
    await log_channel.send(embed=embed)


@bot.event
async def on_guild_update(before, after):
    if before.name != after.name:
        embed = discord.Embed(
            title="Server umbenannt",
            description=f"Der Server wurde umbenannt von `{before.name} zu `{after.name}`",
            color=discord.Color.blue()
        )
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{after.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(after.channels, name="log")
        await log_channel.send(embed=embed)

    if before.icon != after.icon:
        embed = discord.Embed(
            title="Server Icon geändert",
            description=f"Das Icon des Servers wurde geändert",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=after.icon.url)
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{after.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(after.channels, name="log")
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_create(role):
    embed = discord.Embed(
        title="Rolle erstellt",
        description=f"Die Rolle `{role.name}` wurde von {role.guild.owner.mention} erstellt.",
        color=discord.Color.green()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{role.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(role.guild.channels, name="log")
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
        deleter = entry.user
        break
    else:
        deleter = "Unbekannt"

    embed = discord.Embed(
        title="Rolle gelöscht",
        description=f"Die Rolle `{role.name}` wurde von {deleter.mention} gelöscht.",
        color=discord.Color.red()
    )
    german_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(german_tz)
    embed.set_footer(text=f"{role.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(role.guild.channels, name="log")
    await log_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:  
        return

    log_channel = discord.utils.get(message.guild.channels, name="log-messages")
    if log_channel:
        embed = discord.Embed(
            title="Neue Nachricht",
            description=f"{message.author.mention} hat eine Nachricht im Kanal {message.channel.mention} gesendet:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Nachricht", value=message.content, inline=False)
        embed.add_field(name="Nachrichtenlink", value=f"[Zur Nachricht]({message.jump_url})", inline=False)
        embed.add_field(name="User ID", value=message.author.id, inline=True)  
        embed.add_field(name="Nachrichten-ID", value=message.id, inline=True)  
        embed.set_footer(text=f"{message.guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")
        
        if message.author.avatar:
            embed.set_thumbnail(url=message.author.avatar.url)
        
        await log_channel.send(embed=embed)

    if "discord.gg/" in message.content.lower() and not (message.author.guild_permissions.administrator or discord.utils.get(message.author.roles, name="partner")):
        warn_embed = discord.Embed(
            title="⚠️ Warnung ⚠️",
            description=f"{message.author.mention}, du darfst keine Discord-Links teilen!",
            color=discord.Color.red()
        )
        await message.delete()
        await message.channel.send(embed=warn_embed)

    await bot.process_commands(message)

    
@bot.event
async def on_guild_channel_update(before, after):
    modifier = None  
    
    if before.name != after.name:
        async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
            if entry.target.id == before.id:
                modifier = entry.user
                break 
                
        if modifier is None:
            modifier = "Unbekannt"
        
        embed = discord.Embed(
            title="Kanal umbenannt",
            description=f"Der Kanal wurde umbenannt von {modifier.mention if isinstance(modifier, discord.Member) else modifier} von `{before.name}` zu `{after.name}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"{before.guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")
        
        log_channel = discord.utils.get(before.guild.channels, name="log")
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_update(before, after):
    if before.name != after.name:
        async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
            if entry.target == before:
                modifier = entry.user
                break
        else:
            modifier = "Unbekannt"

        embed = discord.Embed(
            title="Rolle umbenannt",
            description=f"Die Rolle {before.name} wurde in {after.name} umbenannt.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Geändert von", value=modifier.mention)
        german_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(german_tz)
        embed.set_footer(text=f"{before.guild.name} | {current_time.strftime('%Y.%m.%d %H:%M')} Uhr")

        log_channel = discord.utils.get(before.guild.channels, name="log")
        await log_channel.send(embed=embed)
        
  
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    embed = discord.Embed(
        title="Reaktion hinzugefügt",
        description=f"{user.mention} hat eine Reaktion {reaction.emoji} zu einer Nachricht hinzugefügt.",
        color=discord.Color.green()
    )
    embed.add_field(name="Nachricht", value=f"[Zur Nachricht]({reaction.message.jump_url})")
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text=f"{reaction.message.guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(reaction.message.guild.channels, name="log")
    if log_channel:
        await log_channel.send(embed=embed)


@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    embed = discord.Embed(
        title="Reaktion entfernt",
        description=f"{user.mention} hat eine Reaktion {reaction.emoji} von einer Nachricht entfernt.",
        color=discord.Color.red()
    )
    embed.add_field(name="Nachricht", value=f"[Zur Nachricht]({reaction.message.jump_url})")
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text=f"{reaction.message.guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")

    log_channel = discord.utils.get(reaction.message.guild.channels, name="log")
    if log_channel:
        await log_channel.send(embed=embed)
      
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if before.channel is None:
            embed = discord.Embed(
                title="Voice beigetreten",
                description=f"{member.mention} ist dem Voice-Channel {after.channel.mention} beigetreten.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} | {datetime.now().strftime('%Y-%m-%d %H:%M')} Uhr")

            log_channel = discord.utils.get(member.guild.channels, name="log")
            if log_channel:
                await log_channel.send(embed=embed)

        elif after.channel is None:
            embed = discord.Embed(
                title="Voice verlassen",
                description=f"{member.mention} hat den Voice-Channel {before.channel.mention} verlassen.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} | {datetime.now().strftime('%Y-%m-%d %H:%M')} Uhr")

            log_channel = discord.utils.get(member.guild.channels, name="log")
            if log_channel:
                await log_channel.send(embed=embed)
    
    elif before.mute != after.mute:
        if after.mute:
            action = "gemutet"
            color = discord.Color.orange()
        else:
            action = "nicht mehr gemutet"
            color = discord.Color.blue()

        embed = discord.Embed(
            title="Stummschaltung geändert",
            description=f"{member.mention} wurde {action}.",
            color=color
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"{member.guild.name} | {datetime.now().strftime('%Y-%m-%d %H:%M')} Uhr")

        log_channel = discord.utils.get(member.guild.channels, name="log")
        if log_channel:
            await log_channel.send(embed=embed)    

            
@bot.command()
async def stop(ctx):
    if ctx.author.id in BOT_OWNER:
        await ctx.send("Bot wird gestoppt.")
        await bot.close()
    else:
        await ctx.send("Du hast keine Rechte, den Bot zu stoppen.")
        print(f"Unauthorized stop attempt by user ID {ctx.author.id}")

@bot.command()
async def wartungsarbeiten(ctx):
    if ctx.author.id in BOT_OWNER:
        await bot.change_presence(activity=discord.Game(name="Wartungsarbeiten"))
        await ctx.send("Bot befindet sich jetzt im Wartungsmodus.")
        await ctx.message.delete()
        print("Der Bot ist in Wartungsarbeiten.")
    else:
        await ctx.send("Dazu hast du keine Rechte!!!")
        print(f"Unauthorized wartungsarbeiten attempt by user ID {ctx.author.id}")
        
@bot.event
async def on_webhooks_update(channel):
    print("on_webhooks_update function called.")
    guild = channel.guild

    try:
        async for entry in guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
            print("Found webhook creation audit log.")
            if entry.extra and entry.extra.channel.id == channel.id:
                print("Webhook creation audit log is relevant to the updated channel.")
                webhook_id = entry.target.id
                try:
                    webhooks = await guild.webhooks()
                    print(f"Number of webhooks in the guild: {len(webhooks)}")
                    webhook = next((w for w in webhooks if w.id == webhook_id), None)
                    if webhook:
                        print("Webhook found.")
                        embed = discord.Embed(
                            title="Webhook erstellt",
                            description=f"Ein neuer Webhook wurde erstellt im Kanal {channel.mention}",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Webhook Name", value=webhook.name, inline=False)
                        embed.add_field(name="Channel ID", value=channel.id, inline=False)
                        embed.set_footer(text=f"{guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")
                        log_channel = discord.utils.get(guild.channels, name="log")
                        if log_channel:
                            await log_channel.send(embed=embed)
                    else:
                        print("Webhook not found.")
                except Exception as e:
                    print(f"Fehler beim Abrufen des Webhooks: {e}")
    except Exception as ex:
        print(f"Error occurred while fetching webhook creation logs: {ex}")
        pass

    async for entry in guild.audit_logs(action=discord.AuditLogAction.webhook_delete, limit=1):
        if entry.extra and entry.extra.channel.id == channel.id:
            webhook_id = entry.target.id
            try:
                embed = discord.Embed(
                    title="Webhook gelöscht",
                    description=f"Ein Webhook wurde gelöscht im Kanal {channel.mention}",
                    color=discord.Color.red()
                )
                embed.add_field(name="Webhook ID", value=webhook_id, inline=False)
                embed.add_field(name="Channel ID", value=channel.id, inline=False)
                embed.set_footer(text=f"{guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")
                log_channel = discord.utils.get(guild.channels, name="log")
                if log_channel:
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Fehler beim Verarbeiten des gelöschten Webhooks: {e}")

    async for entry in guild.audit_logs(action=discord.AuditLogAction.webhook_update, limit=1):
        if entry.extra and entry.extra.channel.id == channel.id:
            webhook_id = entry.target.id
            changes = entry.changes.before
            if 'name' in changes:
                try:
                    webhooks = await guild.webhooks()
                    webhook = next((w for w in webhooks if w.id == webhook_id), None)
                    if webhook:
                        embed = discord.Embed(
                            title="Webhook aktualisiert",
                            description=f"Ein Webhook wurde aktualisiert im Kanal {channel.mention}",
                            color=discord.Color.blue()
                        )
                        embed.add_field(name="Alter Webhook Name", value=changes['name'], inline=False)
                        embed.add_field(name="Neuer Webhook Name", value=webhook.name, inline=False)
                        embed.add_field(name="Channel ID", value=channel.id, inline=False)
                        embed.set_footer(text=f"{guild.name} | {datetime.now().strftime('%Y.%m.%d %H:%M')} Uhr")
                        log_channel = discord.utils.get(guild.channels, name="log")
                        if log_channel:
                            await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"Fehler beim Abrufen des Webhooks: {e}")
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

                
bot.run("Your discord bot token")
