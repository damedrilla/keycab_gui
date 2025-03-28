import requests
from py122u import nfc

def getIDholder(uid):
    headers = {"X-API-KEY": "keycab.api.key"}
    req = requests.get("https://keycabinet.cspc.edu.ph/api/faculty", headers = headers)
    result = req.json()
    print(result)
    for _faculty in range(len(result)):
        if(str(uid) == result[_faculty]['rfid_uid']):
            if (result[_faculty]['status'] == "Disabled"):
                return [403, result[_faculty]["faculty_id"]]
            else:
                return [200, result[_faculty]["faculty_id"]]
        else:
            continue
    return [404, None]

def getUID(stop_flag): 
    def getID():
        uid_parsed = ""
        try:
            reader = nfc.Reader()
            reader.connect()
            raw_uid = reader.get_uid()
            for _byte in range(len(raw_uid)):
                uid_parsed += f'{raw_uid[_byte]:02x}'  # Ensure two-character hex with leading zeroes
            return uid_parsed
        except Exception as e:
            return None

    while not stop_flag.is_set():  # Check if the stop flag is set
        uid = getID()
        if uid is not None:
            return uid
    return None  # Return None if the stop flag is set