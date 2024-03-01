#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED
#           OLD, OUTDATED


import discord
from discord.ext import commands
from random import *
from main import timer
from bot import client


def randdrop(num: int, lst: list):
    result = []
    for i in range(num - 1): result.append(choice(lst))
    return result


@client.command()
async def calc(ctx, dmg: float, defense: float, percent: float, ADL: float):
    if dmg > ADL:
        res = dmg - (defense / 2)
    else:
        res = (dmg - defense) * (1 - (percent / 100))
    await ctx.send('Наносимый урон: ' + str(round(res, 1)))


@calc.error
async def calc_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(description='Введите аргументы:\n.calc <урон> <защита> <защита %> <ЛПУ>', color=0x000000)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
async def tour(ctx, num: int):
    correct = True
    armor = str
    weapon = str
    ranged = str
    another = []
    if num == 1:
        armor = choice(["There could be your list", None]) \
                + " Т." + str(randint(1, 2))
        weapon = choice(["There could be your list", None]) \
                 + " Т." + str(randint(1, 3))
        ranged = choice(["There could be your list", None]) \
                 + " Т." + str(randint(1, 3))
        another = ", ".join(randdrop(num + 1, ["There could be your list", None]))

    elif num == 2:
        armor = choice(["There could be your list", None]) \
                + " Т." + str(randint(2, 4))
        weapon = choice(["There could be your list", None]) \
                 + " Т." + str(randint(3, 5))
        ranged = choice(["There could be your list", None]) \
                 + " Т." + str(randint(3, 5))
        another = ", ".join(randdrop(num, [
            "There could be your list", None
        ]))

    elif num == 3:
        armor = choice(["There could be your list", None]) \
                + " Т." + str(randint(1, 3))
        weapon = choice(["There could be your list", None]) \
                 + " Т." + str(randint(2, 4))
        ranged = choice(["There could be your list", None]) \
                + " Т." + str(randint(1, 4))
        another = ", ".join(randdrop(num, [
            "There could be your list", None
        ]))

    elif num == 4:
        armor = choice(["There could be your list", None]) \
                + " Т." + str(randint(2, 4))
        weapon = choice(["There could be your list", None]) \
                 + " Т." + str(randint(3, 5))
        ranged = choice(["There could be your list", None]) \
                 + " Т." + str(randint(2, 4))
        another = ", ".join(randdrop(num, [
            "There could be your list", None
        ]))

    else:
        correct = False
        if num <= 0:
            await ctx.send("Вы указали неверный номер турнира.")
        else:
            await ctx.send("Такого турнира пока не существует.")

    if correct:
        res = "".join(map(str, ('===========**__Противник:__**===========',
                                '\n__Броня:__ \t\t\t\t\t\t', armor,
                                '\n__Ближнее оружие:__\t', weapon,
                                '\n__Дальнее оружие:__\t', ranged,
                                '\n__Допольнительно:__\t', another
                                )))
        await ctx.send(res)


@client.command()
async def farm(ctx, place: str = None, level: int = 0):
    result = []
    if place is None:
        result.append("Вы не указали место добычи.")
    elif place == "Болото" or place == "болото":
        await timer(ctx, "Сбор ресурсов в болотах...", 0, 30)
        for i in range(8):
            res = choice(
                ["There could be your list", None])
            if res == "Провизия":
                res = choice(["There could be your list", None])
            result.append(res)
    elif place == "Горы" or place == "горы":
        await timer(ctx, "Сбор ресурсов в горах...", 0, 30)
        for i in range(8):
            res = choice(
                ["There could be your list", None])
            if res == "Провизия":
                res = choice(["There could be your list", None])
            result.append(res)
    elif place == "Лес" or place == "лес":
        await timer(ctx, "Сбор ресурсов в лесу...", 0, 30)
        for i in range(8):
            res = choice(["There could be your list", None])
            if res == "Провизия":
                res = choice(["There could be your list", None])
            if res == "Живность":
                res = choice(["There could be your list", None])
            result.append(res)
    elif place == "Лесостепь" or place == "лесостепь":
        await timer(ctx, "Сбор ресурсов в лесостепи...", 0, 30)
        for i in range(8):
            res = choice(
                ["There could be your list", None])
            if res == "Провизия":
                res = choice(["There could be your list", None])
            if res == "Живность":
                res = choice(
                    ["There could be your list", None])
            result.append(res)
    else:
        result.append("Вы не так указали место добычи либо такого места добычи пока не существует.")
    await ctx.send(', '.join(result))


