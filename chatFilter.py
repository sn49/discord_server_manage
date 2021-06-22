import discord
from discord.ext import commands, tasks
from discord.utils import get
import string
import re
import json
from datetime import datetime, timedelta
import os
import random
import asyncio
import emoji
from dateutil import tz

rootname = "data/server"

tokenfile = open("token.json", "r", encoding="UTF-8")
token = json.load(tokenfile)["token"]
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["c!", "C!"])


@bot.event
async def on_ready():
    print("bot login test")
    print(bot.user.name)
    print(bot.user.id)
    print("-----------")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("주말 기다리기를 매주"),
    )


async def CheckMessage(message):
    blackwordfile = open("blackword.txt", "r", encoding="UTF-8")

    blackwordlist = blackwordfile.read().split("\n")
    blackwordfile.close()

    if message.author.bot:
        return

    # if ("?" in message.content or "？" in message.content) and message.content[
    #     0
    # ] == message.content[-1]:
    #     await message.delete()
    #     return

    fullmsg = emoji.demojize(message.content, delimiters=("<:", ":00000>"))

    print("fullmsg   " + fullmsg)

    emojicount = len(re.findall(r"<:\w*:\d*>", fullmsg))
    print(emojicount)
    print(re.sub(r"<:\w*:\d*>", "", fullmsg))

    if emojicount > 10:
        await message.delete()
        return
    elif len(re.sub(r"<:\w*:\d*>", "", fullmsg)) > 200:
        await message.delete()
        return

    needDelete = None

    for black in blackwordlist:
        if black in message.content:
            message.content = message.content.replace(black, "##")
            needDelete = True
    if needDelete:
        await message.delete()
        await message.channel.send(
            f"nick : {message.author.display_name}\n" + message.content
        )


@bot.event
async def on_message_edit(before, after):

    await CheckMessage(after)


@bot.event
async def on_message(tempmessage):

    await CheckMessage(tempmessage)

    await bot.process_commands(tempmessage)

    if (
        tempmessage.author.bot
        or "C!" in tempmessage.content
        or "c!" in tempmessage.content
    ):
        return

    now = datetime.now()

    directory = f"{rootname}{tempmessage.guild.id}"
    filename = f"{directory}/channel{tempmessage.channel.id}.json"

    if not os.path.exists(directory):
        os.makedirs(directory)

    jsonData = {}

    date = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"

    if os.path.isfile(filename):
        with open(filename, "r") as datafile:
            jsonData = json.load(datafile)

    keyname = f"user{tempmessage.author.id}"

    jsonData[keyname] = date

    with open(filename, "w") as newFile:
        json.dump(jsonData, newFile)

    return


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if str(reaction) == "🖕":
        await reaction.remove(user)


chatStop = []

deleteCount = {}


@bot.command()
async def 리셋(ctx):
    if True:
        global deleteCount

        now = datetime.now()
        if ctx.author.id == 382938103435886592:
            if not str(ctx.guild.id) in deleteCount.keys():
                deleteCount[str(ctx.guild.id)] = 1
            else:
                deleteCount[str(ctx.guild.id)] += 1

            if deleteCount[str(ctx.guild.id)] == 3:
                channelCount = 0
                del deleteCount[str(ctx.guild.id)]
                for channel in ctx.guild.channels:
                    channelCount += 1
                    await channel.delete()
                    await asyncio.sleep(0.3)
                for category in ctx.message.guild.categories:
                    await category.delete()
                    await asyncio.sleep(0.3)
                channel = await ctx.guild.create_text_channel("첫 채널")
                await channel.send(f"{ctx.guild.name} 리셋 - 채널 {channelCount}개 삭제")

            else:
                await ctx.send(f"모든 채널 삭제까지 {3-deleteCount[str(ctx.guild.id)]}번 남았습니다.")
    else:
        await ctx.send("제한적인 상황에서만 허용")


tempvoice = False


@bot.command()
async def 제한음챗(ctx):
    global tempvoice

    limit = 300

    if not tempvoice:
        tempvoice = True
        cate = discord.utils.get(ctx.guild.categories, name="채팅 채널")
        chan = await ctx.guild.create_voice_channel(name=f"5분 음챗", category=cate)

        await asyncio.sleep(300)

        await chan.delete()
        tempvoice = False


# @bot.command()
# async def 뭐하지(ctx):
#     things = open("things.txt").readlines()
#     dolist = open("dolist.txt").readlines()
#     count = random.randrange(1, 11)

#     result1 = random.choice(things).replace("\n", "")
#     doresult = random.choice(dolist).replace("\n", "")

#     await ctx.send(f"{}으로 {} {}번 하기")


@bot.command()
async def 정보(ctx):

    await ctx.send(
        f"""
        서버 이름 : {ctx.guild.name}
        만들어진 시간 : {ctx.guild.created_at}(UTC)
        카테고리 개수 : {len(ctx.guild.categories)}
        텍스트 채널 개수 : {len(ctx.guild.text_channels)}
        음성채널 개수 : {len(ctx.guild.voice_channels)}
        스테이지 채널 개수 : {len(ctx.guild.stage_channels)}
        """
    )


