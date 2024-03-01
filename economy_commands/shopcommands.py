from economy import *
from main import displayembed


# In development, experimental


@bot.command(aliases=["shop"])
async def command_shop(ctx, arg="show", *args):
    if arg == "show":
        await shop_show(ctx, *args)
    elif arg == "list":
        await shop_list(ctx)
    elif arg == "create":
        await shop_create(ctx, *args)
    elif arg == "delete":
        await shop_delete(ctx, *args)
    elif arg == "add":
        await shop_add(ctx, *args)
    elif arg == "remove":
        await shop_remove(ctx, *args)
    elif arg == "delete":
        await shop_delete(ctx, *args)
    else:
        await ctx.send(f"Неизвестная подкоманда \"{arg}\"")


async def shop_list(ctx):
    shops = fetch(f"SELECT name FROM shops")
    res = "## Shops:\n"
    if not shops: res = "Магазинов ещё нет."
    else:
        for i in shops: res += "- " + i[0] + "\n"
    await ctx.send(res)


async def shop_show(ctx, name=None, page=1):
    shop_id = fetchone(f"SELECT shop_id FROM shops WHERE name == '{name}'")
    if shop_id[0] is None:
        await ctx.send(f"Магазин \"**{name}**\" не найден.")
        return

    res = " "
    shopitems = fetch(f"SELECT item_id, price, stock FROM shopitems WHERE shop_id = {shop_id[0]}")
    if not shopitems: res = "Магазин пуст."

    # Сборка интерфейса
    else:
        # Перебор предметов
        itemlist = []
        for i in shopitems:
            selected_item = fetchone(f"SELECT name, desc, icon FROM items WHERE item_id = {i[0]}")
            newitem = {
                "ID": str(i[0]),
                "Price": str(i[1]),
                "Name": str(selected_item[0]),
                "Desc": str(selected_item[1]),
                "Icon": str(selected_item[2]),
            }
            itemlist.append(newitem)

        # Упаковка по страницам
        items_page = itempagepacker(itemlist)

        # Проверки
        if len(items_page) <= 1: res = "Магазин пуст."
        elif page >= len(items_page):
            await ctx.send(f"Такой страницы нет. Всего {len(items_page) - 1} страниц.")
            return

        # Сборка контента вывода
        else:
            shop_currency = fetchone(f"SELECT currency_id FROM shops WHERE name == '{name}'")[0]
            shop_currency = fetch(f"SELECT name, icon FROM currencies WHERE currency_id == '{shop_currency}'")[0]
            # Проверка на всякий случай
            if shop_currency is None: await ctx.send(f"Error: Currency is not found.")

            for i in items_page[page]:
                res += str(i["Price"]) + " " + \
                       str(shop_currency[1]) + " : " + \
                       str(i["Name"]) + " " + str(i["Icon"])
                if i["Desc"] != '' and i["Desc"] is not None:
                    res += "\n\t_" + i["Desc"] + "_"
                res += "\n"
            res += f"\npage {page}"

    # Вывод в чат
    await displayembed(ctx,
                       f"Магазин \"**{name}**\"",
                       res,
                       author=(
                           ctx.author.name,
                           ctx.author.avatar
                       ))


async def shop_create(ctx, name=None, shop_currency=None):
    if name is None:
        await ctx.send("Вы не указали название магазина.")
        return
    elif shop_currency is None:
        await ctx.send("Вы не указали валюту магазина.")
        return
    elif fetchone(f"SELECT * FROM shops WHERE name = '{name}'"):
        await ctx.send("Такой магазин уже существует.")
        return

    shop_currency = fetchone(f"SELECT currency_id FROM currencies WHERE name = '{shop_currency}'")
    if not shop_currency:
        await ctx.send("Такой валюты не существует.")
        return

    sqldb.execute("INSERT INTO shops (name, currency_id, icon) VALUES (?, ?, ?)", (name, int(shop_currency[0]), ''))
    await ctx.send(f"Магазин \"**{name}**\" создан.")
    connection.commit()


async def shop_delete(ctx, name=None):
    if name is None:
        await ctx.send("Вы не указали название магазина.")
        return
    elif not fetchone(f"SELECT * FROM shops WHERE name = '{name}'"):
        await ctx.send("Такого магазина не существует.")
        return

    if not await action_submit(ctx, f"Вы собираетесь удалить магазин {name}. "
                                    f"Вся информация в нём будет безвозвратно утеряна."):
        await ctx.send("Удаление магазина отменено.")
    else:
        sqldb.execute(f"DELETE FROM shops WHERE name = '{name}'")
        await ctx.send(f"Магазин \"**{name}**\" удалён.")
        connection.commit()


async def shop_add(ctx, shop: str = None, item=None, price: int = None, stock: int = None):
    if shop is None:
        await ctx.send("Вы не указали название магазина.")
        return
    if item is None:
        await ctx.send("Вы не указали предмет.")
        return
    if price is None:
        await ctx.send("Вы не указали цену.")
        return

    shop_id = fetchone(f"SELECT shop_id FROM shops WHERE name = '{shop}'")[0]
    item_id = fetchone(f"SELECT item_id FROM items WHERE name = '{item}'")[0]

    if shop_id is None:
        await ctx.send("Такого магазина не существует.")
        return
    if item_id is None:
        await ctx.send("Такого предмета не существует.")
        return

    sqldb.execute("INSERT INTO shopitems (shop_id, item_id, price, stock) VALUES (?, ?, ?, ?)",
                  (shop_id, item_id, price, stock))
    connection.commit()
    await ctx.send(f"Предмет \"**{item}**\" добавлен в магазин \"**{shop}**\" "
                   f"по цене \"**{price}**\" в кол-ве \"**{stock}**\" штук в наличии.")


