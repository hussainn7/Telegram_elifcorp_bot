import telebot
import webbrowser
import sqlite3
from telebot import types

bot = telebot.TeleBot("TOKEN")
admins = [1262676599]
staff_members = [12626765991]
name = None
project = None
deadline = None


def admin_view_requests(message):
    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM project_requests WHERE status = 'pending'")
    requests = cur.fetchall()

    if not requests:
        bot.send_message(message.chat.id, "No pending project requests.")
        return

    for req in requests:
        req_id, user_id, user_name, project_name, _ = req
        bot.send_message(
            message.chat.id,
            f"Request ID: {req_id}\nUser: {user_name} (ID: {user_id})\nProject: {project_name}\n",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Approve", callback_data=f'approve_{req_id}'),
                types.InlineKeyboardButton("Reject", callback_data=f'reject_{req_id}')
            )
        )

    cur.close()
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_project_request_decision(call):
    global project, deadline  # Declare them as global

    action, req_id = call.data.split('_')
    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()

    if action == 'approve':
        cur.execute("UPDATE project_requests SET status = 'approved' WHERE id = ?", (req_id,))
        cur.execute("INSERT INTO project (work, dl) VALUES (?, ?)", (project, deadline))
        bot.answer_callback_query(call.id, "Project request approved")
    elif action == 'reject':
        cur.execute("DELETE FROM project_requests WHERE id = ?", (req_id,))
        bot.answer_callback_query(call.id, "Project request rejected")

    conn.commit()
    cur.close()
    conn.close()


def initialize_db():
    with sqlite3.connect('ElifDB.sql') as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(50), surname varchar(50), pass varchar(50))")
        cur.execute("CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY AUTOINCREMENT, work varchar(50), dl varchar(50))")
        cur.execute("CREATE TABLE IF NOT EXISTS project_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT, user_surname TEXT, project_name TEXT, status TEXT)")
        conn.commit()

initialize_db()

def is_admin(user_id):
    return user_id in admins

def is_staff(user_id):
    return user_id in staff_members

@bot.message_handler(commands=["start", 'hello', 'привет'])
def main(message):
    user_id = message.from_user.id

    if is_admin(user_id):
        admin_main(message)
    elif is_staff(user_id):
        staff_main(message)
    else:
        user_main(message)

def admin_main(message):
    bot.send_message(message.chat.id, f'Hello Admin {message.from_user.first_name} {message.from_user.last_name}, choose what interests you.')
    show_users = types.InlineKeyboardButton("Show users", callback_data='show_users')
    check_projects = types.InlineKeyboardButton("Show projects",callback_data='show_projects')
    add_user_button = types.InlineKeyboardButton("Add User", callback_data='add_user')
    show_prj_requests_button = types.InlineKeyboardButton("Show Project Requests", callback_data='show_project_requests')
    markup = types.InlineKeyboardMarkup().add(add_user_button, check_projects, show_users, show_prj_requests_button)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

def staff_main(message):
    bot.send_message(message.chat.id, f'Hello Staff {message.from_user.first_name} {message.from_user.last_name}, choose what interests you.')
    show_users = types.InlineKeyboardButton("Show users", callback_data='show_users')
    check_projects = types.InlineKeyboardButton("Show projects", callback_data='show_projects')
    markup = types.InlineKeyboardMarkup().add(check_projects, show_users)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

