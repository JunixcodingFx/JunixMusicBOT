import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import json
import requests
import asyncio
from collections import deque


#==========Copyright==========

#Copyright 2025 by @junixcodingfx aka @Jonathan.T

#Hilfe? Kein Problem! hier ist unser Email addrese: Hilfe@junixfx.de

#oder Server: https://discord.gg/mW6YJ3GHfq

# Sie können das GitHub Repository deaktivieren und die Version manuell ändern, dies wird jedoch nicht empfohlen.
# Aus Sicherheitsgründen und für automatische Updates sollten Sie das GitHub Repository aktiv lassen.
# Eine Deaktivierung oder Entfernung des Repositories könnte zu Problemen und Sicherheitsrisiken führen.
#==========Copyright-End==========

# Bot Konfiguration
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# GitHub Auto-Updater Konfiguration
GITHUB_REPO = "JunixcodingFx/JunixMusicBOT"
CURRENT_VERSION = "2.0.0"
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

# Musik-Queue System
class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current_song = None
        self.is_playing = False
        self.volume = 1.0

    def add_song(self, song):
        self.queue.append(song)

    def get_next_song(self):
        if self.queue:
            return self.queue.popleft()
        return None

# Queue für jeden Server
queues = {}

# ID System für Songs mit Verbesserter Fehlerbehandlung
song_ids = {}

def setup_music_directory():
    if not os.path.exists('music'):
        os.makedirs('music')
    else:
        for filename in os.listdir('music'):
            if filename.endswith('.mp3'):
                song_id = str(len(song_ids) + 1).zfill(3)
                song_ids[song_id] = filename

def load_song_ids():
    try:
        if os.path.exists('song_ids.json'):
            with open('song_ids.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Fehler beim Laden der Song-IDs: {e}",
            color=discord.Color.red()
        )
        return {}

def save_song_ids():
    try:
        with open('song_ids.json', 'w', encoding='utf-8') as f:
            json.dump(song_ids, f, ensure_ascii=False, indent=2)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Fehler beim Speichern der Song-IDs: {e}",
            color=discord.Color.red()
        )

def generate_song_id():
    return str(len(song_ids) + 1).zfill(3)

# Initialisierung
setup_music_directory()
song_ids = load_song_ids()

# Verbesserte YouTube Download Optionen
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'music/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

