import asyncio

import comms_list
import discord
from discord.ext import commands
from discord import Intents
import random
from bot import bot


async def displayembed(ctx, title='Заголовок', description='Описание', author=None, thumbnail=None):
    embed = discord.Embed(
        title=title,
        description=description,
        colour=discord.Colour.from_rgb(14, 170, 105)
    )
    if author:
        embed.set_author(name=author[0],
                         icon_url=author[1])
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    await ctx.send(embed=embed)


def create_button(bstyle: int, label: str = None, emoji=None):
    if bstyle == 1:
        return discord.ui.button(style=discord.ButtonStyle.primary, label=label, emoji=emoji)
    elif bstyle == 2:
        return discord.ui.button(style=discord.ButtonStyle.secondary, label=label, emoji=emoji)
    elif bstyle == 3:
        return discord.ui.button(style=discord.ButtonStyle.success, label=label, emoji=emoji)
    elif bstyle == 4:
        return discord.ui.button(style=discord.ButtonStyle.danger, label=label, emoji=emoji)


async def button_callback(self, interaction: discord.interactions.Interaction, button: discord.ui.Button, reply):
    self.breply_final = reply
    self.interacted = True
    await self.ctx.send(self.breply_final)
    QTEButton(self.ctx, self.symbol, time=0)
    await disable_button(self, qtemsg)


async def disable_button(self, msg, interaction=discord.interactions.Interaction, button=discord.ui.Button):
    self.clear_items()
    await msg.edit(view=self)


async def edit_slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    print(f"Set the slowmode delay in this channel to {seconds} seconds.")


class QTEButton(discord.ui.View):
    breply = "**`❌`Попытка действия провалена.**"
    symbol = None
    breply_final = breply
    interacted: bool = False

    def __init__(self, ctx, symbol, time: int = None):
        super().__init__(timeout=time)
        self.ctx = ctx
        self.symbol = symbol

    async def qte_button_callback(self, interaction, button, c_symbol):
        if self.symbol == c_symbol: self.breply = '**`✅`Действие совершено успешно!**'
        await button_callback(self, interaction, button, '<@' + str(interaction.user.id) + '> \n' + self.breply)

    @create_button(1, None, '🇽')
    async def button_callback1(self, interaction, button):
        await self.qte_button_callback(interaction, button, '🇽')

    @create_button(1, None, '🇾')
    async def button_callback2(self, interaction, button):
        await self.qte_button_callback(interaction, button, '🇾')

    @create_button(1, None, '🇦')
    async def button_callback3(self, interaction, button):
        await self.qte_button_callback(interaction, button, '🇦')

    @create_button(1, None, '🇧')
    async def button_callback4(self, interaction, button):
        await self.qte_button_callback(interaction, button, '🇧')

    async def on_timeout(self):
        self.clear_items()
        if not self.interacted:
            await self.ctx.send(self.breply_final)
            await disable_button(self, qtemsg)


cutscene_channels = []


# In development
@bot.listen()
async def on_message(message: discord.Message):
    channel_i = [d for d in cutscene_channels if d.get("channel") == message.channel]
    if channel_i and \
            not message.content.startswith(("((", "//")) and \
            any(message.author != d.get("owner") for d in channel_i) and \
            not message.author.bot:
        await message.delete()
        await message.author.send("Вы не можете отправлять сообщения, не являющиеся комментариями "
                                  "(которые не начинаются на \"((\" или \"//\")"
                                  " в режиме катсцены.")


# In development
@bot.command(aliases=[])
async def cutscenemode(ctx):
    channel_i = [d for d in cutscene_channels if d.get("channel") == ctx.channel]
    if not channel_i:
        cutscene_channels.append(dict(channel=ctx.channel, owner=ctx.author))
        await edit_slowmode(ctx, 10)
        await displayembed(ctx,
                           title="",
                           description="# Cutscene mode.\n"
                                       "||`Во время режима катсцены Вы не можете отправлять сообщения, если это не "
                                       "комментарии, а также имеете КД сообщений.`||",
                           )
    elif any(ctx.author == d.get("owner") for d in channel_i):
        for i in channel_i: cutscene_channels.remove(i)
        await edit_slowmode(ctx, 0)
        await displayembed(ctx,
                           title="Cutscene end",
                           description="||`Теперь вы снова можете продолжать писать.`||",
                           # thumbnail="",
                           )


@bot.command(aliases=['q', 'кте'])
async def qte(ctx, arg1=None, *, arg2=''):
    symbolset = ['🇽', '🇾', '🇦', '🇧']
    correct = str(random.choice(symbolset))
    time = None
    global qtemsg

    try:
        if float(arg1) > 0:
            time = float(arg1)
            qtetext = arg2
        else: qtetext = arg1
    except Exception: qtetext = arg1

    qtemsg = await ctx.send(
        qtetext + '\nНажмите **' + correct + '**\n(Время до результата: **' + str(time) + '** секунд.)',
        view=QTEButton(ctx, symbol=correct, time=time))