def user_main(message):
    bot.send_message(message.chat.id, f'Hello {message.from_user.first_name} {message.from_user.last_name}, choose what interests you.')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Elif Education", callback_data="education")
    button2 = types.InlineKeyboardButton("Elif Commerence", callback_data="commerce")
    button3 = types.InlineKeyboardButton("Elif Digital", callback_data='digital')

    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Choose one of the options:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == 'add_user' and is_admin(user_id):
        bot.send_message(call.message.chat.id, "Enter the name of the user you want to add:")
        bot.register_next_step_handler(call.message, add_user_name)
    elif call.data == "education":
        bot.send_message(call.message.chat.id, "It's Elif Education, to place an order type /makeorder")
        show_users_button = types.InlineKeyboardButton("Show Experts", callback_data='show_users')
        show_projects_button = types.InlineKeyboardButton("Show Projects", callback_data='show_projects')
        markup = types.InlineKeyboardMarkup().add(show_users_button, show_projects_button)
        bot.send_message(call.message.chat.id, "Choose an option:", reply_markup=markup)
    elif call.data == "commerce":
        bot.send_message(call.message.chat.id, "It's Elif Commerence, to place an order type /makeorder")
        show_users_button1 = types.InlineKeyboardButton("Show Experts", callback_data='show_users')
        show_projects_button1 = types.InlineKeyboardButton("Show Projects", callback_data='show_projects')
        markup = types.InlineKeyboardMarkup().add(show_users_button1, show_projects_button1)
        bot.send_message(call.message.chat.id, "Choose an option:", reply_markup=markup)
    elif call.data == 'digital':
        bot.send_message(call.message.chat.id, "It's Elif Digital, to place an order type /makeorder")
        show_users_button2 = types.InlineKeyboardButton("Show Experts", callback_data='show_users')
        show_projects_button2 = types.InlineKeyboardButton("Show Projects", callback_data='show_projects')
        markup = types.InlineKeyboardMarkup().add(show_users_button2, show_projects_button2)
        bot.send_message(call.message.chat.id, "Choose an option:", reply_markup=markup)
    elif call.data == 'show_users':
        show_all_users(call.message.chat.id)
    elif call.data == 'show_projects':
        show_all_projects(call.message.chat.id)
    elif call.data == 'show_project_requests' and is_admin(user_id):
        admin_view_requests(call.message)

def add_user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Enter the surname of the user you want to add:")
    bot.register_next_step_handler(message, add_user_surname)

def add_user_surname(message):
    surname = message.text.strip()

    conn = sqlite3.connect('ElifDB.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES (?, ?)", (name, surname))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Experts list", callback_data='show_users'))
    bot.send_message(message.chat.id, f"User {name} {surname} has been added.",reply_markup=markup)

def show_all_users(chat_id):
    conn = sqlite3.connect('ElifDB.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    info = '`'
    for el in users:
        info += (
            f"{'-' * 30}\n"
            f"Name: {el[1]}\n"
            f"Surname: {el[2]}\n")

    cur.close()
    conn.close()

    bot.send_message(chat_id, info)

@bot.message_handler(commands=['prj', 'makeorder'])
def start_second(message):
    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY AUTOINCREMENT, work varchar(50), dl varchar(50))")
    conn.commit()
    cur.close()
    conn.close()

    global project, deadline
    project = None  # Reset the global variables when starting a new project request
    deadline = None

    bot.send_message(message.chat.id, "Enter your project name ")
    bot.register_next_step_handler(message, project_name)

def project_name(message):
    global project
    project = message.text.strip()
    bot.send_message(message.chat.id, "Enter project's deadline format (Date/Month name) ")
    bot.register_next_step_handler(message, project_deadline)

def project_deadline(message):
    global deadline
    deadline = message.text.strip()

    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()

    user_id = message.from_user.id
    user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    cur.execute("INSERT INTO project_requests (user_id, user_name, project_name, status) VALUES (?, ?, ?, 'pending')",
                (user_id, user_name, project))

    conn.commit()
    cur.close()
    conn.close()

    mark = telebot.types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, "Project has been added to queue, wait until approve ")

def show_all_projects(prj_id):
    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM project')
    projects = cur.fetchall()

    info_prj = 'Projects:\n'
    for ell in projects:
        info_prj += (
            f"{'-' * 30}\n"
            f"Project Name: {ell[1]}\n"
            f"Project Deadline: {ell[2]}\n"
        )

    cur.close()
    conn.close()

    bot.send_message(prj_id, info_prj)

@bot.callback_query_handler(func=lambda call: call.data == 'show_project_requests' and is_admin(call.from_user.id))
def show_project_requests(call):
    conn = sqlite3.connect('ElifDB_projects.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM project_requests')
    project_requests = cur.fetchall()

    info_prj_req = 'Project Requests:\n'
    for req in project_requests:
        info_prj_req += (
            f"{'-' * 30}\n"
            f"User ID: {req[1]}\n"
            f"User Name: {req[2]}\n"
            f"Project Name: {req[3]}\n"
        )

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info_prj_req)

@bot.message_handler(commands=['site', 'website'])
def site(message):
    webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b> <em>Information</em> ', parse_mode='html')

@bot.message_handler()
def info(message):
    if message.text.lower() in ['привет', 'hello']:
        bot.send_message(message.chat.id, f'Hello {message.from_user.first_name} {message.from_user.last_name} ')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')

bot.polling(none_stop=True)
