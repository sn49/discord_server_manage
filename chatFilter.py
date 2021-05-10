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

rootname = "data/server"

tokenfile = open("token.json", "r", encoding="UTF-8")
token = json.load(tokenfile)["token"]
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["gus", "Gus", "GUS"])


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
    blackwordfile = open("blackword.txt", encoding="UTF-8")
    blackwordlist = blackwordfile.read().split("\n")

    for black in blackwordlist:
        if black in message.content:
            await message.delete()
            return

    if ("?" in message.content or "？" in message.content) and message.content[
        0
    ] == message.content[-1]:
        await message.delete()
        return

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


@bot.event
async def on_message_edit(before, after):

    await CheckMessage(after)


@bot.event
async def on_message(tempmessage):

    await CheckMessage(tempmessage)

    await bot.process_commands(tempmessage)
    return
    # now = datetime.now()

    # directory = f"{rootname}{tempmessage.guild.id}"
    # filename = f"{directory}/channel{tempmessage.channel.id}.json"

    # if not os.path.exists(directory):
    #     os.makedirs(directory)

    # if tempmessage.author.id in chatStop:
    #     await tempmessage.delete()
    #     return

    # jsonData = {}

    # date = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"

    # if os.path.isfile(filename):
    #     with open(filename, "r") as datafile:
    #         jsonData = json.load(datafile)

    # keyname = f"user{tempmessage.author.id}"

    # jsonData[keyname] = date

    # with open(filename, "w") as newFile:
    #     json.dump(jsonData, newFile)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if str(reaction) == "🖕":
        await reaction.remove(user)


chatStop = []


@bot.command()
async def 쿠폰(ctx):
    directory = f"{rootname}{ctx.guild.id}"
    filename = f"{directory}/channel{ctx.channel.id}.json"

    jsonData = {}

    if os.path.isfile(filename):
        with open(filename, "r") as datafile:
            jsonData = json.load(datafile)

        keyname = f"user{ctx.author.id}"

        if keyname in jsonData.keys():
            await ctx.send(f"{jsonData[keyname]}장 보유중")
            return

    msg = await ctx.send("0장 보유중")


@commands.cooldown(1, 20, commands.BucketType.user)
@bot.command()
async def 도전(ctx):
    now = datetime.now()

    if now.month == 4 and now.day <= 9 or True:
        result = random.random() * 100

        print(result)

        if result < 20:
            chatStop.append(ctx.author.id)
            await ctx.send("2분동안 채팅 못함")

            result = random.random() * 100

            if result < 80:
                directory = f"{rootname}{ctx.guild.id}"
                filename = f"{directory}/coupon.json"
                jsonData = {}

                print(filename)

                keyname = f"user{ctx.author.id}"

                if os.path.isfile(filename):
                    with open(filename, "r") as datafile:
                        jsonData = json.load(datafile)

                        if keyname in jsonData.keys():
                            jsonData[keyname] += 1
                        else:
                            jsonData[keyname] = 1
                else:
                    jsonData[keyname] = 1

                with open(filename, "w") as newFile:
                    json.dump(jsonData, newFile)

                msg = await ctx.send("gus쿠폰 1장 획득!")
            else:
                msg = await ctx.send("쿠폰 획득 실패...")
            await asyncio.sleep(120)
            chatStop.remove(ctx.author.id)
            msg = await ctx.send(f"{ctx.author.nickname}, 채팅 풀림")

        else:
            msg = await ctx.send("통과(테스트 기간 : 4/1 ~ 4/9)")
    else:
        msg = await ctx.send("오류있어서 못씀")


deleteCount = {}


@bot.command()
async def 리셋(ctx):
    if False:
        global deleteCount

        now = datetime.now()
        if ctx.author.id == 382938103435886592:
            if not str(ctx.guild.id) in deleteCount.keys():
                deleteCount[str(ctx.guild.id)] = 1
            else:
                deleteCount[str(ctx.guild.id)] += 1

            if deleteCount[str(ctx.guild.id)] == 3:
                channelCount = 0
                deleteCount[str(ctx.guild.id)] = 0
                for channel in ctx.guild.channels:
                    channelCount += 1
                    await channel.delete()
                    await asyncio.sleep(0.3)
                for category in ctx.message.guild.categories:
                    await category.delete()
                    await asyncio.sleep(0.3)
                channel = await ctx.guild.create_text_channel("시즌3 첫 채널")
                await channel.send(
                    f"시즌2 - 2021-03-31 10:06:02.130079 ~ {now}    채널 {channelCount}개 삭제"
                )

            else:
                await ctx.send(f"모든 채널 삭제까지 {3-deleteCount[str(ctx.guild.id)]}번 남았습니다.")
    else:
        await ctx.send("시즌3 필요할때 가능")


@도전.error
async def chal_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "This command is ratelimited, please try again in {:.2f}s".format(
            error.retry_after
        )
        await ctx.send(msg)
    else:
        raise error


@bot.command()
async def 점수(ctx):
    if False:
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

                if past < 12:
                    score += 6
                elif past < 24:
                    score += 3
                elif past < 36:
                    score += 2
                elif past < 48:
                    score += 1

            print(f"lastchat : {lastchat}")
            lastscore = 14 - lastchat * 2
            if lastscore > 0:
                score += lastscore

        if score // 10 >= 3:
            catename = f"{score // 10 * 10}점 이상"
            cate = discord.utils.get(ctx.guild.channels, name=catename)
            if cate == None:
                cate = await ctx.guild.create_category(name=catename)
            await ctx.channel.edit(category=cate)

        await ctx.send(f"{preText} {score}점")
    else:
        if datetime.now().month == 4 and datetime.now().day == 1:
            await ctx.send("오늘 안으로 gus점수가 돌아올 예정")
        else:
            await ctx.send("그저 뇌절")


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
            / (104 * 60 * 60)
            * 100
        )

        progressbar = ""
        cut = 0
        rangecut = 20
        for i in range(rangecut):
            if percent > cut:
                progressbar += "#"
            else:
                progressbar += "..."
            cut += 100 / rangecut
        await ctx.send(
            f"""{'%.2f'%percent}% [{progressbar}]\n{leave_time.days}일 {limit_h}시간 {limit_m}분 {limit_s}초"""
        )


bot.run(token)
