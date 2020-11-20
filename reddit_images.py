import praw
import requests
import os
import shutil
import unicodedata
import json
from unidecode import unidecode
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

path = os.path.abspath("/path/of/memes/folder")

os.mkdir(path)

url = "https://www.reddit.com"

with open("/path/of/json/credentials/file") as f:
    params = json.load(f)

reddit = praw.Reddit(
    client_id=params["client_id"],
    client_secret=params["api_key"],
    user_agent=params["user_agent"],
    username=params["username"],
    password=params["password"]
)

subreddit = reddit.subreddit("SUBREDDIT NAME")

def remove_emoji(input_string):
    return_string = ""

    for character in input_string:
        try:
            character.encode("ascii")
            return_string += character
        except UnicodeEncodeError:
            replace = unidecode(str(character))
            if replace != "":
                return_string += replace

    return " ".join(return_string.split()) # removes double spaces after replacing emoji

def reddit_posts():
    for name, submission in enumerate(subreddit.hot(limit=100), 1):
        if name == 11:
            break
        else:
            url = (submission.url)
            file_name = str(name)
            if url.endswith(".jpg"):
                file_name += ".jpg"
                found = True
            elif url.endswith(".png"):
                file_name += ".png"
                found = True
            else:
                found = False
            
            if found == True:
                try:
                    r = requests.get(url)
                    with open(file_name, "wb") as f:
                        f.write(r.content)
                except requests.exceptions.RequestException as e:
                    print("Error for {}: {}".format(submission, e))
                    continue
                
                shutil.move("/path/of/folder/" + file_name, path)

                print(file_name)

def send_mail(subject, text, path):
    
    file_names = [os.path.join(path, f) for f in os.listdir(path)]

    #Set up users for email
    gmail_user = input("Enter your email: ")
    gmail_pwd = input("Enter password: ")
    recipients = input("Enter recipient email: ")
    
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = recipients
    msg['Subject'] = subject
    
    msg.attach(MIMEText(text))
    # get all the attachments
    for file in file_names:
        base_name = os.path.basename(file)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="meme0%s"' % base_name)
        msg.attach(part)
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(gmail_user, recipients, msg.as_string())

    print("\nEmail has been sent!")
    
    server.quit()

if __name__ == "__main__":
    reddit_posts()
    send_mail("Today's Report", "Test Email", path)