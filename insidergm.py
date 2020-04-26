#!/usr/bin/env python3
import discord
from discord.ext import commands
from enum import IntEnum, auto
import random
import time
import asyncio
import csv
import glob
import pathlib
import os

# 設定
LimitTime = 300

# 役職Enum
class Role(IntEnum):
    Master = auto()
    People = auto()
    Insider = auto()

# ゲームステータス
class GameStatus(IntEnum):
    NotReady = auto()  
    Ready = auto()
    Question = auto()
    Discussion = auto()

    Judge = auto()
    Votiong = auto()

# 仮答えリスト
answers = ['りんご','ごりら','ばなな']

# デフォルトの答えリスト
defaultAnswerset = 'default'

# 自分のBotのアクセストークンに置き換えてください
TOKEN = ''

# 接続に必要なオブジェクトを生成
client = commands.Bot(command_prefix='/')

# メンバーリスト
gamemember = []

# 現在のゲームのメンバー
# 0.discord.Member
# 1.Role
# 2.投票完了 bool
# 3.Jadge投票結果 Bool
# 4.Votiong 2回めの投票結果 int
currentmember = []


# 現在の答えセット
currentanswerset = ''

# 現在の答え
currentanswer = ''

#ゲームステータス
currentStatus = GameStatus.NotReady

#答えたメンバー
answerMenber = discord.Member

#チャンネル
GameChannel = discord.TextChannel

#ディスカッション時間
RemainTime = 0

def getMasterMember():
    for items in currentmember:
        if items[1] == Role.Master:
            return items[0]
    print("can't find master")

def getInsiderMember():
    for items in currentmember:
        if items[1] == Role.Insider:
            return items[0]
    print("can't find master")

def getCurentMemberList():
    memberstr = ''
    for index in range(len(currentmember)):
        memberstr = memberstr + '\n' + str(index) + ' : ' + currentmember[index][0].mention
    return memberstr


def getCurentMemberListVoting():
    global answerMenber
    memberstr = ''
    for index in range(len(currentmember)):
        if currentmember[index][1] != Role.Master and currentmember[index][0] != answerMenber:
            memberstr = memberstr + '\n' + str(index) + ' : ' + currentmember[index][0].mention
    return memberstr

def clearVote(): # 投票状況をクリア
    global currentmember
    for items in currentmember:
        items[2] = False

