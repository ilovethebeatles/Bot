import asyncio
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
import config
from class_db import db
import imaplib
from telebot.async_telebot import AsyncTeleBot, types

bot = AsyncTeleBot(config.my_token)
database = db()
IMAP_SERVER = config.imap_serv
IMAP_PORT = config.imap_port
EMAIL_ADDRESS = config.imap_email
EMAIL_PASSWORD = config.imap_password

# Создаем словарь для хранения контекстных данных пользователей
user_context = {}

async def monitor_email():
    while True:
        try:
            # Устанавливаем соединение с IMAP сервером
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select(config.imap_inbox_folder)

            # Ищем непрочитые сообщения
            status, message_ids = mail.search(None, config.unseen_messages)

            # Если есть непрочитые сообщения
            if status == config.status_unseen:
                message_ids = message_ids[0].split()
                for message_id in message_ids: # stopped saving consts here
                    # Получаем текст сообщения и его заголовок
                    _, msg_data = mail.fetch(message_id, config.mail_format)
                    print(msg_data)
                    _, msg_bytes = msg_data[0]
                    print(msg_data[0])
                    msg = email.message_from_bytes(msg_bytes)
                    author = msg[config.msg_from]
                    subject, encoding = decode_header(msg[config.subject_info])[0]

                    # Декодируем заголовок
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else config.default_encoding)

                    # Проверяем, является ли это письмо ответом на заявление
                    if config.subject_beginning in subject:
                        # Извлекаем номер заявления из темы письма
                        parts = subject.split(config.splitter)
                        application_id = parts[-1]
                        print(application_id)
                        # Проверяем, что номер заявления является числом
                        if application_id.isdigit():
                            application_id = int(application_id)

                            # Ищем заявление в базе данных по номеру
                            application = database.get_application_by_id(application_id)

                            if application:

                                print(application)
                                # Проверяем содержимое письма на наличие "да" или "нет"
                                body = msg.get_payload(decode=True).decode()
                                print("Дошли сюда")
                                print(body)
                                subj = application[config.subject_num]
                                cur_teacher = application[config.cur_teach_num]
                                new_teacher = application[config.new_teach_num]
                                final_status = application[config.fin_stat_num]
                                cur_teacher_email = database.get_teacher_email_by_name(cur_teacher)
                                new_teacher_email = database.get_teacher_email_by_name(new_teacher)
                                cafedra, cafedra_mail = database.get_cafedra_and_mail_by_subject(subj)
                                if final_status != config.status_rejected:
                                    if cafedra_mail in author:
                                        if body.lower().startswith(config.answer_accepted) or body.lower().startswith(config.answer_accepted_div):
                                            database.update_application_status(application_id, config.final_status, config.status_accepted)
                                            await bot.send_message(application[1], f"Заявление №{application_id} одобрено кафедрой, Вы официально переведены!")
                                        elif body.lower().startswith(config.answer_rejected) or body.lower().startswith(config.answer_rejected_div):
                                            database.update_application_status(application_id, config.final_status, config.status_rejected)
                                            await bot.send_message(application[1],
                                                                   f"Заявление №{application_id} отклонено кафедрой!")
                                    elif cur_teacher_email in author:
                                        if body.lower().startswith(config.answer_accepted) or body.lower().startswith(config.answer_accepted_div):
                                            database.update_application_status(application_id, config.cur_status, config.status_accepted)
                                            await bot.send_message(application[1], f"Заявление №{application_id} одобрено {cur_teacher}!")
                                        elif body.lower().startswith(config.answer_rejected) or body.lower().startswith(config.answer_rejected_div):
                                            database.update_application_status(application_id, config.final_status, config.status_rejected)
                                            await bot.send_message(application[1],
                                                                   f"Заявление №{application_id} отклонено, {cur_teacher} против!")
                                    elif new_teacher_email in author:
                                        if body.lower().startswith(config.answer_accepted) or body.lower().startswith(config.answer_accepted_div):
                                            database.update_application_status(application_id, config.new_status, config.status_accepted)
                                            await bot.send_message(application[1], f"Заявление №{application_id} одобрено {new_teacher}!")
                                        elif body.lower().startswith(config.answer_rejected) or body.lower().startswith(config.answer_rejected_div):
                                            database.update_application_status(application_id, config.final_status, config.status_rejected)
                                            await bot.send_message(application[1],
                                                                   f"Заявление №{application_id} отклонено, {new_teacher} против!")
                                    print("check  cafedra")
                                    application = database.get_application_by_id(application_id)
                                    cur_status = application[config.cur_stat_num]
                                    new_status = application[config.new_stat_num]
                                    final_status = application[config.fin_stat_num]
                                    user_id = application[1]
                                    full_name, course, group = database.get_student_by_id(user_id)
                                    print(cur_status, new_status, final_status, sep = ' ')
                                    if cur_status == config.status_accepted and new_status == config.status_accepted and final_status == config.new:
                                        print("sending to cafedra")
                                        print(cafedra_mail)
                                        if await send_email(f"Заявление {application_id}",
                                                            f"Студент {full_name} {course} курса из группы {group} подал заявление на перевод от {cur_teacher} к {new_teacher} по предмету {subj}. Ответьте да, чтобы принять, ответьте нет, чтобы отклонить",
                                                            cafedra_mail):
                                            print(f"Уведомление отправлено кафедре")
                    # Помечаем письмо как прочитанное
                    mail.store(message_id, config.flags, config.message_seen)

            # Закрываем соединение с IMAP сервером
            mail.logout()
            print(config.checked_successful)

        except Exception as e:
            print(config.checked_unsuccessful, str(e))

        # Пауза в секундах перед следующей проверкой (например, 5 минут)
        await asyncio.sleep(config.time_sleep)

