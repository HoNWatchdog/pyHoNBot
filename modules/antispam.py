#!/usr/bin/env python
"""
"""
from hon.packets import ID
from time import time
import re

silences = {}

def spam_silence(bot, chanid, nick):
	if bot.config.spam_silence == 0:
		return
	if bot.config.spam_clan_immune == 1:
		if nick in bot.nick2id and bot.nick2id[nick] in bot.clan_roster:
			return
	if nick not in silences:
		silences[nick] = 1
	else:
		silences[nick] += 1
	if silences[nick] >= bot.config.spam_silence_ban:
		# bot.banlist.Add('N/A', nick, 'Anti-Spam')
		bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
		del(silences[nick])
	else:
		bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER, chanid, nick, ((60 * bot.config.spam_silence) * 1000))

def checkSpam(bot, origin, data):
	chanid = origin[2]
	nick = bot.id2nick[origin[1]].lower()
	now = time()
	for word in bot.config.badwords:
		if re.search(r'(^|\W)' + word, data.lower()):
			spam_silence(bot, chanid, nick)
	if nick in bot.spamcd:
		for k,t in enumerate(bot.spamcd[nick]):
			if (now - bot.config.spam_length) > t:
				del(bot.spamcd[nick][k])
		if len(bot.spamcd[nick]) >= 4:
			spam_silence(bot, chanid, nick)
			del(bot.spamcd[nick])
		else:
			bot.spamcd[nick].append(now)
	else:
		bot.spamcd[nick] = [now]
checkSpam.event = [ID.HON_SC_CHANNEL_MSG, ID.HON_SC_CHANNEL_EMOTE, ID.HON_SC_CHANNEL_ROLL]
checkSpam.thread = False

def addword(bot, input):
	"""Add word to bad words list"""
	if not input.admin:
		return False
	if not input.group(2):
		return
	word = input.group(2).lower()
	if word not in bot.config.badwords:
		bot.config.set_add('badwords', word)
		bot.reply("Added word to list")
	else:
		bot.reply("Word already in list")
addword.commands = ['addword']

def delword(bot, input):
	"""Delete word from bad words list"""
	if not input.admin:
		return False
	if not input.group(2):
		return
	word = input.group(2).lower()
	if word not in bot.config.badwords:
		bot.reply("Word isn't in list")
	else:
		bot.config.set_del('badwords', word)
		bot.reply("Removed word from list")
delword.commands = ['delword']

def setup(bot):
	bot.spamcd = {}
	bot.config.module_config('spam_clan_immune', [1, 'Clan members are immune to spam protection/bad word silence/bans, 1 = Yes, 0 = No'])
	bot.config.module_config('spam_silence_ban', [3, 'x silences for spam will ban (Covers badword silences too)'])
	bot.config.module_config('spam_silence', [5, 'Silence for x minutes when spam detected, 0 = disabled (Also used for badwords)'])
	bot.config.module_config('spam_length', [5, 'Seconds until messages are removed from the spam stack'])
	bot.config.module_config('badwords', [[], 'List of bad words for insta-silence'])