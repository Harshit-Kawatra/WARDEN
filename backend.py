from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import speech_recognition as sr 
import pytz
import pyttsx3
import subprocess
import webbrowser as wb
import pyautogui as pag 
import pyjokes
import sys
import psutil
from tqdm.auto import tqdm

# FUNCTIONS
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DAYS=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
MONTHS=['january','february','march','april','may','june','july','august','september','october','november','december']
DAY_EXTENTIONS=['rd','st','st','nd']
WAKE = 'warden'
SEARCH = ['search ','search on internet','google',]
NOTE_LIST=['make a note','write down','note down']
CALENDAR_LIST = ['what do i have','events on','do i have plans','am i busy','plans on']
JOKES = ['tell me a joke','joke time', 'happiness plus plus','joke']
SS = ['take a screenshot','capture window']
STATUS = ['batter at','cpu percentage','status of computer','status']
QUIT = ['bye','goodbye','goodnight']
FILES = ['show files','open file explorer','open my pc',]
CHANGE = ['change my name','call me ']


#REPLY FROM W.A.R.D.E.N
def speak(Text):
    engine = pyttsx3.init()
    engine.setProperty('volume',0.9)
    engine.say(Text)
    engine.runAndWait()
    
#GET RESPONSE FROM USER
def get_audio():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=''
        try:
            said=r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: "+str(e))

    return said.lower()

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

#GET EVENTS ON THE SPECIFIED DATE
def get_events(day,service):
    # Call the Calendar API
    date=datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date=datetime.datetime.combine(day, datetime.datetime.max.time())
    utc=pytz.timezone('Asia/Kolkata')
    date=date.astimezone(utc)
    end_date=end_date.astimezone(utc)


    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),
                                         timeMax=end_date.isoformat(),singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f'You have{len(events)} events on this day')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        start_time = str(start.split('T')[1].split('-')[0])
        if int(start_time.split(':')[0]) < 12:
            start_time = start_time + 'am'
        else:
            start_time = str(int(start_time.split(':')[0])-12) + start_time.split(':')[1]
            start_time = start_time + 'pm'

        speak(event['summary']+ 'at' + start_time)

#GET DATE FOR SEARCHING CALENDER
def get_date(text):
    text=text.lower()
    today=datetime.date.today()

    if text.count('today')>0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word)+1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month !=-1:
        year = year+1
    if month ==-1 and day !=-1:
        if day < today.day:
            month = month+1
        else:
            month=today.month
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_the_week = today.weekday() #0-6
        dif = day_of_week - current_day_of_the_week

        if dif < 0 :
            dif +=7
            if text.count("next")>=1:
                dif+=7
        
        
        return today + datetime.timedelta(dif)
    if day != -1:
        return datetime.date(month=month,day=day,year=year)


# MAKE NOTES IN NOTEPAD
def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(':','-') + '-note.txt'
    with open(file_name,'w') as f:
        f.write(text)

    subprocess.Popen(['notepad.exe',file_name])

# SEARCH IN CHROME    
def chrome():
    speak("What do i search")
    chromepath = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    search = get_audio()
    wb.get(chromepath).open_new_tab(search)

#TELL JOKES
def jokes():
    speak(pyjokes.get_joke())

#QUIT WARDEN

def quit():
    hour = datetime.datetime.now().hour

    if hour >= 18:
        speak("GOODNIGHT")
    else :
        speak("GOODBYE")
    sys.exit()

# TAKE A SCREENSHOT 
def screenshot():
    date = datetime.datetime.now()
    ss = str(date).replace(':','-') + '-note.png'
    img = pag.screenshot(ss)

#TELLS STATUS OF PC
def status():
    usage = str(psutil.cpu_percent())
    speak("CPU usage is at" + usage + 'percent')
    battery = psutil.sensors_battery()
    speak('Current Battery at ')
    speak(battery.percent)
    speak('percent')
#OPEN EXPLORER
def explorer():
    speak("opening explorer")
    pag.hotkey('win','e')
#CHANGE USERNAME
def change():
    fname = 'user_name.txt'
    fh=open(fname,'w')
    speak('What do you want me to call you from now')
    new_name = get_audio()
    fh.write(new_name)
    fh.close()


# MAIN
if __name__ == '__main__':
   
    SERVICE = authenticate_google()
    print('W.A.R.D.E.N. Initating....')
    for i in tqdm(range(100001)):
        print("",end='\r')
    fname = 'user_name.txt'
    try:
        fh=open(fname)
        user = fh.read()
        fh.close()
    except:
        speak('What should i call you')
        user = get_audio()
        fh = open(fname,'w')
        fh.write(user)
        fh.close()
    
    while True:
        print("Listening")
        text = get_audio()
        
        if text.count(WAKE) > 0:
            speak(f"Listening Now {user}....")
            text = get_audio()
            for phrase in CALENDAR_LIST:
                if phrase in text:
                    date = get_date(text)
                    if date:
                        get_events(get_date(text),SERVICE)
                    else:
                        speak(f'I dont understand {user} ')
            
            for phrase in NOTE_LIST:
                if phrase in text:
                    speak(f'What do you want me to write down {user} ')
                    note_text = get_audio()
                    note(note_text)
                    speak('I have made a note of that')

            for phrase in SEARCH:
                if phrase in text:
                    chrome()
                    speak('Let me search on the web')
            for phrase in JOKES:
                if phrase in text:
                    jokes()
            for phrase in SS:
                if phrase in text:
                    screenshot()
            for phrase in STATUS:
                if phrase in text:
                    status()
            for phrase in FILES:
                if phrase in text:
                    explorer()
            for phrase in QUIT:
                if phrase in text:
                    quit()
            for phrase in CHANGE:
                if phrase in text:
                    change()