async def start_bot():
    await bot.polling(none_stop=True)

@bot.message_handler(commands=[config.start_command])
async def send_welcome_message(message):
    user_id = message.chat.id
    user_context[user_id] = {}  # Инициализируем контекст пользователя
    await bot.reply_to(message, config.say_hello)

@bot.message_handler(commands=[config.reg_command])
async def register(message):
    user_id = message.chat.id
    user_context[user_id] = {}  # Инициализируем контекст пользователя
    msg = await bot.send_message(user_id, config.name_query)
    user_context[user_id][config.state_field] = config.waiting_for_fullname_state  # Устанавливаем состояние ожидания имени

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_fullname_state)
async def process_fullname(message):
    user_id = message.chat.id
    user_context[user_id][config.fullname_field] = message.text  # Сохраняем имя
    msg = await bot.send_message(user_id, config.course_query)
    user_context[user_id][config.state_field] = config.waiting_for_course_state  # Устанавливаем состояние ожидания курса

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_course_state)
async def process_course(message):
    user_id = message.chat.id
    try:
        course = int(message.text)
        user_context[user_id][config.course_field] = course  # Сохраняем курс
        msg = await bot.send_message(user_id, config.group_query)
        user_context[user_id][config.state_field] = config.waiting_for_group_state  # Устанавливаем состояние ожидания группы
    except ValueError:
        await bot.send_message(user_id, config.value_error_message)

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_group_state)
async def process_group(message):
    user_id = message.chat.id
    user_context[user_id][config.group_field] = message.text  # Сохраняем группу
    database.create_account(user_id, user_context[user_id][config.fullname_field], user_context[user_id][config.course_field], user_context[user_id][config.group_field])
    await bot.send_message(user_id, config.register_successful)
    user_context[user_id] = {}  # Сбрасываем контекст пользователя

