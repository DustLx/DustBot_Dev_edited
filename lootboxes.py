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


from bottoken import TOKEN
import discord
import random
from bot import client
from lootboxes.loot_list import quality_loot, gloss_loot, common_loot
from lootboxes.magerials_list import quality_magerials, common_magerials
import lootchances
import boxes


templates = [
    {
        'name': '',
        'type': '',
        'img': '',
        'desc': '',
        'quality': '',
        'prop': '',
    },
    {
        'name': '',
        'type': '',
        'img': '',
        'desc': '',
        'quality_chance': 0,
        'gloss_chance': 0,
        'stellar_chance': 0,
    },
]


def create_button(bstyle: int, label: str = None, emoji=None):
    if bstyle == 1: return discord.ui.button(style=discord.ButtonStyle.primary, label=label, emoji=emoji)
    elif bstyle == 2: return discord.ui.button(style=discord.ButtonStyle.secondary, label=label, emoji=emoji)
    elif bstyle == 3: return discord.ui.button(style=discord.ButtonStyle.success, label=label, emoji=emoji)
    elif bstyle == 4: return discord.ui.button(style=discord.ButtonStyle.danger, label=label, emoji=emoji)


class ChooseButton(discord.ui.View):
    interacted: bool = False

    def __init__(self, ctx):
        super().__init__()
        self.breply_final = None
        self.ctx = ctx

    async def btn_callback(self, reply, interaction: discord.interactions.Interaction, button: discord.ui.Button):
        self.interacted = True
        self.breply_final = reply
        await choosemsg.edit(content=self.breply_final, view=None)

    @create_button(1, 'Забрать предмет')
    async def btn_callback1(self, interaction, button):
        await self.btn_callback(str('<@' + str(interaction.user.id) + '> \n' +
                                    '*Вы забираете предмет.*'),
                                interaction, button)

    @create_button(1, 'Продать предмет')
    async def btn_callback2(self, interaction, button):
        await self.btn_callback(str('<@' + str(interaction.user.id) + '> \n' +
                                    '*Вы продаёте предмет за* ' + str(defprice(droppeditem.get('quality')))),
                                interaction, button)


def defprice(qual):
    k = '<:ECOkriton_NXRP:918860060183126036>'
    p = '<:ECOprimeshiner_NXRP:925498593094279249>'
    price = '0'

    def ifarmor(itemprice):
        if itemtype == 'Armor': return itemprice * 2
        else: return itemprice

    if qual == '*Плохое*' or qual == 'Дешёвое':
        price = str(ifarmor(250)) + k
    elif qual == '__Качественное__':
        price = str(ifarmor(500)) + k
    elif qual == '**__Блестящее__**':
        price = str(ifarmor(1000)) + k + '; ' + str(ifarmor(20)) + p
    elif qual == '':
        price = ''

    return price


async def lootitem(ctx, box):
    global itemtype
    global droppeditem
    global choosemsg

    if random.randint(1, 100) <= 35: itemtype = 'Armor'
    else: itemtype = 'Weapon'
    if itemtype == 'Weapon': droppeditem = random.choice(box.weaponlist)
    elif itemtype == 'Armor': droppeditem = random.choice(box.armorlist)

    await ctx.send('**' + droppeditem.get('name') + '** ' + '(Качество: ' + droppeditem.get('quality') + ')')
    await ctx.send(droppeditem.get('img'))
    iteminfotext = '**Тип:** ' + droppeditem.get('type') + '\n**Описание:** ' + droppeditem.get('desc') + \
                   '\n**Свойства:** ' + droppeditem.get('prop')
    await ctx.send(str(iteminfotext))

    choosemsg = await ctx.send('Продажа предмета: ' + str(defprice(droppeditem.get('quality'))),
                               view=ChooseButton(ctx))


