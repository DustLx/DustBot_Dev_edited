from bot import bot
import sqlite3

from economy_commands import shopcommands, inventorycommands
from main import displayembed


# In development, experimental


connection = sqlite3.connect('dustbot_economy.db')
sqldb = connection.cursor()


def createTables():
    sqldb.execute("""CREATE TABLE IF NOT EXISTS profiles (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner INTEGER,
        name TEXT,
        bal INTEGER,
        inv INTEGER,
        image TEXT
        )""")

    sqldb.execute("""CREATE TABLE IF NOT EXISTS currencies (
        currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        icon TEXT
        )""")

    sqldb.execute("""CREATE TABLE IF NOT EXISTS items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        desc TEXT,
        icon TEXT,
        reply TEXT
        )""")

    sqldb.execute(f"""CREATE TABLE IF NOT EXISTS balances (
        profile_id INTEGER,
        currency INTEGER,
        balance INTEGER DEFAULT 0
        )""")

    sqldb.execute(f"""CREATE TABLE IF NOT EXISTS inventories (
        profile_id INTEGER,
        item INTEGER,
        count INTEGER DEFAULT 0
        )""")

    sqldb.execute("""CREATE TABLE IF NOT EXISTS shops (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        currency_id INTEGER,
        icon TEXT
        )""")

    sqldb.execute("""CREATE TABLE IF NOT EXISTS shopitems (
        shop_id INTEGER,
        item_id INTEGER,
        price INTEGER,
        stock INTEGER
        )""")


# Utility for easier code

def fetch(sqlRequest, fetchall=True):
    sqldb.execute(sqlRequest)
    if fetchall:
        return sqldb.fetchall()
    else:
        return sqldb.fetchone()


def fetchone(sqlRequest): return fetch(sqlRequest, False)


def itempagepacker(itemlist):
    items_page = [None]
    for i in range(0, len(itemlist), 10):
        page_items = itemlist[i:i + 10]
        items_page.append(page_items)
    return items_page


async def action_submit(ctx, msg):
    await ctx.send(msg + "\nВы уверены? Если да, напишите **\"Да\"**.")
    responded = False
    while not responded:
        res = await bot.wait_for("message")
        if res.author.id == ctx.author.id:
            responded = True
            if res.content == "Да":
                return True
            else: return False


async def universal_inventory_edit(action, selected_item, item_id: int, profile_id: int, count: int):
    # Если предмета ещё не существует в инвентаре
    if not selected_item:
        if action == 'add':
            sqldb.execute(f"INSERT INTO 'inventories' (profile_id, item, count) "
                          f"VALUES (?, ?, ?)", (profile_id, item_id, count))
        else:
            print("У этого профиля нет такого кол-ва указанных предметов.")
            return

    # Если предмет уже существует в инвентаре
    else:
        if not action == "add": count -= count
        # Производим изменение кол-ва предметов в инвентаре
        sqldb.execute(f"UPDATE 'inventories' SET count = {selected_item[1] + count} "
                      f"WHERE profile_id = '{profile_id}' "
                      f"AND item = '{selected_item[0]}'")
        # Если предметов не осталось то удаляем
        if selected_item[1] <= 0:
            sqldb.execute(f"DELETE FROM inventories "
                          f"WHERE profile_id = '{profile_id}' "
                          f"AND item == '{selected_item[0]}'")
    connection.commit()


def trade(ctx, profile_id: int, shop=None, item=None, profile="default", count: int = 1):
    result = {
        "Message": str
    }

    # Считываем данные магазина и айди предмета
    item_id = fetchone(f"SELECT item_id FROM items WHERE name == '{item}'")[0]
    shopdata = fetch(f"SELECT shop_id, currency_id FROM shops WHERE name == '{shop}'")[0]
    shop_id = shopdata[0]
    currency_id = shopdata[1]

    # Получаем общую цену
    price = count * int(fetchone(f"SELECT price FROM shopitems WHERE shop_id = {shop_id} AND item_id = {item_id}")[0])

    # Проверяем, хватает ли балланса
    buyer_balance = fetchone(f"SELECT balance FROM balances WHERE currency = {currency_id} AND profile_id = {profile_id}")[0]
    if buyer_balance < price:
        result["Message"] = "Недостаточно средств."
        return

    # Если склад магазина ограничен то забираем предметы со склада
    stock = fetchone(f"SELECT stock FROM shopitems WHERE item_id = '{item_id}'")[0]
    if stock is not None:
        stock -= count
        # Если столько нет в наличии
        if stock < 0:
            result["Message"] = "Столько указанных предметов нет в наличии магазина."
            return

    # Работа с инвентарём
    await inventorycommands.inv_change(ctx, "add",
                                       item_name=item,
                                       count=count,
                                       profile_name=profile,
                                       profile_owner_id=ctx.author.id,
                                       noReply=True)

    if stock is not None: await shopcommands.shop_edititem(ctx, shop, item, stock)
    await inventorycommands.inv_change(ctx, "add",
                                       item_name=item,
                                       count=stock,
                                       profile_name=shop,
                                       profile_owner_id=ctx.author.id,
                                       noReply=True)

    # Работа с баллансом
    await balance_edit(profile_id, currency_id, -price)

    return result


