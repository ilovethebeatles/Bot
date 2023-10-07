my_token = '6369614389:AAF8Ulpi1pyApEZYuANqs8Xfu2rF-Wk7FfA'
start_command = 'start'
reg_command = 'register'
login_command = 'login'
change_command = 'change'

# connecting to imap
imap_serv = "imap.yandex.ru"
imap_port = 993
imap_email = "student-changer@yandex.ru"
imap_password = "yisgoenqfmqtvytm"
# checking email with imap
imap_inbox_folder = "inbox"
unseen_messages = "(UNSEEN)"
status_unseen = "OK"
mail_format = "(RFC822)"
subject_info = "Subject"
default_encoding = "utf-8"
subject_beginning = "Re: Заявление"
splitter = " "

answer_accepted = "да"
answer_rejected = "нет"
status_accepted = "approved"
status_rejected = "rejected"
flags = "+FLAGS"
message_seen = "\\Seen"
checked_successful = 'checked'
checked_unsuccessful = "Ошибка при мониторинге почты:"
time_sleep = 30

#communication with bot user
type_content = 'text'
say_hello = '''\
Привет! Я ChangeTutor, бот, который поможет тебе с заявлениями о переводе между семинаристами. Зарегистрируйся с помощью команды /register и создавай заявления на перевод с помощью команды /change. '''
name_query = 'Введите имя и фамилию:'
state_field = 'state'
waiting_for_fullname_state = 'waiting_for_fullname'
fullname_field = 'fullname'
course_query = 'Введите курс:'
waiting_for_course_state = 'waiting_for_course'
course_field = 'course'
group_query = 'Введите группу:'
waiting_for_group_state = 'waiting_for_group'
value_error_message = 'Курс должен быть числом. Пожалуйста, введите курс снова.'
group_field = 'group'
register_successful = 'Регистрация успешно завершена!'
subject_query = 'Выберите предмет:'
waiting_for_subject_state = 'waiting_for_subject'
not_registered_user_message = 'Извините, подача заявлений доступна только зарегистрированным пользователям!'
current_subject_field = 'current_subject'
waiting_for_current_teacher_state = 'waiting_for_current_teacher'
current_teacher_request = 'Выберите преподавателя от которого хотите перевестись:'
current_teacher_field = 'current_teacher'
waiting_for_new_teacher_state = 'waiting_for_new_teacher'
new_teacher_request = 'Выберите преподавателя, к которому хотите перевестись:'
application_created_message = 'Заявление на перевод создано, вам будут приходить сообщения об обновлении его статуса.'
#sending message with smtp
smtp_serv = "smtp.yandex.ru"
smtp_port = 587
smtp_mail = "student-changer@yandex.ru"
smtp_pass = "yisgoenqfmqtvytm"
plain_type = "plain"
subj_field = "Subject"
from_field = "From"
to_field = "To"
sending_mail_error_message = "Ошибка при отправке электронной почты:"


#constants from class_db
#connection
pg_host = 'localhost'
pg_port = '5432'
pg_database = 'pg_db'
pg_user = 'postgres'
pg_password = 'postgres'

#запросы на создание
query_create_students="""
        CREATE TABLE students (
            student_id BIGINT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            course INT NOT NULL,
            student_group VARCHAR(20) NOT NULL
        )
        """
query_create_teachers = """
        CREATE TABLE teachers (
            teacher_id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL
        )
        """
query_create_cafedra = """
        CREATE TABLE cafedra (
            cafedra_id SERIAL PRIMARY KEY,
            cafedra_name VARCHAR(100) NOT NULL,
            cafedra_email VARCHAR(100) NOT NULL
        )
"""
query_create_subjects = """
        CREATE TABLE subjects (
            subject_id SERIAL PRIMARY KEY,
            cafedra_id INT REFERENCES cafedra(cafedra_id),
            subject_name VARCHAR(100) NOT NULL
        )
        """
query_create_teacher_subject = """
        CREATE TABLE teacher_subjects (
            teacher_id INT REFERENCES teachers(teacher_id),
            subject_id INT REFERENCES subjects(subject_id),
            PRIMARY KEY (teacher_id, subject_id)
        )
        """
