import discord
from discord.ext import commands
import youtube_dl
from typing import Optional
import os
import requests
import json

#==========Copyright==========

#Copyright 2025 by @junixcodingfx aka @Jonathan.T

#Hilfe? Kein Problem! hier ist unser Email addrese: Hilfe@junixfx.de

#oder Server: https://discord.gg/fUWBR2ym2f

#ihr könte die GITHUB REPO dektivieren und die Version manuell änder oder löscht das einfach :D
#==========Copyright==========

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

Token = " Hier kommt der BOT Token rein "

music_queue = []

# GitHub Auto-Updater Konfiguration
GITHUB_REPO = "JunixcodingFx/JunixMusicBOT"
CURRENT_VERSION = "1.0.0"
AUTO_UPDATE_ENABLED = True  # Kann auf False gesetzt werden um Auto-Updates zu deaktivieren

def check_for_updates():
    if not AUTO_UPDATE_ENABLED:
        return False
        
    try:
        response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")
        latest_release = json.loads(response.text)
        latest_version = latest_release["tag_name"]
        
        if latest_version != CURRENT_VERSION:
            print(f"Neue Version {latest_version} verfügbar! Aktuelle Version: {CURRENT_VERSION}")
            print(f"Download: {latest_release['html_url']}")
            return True
        return False
    except Exception as e:
        print(f"Fehler beim Prüfen auf Updates: {str(e)}")
        return False

# Erstelle Downloads-Ordner, falls nicht vorhanden
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.event
async def on_ready():
    print(f"Bot is ready and logged in as {bot.user}")
    print(f"Aktuelle Version: {CURRENT_VERSION}")
    print(f"Auto-Update ist {'aktiviert' if AUTO_UPDATE_ENABLED else 'deaktiviert'}")
    
    # Prüfe auf Updates beim Start
    if check_for_updates():
        print("Bitte aktualisiere den Bot auf die neueste Version!")
        
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

#==========Commands==========

