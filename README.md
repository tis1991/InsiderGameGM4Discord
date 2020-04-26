# InsiderGameGM4Discord
## 概要
インサイダーゲームのGMをしてくれるdiscord botです。 

GM役を立てなくてもdiscord上でインサイダーゲームが遊べます。 
 
仲間内で遊ぶために作ったのでバグとか変な挙動するところもあると思いますが多めにみてね。 

## インサイダーゲームとは

[インサイダーゲーム](https://oinkgms.com/jp/insider) 

※本プログラムはOink Games様と全く関係ないため問い合わせ等はお控えください。 
 
下記漫画でも紹介されています。 

https://twicomi.com/manga/kotake_spla/1138774359282147328 

## 主な機能
- 役職、答え抽選
- DMによる投票
- 答えセットの管理 

## 動作環境
- Python3.6上動作確認済み 
- Discord botアカウント必要 

## 使い方
### discord botの準備
[discordBotの取得方法](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)

discord botのアカウントを取得の上、使用するdiscordサーバへ登録しておいてください。

### discord botのトークン登録
insidergm.pyの 

```
TOKEN = ''
```

に取得したdiscord botのトークンを入れる。 

### botの起動
```
python3 ./insidergm.py
```
「ログインしました。」と表示されればOKです。

### プレイユーザの登録
```
/joined ユーザ名
```
でプレイするユーザを登録、

```
/members
```
で登録されているユーザを確認できます。

### ゲームの準備、開始

```
/ready
```
でゲームを準備します。DMで各自に役職と答えが届きます。

全員の準備ができたら、
```
/begin
```
でゲーム開始です。

あとはbotのメッセージに沿ってゲームを進めてください。

### わからないことがあったら
```
/help
```
でコマンド一覧が表示されます。

## その他
権利的にマズいところがあったら即対応しますのでご連絡ください。

## 作者
TiS @tis_atisie

## 謝辞
defaultの答えを用意していただいたチャリキさん([@bike_chari_](https://twitter.com/bike_chari_))ありがとうございました。
