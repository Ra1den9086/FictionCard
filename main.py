from telebot import *
import sqlite3
import random
from universe import commons, rares, legendaries, mythics
TOKEN = ('7988172501:AAEVAKZRhu_8tb3BAgeIMMWPKVmrSY2qdJw')
bot = TeleBot(TOKEN)


#получаем информацию из таблицы
def get_table_info(message):
    conn = sqlite3.connect('data_base.sql')
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id int varchar(20), attempts int varchar(30), PTS int varchar(50), new int varchar(3), old_time int varchar(10), new_time int varchar(10), commons str, rares str, legendaries str, mythics str)')
    cur.execute(
        'SELECT * FROM users')
    users = cur.fetchall()
    global users_commons
    global users_rares
    global users_legendaries
    global users_mythics
    global id
    global attempts
    global PTS
    global new
    global old_time
    global new_time
    id = message.from_user.id
    attempts = 5
    PTS = 0
    new = 1
    old_time = 0
    new_time = 1800
    users_commons = ''
    users_rares = ''
    users_legendaries = ''
    users_mythics = ''
    for el in users:
        if el[0] == id:
            attempts = el[1]
            PTS = el[2]
            new = 0
            old_time = el[4]
            new_time = el[5]
            users_commons = el[6]
            users_rares = el[7]
            users_legendaries = el[8]
            users_mythics = el[9]
        elif el[0] != id:
            continue
    if new == 1:
        new = 0
        cur.execute(
            'INSERT INTO users '
            '(id, attempts, PTS, new, old_time, new_time, commons, rares, legendaries, mythics) '
            'VALUES '
            '("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")'
            %
            (id, attempts, PTS, new, old_time, new_time, users_commons, users_rares, users_legendaries, users_mythics))
    conn.commit()
    cur.close()
    conn.close()
#обновляем таблицу
def update_table(message):
    conn = sqlite3.connect('data_base.sql')
    cur = conn.cursor()
    global users_commons
    global users_rares
    global users_legendaries
    global users_mythics
    global id
    global attempts
    global PTS
    global old_time
    global new_time
    cur.execute('UPDATE users SET '
    'attempts=?, PTS=?, old_time=?, new_time=?, commons=?, rares=?, legendaries=?, mythics=? WHERE id = ?',
    (attempts, PTS, old_time, new_time, users_commons, users_rares, users_legendaries, users_mythics, id))
    conn.commit()
    cur.close()
    conn.close()


#Меню
@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    button_keyboard = types.ReplyKeyboardMarkup()
    get_card_btn = types.KeyboardButton('🎴Получить карту')
    open_menu_btn = types.KeyboardButton('🗺Меню')
    button_keyboard.row(get_card_btn, open_menu_btn)
    get_table_info(message)

    button = types.InlineKeyboardMarkup()
    craft_btn = types.InlineKeyboardButton('♻️Крафт', callback_data='craft_menu')
    cards_menu_btn = types.InlineKeyboardButton('📰Мои карты', callback_data='cards_menu')
    button.row(craft_btn, cards_menu_btn)
    bot.send_message(message.chat.id, f'Приветсвую, {message.from_user.first_name}!', reply_markup=button_keyboard)
    bot.send_message(message.chat.id,
                     f'<b>🖊Ник:</b> <a href="tg://user?id={id}">{message.from_user.first_name}</a> \n'
                     f'🤖<b>ID:</b> <code>{id}</code> \n'
                     f'🔄<b>Попытки:</b> {attempts} \n'
                     f'<blockquote><b>⛩PTS:</b> {PTS}</blockquote>'
                     , reply_markup=button, parse_mode='HTML')
#команды для разработчиков
@bot.message_handler(commands=['give'])
def admin_menu(message):
    if message.from_user.id == 1082345086:
        parts = message.text.split()
        get_table_info(message)
        global id
        global attempts
        id = int(parts[1])
        attempts += int(parts[2])
        update_table(message)
        bot.send_message(message.chat.id, f'Успешно выдано {parts[2]} круток пользователю {parts[1]}')

#отслежка кнопок
@bot.callback_query_handler(func=lambda callback: True)
def button_check(callback):
    global temp_num_of_cards
    global num_of_cards_sum
    global time_cards_num
    global time_cards
    global users_commons
    global users_rares
    global users_legendaries
    global users_mythics
    #проверка кнопок в 'моих картах'
    cards_rarity = 'none'
    users_cards_rarity = 'none'
    cards_list_rarity = 'none'
    prefix = 'none'
    if callback.data == 'cards_menu':
        get_table_info(callback)
        button = types.InlineKeyboardMarkup()
        commons_btn = types.InlineKeyboardButton('👶common', callback_data='view_commons')
        rares_btn = types.InlineKeyboardButton('🧵rare', callback_data='view_rares')
        legendaries_btn = types.InlineKeyboardButton('⭐️legendary', callback_data='view_legendaries')
        mythics_btn = types.InlineKeyboardButton('🧩mythic', callback_data='view_mythics')
        button.row(commons_btn, rares_btn)
        button.row(legendaries_btn, mythics_btn)
        bot.send_message(callback.from_user.id, 'Выберите редкость, которую хотите посмотреть', reply_markup=button)

