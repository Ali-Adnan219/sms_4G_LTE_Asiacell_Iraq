import hashlib
import urllib.parse
import random
import time
import requests
import sqlite3

# إنشاء أو فتح قاعدة البيانات
conn = sqlite3.connect('messages.db')
c = conn.cursor()

# إنشاء جدول لتخزين المعرفات
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    text_body text
)
''')

conn.commit()
conn.close()

token_bot='7361574780:AAG851YaeagLbSSKztkM9i64Ru_u4Hfsb14'


TELEGRAM_API_URL = f'https://api.telegram.org/bot{token_bot}/sendMessage'
CHAT_ID = '1951751908'



ip_router="192.168.1.1"


username = "admin"
passwd = "admin"


realm = "Highwmg"

nonce = "1000"
qop = "auth"
uri = "/cgi/xml_action.cgi"
method = "GET"
gn_count = 4
temp = "marvell"


def check_and_store_message(message_id ,body):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    # البحث عن المعرف في قاعدة البيانات
    c.execute('SELECT id FROM messages WHERE id = ?', (message_id,))
    result = c.fetchone()

    if result is None:
        # إذا لم يتم العثور على المعرف، أرسل رسالة إلى تلغرام
        message_text = f'رسالة جديدة: {body}'
        payload = {
            'chat_id': CHAT_ID,
            'text': message_text
        }
        #requests.post(TELEGRAM_API_URL, data=payload)
        print(f"send......message_id:{message_id}")
        #print(requests.text)

        # احفظ المعرف في قاعدة البيانات
        c.execute('INSERT INTO messages (id,text_body) VALUES (?,?)', (message_id,body))
        conn.commit()

    conn.close()


def md5_hash(value):
    """Returns the MD5 hash of the given value as a hexadecimal string."""
    return hashlib.md5(value.encode('utf-8')).hexdigest()

def hex_value(value):
    """Converts a number to a hexadecimal string with leading zeros."""
    return format(value, '08x').upper()

def generate_digest_auth_url(username, realm, passwd, nonce, qop, uri, method, gn_count, temp):
    """Generates Digest Authentication URL with query parameters and Authorization header."""
    # Compute HA1 and HA2
    ha1 = md5_hash(f"{username}:{realm}:{passwd}")
    ha2 = md5_hash(f"{method}:{uri}")
    
    # Generate random cnonce and compute response
    rand = random.randint(0, 100000)
    date = int(time.time())
    salt = f"{rand}{date}"
    cnonce = md5_hash(salt)[:16]
    
    auth_count = hex_value(gn_count)
    digest_response = md5_hash(f"{ha1}:{nonce}:{auth_count}:{cnonce}:{qop}:{ha2}")
    
    gn_count += 1
    
    # Build the URL with query parameters
    params = {
        "Action": "Digest",
        "username": username,
        "realm": realm,
        "nonce": nonce,
        "response": digest_response,
        "qop": qop,
        "cnonce": cnonce,
        "nc": auth_count,
        "temp": temp,
        "_": str(int(time.time() * 1000))  # Current time in milliseconds
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"http://192.168.1.1/login.cgi?{query_string}"
    
    # Build the Authorization header
    auth_header = (f'Digest username="{username}", realm="{realm}", nonce="{nonce}", '
                   f'response="{digest_response}", qop={qop}, cnonce="{cnonce}", nc={auth_count}')
    
    return url, auth_header, gn_count




url, auth_header, updated_gn_count = generate_digest_auth_url(username, realm, passwd, nonce, qop, uri, method, gn_count, temp)
print("Generated URL:", url)
print("Authorization Header:", auth_header)
print("Updated GN Count:", updated_gn_count)




payload = {}
headers = {
  'Accept': '*/*',
  'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7',
  'Authorization': auth_header,
  'Cache-Control': 'no-store, no-cache, must-revalidate',
  'Connection': 'keep-alive',
  'Cookie': 'showChangePaw=1',
  'Dnt': '1',
  'Expires': '-1',
  'Host': f'{ip_router}',
  'Pragma': 'no-cache',
  'Referer': f'http://{ip_router}/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest'
}

response = requests.request("GET", url, headers=headers, data=payload)
cookiess=response.cookies.get("CGISID")




#############2
url = f"http://{ip_router}/xml_action.cgi?method=set"

payload = "<?xml version=\"1.0\" encoding=\"US-ASCII\"?> <RGW><param><method>call</method><session>000</session><obj_path>sms</obj_path><obj_method>sms.list_by_type</obj_method></param><sms_info><sms><page_index>1</page_index><list_type>0</list_type></sms></sms_info></RGW>"
headers = {
  'Accept': 'application/xml, text/xml, */*; q=0.01',
  'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7',
  'Authorization': auth_header,
  'Connection': 'keep-alive',

  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Cookie': f'showChangePaw=1; CGISID={cookiess}; projectConfig=%5Bobject%20Object%5D',
  'Csrftoken': 'hfiehifejfklihefiuehflejhfueihfeuihfeui',
  'Dnt': '1',
  'Host': f'{ip_router}',
  'Origin': f'http://{ip_router}',
  'Referer': f'http://{ip_router}/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest'
}

response = requests.request("POST", url, headers=headers, data=payload)







import xml.etree.ElementTree as ET

# مثال على بيانات XML
#xml_data = '''<?xml version="1.0" encoding="utf-8"?><RGW><sms><resp>0</resp><total>109</total><page_count>11</page_count><node_list><s1><id>245</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,12,09,45,16,+3</date><protocol>0</protocol><type>0</type><read>1</read><status>0</status><location>0</location><body>06390632064a0632064a00200627064406450634062a06310643060c00200644064506480627063506440629002006250633062a062e062f0627064500200627</body></s1><s2><id>244</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,11,09,37,44,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>06250646062a0647062a0020063506440627062d064a062900200627064406250646062a06310646062a002006270644062a064a0020062a06440642064a062a</body></s2><s3><id>243</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,11,09,06,27,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>06390632064a0632064a00200627064406450634062a06310643060c00200644064506480627063506440629002006250633062a062e062f0627064500200627</body></s3><s4><id>242</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,11,08,11,28,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>0639063206cc0632064a00200627064406450634062a06310643060c00200631063506cc062f0643002006270644062d06270644064a00200647064800200033</body></s4><s5><id>241</id><address>Asiacell4G+</address><contact_id>0</contact_id><date>24,08,10,17,58,13,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>06390631063600200035002006230636063906270641002006270644063406470631064a06290020064806440641062a0631062900200645062d062f0648062f</body></s5><s6><id>240</id><address>Asiacell4G+</address><contact_id>0</contact_id><date>24,08,10,10,27,51,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>064506390020002206390631063600200031003000200623063606390627064100200644064306440020062706440634062806430627062a0022060c00200623</body></s6><s7><id>239</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,10,09,43,10,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>06390632064a0632064a00200627064406450634062a06310643060c00200644064506480627063506440629002006250633062a062e062f0627064500200627</body></s7><s8><id>238</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,10,09,42,06,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>0639063206cc0632064a00200627064406450634062a06310643060c002006440642062f002006250633062a064706440643062a00200627064406250646062a</body></s8><s9><id>237</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,10,09,36,27,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>064506280631064806430021002006440642062f0020062a06440642064a062a00200032003000200645064a062c062706280627064a062a002006270646062a</body></s9><s10><id>236</id><address>Asiacell</address><contact_id>0</contact_id><date>24,08,10,08,15,23,+3</date><protocol>0</protocol><type>0</type><read>0</read><status>0</status><location>0</location><body>0639063206cc0632064a00200627064406450634062a06310643060c00200644062a062c064606280020062a0639064406cc06420020062e06370643060c0020</body></s10></node_list><count>10</count></sms></RGW>'''
xml_data =response.text
# تحليل XML
root = ET.fromstring(xml_data)

# دالة لفك تشفير النصوص (للتحويل من UCS-2 على سبيل المثال)
def decode_ucs2(encoded_string):
    decoded = ''
    for i in range(0, len(encoded_string), 4):
        hex_value = encoded_string[i:i+4]
        decoded += chr(int(hex_value, 16))
    return decoded



# عرض محتوى <body>
for body in root.findall('.//node_list/*'):
    encoded_body = body.find('body').text
    id_msg=body.find('id')
    print(id_msg.text)
    # حدد التشفير المناسب هنا
    
    url = f"http://{ip_router}/xml_action.cgi?method=set"

    payload = f'<?xml version="1.0" encoding="US-ASCII"?> <RGW><param><method>call</method><session>000</session><obj_path>sms</obj_path><obj_method>sms.get_by_id</obj_method></param><sms_info><sms><id>{id_msg.text}</id></sms></sms_info></RGW>'
    headers = {
  'Accept': 'application/xml, text/xml, */*; q=0.01',
  'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7',
  #'Authorization': auth_header,
  'Connection': 'keep-alive',

  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Cookie':f'showChangePaw=1; projectConfig=%5Bobject%20Object%5D; CGISID={cookiess}',
  #'Cookie': f'showChangePaw=1; CGISID={response.cookies.get("CGISID")}; projectConfig=%5Bobject%20Object%5D',
  'Csrftoken': 'hfiehifejfklihefiuehflejhfueihfeuihfeui',
  'Dnt': '1',
  'Host': f'{ip_router}',
  'Origin': f'http://{ip_router}',
  'Referer': f'http://{ip_router}/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest'
}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    root = ET.fromstring(response.text)
    
    for body in root.findall('.//sms'):
        encoded_body = body.find('body').text
        id_msg=body.find('id')
        decoded_body = decode_ucs2(encoded_body)
        print(f'Decoded Body: {decoded_body}')
        print(f'id message : {id_msg.text}')
        check_and_store_message(id_msg.text  ,decoded_body)