async def shop_remove(ctx, shop=None, item=None):
    if shop is None:
        await ctx.send("Вы не указали название магазина.")
        return
    if item is None:
        await ctx.send("Вы не указали предмет.")
        return

    shop_id = fetchone(f"SELECT shop_id FROM shops WHERE name = '{shop}'")
    item_id = fetchone(f"SELECT item_id FROM items WHERE name = '{item}'")

    if not shop_id:
        await ctx.send("Такого магазина не существует.")
        return
    if not item_id:
        await ctx.send("Такого предмета не существует.")
        return

    sqldb.execute(f"DELETE FROM shopitems WHERE shop_id = {shop_id} AND item_id = {item_id}")
    connection.commit()
    await ctx.send(f"Предмет \"**{item}**\" удалён из магазина \"**{shop}**\".")


async def shop_edititem(ctx, shop=None, item=None, stock=None, price=None, noReply=False):
    if shop is None:
        await ctx.send("Вы не указали название магазина.")
        return
    if item is None:
        await ctx.send("Вы не указали предмет.")
        return

    shop_id = fetchone(f"SELECT shop_id FROM shops WHERE name = '{shop}'")[0]
    item_id = fetchone(f"SELECT item_id FROM items WHERE name = '{item}'")[0]

    if shop_id is None:
        await ctx.send("Такого магазина не существует.")
        return
    if item_id is None:
        await ctx.send("Такого предмета не существует.")
        return

    sqlcommand = "UPDATE shopitems SET "
    if price is not None: sqlcommand += f"price = '{price}' "
    if price is not None and stock is not None: sqlcommand += "AND "
    if stock is not None: sqlcommand += f"stock = '{stock}' "
    sqlcommand += f"WHERE shop_id = {shop_id} AND item_id = {item_id}"
    print(sqlcommand)

    sqldb.execute(sqlcommand)
    connection.commit()
    if not noReply: await ctx.send(f"Предмет \"**{item}**\" изменён в магазине \"**{shop}**\".")


async def shopedititem(ctx, shop=None, item=None, stock=None, noReply=False):
    if shop is None:
        await ctx.send("Вы не указали название магазина.")
        return
    if item is None:
        await ctx.send("Вы не указали предмет.")
        return

    shop_id = fetchone(f"SELECT shop_id FROM shops WHERE name = '{shop}'")[0]
    item_id = fetchone(f"SELECT item_id FROM items WHERE name = '{item}'")[0]

    if shop_id is None:
        await ctx.send("Такого магазина не существует.")
        return
    if item_id is None:
        await ctx.send("Такого предмета не существует.")
        return

    if stock is not None:
        sqlcommand = f"UPDATE shopitems SET stock = '{stock}' WHERE shop_id = {shop_id} AND item_id = {item_id}"
        sqldb.execute(sqlcommand)
        connection.commit()


@bot.command(aliases=[])
async def buy(ctx, shop=None, item=None, profile="default", count: int = 1):
    # Проверки на обязательные аргументы
    if shop is None:
        await ctx.send("Вы не указали название магазина.")
        return
    elif not fetchone(f"SELECT * FROM shops WHERE name = '{shop}'"):
        await ctx.send("Такого магазина не существует.")
        return
    if item is None:
        await ctx.send("Вы не указали предмет.")
        return
    elif not fetchone(f"SELECT * FROM items WHERE name = '{item}'"):
        await ctx.send("Такого предмета не существует.")
        return
    profile_id = fetchone(f"SELECT profile_id FROM profiles WHERE owner = '{ctx.author.id}'")[0]
    if profile_id is None:
        await ctx.send(f"Профиль {profile} не найден.")
        return

    # Считываем данные магазина и айди предмета
    item_id = fetchone(f"SELECT item_id FROM items WHERE name == '{item}'")[0]
    shopdata = fetch(f"SELECT shop_id, currency_id FROM shops WHERE name == '{shop}'")[0]
    shop_id = shopdata[0]
    currency_id = shopdata[1]

    # Получаем общую цену
    price = count * int(fetchone(f"SELECT price FROM shopitems WHERE shop_id = {shop_id} AND item_id = {item_id}")[0])

    # Проверяем, хватает ли балланса
    balance = fetchone(f"SELECT balance FROM balances WHERE currency = {currency_id} AND profile_id = {profile_id}")[0]
    if balance < price:
        await ctx.send("Недостаточно средств.")
        return

    # Если склад магазина ограничен то забираем предметы со склада
    stock = fetchone(f"SELECT stock FROM shopitems WHERE item_id = '{item_id}'")[0]
    if stock is not None:
        stock -= count
        # Если столько нет в наличии
        if stock < 0:
            await ctx.send("Столько указанных предметов нет в наличии магазина.")
            return

    # Изменяем таблицы
    if stock is not None: await shop_edititem(ctx, shop, item, stock)
    from economy_commands.inventorycommands import inv_change
    await inv_change(ctx, "add",
                     item_name=item,
                     count=count,
                     profile_name=profile,
                     profile_owner_id=ctx.author.id,
                     noReply=True)
    await balance_edit(profile_id, currency_id, -price)

    # Оповещаем о покупке
    currency_icon = fetchone(f"SELECT icon FROM currencies WHERE currency_id = {currency_id}")
    await ctx.send(f"Вы купили х{count} **{item}** за {price} {currency_icon} в магазине \"**{shop}**\".")


if __name__ is "__main__": print("This file cannot be launched as main.")
