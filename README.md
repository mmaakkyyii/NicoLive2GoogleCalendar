# NicoLive2GoogleCalendar
ニコニコチャンネルの特定のタグが付いたニコニコ生放送の予定を取得して、Googleカレンダーに反映するプログラム

## tokenについて
googleカレンダー連携に必要なtokenは '''token/token.pickle'''に置く

## channel_listについて
'''/channel_list/nicolive_list.csv''' はニコニコチャンネルのリストで
名前,チャンネルID,target(tags,title),検索ワード
となるようにする

```/channel_list/linelive_list.csv``` はラインライブのリストで
LINELIVEのID
をチャンネルごとに改行する

## MY_CALENDAR_URLについて
'''url/MY_CALENDAR_URL.txt'''は
カレンダーのURLのみを書いたファイルを置いておく
