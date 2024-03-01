from economy import *
from main import displayembed


# In development, experimental


@bot.command(aliases=['inv'])
async def inventory(ctx, arg="show", *args):
    if arg == "show":
        await inv_show(ctx, *args)
    elif arg == "add":
        await inv_change(ctx, 'add', *args)
    elif arg == "remove":
        await inv_change(ctx, 'remove', *args)
    elif arg == "use":
        await inv_change(ctx, 'use', *args)


async def inv_show(ctx, name='default', page=1, profile_owner_id=0):
    # Если не был дан айди профиля, то смотрим профиль автора
    if not profile_owner_id: profile_owner_id = ctx.author.id

    selected_profile = fetchone(
        f"SELECT profile_id,name,image FROM profiles WHERE owner == {profile_owner_id} AND name == '{name}'")

    if selected_profile is None:
        await ctx.send(f"Профиль \"{name}\" не найден.")
    else:
        profile_id = selected_profile[0]
        name = selected_profile[1]
        image = selected_profile[2]

        # Перебор предметов
        profile_items = fetch(f"SELECT item, count FROM 'inventories' WHERE profile_id = {profile_id}")
        itemlist = []
        for i_item in profile_items:
            selected_item = fetchone(f"SELECT * FROM 'items' WHERE item_id = {i_item[0]}")
            if selected_item:
                newitem = {
                    "Name": str(selected_item[1]),
                    "Icon": str(selected_item[3]),
                    "Count": str(i_item[1])
                }
                itemlist.append(newitem)

        items_page = itempagepacker(itemlist)

        res = ""
        if len(items_page) <= 1: res = "Инвентарь пуст."
        elif page >= len(items_page):
            await ctx.send(f"Такой страницы нет. Всего {len(items_page)-1} страниц.")
            return
        else:
            for item in items_page[page]:
                res += "\n" + item["Count"] + " : " + item["Icon"] + item["Name"] + ";" + \
                       f"\n\npage {page}"

        await displayembed(ctx,
                           f"\tИнвентарь профиля: {name}",
                           res,
                           thumbnail=image,
                           author=(
                               ctx.author.name,
                               ctx.author.avatar
                           ))


async def inv_change(ctx, action, item_name=None, count=1, profile_name='default', profile_owner_id=0, noReply=False):
    try: count = int(count)
    except TypeError:
        await ctx.send("Кол-во предметов должно быть целочисленным!")
        return

    # Выбор профиля
    if not profile_owner_id:  # Если не был дан айди профиля, то смотрим профиль автора
        profile_owner_id = ctx.author.id
    selected_profile = fetchone(f"SELECT profile_id FROM profiles "
                                f"WHERE owner == {profile_owner_id} AND name == '{profile_name}'")

    # Проверки профиля и предмета на валидность
    if selected_profile is None:
        await ctx.send(f"Профиль {profile_name} не найден.")
        return
    elif item_name is None:
        await ctx.send("Вы не указали название предмета.")
        return

    # Выбор предмета из глобального списка предметов
    selected_glob_item = fetchone(f"SELECT * FROM items WHERE name = '{item_name}'")
    if not selected_glob_item:  # Проверка есть ли такой предмет
        await ctx.send("Такой предмет не существует.")
        return

    # Выбор предмета в инвентаре профиля
    selected_item = fetchone(f"SELECT item, count FROM inventories "
                             f"WHERE profile_id = '{selected_profile[0]}' "
                             f"AND item = '{selected_glob_item[0]}'")

    # Этап изменения

    await universal_inventory_edit(
        action=action,
        selected_item=selected_item,
        item_id=selected_glob_item[0],
        profile_id=selected_profile[0],
        count=count
    )

    # Если предмета ещё не существует в инвентаре
    # if not selected_item:
    #     if action == 'add': sqldb.execute(f"INSERT INTO 'inventories' (profile_id, item, count) "
    #                                       f"VALUES (?, ?, ?)", (selected_profile[0], selected_glob_item[0], count))
    #     else:
    #         await ctx.send("У этого профиля нет такого кол-ва указанных предметов.")
    #         return
    #
    # # Если предмет уже существует в инвентаре
    # else:
    #     if not action == "add": count -= count
    #     # Производим изменение кол-ва предметов в инвентаре
    #     sqldb.execute(f"UPDATE 'inventories' SET count = {selected_item[1] + count} "
    #                   f"WHERE profile_id = '{selected_profile[0]}' "
    #                   f"AND item = '{selected_item[0]}'")
    #     # Если предметов не осталось то удаляем
    #     if selected_item[1] <= 0:
    #         sqldb.execute(f"DELETE FROM inventories "
    #                       f"WHERE profile_id = '{selected_profile[0]}' "
    #                       f"AND item == '{selected_item[0]}'")
    # connection.commit()

    # Отправка сообщения, если нужно
    if not noReply:
        msg = ""
        if action == 'add':
            await ctx.send(f"Профилю **{profile_name}** было выдано **{count}** предметов \"**{item_name}**\".")
        elif action == 'use':
            msg += selected_glob_item[4] + f"\n_||`({profile_name}: -{count} \"{item_name}\".)`||_"
        else:
            msg += f"У профиля **{profile_name}** было убрано **{count}** предметов \"**{item_name}**\"."
        await ctx.send(msg)


if __name__ is "__main__": print("This file cannot be launched as main.")