@client.command(aliases=['oba'])
async def openboxarming(ctx, boxtype: str, customrarity: str = 'None'):
    def defrarity(percentage, quality, gloss, stellar):
        res = 'Common'
        if percentage <= quality:
            res = 'Quality'
        if percentage <= gloss:
            res = 'Gloss'
        if percentage <= stellar:
            res = 'Stellar'

        if customrarity.lower() == 'common':
            res = 'Common'
        if customrarity.lower() == 'quality':
            res = 'Quality'
        if customrarity.lower() == 'gloss':
            res = 'Gloss'
        if customrarity.lower() == 'stellar':
            res = 'Stellar'

        return res

    async def generateloot(droppedrarity):
        res = None
        if droppedrarity == 'Common':
            droptype = random.choice(['Rubelite', 'Money', 'Item', 'Item'])
            if droptype == 'Rubelite':
                res = '<:ECOer_pieces_NXRP:980802082137317426> x' + str(random.randint(1, 5))
            if droptype == 'Money':
                res = '<:ECOkriton_NXRP:918860060183126036> x' + str(random.randint(500, 1500))
            if droptype == 'Item':
                await lootitem(ctx, common_loot)

        elif droppedrarity == 'Quality':
            droptype = random.choice(['Rubelite', 'Stargems', 'Apotrope', 'Item', 'Item'])
            if droptype == 'Rubelite':
                res = '<:ECOer_pieces_NXRP:980802082137317426> x' + str(random.randint(6, 12))
            if droptype == 'Stargems':
                res = '<:ECOstargem_NXRP:980802082502213652> x' + str(random.randint(1, 5))
            if droptype == 'Apotrope':
                if random.randint(1, 100) <= 50: res = '**__Апотроп (⭐⭐)__**'
                else: res = '__Апотроп (⭐)__'
            if droptype == 'Item':
                await lootitem(ctx, quality_loot)

        elif droppedrarity == 'Gloss':
            droptype = random.choice(['Stargems', 'Apotrope', 'Item', 'Item', 'Allycard'])
            if droptype == 'Stargems':
                res = '<:ECOstargem_NXRP:980802082502213652> x' + str(random.randint(6, 12))
            if droptype == 'Apotrope':
                res = '**__Апотроп (⭐⭐⭐)__**'
            if droptype == 'Item':
                await lootitem(ctx, gloss_loot)
            if droptype == 'Allycard':
                res = '**__ЭЛЛАЙ-КАРТА__**'

        elif droppedrarity == 'Stellar':
            res = '**ЛУЧШЕЕ КАЧЕСТВО**'
        if res is None: return res
        else: return str(res)

    reply = ''

    async def opendefinedbox(num):
        return await generateloot(defrarity(random.randint(1, 10000) / 100,
                                            boxes.boxeslist[num - 1].get('quality_chance'),
                                            boxes.boxeslist[num - 1].get('gloss_chance'),
                                            boxes.boxeslist[num - 1].get('stellar_chance')))

    if boxtype.lower() == 'обычный': reply = await opendefinedbox(1)
    elif boxtype.lower() == 'серебряный': reply = await opendefinedbox(2)
    elif boxtype.lower() == 'королевский': reply = await opendefinedbox(3)
    elif boxtype.lower() == 'эпический': reply = await opendefinedbox(4)

    else: reply = 'Такого типа сундука или ящика не существует. Убедитесь, что всё было написано верно.'
    if reply is not None: await ctx.send(reply)
    await ctx.message.delete()


async def lootmagerials(ctx, magerials, rarity):
    def definemagerialtype():
        res = None
        if rarity == 'Common':
            if random.randint(1, 100) <= 15:
                res = 'Papyrus or feather'
            elif random.randint(1, 100) <= 35:
                res = 'Primeshiners'
            elif random.randint(1, 100) <= 60:
                res = 'Magic stone'
            elif random.randint(1, 100) <= 100:
                res = 'Uniterial'
            else:
                res = None
        elif rarity == 'Quality':
            if random.randint(1, 100) <= 15:
                res = 'Papyrus or feather'
            elif random.randint(1, 100) <= 35:
                res = 'Primeshiners'
            elif random.randint(1, 100) <= 60:
                res = 'Magic stone'
            elif random.randint(1, 100) <= 100:
                res = 'Uniterial'
            else:
                res = None
        elif rarity == 'Gloss':
            if random.randint(1, 100) <= 15:
                res = 'Papyrus or feather'
            elif random.randint(1, 100) <= 35:
                res = 'Primeshiners'
            elif random.randint(1, 100) <= 60:
                res = 'Magic stone'
            elif random.randint(1, 100) <= 100:
                res = 'Uniterial'
            else:
                res = None
        return res

    # Выдача предмета
    magerialtype = definemagerialtype()
    if magerialtype == 'Magic stone': dropped_magerial = random.choice(magerials.magical_stones)
    elif magerialtype == 'Uniterial': dropped_magerial = random.choice(magerials.uniterials)
    elif magerialtype == 'Papyrus or feather': dropped_magerial = magerials.papyrus_or_feather
    elif magerialtype == 'Primeshiners':
        dropped_magerial = None
        await ctx.send(str(random.randint(magerials.primeshiners[0], magerials.primeshiners[1])) +
                       'x Primeshiner <:ECOprimeshiner_NXRP:925498593094279249>')
    else: dropped_magerial = None

    # Отправка предмета
    if magerialtype != 'Primeshiners':
        await ctx.send('**' + dropped_magerial.get('name') + '** (Качество: *обыкновенное*)')
        await ctx.send(dropped_magerial.get('img'))
        iteminfotext = '**Тип:** ' + dropped_magerial.get('type') + '\n**Описание:** ' + dropped_magerial.get('desc') + \
                       '\n**Свойства:** ' + dropped_magerial.get('prop')
        await ctx.send(str(iteminfotext))