@client.command()
async def collect(ctx, resource: str = None, level: int = 1, rep: int = 1):
    res = "Вы собрали "
    coefficient = ((level + 10) / 10) + (level / 5)
    if resource is None:
        res = "Вы не указали ресурс."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 10) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 6) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 20) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 10) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            ore = choice(["There could be your list", None])
            k = 1
            if ore == '': k = 3
            res = "Вы собрали" + str(round(randint(0, 10) * coefficient) * k) + ore
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 3) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 3) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 3) * coefficient)) + " None."
    elif resource == "None" or resource == "None":
        for i in range(rep):
            res += str(round(randint(0, 6) * coefficient)) + " None."
    else:
        res = "Вы не так указали ресурс либо такого ресурса пока не существует."
    await ctx.send(str(res))


@client.command()
async def mine(ctx, stage: int = 1, level: int = 1):
    res = None
    k = 1
    per = 100
    coefficient = ((level + 10) / 10) + (level / 5)
    if stage == 0:
        res = "А что по-твоему вообще должно быть нулевым ярусом шахты, гений? Поле?"
    elif stage == 1:
        resource = choice(["There could be your list", None])
        if resource == "": per = -75
        if resource == "": per = 200
        if resource == "": per = 200
        if resource == "": per = 100
        if resource == "": per = -20
        if per < 0: k = (100 + per) / 100
        if per > 0: k = per / 100 + 1
        res += str(round(randint(0, 10) * coefficient * k, 2)) + " " + resource + "."
    elif stage == 2:
        resource = choice(["There could be your list", None])

        # could be replaced with match-case now tho
        if resource == "None": per = -60
        if resource == "None": per = 200
        if resource == "None": per = 200
        if resource == "None": per = 100
        if resource == "None": per = -20
        if resource == "None": per = -80
        if resource == "None": per = -90
        if per < 0: k = (100 + per) / 100
        if per > 0: k = per / 100 + 1
        res += str(round(randint(0, 13) * coefficient * k, 2)) + " " + resource + "."
    elif stage == 3:
        resource = choice([
            "There could be your list", None
        ])
        if resource == "None": per = -50
        if resource == "None": per = 200
        if resource == "None": per = 200
        if resource == "None": per = 100
        if resource == "None": per = -20
        if resource == "None": per = -60
        if resource == "None": per = -80
        if resource == "None": per = -80
        if resource == "None": per = -80
        if resource == "None": per = -90
        if per < 0: k = (100 + per) / 100
        if per > 0: k = per / 100 + 1
        res += str(round(randint(0, 16) * coefficient * k, 2)) + " " + resource + "."
    elif stage == 4:
        resource = choice([
            "There could be your list", None
        ])
        if resource == "None": per = -50
        if resource == "None": per = 200
        if resource == "None": per = 200
        if resource == "None": per = 100
        if resource == "None": per = -20
        if resource == "None": per = -40
        if resource == "None": per = -60
        if resource == "None": per = -60
        if resource == "None": per = -80
        if resource == "None": per = -80
        if resource == "None": per = -90
        if per < 0: k = (100 + per) / 100
        if per > 0: k = per / 100 + 1
        res += str(round(randint(0, 15) * coefficient * k, 2)) + " " + resource + "."
    await ctx.send(str(res))