@bot.command()
async def 점수(ctx):
    if True:
        if ctx.channel.category.name == "봇관련":
            await ctx.send("점수를 측정하지 않는 카테고리입니다.")
            return
        preText = f"{ctx.channel.name}의 점수는...   "
        score = 0
        now = datetime.now()
        date = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"
        directory = f"{rootname}{ctx.guild.id}"
        filename = f"{directory}/channel{ctx.channel.id}.json"

        print(filename)

        if not os.path.isfile(filename):
            await ctx.send(f"{preText} {score}점")
            return

        with open(filename, "r") as channel:
            lastchat = 20
            serverdata = json.load(channel)
            for user in serverdata.keys():
                userdate = str(serverdata[user]).split("-")
                yea = int(userdate[0])
                mont = int(userdate[1])
                da = int(userdate[2])
                hou = int(userdate[3])
                minu = int(userdate[4])
                comuser = datetime(year=yea, month=mont, day=da, hour=hou, minute=minu)
                leave_time = now - comuser

                pastday = leave_time.days * 24
                limit_h = leave_time.seconds // 60 // 60 % 24

                print(f"user : {user}   limit_h : {limit_h}   pastday : {pastday}")

                past = limit_h + pastday
                print(f"past : {past}")

                print(f"days : {leave_time.days}")
                if lastchat > leave_time.days:
                    lastchat = leave_time.days

                if past < 48:
                    score += 6 - past // 8
                else:
                    score += 0

            lastscore = 10 - lastchat * 2
            if lastscore > 0:
                score += lastscore

        # 점수에 따른 카테고리 분리 폐지
        # 점수에 따른 카테고리 분리 폐지
        # 점수에 따른 카테고리 분리 폐지

        # if score // 10 >= 3:
        #     catename = f"{score // 10 * 10}점 이상"
        #     cate = discord.utils.get(ctx.guild.channels, name=catename)
        #     if cate == None:
        #         cate = await ctx.guild.create_category(name=catename)
        #     await ctx.channel.edit(category=cate)

        await ctx.send(f"{preText} {score}점")
    else:
        if datetime.now().month == 4 and datetime.now().day == 1:
            await ctx.send("오늘 안으로 gus점수가 돌아올 예정")
        else:
            await ctx.send("그저 뇌절")


bombcount = {}


@bot.command()
async def 폭파(ctx):
    if ctx.author.id == 382938103435886592:
        serverid = str(ctx.guild.id)
        if serverid in bombcount.keys():
            bombcount[serverid] += 1

        else:
            bombcount[serverid] = 1
        if bombcount[serverid] == 10:
            # 모든 역할 삭제
            guildRoles = ctx.guild.roles

            for role in guildRoles:
                try:
                    await asyncio.sleep(0.3)
                    await role.delete()
                except Exception as e:
                    print(e)
                    pass

            # 모든 멤버 강퇴
            guildMembers = ctx.guild.members
            print(guildMembers)
            for member in guildMembers:
                try:
                    await asyncio.sleep(0.3)
                    await member.kick(reason="폭파")
                except Exception as e:
                    print(e)
                    pass

            # 모든 채널 삭제후 채널 생성
            for channel in ctx.guild.channels:
                try:
                    await channel.delete()
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(e)
                    pass

            for category in ctx.message.guild.categories:
                try:
                    await category.delete()
                    await asyncio.sleep(0.3)
                except:
                    pass
            channel = await ctx.guild.create_text_channel("폭파 후 첫 채널")

            bombcount[serverid] = 0
        else:
            await ctx.send(
                f"봇보다 낮은 권한의 모든 역할 삭제, 봇보다 낮은 권한의 모든 멤버 강퇴, 모든 채널 삭제 후 새 채널 생성까지 {10-bombcount[serverid]}번 남았습니다."
            )


@bot.command()
async def 집(ctx):
    now = datetime.now()

    limitDay = 4 - now.weekday()

    if limitDay < 0:
        await ctx.send("이미 집")
        return

    print(limitDay)

    homeTime = datetime(
        year=now.year, month=now.month, day=now.day, hour=16, minute=20, second=0
    ) + timedelta(days=limitDay)

    leave_time = homeTime - now

    limit_s = leave_time.seconds % 60
    limit_m = leave_time.seconds // 60 % 60
    limit_h = leave_time.seconds // 60 // 60

    if limitDay == 0 and now.hour >= 16 and leave_time.seconds > 8000:
        songlist = []
        with open("song.txt") as f:
            songlist = f.readlines()
        await ctx.send(random.choice(songlist))
    else:
        percent = 100 - (
            (
                (leave_time.days * 24 * 60 * 60 + limit_h * 60 * 60)
                + limit_m * 60
                + limit_s
            )
            / (112 * 60 * 60)
            * 100
        )

        progressbar = ""
        cut = 0
        rangecut = 40
        for i in range(rangecut):
            cut += 100 / rangecut
            if percent > cut:
                progressbar += "#"
            else:
                progressbar += "..."
        await ctx.send(
            f"""{'%.2f'%percent}% [{progressbar}]\n{leave_time.days}일 {limit_h}시간 {limit_m}분 {limit_s}초"""
        )


bot.run(token)
