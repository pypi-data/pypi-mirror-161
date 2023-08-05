import requests,random
class Mail():
    def __init__(self, mail:str=None,password:str=None):
        if mail == None or password==None:
            return False
        
        self.mail = mail
        self.password = password
        headers = {
            'authority': 'api.mail.tm',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi,en;q=0.9',
            'origin': 'https://mail.tm',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

        json_data = {
            'address': self.mail,
            'password': self.password,
        }

        response = requests.post('https://api.mail.tm/token', headers=headers, json=json_data)
        self.id = response.json()['id']
        self.token = response.json()['token']
    def RegMail(self):
        headers = {
        'authority': 'api.mail.tm',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi',
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE2NTg5MDI2ODgsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6InJxbGRhbGxmamdnbW1AYXJ4eHdhbGxzLmNvbSIsImlkIjoiNjJlMGQ4OWY2MmQ0Y2M3NWY1MDhlMTQ0IiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzYyZTBkODlmNjJkNGNjNzVmNTA4ZTE0NCJdfX0.Uc6sOupmxHXzMbq4n0OGww_HOgxWAZ57ju_CU9_qa7Ma4c74o76ifXFKKXlTmjAGaPKLyXNSAS1CtWRZpkkR1g',
        'origin': 'https://mail.tm',
        'referer': 'https://mail.tm/',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        usser = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(10))+''.join(str(random.randint(50,500)))
        password = 'Hoanga1979'
        json_data = {
            'address': f'{usser}@arxxwalls.com',
            'password': f'{password}',
        }

        response = requests.post('https://api.mail.tm/accounts', headers=headers, json=json_data)
        if 'id' in response.json():
            mail = response.json()['address']
            return f'["mail": "{mail}", "password": "{password}"]'
        else:
            return response.json()
    def getbox(self):
        headers = {
            'authority': 'api.mail.tm',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi,en;q=0.9',
            'authorization': f'Bearer {self.token}',
            'if-none-match': f'"{self.id}"',
            'origin': 'https://mail.tm',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

        response = requests.get('https://api.mail.tm/messages', headers=headers)
        try:
            id_mail = response.json()['hydra:member'][0]
            return id_mail
        except:
            return response.json()
    def getboxid(self,id_mail:str=None):
        if id_mail==None:
            return False
        headers = {
            'authority': 'api.mail.tm',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi,en;q=0.9',
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE2NTg5MDM4MDYsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6InduaXF5aWpnaWM0OThAYXJ4eHdhbGxzLmNvbSIsImlkIjoiNjJlMGRhYmFlMTRlOTYwOGVhMDQzMWUzIiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzYyZTBkYWJhZTE0ZTk2MDhlYTA0MzFlMyJdfX0.OUJZon0yFbbpvCPG89khxZrCnUgjt7hELghIkX7zyBWL-XbPgI5L_DIdAF7TE7bsb3mJM4u9YPCkla4btB6ZHg',
            'if-none-match': '"62e0dabae14e9608ea0431e3"',
            'origin': 'https://mail.tm',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

        response = requests.get(f'https://api.mail.tm/sources/{id_mail}', headers=headers).json()
        try:
            data = response['data']
            return data
        except:
            return False
    def delebox(self,id_mail:str):
        headers = {
            'authority': 'api.mail.tm',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi,en;q=0.9',
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE2NTg5MDM4MDYsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6InduaXF5aWpnaWM0OThAYXJ4eHdhbGxzLmNvbSIsImlkIjoiNjJlMGRhYmFlMTRlOTYwOGVhMDQzMWUzIiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzYyZTBkYWJhZTE0ZTk2MDhlYTA0MzFlMyJdfX0.OUJZon0yFbbpvCPG89khxZrCnUgjt7hELghIkX7zyBWL-XbPgI5L_DIdAF7TE7bsb3mJM4u9YPCkla4btB6ZHg',
            'if-none-match': '"62e0dabae14e9608ea0431e3"',
            'origin': 'https://mail.tm',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        try:
            response = requests.delete(f'https://api.mail.tm/messages/{id_mail}', headers=headers)
    
            return True
        except:
            return False



# Chay = Mail(mail='wniqyijgic498@arxxwalls.com',password='Hoanga1979')
# id = Chay.getbox()['id']
# source = str(Chay.getboxid(id))
# otp = source.split('<p style=3D"font-family:arial;color:blue;font-size:20px;">  ')[1].split('   ')[0]
# print(otp)
# headers = {
#     'authority': 'api.mail.tm',
#     'accept': 'application/json, text/plain, */*',
#     'accept-language': 'vi,en;q=0.9',
#     'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE2NTg5MDM4MDYsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6InduaXF5aWpnaWM0OThAYXJ4eHdhbGxzLmNvbSIsImlkIjoiNjJlMGRhYmFlMTRlOTYwOGVhMDQzMWUzIiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzYyZTBkYWJhZTE0ZTk2MDhlYTA0MzFlMyJdfX0.OUJZon0yFbbpvCPG89khxZrCnUgjt7hELghIkX7zyBWL-XbPgI5L_DIdAF7TE7bsb3mJM4u9YPCkla4btB6ZHg',
#     'if-none-match': '"62e0dabae14e9608ea0431e3"',
#     'origin': 'https://mail.tm',
#     'referer': 'https://mail.tm/',
#     'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
# }

# response = requests.get('https://api.mail.tm/messages', headers=headers)
# print(response.text)
# # try:
# #     id_mail = response.json()['hydra:member'][0]['id']
# #     response = requests.delete(f'https://api.mail.tm/messages/{id_mail}', headers=headers)
# #     print("Đã Xóa mail")
# # except:
# #     pass