'''
==========КОМАНДЫ ВАЛЮТ И БАЛЛАНСА==========
'''


@bot.command(aliases=['bal'])
async def balance(ctx, name='default'):
    selected_profile = fetchone(
        f"SELECT profile_id,name,image FROM profiles WHERE owner == {ctx.author.id} AND name == '{name}'")

    if selected_profile is None:
        await ctx.send(f"Профиль \"{name}\" не найден.")
    else:
        # Настраиваем переменные с профиля для работы
        profile_id = selected_profile[0]
        name = selected_profile[1]
        image = selected_profile[2]
        res = ""
        # Перебираем все валюты
        curs = fetch(f"SELECT * FROM 'currencies'")
        for i_cur in curs:
            # Выбираем балланс
            balances = fetchone(
                f"SELECT * FROM 'balances' WHERE profile_id = {profile_id} AND currency = {i_cur[0]}")
            # Если балланса с этой валютой нет, то создаём
            if not balances:
                sqldb.execute(f"INSERT INTO 'balances' (profile_id, currency, balance) VALUES (?, ?, ?)",
                              (profile_id, i_cur[0], 0))
                connection.commit()
                # Заново выбираем обновлённую запись балланса по валюте
                balances = fetchone(
                    f"SELECT * FROM 'balances' WHERE profile_id = {profile_id} AND currency = {i_cur[0]}")
            res += f"\n{i_cur[2]} {i_cur[1]}: {str(balances[2])};"

        await displayembed(ctx,
                           f"\tБалланс профиля: {name}.",
                           res,
                           author=(
                               ctx.author.name,
                               ctx.author.avatar
                           ),
                           thumbnail=image)


async def balance_edit(profile_id: int, currency_id, value: int, set: bool = False):
    if set: balance = 0
    else: balance = fetchone(f"SELECT balance FROM 'balances' "
                             f"WHERE profile_id = {profile_id} AND currency = {currency_id}")[0]

    sqldb.execute(f"UPDATE balances SET balance = {balance + value} "
                  f"WHERE profile_id = {profile_id} AND currency = {currency_id}")
    connection.commit()


@bot.command(aliases=['baladd'])
async def balance_add(ctx, profile_name: str, currency_name: str, value: int, owner: int = None):
    if owner is None: owner = ctx.author.id
    profile_id = fetchone(f"SELECT profile_id FROM profiles "
                          f"WHERE owner == {owner} AND name == '{profile_name}'")[0]
    currency_id = fetchone(f"SELECT currency_id FROM currencies "
                           f"WHERE name == '{currency_name}'")[0]
    await balance_edit(profile_id, currency_id, value)
    await ctx.send(f"Профилю {profile_name} добавлено **{currency_name} x{value}**.")


@bot.command(aliases=[])
async def pay(ctx, payer: str = None, currency_name: str = None, value: int = None,
              reciever: str = None, owner: int = None):
    if payer is None:
        return await ctx.send(f"Не указан профиль платящего.")
    if reciever is None:
        return await ctx.send(f"Не указан профиль получателя.")
    if currency_name is None:
        return await ctx.send(f"Не указана валюта.")
    if value is None:
        return await ctx.send(f"Не указано кол-во.")
    if owner is None:
        return await ctx.send(f"Не указан айди аккаунта профиля получателя.")

    await balance_add(ctx, reciever, currency_name, value, owner)

    profile_id = fetchone(f"SELECT profile_id FROM profiles "
                          f"WHERE owner == {ctx.author.id} AND name == '{payer}'")[0]
    currency_id = fetchone(f"SELECT currency_id FROM currencies "
                           f"WHERE name == '{currency_name}'")[0]
    await balance_edit(profile_id, currency_id, -value)
    await ctx.send(f"Профилю {payer} добавлено **{currency_name} x{value}**.")