async def play_next(ctx):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = MusicQueue()
    
    queue = queues[ctx.guild.id]
    if queue.queue:
        next_song = queue.get_next_song()
        if next_song:
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(next_song['file']),
                volume=queue.volume
            )
            ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx), bot.loop).result() if e is None else ctx.send(embed=discord.Embed(
                    title="❌ Fehler",
                    description=f"Ein Fehler ist aufgetreten: {e}",
                    color=discord.Color.red()
                ))
            )
            embed = discord.Embed(
                title="🎵 Aktuelle Wiedergabe",
                description=f"Spiele jetzt: {next_song['title']}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

@bot.event
async def on_ready():
    # Prüfe auf Updates beim Start
    if check_for_updates():
        embed = discord.Embed(
            title="⚠️ Update verfügbar",
            description="Bitte aktualisiere den Bot auf die neueste Version!",
            color=discord.Color.gold()
        )
        
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Unbekannter Befehl",
            description="Nutze `!hilfe` für eine Liste aller Befehle.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Ein Fehler ist aufgetreten: {str(error)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f'Latenz: {latency:.2f} ms',
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        embed = discord.Embed(
            title="❌ Fehler",
            description="Du musst in einem Sprachkanal sein!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if ctx.voice_client:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    else:
        await ctx.author.voice.channel.connect()
    
    embed = discord.Embed(
        title="✅ Erfolgreich beigetreten",
        description=f"Bin dem Kanal '{ctx.author.voice.channel}' beigetreten!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def play(ctx, *, query=None):
    if not query:
        embed = discord.Embed(
            title="ℹ️ Verwendung",
            description="Verwendung: `!play <Song-ID/URL/Suchbegriff>`",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return

    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            embed = discord.Embed(
                title="❌ Fehler",
                description="Du musst in einem Sprachkanal sein!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = MusicQueue()

    try:
        # URL oder Suche
        if query.startswith(('http://', 'https://', 'www.')):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                song_id = generate_song_id()
                song_ids[song_id] = os.path.basename(filename)
                save_song_ids()
                
                song_info = {
                    'file': filename,
                    'title': info['title'],
                    'id': song_id
                }
                
                queues[ctx.guild.id].add_song(song_info)
                
                embed = discord.Embed(
                    title="✅ Song hinzugefügt",
                    description=f"Zur Warteschlange hinzugefügt: {info['title']} (ID: {song_id})",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
                if not ctx.voice_client.is_playing():
                    await play_next(ctx)
        
        # Song-ID
        elif query in song_ids:
            filename = os.path.join('music', song_ids[query])
            if os.path.exists(filename):
                song_info = {
                    'file': filename,
                    'title': song_ids[query],
                    'id': query
                }
                queues[ctx.guild.id].add_song(song_info)
                
                embed = discord.Embed(
                    title="✅ Song hinzugefügt",
                    description=f"Zur Warteschlange hinzugefügt: {song_ids[query]}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
                if not ctx.voice_client.is_playing():
                    await play_next(ctx)
            else:
                embed = discord.Embed(
                    title="❌ Fehler",
                    description="Datei nicht gefunden!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Fehler",
                description="Ungültige Song-ID oder URL!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Ein Fehler ist aufgetreten: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def stop(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="❌ Fehler",
            description="Es wird gerade nichts abgespielt!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    ctx.voice_client.stop()
    queues[ctx.guild.id].queue.clear()
    
    embed = discord.Embed(
        title="⏹️ Wiedergabe gestoppt",
        description="Wiedergabe gestoppt und Warteschlange geleert!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="❌ Fehler",
            description="Es wird gerade nichts abgespielt!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    ctx.voice_client.stop()
    
    embed = discord.Embed(
        title="⏭️ Song übersprungen",
        description="Song wurde übersprungen!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def volume(ctx, vol: int = None):
    if vol is None:
        embed = discord.Embed(
            title="ℹ️ Verwendung",
            description="Verwendung: `!volume <0-100>`",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
        
    if not ctx.voice_client:
        embed = discord.Embed(
            title="❌ Fehler",
            description="Ich bin in keinem Sprachkanal!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    if not 0 <= vol <= 100:
        embed = discord.Embed(
            title="❌ Fehler",
            description="Lautstärke muss zwischen 0 und 100 liegen!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    queues[ctx.guild.id].volume = vol / 100
    if ctx.voice_client.source:
        ctx.voice_client.source.volume = vol / 100
    
    embed = discord.Embed(
        title="🔊 Lautstärke angepasst",
        description=f"Lautstärke auf {vol}% gesetzt!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    if not song_ids:
        embed = discord.Embed(
            title="ℹ️ Information",
            description="Keine Songs in der Bibliothek!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
        
    embed = discord.Embed(
        title="📚 Song-Bibliothek",
        color=discord.Color.blue()
    )
    
    songs_list = ""
    for song_id, filename in song_ids.items():
        songs_list += f"`{song_id}` - {filename}\n"
        
    # Teile die Liste auf, wenn sie zu lang ist
    if len(songs_list) > 1024:
        parts = [songs_list[i:i+1024] for i in range(0, len(songs_list), 1024)]
        for i, part in enumerate(parts, 1):
            embed.add_field(name=f"Seite {i}", value=part, inline=False)
    else:
        embed.description = songs_list
        
    await ctx.send(embed=embed)

@bot.command()
async def pause(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        embed = discord.Embed(
            title="❌ Fehler",
            description="Es wird gerade nichts abgespielt!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.pause()
    
    embed = discord.Embed(
        title="⏸️ Pausiert",
        description="Wiedergabe pausiert!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def resume(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_paused():
        embed = discord.Embed(
            title="❌ Fehler",
            description="Es ist nichts pausiert!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    ctx.voice_client.resume()
    
    embed = discord.Embed(
        title="▶️ Fortgesetzt",
        description="Wiedergabe fortgesetzt!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        embed = discord.Embed(
            title="❌ Fehler",
            description="Ich bin in keinem Sprachkanal!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
        
    await ctx.voice_client.disconnect()
    if ctx.guild.id in queues:
        del queues[ctx.guild.id]
    
    embed = discord.Embed(
        title="👋 Auf Wiedersehen",
        description="Auf Wiedersehen!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='hilfe', aliases=['help'])
async def hilfe(ctx):
    embed = discord.Embed(
        title="📖 Hilfe",
        description="Hier sind alle verfügbaren Befehle:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎵 Musik-Befehle",
        value="""
        `!play <ID/URL>` - Spielt Musik ab
        `!pause` - Pausiert die Wiedergabe
        `!resume` - Setzt Wiedergabe fort
        `!stop` - Stoppt die Wiedergabe
        `!skip` - Überspringt aktuellen Song
        `!volume <0-100>` - Ändert die Lautstärke
        `!list` - Zeigt alle verfügbaren Songs
        """,
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Allgemeine Befehle",
        value="""
        `!join` - Bot tritt Sprachkanal bei
        `!leave` - Bot verlässt Sprachkanal
        `!ping` - Zeigt Bot-Latenz
        """,
        inline=False
    )
    
    embed.set_footer(text="Du kannst mich hier ändern - Bei Fragen wende dich an die Endwklerer Jonathan.T " , icon_url="https://avatars.githubusercontent.com/u/162313298?s=400&u=5de53beb974f47dad7373049900b80f0b211998f&v=4")
    await ctx.send(embed=embed)

# Starte den Bot
bot.run('Bitte hier deinen Bot Token einfügen !')
