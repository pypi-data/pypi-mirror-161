#! /usr/bin/env python3

# pip3 install python-telegram-bot
# BotFather /setprivacy disable
# add to group

import telegram
import sys, os
import time
from telegram import error
from rs4 import argopt

class Telegram:
    def __init__ (self, token, chat_id = None):
        self.token = token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token = token)

    def show_messages (self):
        updates = self.bot.getUpdates()
        for u in updates:
            print(u.message)

    def updates (self):
        return self.bot.getUpdates()

    def send (self, msg, chat_id = None):
        msgs = self.updates ()
        if msgs and self.chat_id is None:
            self.chat_id = msgs [-1].message.chat.id

        self.bot.sendMessage (
            chat_id or self.chat_id,
            msg
        )


if __name__ == "__main__":
    argopt.add_option ("-t=TOKEN", "--token=", "telegram token")
    argopt.add_option ("-c=CHAT_ID", "--chat-id=", "telegram chat ID")

    options = argopt.get_options ()
    if "--help" in sys.argv:
        argopt.usage (True)

    token = options.get ("--token", os.environ.get ('TELEGRAM_TOKEN'))
    if not token:
        raise SystemExit ('telegram token reqired')
    chat_id = options.get ("--chat-id", os.environ.get ('TELEGRAM_CHAT_ID'))
    commit_title = os.environ.get ("CI_COMMIT_TITLE", "")
    if commit_title.find ('--tg-silent') != -1:
        sys.exit ()

    bot = Telegram (token, chat_id)
    for i in range (7):
        try:
            bot.send (' '.join (options.argv))
        except error.TimedOut:
            time.sleep (2)
            continue
        break
