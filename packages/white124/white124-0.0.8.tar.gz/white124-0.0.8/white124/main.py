import json
import socket
import time

import pymysql

class MySQL:
    '''
    Класс предназначен для получения информации с базы данных и для дальнейшей отправки
    с помощью сервер-клиент в json формате предварительно используя серилизацию

    from white124 import MySQL
    sql = MySQL()
    sql.config_sql("Логин", "Пароль", "Хост")
    connect = sql.connect
    '''

    USER = ""
    PASSWORD = ""
    HOST = ""
    def config_sql(self, user, password, host):
        ''' Найстрока подключения к базе данных MySQL '''
        self.USER = user
        self.PASSWORD = password
        self.HOST = host
        print(self.HOST, self.USER, self.PASSWORD)

    def config_socket(self, host="", port=None, server=None):
        ''' Настройка подключения Socket '''
        if server == None:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, )
            self.server.settimeout(3)
            self.server.connect((host, port))
            self.server.settimeout(None)
            return self.server
        else:
            self.server = server
            return self.server

    def connect(self, query, method=None, json_ser=True, logs=False):
        """
        :param method: None, fetchall, fetchone (для обратного ответа)
        :param json: True - json serialization (для отправки используя Socket)
        :return: None, cursor.fetchall(), cursor.fetchone()

        Example of a function call:
        connect("INSERT INTO users ('email', 'password') VALUE ('info@mail.ru', 'myPass')")
        vars = connect("SELECT * FROM users", "fetchall")
        """

        try:
            connection = pymysql.connect(
                host=self.HOST,
                user=self.USER,
                passwd=self.PASSWORD,
                database=self.USER,
                cursorclass=pymysql.cursors.DictCursor
            )

            if logs:
                print("Успешное подключение к базе данных...")
                print("#" * 20)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if method == None:
                        connection.commit()
                        return None

                    if method == "fetchall":
                        if json_ser:
                            return json.dumps(cursor.fetchall())
                        else:
                            return cursor.fetchall()

                    if method == "fetchone":
                        if json_ser:
                            return json.dumps(cursor.fetchone())
                        else:
                            return cursor.fetchone()

            except Exception as ex:
                print(f"Ошибка в запросе к базе данных / {ex}")

            finally:
                connection.close()

        except Exception as ex:
            print(f"Ошибка подключения к базе данных / {ex}")

    def send_bd(self, json_data, bytes=1024, _recv=True, _str=False, time_sleep=0.1, logs=False):
        """
        Отправка запросов на сервер используя Socket и json (серилизация)
        :param json_data: Запрос на сервер в json формате
        :param bytes: Байт (default=1024)
        :param _recv: Если не нужен ответ тогда указать False (default=True)
        :param _str: Для отправки ответа обычной строкой (default=False)
        :param time_sleep: Опционально, пауза между отправкой сообщения (default=0.1) могут быть сбои если указать 0
        :return: список dict
        """
        try:
            _datas = json.dumps(json_data).encode("utf-8")
            _bytes = len(_datas)
            self.server.send(str(_bytes).encode("utf-8"))
            time.sleep(time_sleep)
            self.server.sendall(_datas)
            if _recv:
                try:
                    if logs:
                        print(f"Количество байт: {_bytes}")
                    if logs:
                        print(f"data: {_datas}")

                    files =b''
                    _bytes = self.server.recv(bytes)
                    time.sleep(time_sleep)
                    _datas = self.server.recv(bytes)

                    if int(_bytes) != int(len(_datas)):
                        while _datas:
                            files = files+_datas
                            if int(len(files)) == int(_bytes):
                                print("Байты совпали")
                                break
                            _datas = self.server.recv(bytes)

                    elif int(_bytes) == int(len(_datas)):
                        files = _datas

                    str_files = str(files.decode("utf-8"))

                    if _str:
                        return str_files

                    rows = json.loads(str_files)
                    return rows

                except Exception as ex:
                    print(f"Ошибка в приеме данных / {ex}")
                    rows = {}
                    return rows

        except Exception as ex:
            print(f"Ошибка в настройках подключения к серверу / {ex}")
            rows = {}
            return rows