@bot.command(name="join", help="Tritt deinem Sprachkanal bei")
async def join(ctx):
    if not ctx.message.author.voice:
        embed = discord.Embed(
            title="Fehler", 
            description="Du bist in keinem Sprachkanal",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    channel = ctx.message.author.voice.channel
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
        
    embed = discord.Embed(
        title="Erfolg", 
        description=f"Sprachkanal beigetreten: {channel.name}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="leave", help="Verlässt den Sprachkanal")
async def leave(ctx):
    if not ctx.voice_client:
        embed = discord.Embed(
            title="Fehler",
            description="Ich bin in keinem Sprachkanal",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    await ctx.voice_client.disconnect()
    embed = discord.Embed(
        title="Erfolg",
        description="Sprachkanal verlassen",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="play", help="Spielt ein Lied von YouTube URL oder Suchbegriff")
async def play(ctx, *, query: str):
    if not ctx.voice_client:
        await join(ctx)
        
    if not ctx.voice_client:  # Falls Join fehlgeschlagen
        return
        
    async with ctx.typing():
        try:
            # Erstelle eindeutigen Dateinamen
            filename = f"downloads/{ctx.message.id}.mp3"
            
            player = await YTDLSource.create_source(ctx, query, loop=bot.loop, download_path=filename)
            ctx.voice_client.play(
                player,
                after=lambda e: print(f'Player error: {e}') if e else os.remove(filename)
            )

            embed = discord.Embed(
                title="Spielt jetzt",
                description=f"[{player.title}]({player.web_url})\nHeruntergeladen als: {filename}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Fehler",
                description=f"Ein Fehler ist aufgetreten: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

@bot.command(name="stop", help="Stoppt die Wiedergabe und leert die Warteschlange")
async def stop(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="Fehler",
            description="Es wird nichts abgespielt",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.stop()
    music_queue.stop()
    embed = discord.Embed(
        title="Erfolg",
        description="Wiedergabe gestoppt und Warteschlange geleert",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="resume", help="Setzt die Wiedergabe fort")
async def resume(ctx):
    if not ctx.voice_client:
        embed = discord.Embed(
            title="Fehler",
            description="Ich bin in keinem Sprachkanal",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    if not ctx.voice_client.is_paused():
        embed = discord.Embed(
            title="Fehler",
            description="Nicht pausiert",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.resume()
    embed = discord.Embed(
        title="Erfolg",
        description="Wiedergabe fortgesetzt",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="pause", help="Pausiert das aktuelle Lied")
async def pause(ctx):
    if not ctx.voice_client:
        embed = discord.Embed(
            title="Fehler",
            description="Ich bin in keinem Sprachkanal",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    if ctx.voice_client.is_paused():
        embed = discord.Embed(
            title="Fehler",
            description="Bereits pausiert",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.pause()
    embed = discord.Embed(
        title="Erfolg",
        description="Wiedergabe pausiert",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="skip", help="Überspringt das aktuelle Lied")
async def skip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="Fehler",
            description="Es wird nichts abgespielt",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.stop()
    music_queue.skip()
    embed = discord.Embed(
        title="Erfolg",
        description="Lied übersprungen",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="queue", help="Zeigt die aktuelle Warteschlange")
async def queue(ctx):
    queue_content = music_queue.get_queue()
    if not queue_content:
        queue_content = "Warteschlange ist leer"
        
    embed = discord.Embed(
        title="Warteschlange",
        description=queue_content,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="clear", help="Leert die Warteschlange")
async def clear(ctx):
    music_queue.clear()
    embed = discord.Embed(
        title="Erfolg",
        description="Warteschlange geleert",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="remove", help="Entfernt ein Lied aus der Warteschlange nach Index")
async def remove(ctx, index: Optional[int] = None):
    if index is None:
        embed = discord.Embed(
            title="Fehler",
            description="Bitte gib einen Index zum Entfernen an",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    try:
        music_queue.remove(index)
        remove_song(index)
        embed = discord.Embed(
            title="Erfolg",
            description=f"Lied an Position {index} aus der Warteschlange entfernt",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except IndexError:
        embed = discord.Embed(
            title="Fehler",
            description="Ungültiger Warteschlangenindex",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="loop", help="Schaltet die Wiedergabe in den Loop-Modus um")
async def loop(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="Fehler",
            description="Es wird nichts abgespielt",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.loop = not ctx.voice_client.loop
    embed = discord.Embed(
        title="Erfolg",
        description="Loop-Modus aktiviert" if ctx.voice_client.loop else "Loop-Modus deaktiviert",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="volume", help="Stellt die Lautstärke ein")
async def volume(ctx, *, volume: Optional[int] = None):
    if volume is None:
        embed = discord.Embed(
            title="Fehler",
            description="Bitte gib eine Lautstärke zwischen 0 und 100 ein",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if not ctx.voice_client:
        embed = discord.Embed(
            title="Fehler",
            description="Ich bin in keinem Sprachkanal",
            color=discord.Color.red() 
        )
        await ctx.send(embed=embed)
        return

    ctx.voice_client.volume = volume / 100
    embed = discord.Embed(
        title="Erfolg",
        description=f"Lautstärke auf {volume}% gesetzt",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed) 

@bot.command(name="nowplaying", help="Zeigt das aktuelle Lied an")
async def nowplaying(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="Fehler",
            description="Es wird nichts abgespielt",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    song = ctx.voice_client.current
    embed = discord.Embed(
        title="Aktuelles Lied",
        description=f"[{song.title}]({song.web_url})",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="help", help="Zeigt alle Befehle an")
async def help(ctx):
    embed = discord.Embed(
        title="Hilfe",
        description="Hier sind alle Befehle:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!join", value="Tritt deinem Sprachkanal bei", inline=False)
    embed.add_field(name="!leave", value="Verlässt den Sprachkanal", inline=False)
    embed.add_field(name="!play <url>", value="Spielt ein Lied von einer YouTube URL", inline=False)
    embed.add_field(name="!stop", value="Stoppt die Wiedergabe und leert die Warteschlange", inline=False)
    embed.add_field(name="!resume", value="Setzt die Wiedergabe fort", inline=False)
    embed.add_field(name="!pause", value="Pausiert das aktuelle Lied", inline=False)
    embed.add_field(name="!skip", value="Überspringt das aktuelle Lied", inline=False)  
    embed.add_field(name="!queue", value="Zeigt die aktuelle Warteschlange", inline=False)
    embed.add_field(name="!clear", value="Leert die Warteschlange", inline=False)

@bot.command(name="update", help="Prüft auf Updates")
async def check_update(ctx):
    if check_for_updates():
        embed = discord.Embed(
            title="Update verfügbar!",
            description=f"Eine neue Version ist verfügbar!\nAktuelle Version: {CURRENT_VERSION}\nBitte aktualisiere den Bot.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="Kein Update verfügbar",
            description=f"Der Bot ist auf dem neuesten Stand (Version {CURRENT_VERSION})",
            color=discord.Color.green()
        )
    await ctx.send(embed=embed)

@bot.command(name="toggleupdate", help="Aktiviert/Deaktiviert Auto-Updates")
async def toggle_update(ctx):
    global AUTO_UPDATE_ENABLED
    AUTO_UPDATE_ENABLED = not AUTO_UPDATE_ENABLED
    embed = discord.Embed(
        title="Auto-Update Status",
        description=f"Auto-Updates sind jetzt {'aktiviert' if AUTO_UPDATE_ENABLED else 'deaktiviert'}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

bot.run(Token)