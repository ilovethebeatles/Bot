import psycopg2
from telebot import TeleBot
import smtplib
import config

class db:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=config.pg_host,
            port=config.pg_port,
            database=config.pg_database,
            user=config.pg_user,
            password=config.pg_password
        )

        # Create a cursor
        cursor = self.connection.cursor()

        # Drop the "applications" table
        cursor.execute("DROP TABLE IF EXISTS applications")

        # Drop the "teacher_subjects" table
        cursor.execute("DROP TABLE IF EXISTS teacher_subjects")

        # Drop the "students" table
        cursor.execute("DROP TABLE IF EXISTS students")

        # Drop the "subjects" table
        cursor.execute("DROP TABLE IF EXISTS subjects")

        # Drop the "teachers" table
        cursor.execute("DROP TABLE IF EXISTS teachers")
        cursor.execute("DROP TABLE cafedra CASCADE")

        # Commit the changes and close the cursor and connection
        self.connection.commit()
        cursor.close()

        cursor = self.connection.cursor()

        # SQL-запрос для создания таблицы "students"
        create_students_table_query = config.query_create_students

        # SQL-запрос для создания таблицы "teachers"
        create_teachers_table_query = config.query_create_teachers

        create_cafedra_table_query = config.query_create_cafedra

        # SQL-запрос для создания таблицы "subjects"
        create_subjects_table_query = config.query_create_subjects

        create_teacher_subjects_table_query = config.query_create_teacher_subject

        # SQL-запрос для создания таблицы "applications"
        create_applications_table_query = config.query_create_application

        # Выполнить SQL-запросы для создания таблиц
        cursor.execute(create_students_table_query)
        cursor.execute(create_teachers_table_query)
        cursor.execute(create_cafedra_table_query)
        cursor.execute(create_subjects_table_query)
        cursor.execute(create_teacher_subjects_table_query)
        cursor.execute(create_applications_table_query)

        # Закрыть курсор и выполнить коммит (сохранить изменения в базе данных)
        cursor.close()
        self.connection.commit()

        cursor = self.connection.cursor()

        # Sample data for teachers and subjects
        teachers_data = config.insert_teachers
        cafedra_data = config.insert_cafedra
        subjects_data = config.insert_subjects

        # Insert data into the "teachers" table
        insert_teacher_query = config.query_insert_teachers
        cursor.executemany(insert_teacher_query, teachers_data)
        insert_cafedra_query = config.query_insert_cafedra
        cursor.executemany(insert_cafedra_query, cafedra_data)
        # Insert data into the "subjects" table
        insert_subject_query = config.query_insert_subjects
        cursor.executemany(insert_subject_query, subjects_data)

        # Sample data for teacher_subjects (teacher_id, subject_id pairs)
        teacher_subjects_data = config.insert_teacher_subject

        # Insert data into the "teacher_subjects" table
        insert_teacher_subjects_query = config.query_insert_teacher_subject
        cursor.executemany(insert_teacher_subjects_query, teacher_subjects_data)

        # Commit the changes and close the cursor and connection
        self.connection.commit()
        cursor.close()

    def create_account(self, student_id, fullname, course, group):
        insert_user_query = config.query_insert_user
        with self.connection.cursor() as cursor:
            cursor.execute(insert_user_query, (student_id, fullname, course, group))
        self.connection.commit()
    def check_user_registration(self, user_id):
        check_reg_query = config.query_check_reg
        with self.connection.cursor() as cursor:
            cursor.execute(check_reg_query, (user_id,))
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False
    def get_subjects(self):
        query = config.query_get_subjects
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            subjects = [row[0] for row in cursor.fetchall()]
        return subjects
    def get_teachers_by_subject(self, subject):
        query = config.query_get_teachers_by_subject
        with self.connection.cursor() as cursor:
            cursor.execute(query, (subject,))
            teachers = cursor.fetchall()
        return [teacher[0] for teacher in teachers]

    def create_application(self, student_id, subject, current_teacher, new_teacher):
        insert_application_query = config.query_insert_application
        with self.connection.cursor() as cursor:
            cursor.execute(insert_application_query, (student_id, subject, current_teacher, new_teacher, config.new, config.new, config.new))
            application_id = cursor.fetchone()[0]
        self.connection.commit()
        return application_id

    def get_application_by_id(self, appl_id):
        query = config.query_get_application_by_id
        with self.connection.cursor() as cursor:
            cursor.execute(query, (appl_id,))
            application = cursor.fetchone()
        return application
    def get_cafedra_and_mail_by_subject(self, subject):
        query = config.query_get_cafedra_and_mail
        with self.connection.cursor() as cursor:
            cursor.execute(query, (subject,))
            cafedra, cafedra_email = cursor.fetchone()
        return cafedra, cafedra_email
    def update_application_status(self, application_id, field, new_status_value):
        if field == config.cur_status:
            update_status_query = config.query_update_application_cur_status
        elif field == config.new_status:
            update_status_query = config.query_update_application_new_status
        else:
            update_status_query = config.query_update_application_final_status
        with self.connection.cursor() as cursor:
            cursor.execute(update_status_query, (new_status_value, application_id))
        self.connection.commit()
    def get_student_by_id(self, id):
        query = config.query_get_student
        with self.connection.cursor() as cursor:
            cursor.execute(query, (id,))
            fullname, course, group = cursor.fetchone()
        return fullname, course, group
    def get_teacher_email_by_name(self, teacher_name):
        query = config.query_get_teacher_email_by_name
        with self.connection.cursor() as cursor:
            cursor.execute(query, (teacher_name,))
            email = cursor.fetchone()
        return email[0]
