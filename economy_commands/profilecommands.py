from economy import *
from main import displayembed


# In development, experimental


@bot.command(aliases=[])
async def profile(ctx, arg1='default', name='default', *args):
    if arg1 == "show":
        await profile_show(ctx, name)
    elif arg1 == "create":
        await profile_create(ctx, name, *args)
    elif arg1 == "delete":
        await profile_delete(ctx, name)
    elif arg1 == "rename":
        await profile_edit(ctx, name, *args)
    elif arg1 == "reimage":
        await profile_edit(ctx, name, *args, doReimage=True)
    elif arg1 == "list":
        await profile_list(ctx)
    else:
        await profile_list(ctx)


async def profile_show(ctx, name='default'):
    selected_profile = fetchone(
        f"SELECT name,owner,image FROM profiles WHERE owner == {ctx.author.id} AND name == '{name}'")
    if selected_profile is None:
        await ctx.send(f"Профиль \"{name}\" не найден.")
    else:
        await displayembed(ctx,
                           selected_profile[0],
                           f"Владелец: <@{selected_profile[1]}>.",
                           thumbnail=selected_profile[2],
                           author=(
                               ctx.author.name,
                               ctx.author.avatar
                           ))


async def profile_create(ctx, name="default", image=""):
    # Проверяем, существует ли профиль
    if fetchone(
            f"SELECT name FROM profiles WHERE name == '{name}' AND owner == {ctx.author.id}"
    ) is not None:
        await ctx.send("Такой профиль уже имеется.")
        return

    # Создаём запись нового профиля
    sqldb.execute(f"INSERT INTO profiles (owner, name, bal, inv, image) VALUES (?, ?, ?, ?, ?)",
                  (ctx.author.id, name, 0, 0, image))
    connection.commit()

    # Вытаскиваем айди нового профиля для дальнейшей работы
    profile_id = fetchone(
        f"SELECT profile_id FROM profiles WHERE owner == {ctx.author.id} AND name == '{name}'"
    )[0]

    # Заполняем валюты
    selected_curs = fetch(f"SELECT currency_id FROM 'currencies'")
    for i_currency in selected_curs:
        sqldb.execute(f"INSERT INTO 'balances' (profile_id, currency, balance) VALUES (?, ?, ?)",
                      (profile_id, i_currency[0], 0))

    connection.commit()
    await ctx.send(f"Профиль {name} создан.")


async def profile_delete(ctx, name=None):
    if name is None:
        await ctx.send("Название профиля не указано.")
        return
    if fetchone(
            f"SELECT name FROM profiles WHERE owner == {ctx.author.id}") is None:
        await ctx.send("Такой профиль не существует.")
        return

    if not await action_submit(ctx, f"Вы собираетесь удалить профиль {name}."
                                    f"Вся информация в нём будет безвозвратно утеряна."):
        await ctx.send("Удаление профиля отменено.")
    else:
        profile_id = fetchone(
            f"SELECT profile_id FROM profiles WHERE owner == {ctx.author.id} AND name == '{name}'"
        )[0]

        sqldb.execute(f"DELETE FROM profiles WHERE name == '{name}' AND owner == {ctx.author.id}")
        sqldb.execute(f"DELETE FROM balances    WHERE profile_id == {profile_id}")
        sqldb.execute(f"DELETE FROM inventories WHERE profile_id == {profile_id}")

        await ctx.send(f"Профиль {name} был удалён.")
        connection.commit()


async def profile_edit(ctx, name='default', newarg=None, doReimage=False):
    old_profile = fetchone(
        f"SELECT name FROM profiles WHERE owner == {ctx.author.id} AND name == '{name}'")
    if old_profile is None:
        await ctx.send(f"Профиль \"{name}\" не найден.")

    else:
        if doReimage:
            if newarg is None: newarg = ''
            sqldb.execute(f"UPDATE 'profiles' SET image = '{newarg}' "
                          f"WHERE owner == {ctx.author.id} AND name == '{name}'")
            await ctx.send(f"Изображение профиля \"{old_profile[0]}\" изменено на {newarg}.")
        else:
            if newarg is None: newarg = 'default'
            sqldb.execute(f"UPDATE 'profiles' SET name = '{newarg}' "
                          f"WHERE owner == {ctx.author.id} AND name == '{name}'")
            await ctx.send(f"Имя профиля \"{old_profile[0]}\" изменено на {newarg}.")


async def profile_list(ctx):
    profiles = fetch(
        f"SELECT name FROM profiles WHERE owner == {ctx.author.id}")
    res = ""
    for profil in profiles:
        res += f"{profil[0]};\n"
    await displayembed(ctx,
                       f"Профили {ctx.author.name}",
                       res,
                       author=(
                           ctx.author.name,
                           ctx.author.avatar
                       ))


if __name__ is "__main__": print("This file cannot be launched as main.")