query_create_application = """
        CREATE TABLE applications (
            application_id SERIAL PRIMARY KEY,
            student_id BIGINT REFERENCES students(student_id),
            subject VARCHAR(100),
            current_teacher VARCHAR(100),
            new_teacher VARCHAR(100),
            cur_status VARCHAR(10),
            new_status VARCHAR(10),
            final_status VARCHAR(10),
            timestamp TIMESTAMP
        )
        """
insert_teachers = [
            ('John Smith', 'iakushkova.l@yandex.ru'),
            ('Alice Johnson', 'iakushkova.es@phystech.edu'),
            ('David Wilson', 'david.wilson@example.com'),
            ('Emily Brown', 'emily.brown@example.com'),
            ('Michael Lee', 'michael.lee@example.com')
        ]
query_insert_teachers = "INSERT INTO teachers (full_name, email) VALUES (%s, %s)"
insert_cafedra = [
            ('Maths', "maths-cafedra@yandex.ru"),
            ('Phys',"phys@yandex.ru"),
            ('Chembio', "chembio@yandex.ru"),
            ('Hum', "hum@yandex.ru")
        ]
query_insert_cafedra = "INSERT INTO cafedra (cafedra_name, cafedra_email) VALUES (%s, %s)"
insert_subjects = [
            (1, 'Mathematics'),
            (2, 'Physics'),
            (3, 'Chemistry'),
            (3, 'Biology'),
            (4, 'History'),
            (4, 'English')
        ]

query_insert_subjects = "INSERT INTO subjects (cafedra_id, subject_name) VALUES (%s, %s)"
insert_teacher_subject = [
            (1, 1),  # John Smith teaches Mathematics
            (2, 1),  # Alice Johnson teaches Mathematics
            (3, 3),  # David Wilson teaches Chemistry
            (4, 4),  # Emily Brown teaches Biology
            (5, 5),  # Michael Lee teaches History
            (1, 6),  # John Smith also teaches English
        ]
query_insert_teacher_subject = "INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (%s, %s)"
query_insert_user = 'INSERT INTO students (student_id, full_name, course, student_group) VALUES (%s, %s, %s, %s)'
query_check_reg = 'SELECT student_id FROM students WHERE student_id = %s'
query_get_subjects = "SELECT subject_name FROM subjects"
query_get_student = "SELECT full_name, course, student_group FROM students WHERE student_id = %s "
query_get_teachers_by_subject = "SELECT t.full_name FROM teachers t " \
                "JOIN teacher_subjects ts ON t.teacher_id = ts.teacher_id " \
                "JOIN subjects s ON ts.subject_id = s.subject_id " \
                "WHERE s.subject_name = %s"
query_insert_application = """
        INSERT INTO applications (student_id, subject, current_teacher, new_teacher, cur_status, new_status, final_status, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING application_id
        """
query_get_application_by_id = "SELECT * FROM applications WHERE application_id = %s"
query_update_application_cur_status = "UPDATE applications SET cur_status = %s WHERE application_id = %s"
query_update_application_new_status = "UPDATE applications SET new_status = %s WHERE application_id = %s"
query_update_application_final_status = "UPDATE applications SET final_status = %s WHERE application_id = %s"
query_get_teacher_email_by_name = "SELECT email FROM teachers WHERE full_name = %s"
query_get_cafedra_and_mail = """
    SELECT cafedra_name, cafedra_email
    FROM subjects
    JOIN cafedra ON subjects.cafedra_id = cafedra.cafedra_id
    WHERE subjects.subject_name = %s
"""

new_status = 'new_status'
cur_status = 'cur_status'
final_status = 'final_status'
new = 'new'
msg_from = 'From'
answer_accepted_div = '<div>да'
answer_rejected_div = '<div>нет'
subject_num = 2
cur_teach_num = 3
new_teach_num = 4
cur_stat_num = 5
new_stat_num = 6
fin_stat_num = 7