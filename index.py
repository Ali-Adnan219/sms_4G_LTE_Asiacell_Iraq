import hashlib
import urllib.parse
import random
import time
import requests
import sqlite3
import xml.etree.ElementTree as ET

# إعدادات Telegram
TOKEN_BOT = '7361574780:AAG851YaeagLbSSKztkM9i64Ru_u4Hfsb14'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN_BOT}/sendMessage'
CHAT_ID = '1951751908'

# إعدادات router
IP_ROUTER = "192.168.1.1"
USERNAME = "admin"
PASSWD = "admin"
REALM = "Highwmg"
NONCE = "1000"
QOP = "auth"
URI = "/cgi/xml_action.cgi"
METHOD = "GET"
GN_COUNT = 4
TEMP = "marvell"

def create_database():
    """إنشاء قاعدة البيانات والجدول إذا لم يكن موجودًا."""
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        text_message   text  
    )
    ''')
    conn.commit()
    conn.close()

def check_and_store_message(message_id, body):
    """التحقق من المعرف وتخزين الرسالة في قاعدة البيانات وإرسال إشعار إلى تلغرام."""
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
        #response = requests.post(TELEGRAM_API_URL, data=payload)
        print(f"Message sent: ID {message_id}")
        #print(f"Telegram response: {response.text}")

        # احفظ المعرف في قاعدة البيانات
        c.execute('INSERT INTO messages (id ,text_message) VALUES (?,?)', (message_id,body))
        conn.commit()

    conn.close()

def md5_hash(value):
    """إرجاع تجزئة MD5 للقيمة المعطاة كنص سداسي."""
    return hashlib.md5(value.encode('utf-8')).hexdigest()

def hex_value(value):
    """تحويل عدد إلى نص سداسي مع الأصفار البادئة."""
    return format(value, '08x').upper()

def generate_digest_auth_url(username, realm, passwd, nonce, qop, uri, method, gn_count, temp):
    """إنشاء URL لتوثيق Digest مع معلمات الاستعلام ورأس التفويض."""
    ha1 = md5_hash(f"{username}:{realm}:{passwd}")
    ha2 = md5_hash(f"{method}:{uri}")
    
    rand = random.randint(0, 100000)
    date = int(time.time())
    salt = f"{rand}{date}"
    cnonce = md5_hash(salt)[:16]
    
    auth_count = hex_value(gn_count)
    digest_response = md5_hash(f"{ha1}:{nonce}:{auth_count}:{cnonce}:{qop}:{ha2}")
    
    gn_count += 1
    
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
        "_": str(int(time.time() * 1000))  # الوقت الحالي بالميلي ثانية
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"http://{IP_ROUTER}/login.cgi?{query_string}"
    
    auth_header = (f'Digest username="{username}", realm="{realm}", nonce="{nonce}", '
                   f'response="{digest_response}", qop={qop}, cnonce="{cnonce}", nc={auth_count}')
    
    return url, auth_header, gn_count

def get_sms_data():
    """الحصول على بيانات الرسائل من router."""
    url, auth_header, updated_gn_count = generate_digest_auth_url(
        USERNAME, REALM, PASSWD, NONCE, QOP, URI, METHOD, GN_COUNT, TEMP
    )
    
    print("Generated URL:", url)
    print("Authorization Header:", auth_header)
    print("Updated GN Count:", updated_gn_count)

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7',
        'Authorization': auth_header,
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Connection': 'keep-alive',
        'Cookie': 'showChangePaw=1',
        'Dnt': '1',
        'Expires': '-1',
        'Host': IP_ROUTER,
        'Pragma': 'no-cache',
        'Referer': f'http://{IP_ROUTER}/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.get(url, headers=headers)
    cookies = response.cookies.get("CGISID")

    payload = "<?xml version=\"1.0\" encoding=\"US-ASCII\"?> <RGW><param><method>call</method><session>000</session><obj_path>sms</obj_path><obj_method>sms.list_by_type</obj_method></param><sms_info><sms><page_index>1</page_index><list_type>0</list_type></sms></sms_info></RGW>"
    
    headers.update({
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'showChangePaw=1; CGISID={cookies}; projectConfig=%5Bobject%20Object%5D',
        'Csrftoken': 'hfiehifejfklihefiuehflejhfueihfeuihfeui'
    })

    response = requests.post(f"http://{IP_ROUTER}/xml_action.cgi?method=set", headers=headers, data=payload)
    return response.text ,cookies

def decode_ucs2(encoded_string):
    """فك تشفير نصوص UCS-2 إلى نصوص UTF-8."""
    decoded = ''
    for i in range(0, len(encoded_string), 4):
        hex_value = encoded_string[i:i+4]
        decoded += chr(int(hex_value, 16))
    return decoded

def process_sms_data(xml_data ,cookies):
    """معالجة بيانات الرسائل وفك تشفير النصوص."""
    root = ET.fromstring(xml_data)

    for sms in root.findall('.//node_list/*'):
        id_msg = sms.find('id')
        body_elem = sms.find('body')

        if id_msg is not None and body_elem is not None:
            encoded_body = body_elem.text
            decoded_body = decode_ucs2(encoded_body)
            print(f'ID: {id_msg.text}')
            print(f'Decoded Body: {decoded_body}')
            get_one_sms_data(id_msg.text,cookies)
            #check_and_store_message(id_msg.text, decoded_body)


def process_one_sms_data(xml_data):
    """معالجة بيانات الرسائل وفك تشفير النصوص."""
    root = ET.fromstring(xml_data)

    for sms in root.findall('.//sms'):
        id_msg = sms.find('id')
        body_elem = sms.find('body')

        if id_msg is not None and body_elem is not None:
            encoded_body = body_elem.text
            decoded_body = decode_ucs2(encoded_body)
            print(f'ID: {id_msg.text}')
            print(f'Decoded Body: {decoded_body}')
            check_and_store_message(id_msg.text, decoded_body)




def get_one_sms_data(id,cookies):
    url = f"http://{IP_ROUTER}/xml_action.cgi?method=set"

    payload = f'<?xml version="1.0" encoding="US-ASCII"?> <RGW><param><method>call</method><session>000</session><obj_path>sms</obj_path><obj_method>sms.get_by_id</obj_method></param><sms_info><sms><id>{id}</id></sms></sms_info></RGW>'
    headers = {
    'Accept': 'application/xml, text/xml, */*; q=0.01',
    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7',
    'Connection': 'keep-alive',

    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie':f'showChangePaw=1; projectConfig=%5Bobject%20Object%5D; CGISID={cookies}',
    #'Cookie': f'showChangePaw=1; CGISID={response.cookies.get("CGISID")}; projectConfig=%5Bobject%20Object%5D',
    'Csrftoken': 'hfiehifejfklihefiuehflejhfueihfeuihfeui',
    'Dnt': '1',
    'Host': f'{IP_ROUTER}',
    'Origin': f'http://{IP_ROUTER}',
    'Referer': f'http://{IP_ROUTER}/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    process_one_sms_data(response.text)


def main():
    """الدالة الرئيسية لتشغيل جميع العمليات."""
    create_database()
    xml_data ,cookies = get_sms_data()
    print(  xml_data,cookies)
    process_sms_data(xml_data ,cookies)

if __name__ == "__main__":
    main()
