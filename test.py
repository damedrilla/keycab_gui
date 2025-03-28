from py122u import nfc
def check():
    err_msg = ""
    try:
        nfc.Reader()  # NFC reader is connected
    except Exception as e:
        err_msg = str(e)
    
    if err_msg == "No readers available":
        print('disconnected')
    else:
        print('connected')
    
is_nfc_reader_connected()