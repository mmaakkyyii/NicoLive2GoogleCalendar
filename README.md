# NicoLive2GoogleCalendar
ニコニコチャンネルの特定のタグが付いたニコニコ生放送の予定を取得して、Googleカレンダーに反映するプログラム

## tokenについて
googleカレンダー連携に必要なtokenは '''token/token.pickle'''に置く

## channel_listについて
'''/channel_list/channel_list.csv'''は
名前,チャンネルID,target(tags,title),検索ワード
となるようにする

## MY_CALENDAR_URLについて
'''url/MY_CALENDAR_URL.txt'''は
カレンダーのURLのみを書いたファイルを置いておく
