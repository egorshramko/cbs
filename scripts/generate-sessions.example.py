import psycopg2
import datetime
import random

# Подключение к базе
connection = psycopg2.connect(
    dbname = {ваше_название_базы_данных},
    user = {имя_пользователя_базы},
    password = {пароль_базы},
    host = {хост_базы},
    port = {порт_базы})

cursor = connection.cursor()

def generate_random_datetime():
    #Генерация даты сеанса (рандомная в пределах 2 дней от момента запуска скрипта)
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=2)
    time_delta = end_date - start_date
    total_seconds = int(time_delta.total_seconds())
    random_seconds = random.randint(0, total_seconds)
    random_datetime = start_date + datetime.timedelta(seconds=random_seconds)

    #Округление даты сеанса до круглых минут
    random_datetime_minutes = random_datetime.minute
    rounded_minutes = round(random_datetime_minutes, -1)
    if rounded_minutes >= 60:
        rounded_minutes = 0
    random_datetime = random_datetime.replace(minute=rounded_minutes, second=0, microsecond=0)
    return random_datetime

def duration_to_minutes(duration_nanosec):
    return int(duration_nanosec / (60 * 10**9))

# Функция проверки сгенерированной даты сеанса
def check_sessiondate(hall_id, movie_duration_minutes, ses_datetime):

    # Получение длительности фильма и даты ближайшего сеанса в зале до проверяемой даты
    cursor.execute("SELECT m.duration, s.session_datetime " \
    "FROM hall AS h INNER JOIN session_ AS s ON h.id = s.hall " \
    "INNER JOIN movie AS m ON s.movie = m.id " \
    "WHERE s.session_datetime <= %s AND s.hall = %s " \
    "ORDER BY s.session_datetime DESC LIMIT 1", (ses_datetime, hall_id,))

    # Ближайший сеанс в зале из БД до проверяемой даты
    closer_before_session = cursor.fetchone()

    # Левая часть проверки (начало нового сеанса должно быть после завершения предыдущего)
    left_check = True
    if closer_before_session is not None:
        closer_before_session_duration = closer_before_session[0][0]
        closer_before_session_datetime = datetime.datetime(closer_before_session[0][1])
        closer_before_session_end_datetime = datetime.datetime(closer_before_session_datetime) + \
            datetime.timedelta(minutes=duration_to_minutes(closer_before_session_duration))
        left_check = ses_datetime > closer_before_session_end_datetime
        
    # Вычисление даты-времени конца сеанса
    ses_end_datetime = ses_datetime + datetime.timedelta(minutes=movie_duration_minutes)

    # Получение длительности фильма и даты ближайшего сеанса в зале после проверяемой даты
    cursor.execute("SELECT s.session_datetime " \
    "FROM hall AS h INNER JOIN session_ AS s ON h.id = s.hall " \
    "WHERE s.session_datetime >= %s AND s.hall = %s " \
    "ORDER BY s.session_datetime ASC LIMIT 1", (ses_datetime, hall_id,))

    closer_after_session = cursor.fetchone()

    # Правая часть проверки (конец нового сеанса должен быть до начала следующего сеанса)
    right_check = True
    if closer_after_session is not None:
        closer_after_session_datetime = datetime.datetime(closer_after_session[0][0])
        right_check = ses_end_datetime < closer_after_session_datetime

    return left_check and right_check

def generate_checked_session_date(hall_id, movie_duration):
    random_datetime = generate_random_datetime()
    while not check_sessiondate(hall_id, movie_duration, random_datetime):
        random_datetime = generate_random_datetime()

    return random_datetime


try:
    insert_query = "INSERT INTO session_ (id, created_at, session_datetime, actual, movie, hall) " \
    "VALUES (%s, %s, %s, %s, %s, %s);"

    # Получение актуального id сеанса
    cursor.execute("SELECT last_value FROM session_pkey_seq;")
    current_session_id = cursor.fetchone()[0]

    insert_data = []

    for i in range(25):

        print(f"[{i + 1}/25] Формирование строки", end="\n")

        #Получение списка ID фильмов
        cursor.execute("SELECT id FROM movie")
        movie_id_rows = cursor.fetchall()
        movie_ids = [movie_id[0] for movie_id in movie_id_rows]

        #Получение списка ID залов всех кинотеатров
        cursor.execute("SELECT id FROM hall")
        hall_id_rows = cursor.fetchall()
        hall_ids = [hall_id[0] for hall_id in hall_id_rows]

        #Генерация рандомного фильма и зала
        movie_id = movie_ids[random.randint(0, movie_ids.__len__() - 1)]
        hall_id = hall_ids[random.randint(0, hall_ids.__len__() - 1)]

        print(f"[{i + 1}/25] Сгенерированы фильм и зал", end="\n")

        #Получение длительности фильма
        duration_query = "SELECT duration FROM movie WHERE id = %s"
        cursor.execute(duration_query, (movie_id,))
        movie_duration_nanosec = cursor.fetchone()[0]
        print(f"[{i + 1}/25] Получена длительность фильма", end="\n")

        #Перевод длительности в минуты
        movie_duration_min = duration_to_minutes(movie_duration_nanosec)

        session_datetime = generate_checked_session_date(hall_id, movie_duration_min)
        print(f"[{i + 1}/25] Сгенерирована дата и время сеанса", end="\n")

        record = (current_session_id, datetime.datetime.now(), session_datetime, "True", movie_id, hall_id)
        current_session_id += 1
        insert_data.append(record)

        print(f"[{i + 1}/25] Сгенерирована строка: {record}", end="\n")

    # execute_values(cursor, insert_query, insert_data)
    cursor.executemany(insert_query, insert_data)
    cursor.execute(f"ALTER SEQUENCE session_pkey_seq RESTART WITH {current_session_id};")
    connection.commit()

except Exception as error:
    print("Ошибка при работе с базой:", error)
    print(error)
    connection.rollback()

finally:
    connection.close()