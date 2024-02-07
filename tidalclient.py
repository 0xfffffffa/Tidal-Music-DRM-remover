#!/usr/bin/python


import requests
import os
import json
import base64
from Crypto.Cipher import AES
import Crypto.Util.Counter

session_id = ""
user_id = ""


class tidal: 

    def authenticated_headers(self,tidaltoken):
        self.authenticated_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) TIDAL/2.1.1 Chrome/53.0.2785.143 Electron/1.4.12 Safari/537.36',
            'Origin': 'https://desktop.tidal.com',
            'X-Tidal-SessionId': tidaltoken,
            'Referer': 'https://desktop.tidal.com/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US'
        }

    def set_headers(self):
        self.default_headers = {
            'X-Tidal-Token': '4zx46pyr9o8qZNRw',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) TIDAL/2.1.1 Chrome/53.0.2785.143 Electron/1.4.12 Safari/537.36',
            'Origin': 'https://desktop.tidal.com',
            'Referer': 'https://desktop.tidal.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US'
        }



    def login(self,username, password):
        self.set_headers()
        global session_id
        global user_id
        login_data = {
                'username': username,
                'password': password,
                'clientVersion': '2.0.0--36'
        }
        response = requests.post("https://api.tidal.com/v1/login/username?countryCode=US",login_data,headers=self.default_headers,allow_redirects=False)
        try:
            session_id = json.loads(response.text)['sessionId']
            user_id = json.loads(response.text)['userId']
            self.authenticated_headers(session_id)
            print "[x] Logged in successfully!"
        except:
            print "[!] Failure logging in"

    def makecoverurl(self,string):
        url = string.split("-")
        x = "https://resources.tidal.com/images/%s/%s/%s/%s/%s/320x320.jpg" % (url[0],url[1],url[2],url[3],url[4])
        return x

    def search(self,query):
        response = requests.get("https://api.tidal.com/v1/search?query=" + query + "&limit=100&offset=0&types=ARTISTS&countryCode=GB",headers=self.authenticated_headers,allow_redirects=False)
        #album = json.loads(response.text)
        artists = json.loads(response.text)
        #return artists
        if (len(artists["artists"]["items"]) > 0):
            number_of_artists = len(artists["artists"]["items"]) - 1
            while (number_of_artists >= 0):
                x = raw_input("[!] Found artist: %s is this what you're looking for? " % artists["artists"]["items"][number_of_artists]["name"].encode("ascii",'ignore'))
                if (x == "yes"):
                    artistname = (artists["artists"]["items"][number_of_artists]["name"].encode("ascii",'ignore')).replace(" ","%20")
                    artistid = artists["artists"]["items"][number_of_artists]["url"].split("/")[-1]
                    print "[x] The artist id is: %s" % (artistid)
                    response = requests.get("https://api.tidal.com/v1/artists/" + artistid + "/albums?limit=999&countryCode=GB",headers=self.authenticated_headers,allow_redirects=False)
                    albums = json.loads(response.text)
                    length = len(albums["items"]) - 1

                    while (length >= 0):
                       x = raw_input("[x] Album found: %s would you like to download this album? " % (albums["items"][length]["title"]).encode('ascii','ignore'))
                       if (x == "yes"):
                            url = albums["items"][length]["url"]
                            albumname = albums["items"][length]["title"].encode('ascii','ignore').replace(" ","-")
                            s = "mkdir %s" % (albumname)
                            os.system(s)
                            coverart = self.makecoverurl(albums["items"][length]["cover"])
                            f = open(albumname + "/" + albumname + ".jpg","wb")
                            response = requests.get(coverart,headers=self.authenticated_headers,stream=True,allow_redirects=False)
                            for block in response.iter_content(1024):
                                f.write(block)

                            album_no = url.split("/")[4]
                            response = requests.get("https://api.tidal.com/v1/albums/" + album_no + "/items?limit=100&countryCode=GB",headers=self.authenticated_headers,allow_redirects=False)
                            songs = json.loads(response.text)
                            number_of_songs = len(songs["items"]) - 1 
                            while (number_of_songs >= 0):
                                trackurl = songs["items"][number_of_songs]["item"]["url"]
                                trackid = trackurl.split("/")[-1]
                                title =  songs["items"][number_of_songs]["item"]["title"].encode('ascii','ignore')
                                print "[!] Now downloading album track: %s" % title
                                self.decrypt(trackid,title,albumname)
                                number_of_songs = number_of_songs - 1
                            s = "rm -rf %s/*encrypted*" % (albumname)
                            os.system(s)
                       length = length - 1
               

                number_of_artists = number_of_artists - 1


    def decrypt(self,trackid,title,albumname):

        r = requests.get("https://api.tidal.com/v1/tracks/"+trackid+"/streamUrl?soundQuality=LOSSLESS&countryCode=GB",headers=self.authenticated_headers,allow_redirects=False)
        result = json.loads(r.text)
        url = result["url"]

        encryptionKey = result["encryptionKey"]
        directory= albumname

       #if not os.path.exists(directory):
       #     os.makedirs(directory)


        with open(os.path.join(directory,url.split('/')[5].split('?')[0]+'__encrypted'), 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print("something went wrong")
                print response

            for block in response.iter_content(1024):
                handle.write(block)
            #print encryptionKey

        total_key = base64.b64decode(encryptionKey)

        iv = total_key[:16]
        key = total_key[16:]
        #print total_key.encode("hex")
        #print "iv: ", iv.encode("hex") 
        #print "key: ", key.encode("hex")

        static_key_b64="UIlTTEMmmLfGowo/UC60x2H45W6MdGgTRfo/umg4754="
        static_key = base64.b64decode(static_key_b64)

        cipher_decrypt_key = AES.new( static_key , AES.MODE_CBC , iv)
        decrypted_key = cipher_decrypt_key.decrypt(key)

        second_key = decrypted_key[:16]
        second_iv = decrypted_key[16:][:8]

        #print "second_iv: ",second_iv.encode("hex")
        #print "second_key: ",second_key.encode("hex") 
        #sys.exit(0)
        f = open(os.path.join(directory,url.split('/')[5].split('?')[0]+'__encrypted')).read()
        f = f + ( 16 - len(f) % 16 ) * "\x00"
        

        ctr=second_iv+"\x00"*8
        ctr = Crypto.Util.Counter.new(128, initial_value=long(ctr.encode("hex"),16))
        cipher = AES.new(second_key, AES.MODE_CTR , counter=ctr)
        #print len(f)
        d = cipher.decrypt(f)

        with open(os.path.join(directory,url.split('/')[5].split('?')[0]), "wb") as file:
            file.write(d)

        path = os.path.join(directory,url.split('/')[5].split('?')[0])

        new_title = title.encode("ascii","ignore").replace(" ","-").replace("'","\\'").replace("`","\\`").replace("(","\\(").replace(")","\\)")


        string = "mv %s %s/%s.flac" % (path,albumname,new_title)


        os.system(string)

     

    
