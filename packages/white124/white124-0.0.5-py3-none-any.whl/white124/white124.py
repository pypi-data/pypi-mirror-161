import json
import socket
import pymysql

class MySQL:

    '''
    Класс предназначен для получения информации с базы данных и для дальнейшей отправки
    с помощью сервер-клиент в json формате предварительно используя серилизацию

    from white124 import MySQL
    sql = MySQL()
    sql.config_sql("Логин", "Пароль")
    connect = sql.connect
    '''

    USER = ""
    PASSWORD = ""
    HOST = ""
    def config_sql(self, user, password, host="white1iz.beget.tech"):
        self.USER = user
        self.PASSWORD = password
        self.HOST = host
        print(self.HOST, self.USER, self.PASSWORD)

    def config_socket(self, host="", port=None, server=None):
        if server == None:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, )
            self.server.settimeout(3)
            self.server.connect((host, port))
            self.server.settimeout(None)
        else:
            self.server = server
            print(f'Принтую сервер из метода Connect: {self.server}')

    def connect(self, query, method=None, json_ser=True, logs=True):
        """
        import pymysql
        import json

        :param method: None, fetchall, fetchone
        :param json: True - json serialization
        :return: None, cursor.fetchall(), cursor.fetchone()

        Example of a function call:
        connect("INSERT INTO users ('email', 'password') VALUE ('info@mail.ru', 'myPass')")
        vars = connect("SELECT * FROM users", "fetchall")
        """

        try:
            connection = pymysql.connect(
                host=self.HOST,
                user=self.USER,
                # passwd="Anq4jq%Y", # Phone
                passwd=self.PASSWORD,  # PC
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

    def send_bd(self, json_data, bytes=1024, _recv=True, _str=False):
        """
        Отправка запросов на сервер
        :param json_data:
        :param bytes:
        :return: список dict
        """
        try:
            #print("В ФУНКЦИИ SEND_BD//////////////////////////")
            _datas = json.dumps(json_data).encode("utf-8")
            #print(f"Принтую _datas: {_datas}")
            _bytes = len(_datas)
            #print(f"Принтую _bytes: {_bytes}, и тип: {type(_bytes)}")
            self.server.send(str(_bytes).encode("utf-8"))
            self.server.sendall(_datas)
            #print("ИДУ ДАЛЬШЕ!......................................")
            if _recv:

                try:
                    files =b''
                    _bytes = self.server.recv(bytes)
                    print(f"Байтов>: {_bytes}")
                    _datas = self.server.recv(bytes)
                    print(f"Первая партия: {_datas}")
                    if int(_bytes) != int(len(_datas)):
                        while _datas:
                            print("я в цикле")
                            files = files+_datas
                            #print(f"Переменная files: {files}")

                            if int(len(files)) == int(_bytes):
                                print("Байты совпали")
                                break

                            _datas = self.server.recv(bytes)
                            #print(f"Партии в цикле: {_datas}")
                    elif int(_bytes) == int(len(_datas)):
                        files = _datas
                        #print(f"Байтов меньше для цикла: {files}")


                    #print(files)
                    #print(f"ПРИНТУЮ ТИП files: {type(files)}")
                    str_files = str(files.decode("utf-8"))
                    #print(f"ПРИНТУЮ ТИП str_files: {type(str_files)}, Значение переменной: {str_files}")
                    if _str:
                        return str_files

                    rows = json.loads(str_files)
                    #rows = json.loads(str(server.recv(bytes).decode("utf-8")))
                    #print(type(rows))
                    #print(rows)

                    return rows

                except Exception as ex:
                    print(f"Ошибка в приеме данных / {ex}")
                    rows = {}

                    return rows

        except Exception as ex:
            print(f"Ошибка в настройках подключения к серверу / {ex}")
            rows = {}

            return rows