async def pingres(ctx, res): await ctx.send(ctx.author.mention + '\n' + str(res))


@bot.command(aliases=['c', 'ш'])
async def chance(ctx, arg1: int = 100, arg2: int = None, loop: int = 1):
    if arg2 is None:
        end = arg1
        begin = 1
    else:
        begin = arg1
        end = arg2

    res = ''
    for i in range(loop):
        res += str(begin) + '-' + str(end) + ': ' + str(random.randint(begin, end)) + '\n'
    await pingres(ctx, res)
    await ctx.message.delete()


# Fast .chance templates
@bot.command(aliases=['m', 'mc', 'м', 'мш'])
async def multichance(ctx, arg): await chance(ctx, loop=int(arg))

@bot.command(aliases=['1000', 'к'])
async def k(ctx): await chance(ctx, 1000)

@bot.command(aliases=['10000', '10k', '10к', '2', '5'])
async def tenk(ctx): await chance(ctx, 10000)

@bot.command(aliases=['6', 'six'])
async def cube(ctx): await chance(ctx, 6)

@bot.command(aliases=['10'])
async def ten(ctx): ctx, await chance(ctx, 10)


@bot.command(aliases=['operation', 'o', 't'])
async def timer(ctx, reply: str, sec: int = 0, minute: int = 0, hour: int = 0):
    dur = sec
    dur += minute * 60
    dur += hour * 60 * 60
    float(dur)

    await pingres(ctx, "Операция \"" + reply + "\" запущена")
    await asyncio.sleep(dur)
    await pingres(ctx, "Операция \"" + reply + "\" завершена")


@bot.command(aliases=['dr', 'd'])
async def difrand(ctx, *, numbers):
    numbers_list = numbers.split(' ')
    result = [int(item) for item in numbers_list]
    length_numbers = len(result)
    counter = 0
    number = []
    for i in range(length_numbers):
        await_number = random.randint(1, result[counter])
        number.append(await_number)
        counter += 1
    str_number = [str(it) for it in number]

    await pingres(ctx, ', '.join(str_number))


# Old
@bot.command(aliases=['r'])
async def rand(ctx, number: int, count: int):
    res = []
    for i in range(count): res.append(random.randint(1, number))
    await pingres(ctx, str(res)[1:-1])


@bot.command(aliases=['strings'])
async def s(ctx, count: int, *, lst):
    lst = lst.split('; ')
    res = []
    for i in range(count): res.append(random.choice(lst))
    await pingres(ctx, '; '.join(res))


@bot.command()
async def repeat(ctx, count: int, *, args):
    for i in range(count): await ctx.send(args)


# Old
@bot.command(aliases=['gc'])
async def gencomms(ctx, count: int, preferred_difficulty=None):
    def gencomm():
        commtype = random.choice(['dangerous', 'dangerous', 'dangerous', 'dangerous', 'peaceful', 'unknown'])
        if commtype == 'dangerous':
            def dangerdif():
                if preferred_difficulty is None:
                    gendif = random.randint(1, 7)
                else:
                    if preferred_difficulty in ('Нормальное', 'Нормальная', 'Нормальный', 'Normal', '2', '3', '4'):
                        gendif = random.choice([random.randint(1, 7),
                                                random.randint(2, 4)])
                    elif preferred_difficulty in ('Среднее', 'Средняя', 'Средний', 'Middle', '5', '6', '7'):
                        gendif = random.choice([random.randint(1, 7),
                                                random.randint(5, 7)])
                    else:
                        return 'Не могу найти указанной предпочитаемой сложности в списке. Возможно, Вы написали её ' \
                               'неверно.'

                if gendif == 1:
                    return 'Лёгкое'
                elif 2 <= gendif <= 4:
                    return 'Нормальное ' + str((gendif - 1))
                elif 5 <= gendif <= 7:
                    return 'Усложнённое ' + str((gendif - 4))
                elif 8 <= gendif <= 10:
                    return 'Среднее ' + str((gendif - 7))

            return random.choice(comms_list.dangerous) + '\n[_' + dangerdif() + '_]'
        elif commtype == 'peaceful':
            return random.choice(comms_list.peaceful) + '\n[_Безопасное_]'
        elif commtype == 'unknown':
            return random.choice(comms_list.unknown) + '\n[_Неизвестное_]'

    def gencommslist(comms_count):
        res = '1) ' + gencomm()
        for i in range(comms_count - 1):
            res += '\n' + str(i + 2) + ') ' + gencomm()
        return str(res)

    await ctx.send('```\n' + gencommslist(count) + '\n```')


# Old
@bot.command(aliases=['cs'])
async def commsstat(ctx):
    await ctx.send('Опасных: ' + str(len(comms_list.dangerous)) +
                   '\nМирных: ' + str(len(comms_list.peaceful)) +
                   '\nНеизвестных: ' + str(len(comms_list.unknown)))