@bot.message_handler(commands=[config.change_command])
async def change_tutors(message):
    user_id = message.chat.id
    if database.check_user_registration(user_id):
        print('OK1')
        subjects = database.get_subjects()
        print('OK2')
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for subject in subjects:
            kb.add(types.KeyboardButton(subject))

        user_context[user_id] = {}  # Инициализируем контекст пользователя
        msg = await bot.send_message(user_id, config.subject_query, reply_markup=kb)
        user_context[user_id][config.state_field] = config.waiting_for_subject_state  # Устанавливаем состояние ожидания предмета
    else:
        await bot.send_message(message.chat.id, config.not_registered_user_message)

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_subject_state)
async def choose_current_teacher(message):
    user_id = message.chat.id
    current_subject = message.text
    teachers = database.get_teachers_by_subject(current_subject)

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for teacher in teachers:
        markup.add(types.KeyboardButton(text=teacher))

    user_context[user_id][config.current_subject_field] = current_subject  # Сохраняем предмет
    user_context[user_id][config.state_field] = config.waiting_for_current_teacher_state  # Устанавливаем состояние ожидания текущего преподавателя
    msg = await bot.send_message(user_id, config.current_teacher_request, reply_markup=markup)

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_current_teacher_state)
async def choose_new_teacher(message):
    user_id = message.chat.id
    current_teacher = message.text
    teachers = database.get_teachers_by_subject(user_context[user_id][config.current_subject_field])

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for teacher in teachers:
        if teacher != current_teacher:
            markup.add(types.KeyboardButton(text=teacher))

    user_context[user_id][config.current_teacher_field] = current_teacher  # Сохраняем текущего преподавателя
    user_context[user_id][config.state_field] = config.waiting_for_new_teacher_state  # Устанавливаем состояние ожидания нового преподавателя
    msg = await bot.send_message(user_id, config.new_teacher_request, reply_markup=markup)

@bot.message_handler(func=lambda message: user_context.get(message.chat.id, {}).get(config.state_field) == config.waiting_for_new_teacher_state)
async def make_application(message):
    user_id = message.chat.id
    print('OK3')
    new_teacher = message.text
    print('OK4')
    application_id = database.create_application(user_id, user_context[user_id][config.current_subject_field], user_context[user_id][config.current_teacher_field], new_teacher)
    print('OK5')
    email_current = database.get_teacher_email_by_name(user_context[user_id][config.current_teacher_field])
    email_new = database.get_teacher_email_by_name(new_teacher)
    print('OK6')
    print(user_context[user_id])
    full_name, course, group = database.get_student_by_id(user_id)
    if await send_email(f"Заявление {application_id}", f"Студент {full_name} {course} курса из группы {group} подал заявление на перевод от вас к {new_teacher} по предмету {user_context[user_id][config.current_subject_field]}. Ответьте да, чтобы принять, ответьте нет, чтобы отклонить", email_current):
        print(f"Уведомление отправлено учителю {user_context[user_id][config.current_teacher_field]}")

    if await send_email(f"Заявление {application_id}", f"Студент {full_name} {course} курса из группы {group} подал заявление на перевод к вам от {user_context[user_id][config.current_teacher_field]} по предмету {user_context[user_id][config.current_subject_field]}. Ответьте да, чтобы принять, ответьте нет, чтобы отклонить", email_new):
        print(f"Уведомление отправлено учителю {new_teacher}")
    await bot.send_message(user_id, config.application_created_message)
    user_context[user_id] = {} #сбросили контекст

async def send_email(subject, message, to_email):
    print("I try to send")
    smtp_server = config.smtp_serv
    smtp_port = config.smtp_port
    smtp_username = config.smtp_mail
    smtp_password = config.smtp_pass
    print("succes1")
    msg = MIMEText(message, config.plain_type, config.default_encoding)
    msg[config.subj_field] = subject
    msg[config.from_field] = smtp_username
    msg[config.to_field] = to_email
    print("succes2")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        print("succes3")
        server.starttls()
        print("succes4")
        server.login(smtp_username, smtp_password)
        print("succes5")
        server.sendmail(smtp_username, to_email, msg.as_string())
        print("succes6")
        server.quit()
        print("succes7")
        return True
    except Exception as e:
        print(config.sending_mail_error_message, str(e))
        return False

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_email())
    loop.create_task(start_bot())
    loop.run_forever()
