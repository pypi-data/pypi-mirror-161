"""
ChainBreakerClient
"""
import requests
import getpass
import pandas as pd
import os
import functools
import webbrowser
from typing import List

API_VERSION = "1.0.4"

def token_required(f):
    @functools.wraps(f) 
    def wrapper(self, *args, **kwargs):
        if self._token == None:
            return "You must be logged to execute this function!"
        return f(self, *args, **kwargs)
    return wrapper

class ChainBreakerClient():

    def __init__(self, endpoint):
        self._endpoint = endpoint
        self._name = None
        self._email = None
        self._permission = None
        self._token = None
          
    def get_status(self):
        """
        Get endpoint status.
        """
        try:
            res = requests.get(self._endpoint + "/status").status_code
            if res == 200:
                print("Endpoint is online")
                return 200 #"Endpoint is online"
        except: 
            pass 
        print("Endpoint is offline. Check our website for more information.")
        api_version = res.json()["api_version"]
        if api_version != API_VERSION:
            print(f"""Please update ChainBreakerAPI package, server is using {api_version} 
                      and your current version is {API_VERSION}. This might generate errors in some 
                      functions.""".replace("\n", " "))
        return 400

    def enter_password(self):
        """
        Enter new password function.
        """
        new_password = getpass.getpass("New password: ")
        repeat_password = getpass.getpass("Repeat new password: ")
        if new_password != repeat_password: 
            print("New passwords don't match")
            print("")
            return self.enter_password()
        return new_password

    def register(self):
        """
        This functions lets users to register to ChainBreaker.
        """
        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        data = {"name": name, "email": email, "password": password}
        res = requests.put(self._endpoint + "/user/register", data)
        if res.status_code == 200:
            return "Your account has been created succesfully. Your current permission is 'reader'. If you require more advanced permissions please write us an email to chainbreakerinfo@gmail.com."
        else:
            return "Error. Your account has not been created. Please try later or contact us to chainbreakerinfo@gmail.com."

    def login(self, *args):
        """
        This function lets the user to connect to ChainBreaker Service.
        """
        if len(args) == 2:
            email = args[0]
            password = args[1]
            data = {"email": email, "password": password, "expiration": 0}
        else:
            email = input("Email: ")
            password = getpass.getpass("Password: ")
        #expiration = input("Set session expiration in minutes (enter 0 for no expiration): ")
        expiration = 0
        data = {"email": email, "password": password, "expiration": expiration}
        res = requests.post(self._endpoint + "/user/login", data)
        if res.status_code == 200:
            res = res.json()
            self._token = res["token"]
            self._name = res["name"]
            self._email = res["email"]
            self._permission = res["permission"]
            return "Hi {}! You are now connected to ChainBreaker API. Your current permission level is '{}'. If you have any questions don't hesitate to contact us!".format(self._name, self._permission)
        print(res.text)
    
    @token_required
    def logout(self):
        """
        This functions lets the users to logout from their account.
        """
        self._token = None
        self._email = None
        self._name = None
        self._permission = None
        print("Session closed.")

    @token_required
    def change_password(self):
        """
        This function lets the user to change her/his password.
        """
        old_password = getpass.getpass("Old password: ")
        new_password = self.enter_password()
        headers = {"x-access-token": self._token}
        data = {"recover_password": "False", "old_password": old_password, "new_password": new_password}
        res = requests.put(self._endpoint + "/user/change_password", data = data, headers = headers).json()["message"]
        return res

    def recover_password(self):
        """
        This function lets the user to recover her/his password, if the user forgot it.
        """
        return "Please email to chainbreakerinfo@gmail.com asking for a recover of your password."
        if self._token == None: 
            # Send email.
            email = input("Email: ")
            data = {"email": email}
            res = requests.post(self._endpoint + "/user/recover_password", data = data).text
            
            # Change password.
            token = input("Enter Recovery token  (check your email): ")
            new_password = self.enter_password()
            headers = {"x-access-token": token}
            data = {"recover_password": "True", "new_password": new_password}
            res = requests.put(self._endpoint + "/user/change_password", data = data, headers = headers).json()["message"]
            return res
        return "You are logged into your account. Use this function only if you forgot your password and you are not logged into your account."
            
    @token_required     
    def get_account_info(self):
        """
        Print account information.
        """
        print("-- ChainBreaker Account Information --")
        print("")
        print("Name: ", self._name)
        print("Email: ", self._email)
        print("Permission: ", self._permission)

    @token_required
    def get_df(self, info, reduced = False):
        df = pd.DataFrame(info)
        columns = ["id_ad", "data_version", "author", "language", "link", "id_page", "title", "text", "category", 
        "first_post_date", "extract_date", "website", "phone", "country", "region", "city", "place", "latitude", 
        "longitude", "zoom", "email", "external_website", "reviews_website", 
        "ethnicity", "nationality", "age", "screenshot", "score_risk"]
        if reduced: 
            columns = ["id_ad", "link", "title", "text", "first_post_date", "website", "ethnicity", "phone", "country", "region", "city", "external_website", "screenshot"]
        df = df[columns]
        df.set_index("id_ad", inplace = True)
        return df

    @token_required
    def get_sexual_ads(self, language = "", website = "", start_date = "0001-01-01", end_date = "9999-01-01"): #, features = True, locations = False, comments = False, emails = False, names = False, phone = False, whatsapp = False):
        """
        This function returns sexual ads data from ChainBreaker Database.
        - language can be: "spanish", "english" or "" (all).
        - website can be: 
          - "mileroticos", "skokka" or "" (all) (for "spanish")
          - "leolist" or "" (all) (for "english")
        - start_date: String in %Y-%m-%d format. Example: 2021-04-28. Default value: 0001-01-01
        - end_date: String in %Y-%m-%d format. Example: 2022-08-30. Default value: 9999-01-01
        """

        headers = {"x-access-token": self._token}
        data = {"language": language, "website" : website, "start_date": start_date, "end_date": end_date}
        route = "/data/get_sexual_ads?from_id="
            
        def get_total_fetch(dataframes):
            results_fetch = 0
            for df in dataframes:
                results_fetch += df.shape[0]
            return results_fetch
         
        from_id = 0
        dataframes = list()
        
        res = requests.post(self._endpoint + route + str(from_id), data = data, headers = headers)
        if res.status_code == 401: 
            res = res.json()
            print(res["message"])
            return pd.DataFrame()
        
        res = res.json()
        df = self.get_df(res["ads"])
        dataframes.append(df)
        from_id = int(res["last_id"])
        total_results = int(res["total_results"])
        progress = get_total_fetch(dataframes) / total_results * 100
        print("Progress: ", round(progress, 3))
        
        while get_total_fetch(dataframes) < total_results:
            res = requests.post(self._endpoint + route + str(from_id), data = data, headers = headers)
            if res.status_code == 401: 
                break
            res = res.json()
            df = self.get_df(res["ads"])
            dataframes.append(df)
            from_id = int(res["last_id"])
            os.system("cls")
            progress = get_total_fetch(dataframes) / total_results * 100
            print("Progress: ", round(progress, 3))
        
        # Join dataframes and return result.
        return pd.concat(dataframes, axis=0)
    
    @token_required
    def get_sexual_ads_by_id(self, ids_list: List[int], reduced_version = False):
        reduced_version = "0" if reduced_version == False else "1"
        data = {"ads_ids": ids_list, "reduced_version": reduced_version}
        headers = {"x-access-token": self._token}
        res = requests.post(self._endpoint + "/data/get_sexual_ads_by_id", data = data, headers = headers) #.json()["ads"]
        if res.status_code != 200: 
            res = res.json()
            print(res["message"])
            return pd.DataFrame()
        res = res.json()
        df = self.get_df(res["ads"], reduced = bool(int(reduced_version)))
        return df

    @token_required
    def get_glossary(self, domain = ""):
        """
        This function returns the glossary of terms contained in ChainBreaker Database.
        - domain can be: "sexual", "general" or "" (all).
        This glossary was shared by Lena Garrett from Stop The Traffik.
        For more information please contact her: Lena.Garrett@stopthetraffik.org
        """
        data = {"domain": domain}
        headers = {"x-access-token": self._token}
        res = requests.post(self._endpoint + "/data/get_glossary", data = data, headers = headers).json()["glossary"]
        df = pd.DataFrame(res)
        columns = ["id_term", "domain", "term", "definition"]
        df = df[columns]
        df.set_index("id_term", inplace = True)
        return df
   
    @token_required
    def get_keywords(self, language = ""):
        """
        This function returns the set of keywords contained in ChainBreaker Database
        - language can be: "english", "spanish", "portuguese", "russian" or "" (all).
        These keywords were shared by Lena Garrett from Stop The Traffik.
        For more information please contact her: Lena.Garrett@stopthetraffik.org
        """
        data = {"language": language}
        headers = {"x-access-token": self._token}
        res = requests.post(self._endpoint + "/data/get_keywords", data = data, headers = headers).json()["keywords"]
        df = pd.DataFrame(res)
        columns = ["id_keyword", "language", "keyword", "english_translation", "meaning", "age_flag", "trafficking_flag", "movement_flag"]
        df = df[columns]
        df.set_index("id_keyword", inplace = True)
        return df

    @token_required
    def search_phone(self, phone):
        headers = {"x-access-token": self._token}
        data = {"phone": phone}
        res = requests.post(self._endpoint + "/data/search_phone", data = data, headers = headers)
        if res.status_code == 200:
            res = res.json()
            df = self.get_df(res["ads"])
            return df
        else: 
            print("Phone not found.")
            return 404
        
    @token_required
    def get_phone_score_risk(self, phone):
        headers = {"x-access-token": self._token}
        data = {"phone": phone}
        res = requests.post(self._endpoint + "/data/get_phone_score_risk", data = data, headers = headers)
        if res.status_code == 200:
            score_risk = res.json()["score_risk"]
            return score_risk
        else: 
            print("Phone not found.")
            return 404

    @token_required
    def get_communities(self, country = ""):
        headers = {"x-access-token": self._token}
        data = {"country": country}
        res = requests.post(self._endpoint + "/graph/get_communities", data = data, headers = headers)
        if res.status_code == 200:
            communities = res.json()["communities"] 
            for community in communities:
                for i in range(len(community)):
                    community[i] = int(community[i])
            return communities
        else: 
            message = res.json()["message"]
            print(message)
            return 404

    @token_required
    def download_communities(self, country: str, start_date: str = "0001-01-01", end_date: str = "2022-07-20", export_folder: str = ""):
        headers = {"x-access-token": self._token}
        data = {"country": country, "start_date": start_date, "end_date": end_date}
        res = requests.post(self._endpoint + "/graph/download_communities", data = data, headers = headers)
        with open(f"./{export_folder}/communities_{country}_from_{start_date}_to_{end_date}.xlsx", "wb") as f:
            f.write(res.content)

    @token_required
    def get_labels_count(self):
        res = requests.get(self._endpoint + "/graph/get_labels_count")
        if res.status_code == 200:
            return pd.DataFrame(res.json()["labels_count"])
        else: 
            message = res.json()["message"]
            print(message)
            return 404

    @token_required
    def get_communities_stats(self, country = ""):
        return True

    @token_required
    def get_token(self):
        return self._token