#смотрим список карт
    if callback.data == 'view_commons':
        prefix = '👶'
        cards_rarity = commons
        users_cards_rarity = users_commons
        cards_list_rarity = 'common'
    elif callback.data == 'view_rares':
        prefix = '🧵'
        cards_rarity = rares
        users_cards_rarity = users_rares
        cards_list_rarity = 'rare'
    elif callback.data == 'view_legendaries':
        prefix = '⭐️'
        cards_rarity = legendaries
        users_cards_rarity = users_legendaries
        cards_list_rarity = 'legendary'
    elif callback.data == 'view_mythics':
        prefix = '🧩'
        cards_rarity = mythics
        users_cards_rarity = users_mythics
        cards_list_rarity = 'mythic'

    if users_cards_rarity != 'none' and cards_rarity != 'none':
        time_cards_num = []
        time_cards = []
        num_of_cards_sum = 0
        temp_num_of_cards = 0
        for el in cards_rarity:
            if users_cards_rarity.count(el) != 0:
                time_cards_num.append(users_cards_rarity.count(el))
                time_cards.append(el)
                num_of_cards_sum += 1
        button = types.InlineKeyboardMarkup()
        left_btn = types.InlineKeyboardButton('⬅️', callback_data='left')
        mid_btn = types.InlineKeyboardButton(f'{temp_num_of_cards + 1}/{num_of_cards_sum}', callback_data='mid')
        right_btn = types.InlineKeyboardButton('➡️', callback_data='right')
        button.row(left_btn, mid_btn, right_btn)
        try:
            bot.send_message(callback.from_user.id, f'{prefix}{time_cards[temp_num_of_cards]} (x{time_cards_num[temp_num_of_cards]})',
                         reply_markup=button)
        except IndexError:
            bot.send_message(callback.from_user.id, f'У вас нету карт редкости <b>{cards_list_rarity}!</b>', parse_mode='HTML')



    if callback.data == 'left':
        if temp_num_of_cards > 0:
            temp_num_of_cards -= 1
            button = types.InlineKeyboardMarkup()
            left_btn = types.InlineKeyboardButton('⬅️', callback_data='left')
            mid_btn = types.InlineKeyboardButton(f'{temp_num_of_cards + 1}/{num_of_cards_sum}', callback_data='mid')
            right_btn = types.InlineKeyboardButton('➡️', callback_data='right')
            button.row(left_btn, mid_btn, right_btn)
            bot.edit_message_text(
            f'{time_cards[temp_num_of_cards]} (x{time_cards_num[temp_num_of_cards]})',
            callback.from_user.id,
            callback.message.message_id,
            reply_markup=button)

    elif callback.data == 'right':
        if temp_num_of_cards + 1 != num_of_cards_sum:

            temp_num_of_cards += 1
            button = types.InlineKeyboardMarkup()
            left_btn = types.InlineKeyboardButton('⬅️', callback_data='left')
            mid_btn = types.InlineKeyboardButton(f'{temp_num_of_cards + 1}/{num_of_cards_sum}', callback_data='mid')
            right_btn = types.InlineKeyboardButton('➡️', callback_data='right')
            button.row(left_btn, mid_btn, right_btn)
            bot.edit_message_text(
                f'{time_cards[temp_num_of_cards]} (x{time_cards_num[temp_num_of_cards]})',
                callback.from_user.id,
                callback.message.message_id,
                reply_markup=button)




#обработка не комманд
@bot.message_handler()
def get_text(message):
    if message.text == '🎴Получить карту':
        get_table_info(message)
        message_time = message.date
        dt = datetime.fromtimestamp(message_time)
        h = dt.hour
        m = dt.minute
        s = dt.second
        new_time = h * 60 * 60 + m * 60 + s
        global old_time
        diffrence = new_time - old_time
        time_left = 1800 - diffrence
        h = time_left // 3600
        m = (time_left % 3600) // 60
        s = time_left % 60


        global attempts
        global PTS
        if attempts > 0 or diffrence >= 1800:
            chance = random.randint(0, 10000)
            if chance > 0 and chance < 26:
                card = random.choice(mythics)
                prefix = '🧩'
                global users_mythics
                users_mythics += f'{card}'
                add_card = 'mythic'
                add_pts = 10000
            elif chance > 25 and chance < 126:
                card = random.choice(legendaries)
                prefix = '⭐️'
                global users_legendaries
                users_legendaries += f'{card}'
                add_card = 'legendary'
                add_pts = 5000
            elif chance > 125 and chance < 1125:
                card = random.choice(rares)
                prefix = '🧵'
                global users_rares
                users_rares += f'{card}'
                add_card = 'rare'
                add_pts = 2000
            elif chance > 1125 and chance < 10001:
                card = random.choice(commons)
                prefix = '👶'
                global users_commons
                users_commons += f'{card}'
                add_pts = 1000
            bot.send_message(message.chat.id, f'<i>Вы получили:</i> \n<b>{prefix}{card}!</b> \n\n<blockquote><b>⛩PTS:</b> + {add_pts} ({PTS + add_pts})</blockquote>', parse_mode='HTML')
            attempts -= 1
            PTS += add_pts
            if diffrence >= 1800:
                old_time = new_time
                new_time = 0
                attempts += 1
            update_table(message)


        elif attempts <= 0 and diffrence < 1800:
            bot.send_message(message.chat.id, f'У вас недостаточно попыток! \nВозвращайтесь через {h}ч {m}м {s}с')

    elif message.text == '🗺Меню':
        menu(message)

bot.polling(non_stop=True)