@client.command(aliases=['obs'])
async def openboxsupply(ctx, boxtype: str, customrarity: str = 'None'):
    def defrarity(percentage, quality, gloss):
        res = 'Common'
        if percentage <= quality:
            res = 'Quality'
        if percentage <= gloss:
            res = 'Gloss'

        if customrarity.lower() == 'common':
            res = 'Common'
        if customrarity.lower() == 'quality':
            res = 'Quality'
        if customrarity.lower() == 'gloss':
            res = 'Gloss'

        return res

    async def generateloot(droppedrarity):
        res = None

        def definedroptype(rarity):
            definedroptype_res = None
            percentageloot = random.randint(1, 10000) / 100
            if percentageloot <= lootchances.lootchanceslist[rarity - 1].get('rubelite_chance'):
                definedroptype_res = 'Rubelite'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('item_chance'):
                definedroptype_res = 'Item'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('kriton_chance'):
                definedroptype_res = 'Money'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('mending_liquor_chance'):
                definedroptype_res = 'Mending liquor'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('magerials_chance'):
                definedroptype_res = 'Magerials'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('apotrope_chance'):
                definedroptype_res = 'Apotrope'
            elif percentageloot <= lootchances.lootchanceslist[rarity - 1].get('descroll_chance'):
                definedroptype_res = 'Descroll'
            else: return 'Error: Invalid droptype'
            return definedroptype_res

        if droppedrarity == 'Common':
            droptype = definedroptype(1)

            if droptype == 'Rubelite':
                res = '<:ECOer_pieces_NXRP:980802082137317426> x' + str(random.randint(1, 5))
            elif droptype == 'Apotrope':
                if random.randint(1, 100) <= 50: res = '__Апотроп (⭐)__'
                else: res = ('Просвящающее масло', 'https://static.wikia.nocookie.net/genshin-impact/images/1/17/'
                                    'Предмет_Священное_масло.png/revision/latest?cb=20210710192246&path-prefix=ru')
            elif droptype == 'Money':
                res = '<:ECOkriton_NXRP:918860060183126036> x' + str(random.randint(250, 1000))
            elif droptype == 'Item':
                await lootitem(ctx, common_loot)
            elif droptype == 'Magerials':
                await lootmagerials(ctx, common_magerials, 'Common')
            elif droptype == 'Mending liquor':
                res = ('Bodging mending liquor',
                       'https://cdn.discordapp.com/attachments/971387310572728361/1028944793889407006/1.png')
            else: res = droptype

        elif droppedrarity == 'Quality':
            droptype = definedroptype(2)

            if droptype == 'Rubelite':
                res = '<:ECOer_pieces_NXRP:980802082137317426> x' + str(random.randint(6, 12))
            if droptype == 'Apotrope':
                apotrope_chance = random.randint(1, 100)
                if apotrope_chance <= 25: res = '**__Апотроп (⭐⭐⭐)__**'
                elif apotrope_chance <= 65: res = '__Апотроп (⭐⭐)__'
                else: res = ('Просвящающая эссенция', 'https://static.wikia.nocookie.net/genshin-impact/images/8/84/'
                                    'Предмет_Священная_эссенция.png/revision/latest?cb=20210710192235&path-prefix=ru')
            if droptype == 'Item':
                await lootitem(ctx, quality_loot)
            if droptype == 'Magerials':
                await lootmagerials(ctx, quality_magerials, 'Quality')
            if droptype == 'Mending liquor':
                res = ('Refiting mending liquor',
                       'https://cdn.discordapp.com/attachments/971387310572728361/1028944793553862696/2.png')
            if droptype == 'Descroll':
                if random.randint(1, 100) <= 65: '__Дескрол х5 (⭐)__'
                else: res = '**__Дескрол х5 (⭐⭐)__**'

        elif droppedrarity == 'Gloss':
            droptype = definedroptype(3)

            if droptype == 'Apotrope':
                res = '**__Апотроп (⭐⭐⭐)__**'
            if droptype == 'Magerials':
                await lootmagerials(ctx, quality_magerials, 'Gloss')
            if droptype == 'Mending liquor':
                res = ('**Enduring mending liquor**',
                       'https://cdn.discordapp.com/attachments/971387310572728361/1028944793096687666/3.png')
            if droptype == 'Descroll':
                if random.randint(1, 100) <= 65: '__Дескрол х5 (⭐)__'
                else: res = '**__Дескрол х5 (⭐⭐)__**'

        if res is None or type(res) == tuple: return res
        else: return str(res)

    reply = None

    async def opendefinedbox(num):
        return await generateloot(defrarity(random.randint(1, 10000) / 100,
                                            boxes.supplyboxeslist[num - 1].get('quality_chance'),
                                            boxes.supplyboxeslist[num - 1].get('gloss_chance')))

    if boxtype.lower() == 'простой': reply = await opendefinedbox(1)
    elif boxtype.lower() == 'богатый': reply = await opendefinedbox(2)
    else: reply = 'Такого типа сундука или ящика не существует. Убедитесь, что всё было написано верно.'

    if reply is not None:
        if type(reply) == tuple:
            for i in reply: await ctx.send(i)
        else: await ctx.send(reply)

    await ctx.message.delete()

client.run(TOKEN)
