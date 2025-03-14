import requests
import random
import string
import time
from colorama import Fore, init

init(autoreset=True)

# TempMail API (Replace with working API if needed)
TEMPMAIL_API = "https://www.1secmail.com/api/v1/"

# Facebook Sign-up URL
FB_SIGNUP_URL = "https://m.facebook.com/reg"

# List of foreign names and surnames
first_names = ["Hiroshi", "Matteo", "Ivan", "Pierre", "Ahmed", "Fatima", "Aisha", "Yuki", "Carlos", "Dimitri", 
               "Sofia", "Elena", "Nia", "Viktor", "Lars", "Hana", "Leila", "Miguel", "Amira", "Arvid", "Mikhail", 
               "Klara", "Júlia", "Katya", "Farhan"]

last_names = ["Nakamura", "Rossi", "Petrov", "Dubois", "El-Sayed", "Oliveira", "Takahashi", "García", "Novak", 
              "Müller", "Ibrahim", "Schmidt", "Fernández", "Jovanović", "Weber", "Sato", "Wang", "Lopez", "Kovács", 
              "Aliyev", "Huber", "Martins", "Pereira", "Moretti", "Sorokin"]

# Generate a random password
def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Get a new temporary email
def get_temp_email():
    response = requests.get(f"{TEMPMAIL_API}?action=genRandomMailbox&count=1")
    if response.status_code == 200:
        email = response.json()[0]
        print(Fore.GREEN + f"[+] Generated Email: {email}")
        return email
    else:
        print(Fore.RED + "[!] Failed to get temp email.")
        return None

# Generate a random birthday
def generate_birthday():
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(1985, 2002)
    return str(day), str(month), str(year)

# Get OTP from TempMail
def get_email_otp(email):
    domain = email.split("@")[1]
    username = email.split("@")[0]
    inbox_url = f"{TEMPMAIL_API}?action=getMessages&login={username}&domain={domain}"
    
    for _ in range(10):  # Retry 10 times for OTP
        response = requests.get(inbox_url)
        if response.status_code == 200 and response.json():
            messages = response.json()
            for msg in messages:
                if "Facebook" in msg['subject']:
                    mail_id = msg['id']
                    content_url = f"{TEMPMAIL_API}?action=readMessage&login={username}&domain={domain}&id={mail_id}"
                    msg_content = requests.get(content_url).json()
                    otp = ''.join(filter(str.isdigit, msg_content['body']))
                    print(Fore.YELLOW + f"[+] OTP Received: {otp}")
                    return otp
        time.sleep(5)  # Wait before retrying
    return None

# Create a Facebook account
def create_facebook_account():
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = get_temp_email()
    if not email:
        return None
    
    password = generate_password()
    day, month, year = generate_birthday()
    
    session = requests.Session()
    
    data = {
        "firstname": first_name,
        "lastname": last_name,
        "reg_email__": email,
        "reg_passwd__": password,
        "sex": "2",  # Male as default
        "birthday_day": day,
        "birthday_month": month,
        "birthday_year": year,
        "submit": "Sign Up"
    }

    response = session.post(FB_SIGNUP_URL, data=data)

    if "checkpoint" in response.url:
        print(Fore.RED + "[!] Facebook detected suspicious activity.")
        return None
    
    otp = get_email_otp(email)
    if otp:
        print(Fore.GREEN + f"[+] Facebook account created successfully: {first_name} {last_name} | {email} | {password}")
        return f"{first_name} {last_name} | {email} | {password}"
    
    print(Fore.RED + "[!] Failed to verify account.")
    return None

# Main function with menu
def main():
    num_accounts = int(input("Enter the number of accounts to create: "))
    
    with open("accounts.txt", "a") as file:
        for _ in range(num_accounts):
            account = create_facebook_account()
            if account:
                file.write(account + "\n")

    print(Fore.GREEN + "[+] All accounts saved in accounts.txt")

if __name__ == "__main__":
    main()
