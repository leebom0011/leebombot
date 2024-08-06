
import nextcord
from nextcord.ext import commands
import youtube_dl
import yt_dlp as youtube_dl
import asyncio
from gtts import gTTS
import os

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!") and "@", intents=nextcord.Intents.all())
                #  command_prefix 란 시작할 명령어


# 입장메시지
@bot.event
async def on_member_join(member):
    channel1 = bot.get_channel(1270033111845179482) # 입장메시지를 보낼 채널 아이디
    await channel1.send(f"```{member.name} 님 서버에 오신 것을 환영합니다.```")  # 입장하였을때 채널에 메시지를 보냄
# 퇴장메시지
@bot.event
async def on_member_remove(member):
    channel1 = bot.get_channel(1270033123341500459) # 퇴장메시지를 보낼 채널 아이디
    await channel1.send(f"```{member.name} 님이 서버를 떠났습니다. 안녕히 가세요.```")  # 퇴장하였을때 채널에 메시지를 보냄

# 메세지 갯수 삭제
@bot.command(name="지우기")
async def delete_messages(ctx, num: int):
    if num < 1:
        await ctx.send("1 이상의 숫자를 입력하세요.")
        return
    
    # 사용자로부터 입력받은 숫자만큼 메시지를 삭제합니다.
    await ctx.channel.purge(limit=num + 1)  # 명령어 메시지도 포함하여 삭제
    await ctx.send(f'메시지를 삭제했습니다.', delete_after=2)


#"봇"이 준비 완료되면 터미널에 출력
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start("MTI2OTgwMzE1ODk3MzE4NjE2Mg.GV1zO6.QxRilEsHZU8vi1GuEFxZxf_U80Pt5B0P6ye120")

#인사 명령어
@bot.command(name="안녕") # 명령
async def 인사(ctx):
    await ctx.send(f'{ctx.author.name}님 오늘도 좋은 하루 보내시길 바래요.')  # 답변

@bot.command(name="하이")  # 명령
async def 하이(ctx):
    await ctx.send(f'{ctx.author.name}님 하이티비 입니다!')  # 답변

# 입장/퇴장 명령어
@bot.command(aliases=['입장'])
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel      # 입장코드
        await channel.connect()
        print("음성 채널 정보: {0.author.voice}".format(ctx))
        print("음성 채널 이름: {0.author.voice.channel}".format(ctx))
    else:
        embed = nextcord.Embed(title='음성 채널에 유저가 존재하지 않습니다.',  color=nextcord.Color(0xFF0000))
        await ctx.send(embed=embed)
 
@bot.command(aliases=['퇴장'])
async def out(ctx):
    try:
        await ctx.voice_client.disconnect()   #퇴장 코드
    except AttributeError as not_found_channel:
        embed = nextcord.Embed(title='봇이 존재하는 채널을 찾지 못하였습니다.',  color=nextcord.Color(0xFF0000))
        await ctx.send(embed=embed)

youtube_dl.utils.bug_reports_message = lambda: ''



ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



class Music(commands.Cog):  #음악재생을 위한 클래스
    def __init__(self, bot):
        self.bot = bot



    @commands.command(aliases=['노래'])
    async def play(self, ctx, *, url):


        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'플레이어 에러 : {e}') if e else None)
        embed = nextcord.Embed(title=f'현재 재생중인 음악 : {player.title}',  color=nextcord.Color(0xF3F781))
        await ctx.send(embed=embed)


    @commands.command(aliases=['볼륨'])
    async def volume(self, ctx, volume: int):


        if ctx.voice_client is None:
            embed = nextcord.Embed(title="음성 채널에 연결되지 않았습니다.",  color=nextcord.Color(0xFF0000))
            return await ctx.send(embed=embed)

        ctx.voice_client.source.volume = volume / 100  # 볼륨변경코드
        embed = nextcord.Embed(title=f"볼륨을 {volume}%으로 변경되었습니다.",  color=nextcord.Color(0x0040FF))
        await ctx.send(embed=embed)

    @commands.command(aliases=['삭제'])
    async def stop(self, ctx):


        await ctx.voice_client.disconnect()  # 음성채팅에서 나가는 코드

    @commands.command(aliases=['중지'])
    async def pause(self, ctx):


        if ctx.voice_client.is_paused() or not ctx.voice_client.is_playing():
            embed = nextcord.Embed(title="음악이 이미 일시 정지 중이거나 재생 중이지 않습니다.",  color=nextcord.Color(0xFF0000))
            await ctx.send(embed=embed)


        ctx.voice_client.pause()   # 정지하는 코드

    @commands.command(aliases=['재생'])
    async def resume(self, ctx):


        if ctx.voice_client.is_playing() or not ctx.voice_client.is_paused():   
            embed = nextcord.Embed(title="음악이 이미 재생 중이거나 재생할 음악이 존재하지 않습니다.",  color=nextcord.Color(0xFF0000))
            await ctx.send(embed=embed)

        ctx.voice_client.resume()    # 다시 재생하는 코드

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed = nextcord.Embed(title="음성 채널에 연결되어 있지 않습니다.",  color=nextcord.Color(0xFF0000))
                await ctx.send(embed=embed)
                raise commands.CommandError("작성자가 음성 채널에 연결되지 않았습니다.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


 
 
intents = nextcord.Intents.default()
intents.message_content = True





bot.add_cog(Music(bot))


bot.run("MTI2OTgwMzE1ODk3MzE4NjE2Mg.GV1zO6.QxRilEsHZU8vi1GuEFxZxf_U80Pt5B0P6ye120") #토큰