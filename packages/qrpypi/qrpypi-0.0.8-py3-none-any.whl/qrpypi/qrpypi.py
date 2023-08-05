import requests
import shutil

class qrcode():

    def make(url):
    
        normalurl = "https://api.qrserver.com/v1/create-qr-code/?size450x450&data="+str(url)
        print("https://api.qrserver.com/v1/create-qr-code/?size450x450&data="+str(url))


        url = normalurl
        file_name = "qrocde.png"
        res = requests.get(url, stream = True)

        if res.status_code == 200:
            with open(file_name,'wb') as f:
                shutil.copyfileobj(res.raw, f)
        else:
            print('Image Couldn\'t be retrieved')