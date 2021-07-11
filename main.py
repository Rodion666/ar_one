from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import socket
import time
import datetime
import threading
import json

class Mimic:
    def __init__(self, th_max_limit, th_time_limit):
        self.th_max_limit = th_max_limit
        self.th_time_limit = th_time_limit
        self.localhost = '127.0.0.1'
        self.contr_int_port = 10190
        self.th_int_port = 10500
        self.th_gen_name = (f"t{i}:{self.th_int_port+i}" for i in range(1000000))
        self.th_word_namePort = {}
        self.th_word_nameTime = {}
        self.th_count = 1
        self.th_get_s_l = False
        self.counter_good_acc = 0
        self._timer = 360
        self.th_stack = True

    def start(self):
        th_b_c = threading.Thread(target=self.th_build_controller, name='th_b_c')
        th_b_c.start()    

    def th_get_server(self):
        th_controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        th_controller.bind( (self.localhost, int(self.contr_int_port)) )
        th_controller.listen(100)
        while True:
            user_socket, address = th_controller.accept()
            data = user_socket.recv(2048)
            self.th_data_controller(data.decode('utf-8'))
        th_controller.close()

    def th_data_controller(self, _data):
        _acc_list = []
        with open('good_acc.json', 'r') as data:
            _acc_list = json.load(data)
        _acc_list.append(_data)
        with open('good_acc.json', 'w') as data:
            try:
                json.dump(_acc_list, data, indent=4)
            except ValueError:
                print('MY ERR! Something wrong with writting good_acc.json')
                return None

    def th_build_controller(self):
        if self.th_get_s_l == False:
            self.th_get_s_l = True
            th_g_s = threading.Thread(target=self.th_get_server, name='the_get_server')
            th_g_s.start()
            

        while True:
            if len(self.th_word_namePort) < self.th_count and self.th_stack:
                self.th_stack = False
                self.th_up()
                time.sleep(20)


    # def th_killer(self):
    #     for key in self.th_word_nameTime:
    #         if datetime.datetime.now().strftime("%H.%M.%S") - self.th_word_nameTime[key] > :


    def clean_port_data(self, _port):
        del self.th_word_namePort[_port]
        del self.th_word_nameTime[_port]
        # self.th_build_controller()


    def proxy_txtToJSON(self):
        """текстовый документ в JSON файл"""
        with open('http.txt', 'r') as data:
            proxy_data = []
            for line in data:
                if line != ' ' and line != '\n':
                    proxy_data.append(line[:-1:])
        with open('new_proxy.json', 'w') as data:
            try:
                json.dump(proxy_data, data, indent=4)
            except ValueError:
                print('MY ERR! PROXY is empty!')
                return None

    def proxy_next_JSON(self):
        with open('new_proxy.json', 'r') as data:
            try:
                _proxy_read = json.load(data)
            except ValueError:
                print("MY ERR! Cant load 'new_proxy.json'")
                return None
            try:
                _proxy_line = _proxy_read.pop()
            except KeyError:
                print("MY ERR! Cant load 'new_proxy.json' or read")
                return None
        with open('new_proxy.json', 'w') as data:
            json.dump(_proxy_read, data, indent=4)

        return _proxy_line

    def acc_txtToJSON(self):
        """текстовый документ в JSON файл"""
        write_dict = {}
        with open('acc.txt', 'r') as data:
            for line in data:
                if line != ' ' and line != '\n':
                    write_dict[line.split(':')[0]] = line.split(':')[1][:-1:]
        with open('acc.json', 'w') as data:
            try:
                json.dump(write_dict, data, indent=4)
            except ValueError:
                print('MY ERR! Attention! spot acc.txt is empty !')
                return None

    def acc_next_JSON(self):
        """возвращает элемент из словаря(log:pass) и добавляет использованный акк в old, 
        перезаписывает new_acc без использованного ака"""
        _old_acc = {}
        with open('new_acc.json', 'r') as data:
            try:
                _acc_read = json.load(data)
            except ValueError:
                print('MY ERR! Attention! new_acc.json is empty ')
                return None
            try:
                _acc_line = _acc_read.popitem()
            except KeyError:
                print('MY ERR! Attention! new_acc.json is empty ')
                return None
                
        with open('new_acc.json', 'w') as data:
            json.dump(_acc_read, data, indent=4)

        with open('old_acc.json', 'r') as data:
            try:
                _old_acc = json.load(data)
            except ValueError:
                pass

        with open('old_acc.json', 'w') as data:
            _old_acc[_acc_line[0]] = _acc_line[1]
            json.dump(_old_acc, data, indent=4)
        
        return _acc_line


    def th_up(self):
        """Создает поток, берет данные из генератора имен/портов th_gen_name"""
        arr_name_port = next(self.th_gen_name).split(':')
        self.th_word_namePort[arr_name_port[1]] = arr_name_port[0]
        self.th_word_nameTime[arr_name_port[1]] = datetime.datetime.now().strftime("%H.%M.%S")
        arr_name_port[0] = threading.Thread(target=self.th_engine, name=arr_name_port[0], args=(arr_name_port[0], arr_name_port[1], self.acc_next_JSON(), self.proxy_next_JSON()))
        arr_name_port[0].start()
        
    def th_engine(self, _name, _port, _acc, _proxy):
        """Это то что творится внутри каждого потока. Потоки используют сокеты для получения и передачи данных"""
        th_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        th_client.bind( (self.localhost, int(_port)) )

        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument("--remote-debugging-port=9292")
            chrome_options.add_argument(f'--user-data-dir=chromes/selenium_3')
            chrome_options.add_argument(f'--proxy-server={_proxy}')
            # chrome_options.add_argument(f"user-agent={self.th_user_agent}")
            driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
            

           
            # ffo = Options()
            # ffo.add_argument('--headless')
            # webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
            #     "httpProxy": _proxy,
            #     "ftpProxy": _proxy,
            #     "sslProxy": _proxy,
            #     "proxyType": "MANUAL"
            # }
            

            # driver = webdriver.Firefox(options=ffo)

            # self.th_check_ip(driver)

            _acc_res = self.th_acc_check(driver, _acc)
            # _acc_res = False

            # print("MY ERR! acc_check def done")
            if _acc_res:
                th_client.connect((self.localhost, int(self.contr_int_port)))   
                data = f'{_acc[0]}:{_acc[1]}'
                th_client.send(data.encode('utf-8'))
                self.th_stack = True
                num = 1
                while num < self._timer:
                    num += 1
                    print(f"{_acc[0]}:{num} min")
                    time.sleep(60)
        except Exception as error:
            print(error)
        finally:
            # print('MY ERR! Finnaly')
            th_client.close()
            self.clean_port_data(_port)
            self.th_stack = True
            print(len(self.th_word_namePort))
            driver.quit()

    def th_acc_check(self, _what, _who):
        pass
     
    def th_check_ip(self, _what):
        _what.get('https://www.whoer.net')
        time.sleep(20)
        print(_what.find_element_by_xpath('//*[@id="main"]/section[1]/div/div/div/div[1]/div/strong').text)
          

    def th_req_res_script(self):
        pass

mimic_one = Mimic(10, 10)

if __name__ == '__main__':
    # mimic_one.proxy_txtToJSON()
    # mimic_one.acc_txtToJSON()
    mimic_one.th_build_controller()