def loadAnswer(answerFileName:str):
    global answers
    global currentanswerset

    p_abs = pathlib.Path(__file__).parent / pathlib.Path('answer')

    if answerFileName == 'all': # すべて読み込み
        files = p_abs.glob('*.csv')
        for file in files:
            with open(file,encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    answers.extend(row)
        currentanswerset = 'all'

            
    else: # 個別読み込み
        answers.clear()

        answerPath = p_abs / pathlib.Path(answerFileName + '.csv')
        with open(answerPath,encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                answers.extend(row)
        
        currentanswerset = answerFileName
    

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    
    # 答えロード
    loadAnswer(defaultAnswerset)
    
    pass

# 猫コマンド
@client.command()
async def neko(ctx):
    """ねこのふりをしてあいさつをする"""
    await ctx.send(f'{ctx.author.mention} にゃにゃにゃん')

# 答えリスト更新
@client.command()
async def updateanswer(ctx,arg):
    """答えセット名:文字列 答えセットを更新する。allですべての答えセットを含める。"""
    loadAnswer(str(arg))
    await ctx.send(f'答えセットを {str(arg)} に更新しました。')

# 答えリスト表示
@client.command()
async def listanswer(ctx):
    """存在する答えセットを表示する"""
    p_abs = pathlib.Path(__file__).parent / pathlib.Path('answer')
    files = p_abs.glob('*.csv')
    # files = glob.glob('./answer/*')
    for file in files:
        await ctx.send(f'{file.name.rstrip(".csv")}')

@client.command()
async def answerset(ctx):
    """現在の答えセット名を表示する"""
    await ctx.send(f'現在の答えセットは {currentanswerset} です')

# ユーザ追加
@client.command(aliases=['jo'])
async def joined(ctx, *, member: discord.Member):
    """ユーザ名：文字列　参加ユーザを追加する"""
    gamemember.append(member)
    await ctx.send('{0} joined on {0.joined_at}'.format(member))

# ユーザ削除
@client.command()
async def removed(ctx, *, member: discord.Member):
    """ユーザ名：文字列　参加ユーザを除外する"""
    gamemember.remove(member)
    await ctx.send('{0} remove on {0.joined_at}'.format(member))

# ユーザクリア
@client.command()
async def clear(ctx):
    """すべてのユーザを除外する"""
    gamemember.clear()
    await ctx.send('全ユーザを削除しました。')

# ユーザ確認
@client.command()
async def members(ctx):
    """現在のユーザを確認する"""
    memberstr = ''
    for item in gamemember:
        memberstr = memberstr + '\n' + item.display_name
    await ctx.send('-Members-\n {0}'.format(memberstr))

# ゲーム準備
@client.command()
async def ready(ctx):
    """ゲームの役職や答えを準備する"""
    global currentStatus
        

    if currentStatus != GameStatus.NotReady:
        await ctx.send('Error:ゲームを準備できません。')
        return

    # 役職抽選
    # Master
    MasterIdx = random.randint(0,len(gamemember)-1)

    # Insider
    while True:
        InsiderIdx = random.randint(0,len(gamemember)-1)
        if MasterIdx != InsiderIdx:
            break

    #currentmember初期化
    global currentmember
    currentmember.clear()
    role = Role.People

    for index in range(len(gamemember)):
        if index == MasterIdx:
            role = Role.Master
        elif index == InsiderIdx:
            role = Role.Insider
        else:
            role = Role.People

        currentmember.append([gamemember[index],role,False,False,0])

    # 答え抽選
    global currentanswer
    currentanswer = answers[random.randint(0,len(answers)-1)]

    # 各自にDM送信
    for index in range(len(currentmember)):

        if currentmember[index][1] == Role.Master:
            rolestr = 'マスター'
            ansstr = '答えは『' + currentanswer + '』です。'
            
        elif currentmember[index][1] == Role.Insider:
            rolestr = 'インサイダー'
            ansstr = '答えは『' + currentanswer + '』です。'
            
        else:
            rolestr = '一般人'  
            ansstr = '答えはナイショです。'    
        
        sendstr =  currentmember[index][0].display_name + 'さんの役職は『' + rolestr + '』です。\n'
        sendstr = sendstr + ansstr

        dm = await currentmember[index][0].create_dm()
        await dm.send(f"{sendstr}")

    # 完了通知
    memberstr = getCurentMemberList()
    readystr = '以下のメンバーでインサイダーゲームを準備しました。\n\n' 
    readystr = readystr +  memberstr + '\n 番号はメンバー番号となります。\n\n'
    readystr = readystr + '各位にDMにて今回の役職を送信しました。ご確認ください。\n ※マスターとインサイダーには答えもご確認ください。\n\n'
    readystr = readystr +  '『/begin』でインサイダーゲームを開始します。'
    await ctx.send(f'{readystr}')

  
    currentStatus = GameStatus.Ready


# ゲームスタート
@client.command()
async def begin(ctx):
    """ゲームをスタートする"""
    global GameChannel
    global currentStatus

    if currentStatus != GameStatus.Ready:
        await ctx.send('Error:準備が整っていません')
        return

    GameChannel = ctx.message.channel
    mastermember = getMasterMember()

    startstr = 'インサイダーゲームを開始します!\n\n'
    startstr = startstr + 'Masterは' + mastermember.mention + 'さんです。\n'
    startstr = startstr + mastermember.mention + 'さんに質問をして答えを当てましょう！\n\n'
    
    memberstr = getCurentMemberList()

    startstr = startstr + '答えが出たら「/answer 答えたメンバー番号」を入力してください。\n\n' + memberstr
    startstr = startstr + '\n制限時間は' + str(LimitTime) + '秒です。'
    await ctx.send(f'{startstr}')

    secs = 1
    
    global RemainTime
    RemainTime = 0
    
    currentStatus = GameStatus.Question

    for i in range(LimitTime):
        await asyncio.sleep(secs)
        RemainTime = RemainTime + secs
        if LimitTime - i == LimitTime/2:
            await ctx.send(f'残り{LimitTime/2}秒です。')
        elif LimitTime - i == LimitTime/5:
            await ctx.send(f'残り{LimitTime/5}秒です。')
        elif LimitTime - i == 10:
            await ctx.send(f'残り10秒です。')
        
        if currentStatus != GameStatus.Question:
            break
    

    if currentStatus == GameStatus.Question: #まだ質問タイムなら
        timeupstr = 'TimeUp！\n\n'
        timeupstr = timeupstr + 'ギリギリで答えが出た場合\n\t→「/answer 答えたメンバー番号」を入力してください'
        timeupstr = timeupstr + '答えが出なかった場合\n\t→「/end」を入力してください。」'

        await ctx.send(f'{timeupstr}')


@client.command()
async def end(ctx):
    """答えが出なかった場合"""
    if currentStatus != GameStatus.Question:
        await ctx.send('Error:質問時間ではありませんでした')
        return
    await endResult(False,False)

#回答
@client.command()
async def answer(ctx,id):
    """ユーザ番号：整数　答えたユーザを指定する"""
    global answerMenber
    global currentStatus

    if currentStatus != GameStatus.Question:
        await ctx.send('Error:準備が整っていません')
        return

    if currentmember[int(id)][1] ==  Role.Master:
        await ctx.send('Error:Masterは回答者になりません')
        return
        

    answerMenber = currentmember[int(id)][0]
    
    answerstr = answerMenber.mention + 'さんが見事答えを言い当てました。\n'
    answerstr = answerstr + 'でもチョット待って！'+ answerMenber.mention + 'さんはインサイダーかもしれません。\n'
    answerstr = answerstr + 'また、他にも怪しい人がいるかも知れません。振り返ってみんなで考えてみましょう。\n\n'
    answerstr = answerstr + '振り返りが早めに終わったら「/enddis」でスキップすることもできます。\n'
    answerstr = answerstr + '制限時間は' + str(RemainTime) + '秒です。'
    await ctx.send(f'{answerstr}')

    currentStatus = GameStatus.Discussion

    await asyncio.sleep(RemainTime)

    if currentStatus == GameStatus.Discussion: # まだ話し合い中なら終わらせる
        await jadgeAnnounce()

#振り返り終了
@client.command()
async def enddis(ctx):
    """話し合いを終了する"""
    await jadgeAnnounce()


async def jadgeAnnounce():
    global currentStatus

    if currentStatus != GameStatus.Discussion:
        await GameChannel.send('Error:終わらせる話し合いがありません。')
        return

    disstr = '回答者以外は' + str(answerMenber.mention) + 'さんがインサイダーであるか否か、各自投票をお願いします。\n\n'
    await GameChannel.send(f'{disstr}')
    
    clearVote()

    #各自にDM
    jadgedmstr = answerMenber.display_name + 'さんはインサイダーだと思いますか？\n'
    jadgedmstr = jadgedmstr + '私に以下のDMを送って投票してください。\n\n'
    jadgedmstr = jadgedmstr + '回答者はインサイダーである\n'
    jadgedmstr = jadgedmstr + '\t→「/judge yes」\n'
    jadgedmstr = jadgedmstr + '回答者はインサイダーではない\n'
    jadgedmstr = jadgedmstr + '\t→「/judge no」\n'
    jadgedmstr = jadgedmstr + '※/judgeは/juに省略できます\n'

    for index in range(len(currentmember)):
        if currentmember[index][0] != answerMenber: #回答者以外にDM送信
            dm = await currentmember[index][0].create_dm()
            await dm.send(f"{jadgedmstr}")

    currentStatus = GameStatus.Judge



# インサイダーか投票
@client.command(aliases=['ju'])
@commands.dm_only()
async def judge(ctx,arg):
    """回答者がインサイダーか投票する"""
    global currentStatus

    if currentStatus != GameStatus.Judge:
        await GameChannel.send('Error:投票時間ではありません')
        return

    str = arg
    if str == 'yes' or str == 'y':
        isInsider = True
    elif str == 'no' or str == 'n':
        isInsider = False
    else:
        #エラー
        await ctx.send('引数は「yes」または「no」を入れてください。')
        return

    for item in currentmember:
        if ctx.author == item[0]:
            item[3] = isInsider
            item[2] = True
            break

    await GameChannel.send(f'{ctx.author.display_name} さん投票完了')

    Sended = True
    
    #投票が完了したか確認
    for items in currentmember:
        if items[0] != answerMenber:
            # Sended = Sended and items[2]
            Sended = Sended and items[2]

    if Sended:
        #投票完了
        await resultJadge()



# 回答者＝インサイダーか投票結果
async def resultJadge():
    global currentStatus

    resultstr = '全員の投票が完了しました。\n\n'
    resultstr = resultstr + '<投票結果>\n'

    result = ''
    vote = ''
    voteInsider = 0
    voteNotInsider = 0
    for items in currentmember:
        if items[0] != answerMenber:
            if items[3]:
                vote = 'インサイダーである！'
                voteInsider = voteInsider + 1
            else:
                vote = 'インサイダーではない！'
                voteNotInsider = voteNotInsider + 1

            result = result + items[0].display_name + ' : ' + vote + '\n'

    resultstr = resultstr + result 
    resultstr = resultstr + '\n <合計>\n'
    resultstr = resultstr + 'インサイダーである : ' + str(voteInsider) + '\n'
    resultstr = resultstr + 'インサイダーではない : ' + str(voteNotInsider) + '\n\n'
    
    if voteInsider > voteNotInsider:
        resultstr = resultstr + '多数決の結果、皆さんはの予想は「' + answerMenber.display_name + 'さんがインサイダーだ」という結論になりました\n'
        expectInsider = True
    else:
        resultstr = resultstr + '多数決の結果、皆さんはの予想は「' + answerMenber.display_name + 'さんがインサイダーではない」という結論になりました\n'
        expectInsider = False
        
    
    resultstr = resultstr + answerMenber.display_name + 'さんは… \n'

    await GameChannel.send(f'{resultstr}')

    for index in range(3):
        await GameChannel.send('...')
        await asyncio.sleep(1)
        index
    

    for items in currentmember:
        if items[0] == answerMenber:
            if items[1] == Role.Insider:
                isInsider = True
            else:
                isInsider = False
            break
    
    if isInsider:
        resultstr = answerMenber.display_name + 'さんはインサイダーでした！\n'
        await GameChannel.send(f'{resultstr}')
        if expectInsider:
            await endResult(False,True)
        else:
            await endResult(True,True)
    else:
        resultstr = 'インサイダーではありませんでした！\n' 
        await GameChannel.send(f'{resultstr}')
        if expectInsider:
            await endResult(True,True)
        else:
            await voteAnnounce()
            
    

#投票アナウンス
async def voteAnnounce():
    global currentStatus
    resultstr = 'では、インサイダーは誰でしょう？各自DMから投票をお願いします。\n'
    await GameChannel.send(f'{resultstr}')

    resultstr = 'この中でインサイダーは誰でしょう？\n'
    resultstr = resultstr + getCurentMemberListVoting()
    resultstr = resultstr + '\n'
    resultstr = resultstr + '私に以下のDMを送ってお応えください\n\n'
    resultstr = resultstr + '/vote ユーザ番号\n'
    resultstr = resultstr + '/voteは/vに省略可能'

    for index in range(len(currentmember)):
        dm = await currentmember[index][0].create_dm()
        await dm.send(f"{resultstr}")    
    
    clearVote()
    currentStatus = GameStatus.Votiong


@client.command(aliases=['v'])
@commands.dm_only()
async def vote(ctx,arg):
    """ユーザ番号：整数　インサイダーだと思う人を投票する"""
    global currentStatus

    if currentStatus != GameStatus.Votiong:
        await GameChannel.send('Error:投票時間ではありません')
        return
    
    for items in currentmember:
        if items[0] == ctx.author:
            items[4] = int(arg)
            items[2] = True
    
    await GameChannel.send(f'{ctx.author.display_name} さん投票完了')

    Sended = True
    
    #投票が完了したか確認
    for items in currentmember:
        Sended = Sended and items[2]

    if Sended:
        #投票完了
        await resultVote()
    

async def resultVote():
    resultstr = '全員の投票が完了しました。\n\n'

    resultstr = resultstr + '<投票結果>\n'

    result = [] 

    for index in range(len(currentmember)):
        result.append(0)
    
    votestr = ''

    for index in range(len(currentmember)):
        votestr = votestr + currentmember[index][0].display_name + ' : ' + currentmember[currentmember[index][4]][0].display_name + '\n'
        result[currentmember[index][4]] = result[currentmember[index][4]] + 1

    resultstr = resultstr + votestr

    resultstr = resultstr + '\n <合計>\n'

    totalstr = ''
    for index in range(len(result)):
        totalstr = totalstr + currentmember[index][0].display_name + ' : ' + str(result[index]) + '\n'

    resultstr = resultstr + totalstr

    maxcount = 0 
    max_memberindex = 0

    for index in range(len(result)):
        if result[index] == max(result):
            maxcount = maxcount + 1
            max_memberindex = index

    expectMember = discord.Member

    resultstr = resultstr + '\n'

    if maxcount == 1: #最大が1個なら投票終了
        expectMember = currentmember[max_memberindex][0]
        resultstr = resultstr + '最も得票が多いのは' + expectMember.display_name + 'さんでした。\n'
    else: #最大が複数ある場合は回答者が指名した人
        for item in currentmember:
            if item[0] == answerMenber:
                expectMember = currentmember[item[4]][0]
                break

        resultstr = resultstr + '最も得票が多い人が複数いるので回答者の選んだ' + expectMember.display_name + 'さんを最多得票とします。\n'
    
    resultstr = resultstr + expectMember.display_name + 'さんは...'
    await GameChannel.send(f'{resultstr}')


    for index in range(3):
        await GameChannel.send('...')
        await asyncio.sleep(1)
        index

    for item in currentmember:
        if item[0] == expectMember:
            if item[1] == Role.Insider:
                await GameChannel.send(f'インサイダーでした！\n')
                await endResult(False,True)
                
            else:
                await GameChannel.send(f'インサイダーではありませんでした！\n') 
                await endResult(True,True)

#終了リザルト
async def endResult(isWonInsider:bool,isElucidation:bool):

    global currentStatus

    str = 'ゲーム終了！\n\n'
    if isWonInsider:
        str = str + 'インサイダーの勝利です！\n\n'
    else:
        str = str + 'マスター＆一般人の勝利です！\n\n'
    

    memstr = ''

    for items in currentmember:
        if items[1] == Role.Insider:
            rolename = 'インサイダー'
        elif items[1] == Role.Master:
            rolename = 'マスター'
        else:
            rolename = '一般人'
        
        memstr = memstr + items[0].mention + ' : ' + rolename + '\n'

    str = str + memstr + '\n'
    str = str + '答え：『' + currentanswer + '』\n\n'
    str = str + 'ゲームをリセットします。\n'
    str = str + '次のゲームの準備ができたら「/ready」で準備してください。'

    await GameChannel.send(f'{str}')

    currentStatus = GameStatus.NotReady

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)