@bot.command(aliases=['balset'])
async def balance_set(ctx, profile_name: str, currency_name: str, value: int, owner: int = None):
    if owner is None: owner = ctx.author.id
    profile_id = fetchone(f"SELECT profile_id FROM profiles "
                          f"WHERE owner == {owner} AND name == '{profile_name}'")[0]
    currency_id = fetchone(f"SELECT currency_id FROM currencies "
                           f"WHERE name == '{currency_name}'")[0]
    await balance_edit(profile_id, currency_id, value, set=True)
    await ctx.send(f"Профилю {profile_name} установлен баланс **{currency_name} в {value}**.")


@bot.command(aliases=['cur'])
async def currency(ctx, arg="show", *args):
    if arg == "show":
        await   currency_show(ctx)
    elif arg == "create":
        await currency_create(ctx, *args)
    elif arg == "delete":
        await currency_delete(ctx, *args)


async def currency_show(ctx):
    currencies = fetch(f"SELECT * FROM 'currencies'")
    if not currencies:
        await ctx.send("Ни одной валюты ещё не создано.")
    else:
        res = ""
        for cur in currencies:
            res += "\n" + cur[2] + " " + cur[1] + ";"
        await displayembed(ctx,
                           "Валюты",
                           res,
                           author=(
                               ctx.author.name,
                               ctx.author.avatar
                           ))


async def currency_create(ctx, name=None, icon=''):
    if name is None:
        await ctx.send("Вы не указали название валюты.")
    else:
        selected_currency = fetchone(f"SELECT * FROM currencies WHERE name = '{name}'")
        if selected_currency:
            await ctx.send("Такая валюта уже существует.")
        else:
            sqldb.execute(f"INSERT INTO currencies (name, icon) VALUES (?, ?)", (name, icon))
            await ctx.send(f"Валюта {icon}{name} создана.")
            connection.commit()


async def currency_delete(ctx, name=None):
    if name is None:
        await ctx.send("Вы не указали название валюты.")
    else:
        if await action_submit(ctx, f"Вы собираетесь удалить валюту {name}. "
                                    f"Это удалит баллансы по этой валюте у всех профилей безвозвратно."):
            selected_currency = fetchone(
                f"SELECT * FROM currencies WHERE name == '{name}'")
            if not selected_currency:
                await ctx.send("Такая валюта не существует.")
            else:
                sqldb.execute(f"DELETE FROM currencies WHERE name == '{name}'")
                await ctx.send(f"Валюта {name} удалена.")
                connection.commit()


'''
==========КОМАНДЫ ПРЕДМЕТОВ==========
'''


@bot.command(aliases=[])
async def item(ctx, arg="show", *args):
    if arg == "show":
        await   item_show(ctx)
    elif arg == "create":
        await item_create(ctx, *args)
    elif arg == "delete":
        await item_delete(ctx, *args)


@bot.command(aliases=[])
async def items(ctx):
    await item_show(ctx)


async def item_show(ctx):
    sqldb.execute(f"SELECT * FROM 'items'")
    items = sqldb.fetchall()
    if not items:
        await ctx.send("Ни одного предмета ещё не создано.")
    else:
        res = ""
        for item in items:
            icon = item[3]
            name = item[1]
            desc = item[2]
            repl = item[4]

            res += f"\n**{icon} {name}**"
            if desc != '' and desc is not None:
                res += f"\n\t_{desc}_"
            res += f"\n\tReply: _`{repl}`_;"
            res += "\n"

        await displayembed(ctx,
                           "Предметы",
                           res,
                           author=(
                               ctx.author.name,
                               ctx.author.avatar
                           ))


async def item_create(ctx, name=None, icon='', desc=''):
    if name is None:
        await ctx.send("Вы не указали название предмета.")
    elif fetchone(f"SELECT * FROM items WHERE name = '{name}'"):
            await ctx.send("Такой предмет уже существует.")
    else:

        sqldb.execute(f"INSERT INTO items (name, desc, icon, reply) VALUES (?, ?, ?, ?, ?)",
                      (name, desc, icon, f'Предмет **{name}** использован.', 0))
        await ctx.send(f"Предмет **{icon}{name}** создан.")
        connection.commit()


async def item_delete(ctx, name=None):
    if name is None:
        await ctx.send("Вы не указали название предмета.")
    else:
        if await action_submit(ctx, f"Вы собираетесь глобально удалить предмет {name}. "
                                    f"Это удалит все такие предметы у всех профилей безвозвратно."):
            sqldb.execute(f"SELECT * FROM items WHERE name == '{name}'")
            selected_currency = sqldb.fetchone()
            if not selected_currency:
                await ctx.send("Такой предмет не существует.")
            else:
                sqldb.execute(f"DELETE FROM items WHERE name == '{name}'")
                await ctx.send(f"Предмет **{name}** удалён.")
                connection.commit()


createTables()


if __name__ is "__main__": print("This file cannot be launched as main.")