class ChainBreakerExpert(ChainBreakerClient):
    def __init__(self, endpoint):
        super().__init__(endpoint)

class ChainBreakerScraper(ChainBreakerClient):
    def __init__(self, endpoint):
        super().__init__(endpoint)

    @token_required
    def get_soup(self, url):
        """
        Get a soup object of an url or website.
        This function should only be used for websites without an anti-bot software.
        ChainBreaker includes a proxy service in order to make the extraction anonymously, 
        however this service is not always online. 
        """
        headers = {"x-access-token": self._token}
        data = {"url": url}
        return requests.post(self._endpoint + "/scraper/get_soup", data = data, headers = headers).json()["result"]

    @token_required
    def does_ad_exist(self, id_page, website, country):
        """
        Get if an ad exist using th id_page.
        """
        headers = {"x-access-token": self._token}
        data = {"id_page": id_page, "website": website, "country": country}
        return requests.post(self._endpoint + "/scraper/does_ad_exists", data = data, headers = headers).json()["does_ad_exist"]

    @token_required
    def insert_ad(self, author, language, link, id_page, title, text, category,
                  first_post_date, extract_date, website, phone, country, 
                  region, city, place, email, external_website, reviews_website, comments,
                  latitude, longitude, ethnicity, nationality, age, screenshot):
        """
        This function allow scraper to insert advertisements.
        """
        data = {}

        # Ad info.
        data["author"] = author
        data["language"] = language
        data["link"] = link
        data["id_page"] = id_page
        data["title"] = title
        data["text"] = text
        data["category"] = category
        data["first_post_date"] = first_post_date
        data["extract_date"] = extract_date
        data["website"] = website
        
        # Phone info.
        data["phone"] = phone
        
        # Location info.
        data["country"] = country
        data["region"] = region
        data["city"] = city
        data["place"] = place

        # Extra info.
        data["email"] = email
        data["external_website"] = external_website
        data["reviews_website"] = reviews_website

        # Comments info.
        data["comments"] = comments

        # Extra parameters.
        data["latitude"] = latitude
        data["longitude"] = longitude
        data["ethnicity"] = ethnicity
        data["nationality"] = nationality
        data["age"] = age
        data["screenshot"] = screenshot

        headers = {"x-access-token": self._token}
        res = requests.post(self._endpoint + "/scraper/insert_ad", data = data, headers = headers)
        return data, res

    @token_required    
    def get_image_faces(self, filepath, padding = 30):
        #headers = {"x-access-token": self._token, "content-type": "image/jpeg"}
        
        # Open image and change order of b, g, r to r, g, b
        #img = cv2.imread(filepath)
        #b, g, r = cv2.split(img)
        #img = cv2.merge([r, g, b])

        # Encode image and send it to the app.
        #_, img_encoded = cv2.imencode(".jpg", img)
        #data = img_encoded.tobytes()
        #faces = requests.post(self._endpoint + "/api/machine_learning/get_image_faces", data = data, headers = headers).json()["faces_data"]

        #outputs = list()
        #for face in faces: 
        #    endX = int(face["endX"])
        #    endY = int(face["endY"])
        #    startX = int(face["startX"])
        #    startY = int(face["startY"])
        #    result = img[startY - padding: endY + padding, startX - padding: endX + padding]
        #    outputs.append(result)
        return "Sorry. Service not currently available."
    
class ChainBreakerAdmin(ChainBreakerScraper):
    def __init__(self, endpoint):
        super().__init__(endpoint)

    @token_required        
    def create_user(self):
        """
        This functions allows administrators to create new users.
        """
        if  self._permission == "admin":
            name = input("User name: ")
            email = input("User email: ")
            permission = input("User permission: ")
            
            headers = {"x-access-token": self._token}
            data = {"name": name, "email": email, "permission": permission}
            res = requests.put(self._endpoint + "/user/create_user", data = data, headers = headers).json()["message"]
            return res
        else: 
            print("Only administrators can execute this function.")