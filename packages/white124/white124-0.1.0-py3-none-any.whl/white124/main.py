import json

class MySQL:
    '''
    Класс предназначен для получения информации с базы данных и для дальнейшей отправки
    с помощью сервер-клиент в json формате предварительно используя сериализацию

    from white124 import MySQL
    sql = MySQL()
    sql.config_sql("Логин", "Пароль", "Хост")
    connect = sql.connect
    '''

    import socket
    import time
    import pymysql

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
            self.server = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM, )
            self.server.settimeout(3)
            self.server.connect((host, port))
            self.server.settimeout(None)
            return self.server
        else:
            self.server = server
            return self.server

    def connect(self, query, method=None, json_ser=True, logs=False, comment=""):
        """
        :param method: None, fetchall, fetchone (для обратного ответа)
        :param json: True - json сериализация (для отправки используя Socket)
        :return: None, cursor.fetchall(), cursor.fetchone()

        Example of a function call:
        connect("INSERT INTO users ('email', 'password') VALUE ('info@mail.ru', 'myPass')")
        vars = connect("SELECT * FROM users", "fetchall")
        """

        try:
            connection = self.pymysql.connect(
                host=self.HOST,
                user=self.USER,
                passwd=self.PASSWORD,
                database=self.USER,
                cursorclass=self.pymysql.cursors.DictCursor
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
                print(f"Ошибка в запросе к базе данных /{comment}/ {ex}")

            finally:
                connection.close()

        except Exception as ex:
            print(f"Ошибка подключения к базе данных /{comment}/ {ex}")

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
            self.time.sleep(time_sleep)
            self.server.sendall(_datas)
            if _recv:
                try:
                    if logs:
                        print(f"Количество байт: {_bytes}")
                    if logs:
                        print(f"data: {_datas}")

                    files =b''
                    _bytes = self.server.recv(bytes)
                    self.time.sleep(time_sleep)
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

class DomGosuslugi:
    ''' Класс для работы с сайтом https://dom.gosuslugi.ru '''

    from dadata import Dadata
    import re

    TOKEN = ""
    SECRET = ""

    def config_apiFias(self, token="", secret=""):
        self.TOKEN = token
        self.SECRET = secret

    def apiFias(self, method="", ogrn="", address="", region="", json_ser=True):
        """
        Использует библиотеку Dadata для формирования правильного адреса в формате ФИАС (ГИС ЖКХ) для 83 региона
        :param method: party - Поиск организации по ОГРН; region - Формирование адреса в формате ФИАС
        :param ogrn: при выборе метода "region" указать ОГРН для поиска организации
        :param address: при выборе метода "region" указать адрес в произвольной форме
        :param region: при выборе метода "region" можно дополнительно указать регион
        :param json_ser: Сериализация для оправки по Socket, default(True)
        :return: список dict
        """
        try:
            with self.Dadata(self.TOKEN, self.SECRET) as dadata:
                if method == "party":
                    result = dadata.find_by_id(
                        "party",
                        query=str(ogrn)
                    )
                    name = result[0]['value']
                    fio = result[0]['data']['management']['name']
                    adress = result[0]['data']['address']['value']

                    info = {"ogrn": ogrn, "name": name, "fio": fio, "adress": adress}
                if method == "region":
                    with self.Dadata(self.TOKEN, self.SECRET) as dadata:
                        if region != "":
                            result = dadata.suggest(
                                "fias",
                                str(address)
                            )
                        else:
                            result = dadata.suggest(
                                "fias",
                                str(address),
                                locations=[{'region': region}]
                            )

                    full_adress = result[0]['value']

                    if result != []:
                        item_adress_format_gis = f"{result[0]['unrestricted_value']}"

                        try:
                            item_adress_format_gis = self.re.sub('Ненецкий АО', 'АО Ненецкий', str(full_adress))
                        except:
                            pass

                        try:
                            item_adress_format_gis = self.re.sub('Заполярный р-н', 'р-н Заполярный',
                                                            str(full_adress))
                        except:
                            pass

                        try:
                            item_adress_format_gis = self.re.sub('Заполярный р-н', 'р-н Заполярный',
                                                            str(full_adress))
                        except:
                            pass

                        try:
                            item_adress_format_gis = self.re.sub('поселок', 'п', str(full_adress))
                        except:
                            pass

                        try:
                            item_adress_format_gis = self.re.sub('село', 'с', str(full_adress))
                        except:
                            pass

                        try:
                            item_adress_format_gis = self.re.sub(' д ', ' д. ', str(full_adress))
                        except:
                            pass

                        if result[0]['data']['city'] != None:
                            temp_city = result[0]['data']['city']

                        if result[0]['data']['city'] == None:
                            temp_city = result[0]['data']['settlement']

                        item_adress_compact = f"{temp_city} {result[0]['data']['street_with_type']} {result[0]['data']['house']}"

                        info = {
                            "item_adress_format_gis": item_adress_format_gis,
                            "item_adress_compact": item_adress_compact,
                            "item_adress_city": temp_city,
                            "item_adress_ul": result[0]['data']['street_with_type'],
                            "item_adress_home": result[0]['data']['house'],
                            "item_adress_fias_code": result[0]['data']['house_fias_id']
                        }
                    else:
                        info = {}

            return json.dumps(info)
        except Exception as ex:
            return json.dumps({})