#!/usr/bin/env python3

from __future__ import print_function

from tkinter import *
import locale
import threading
import requests
import json
import traceback
import feedparser
import re

from PIL import Image, ImageTk

import argparse
import os.path

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

import time
from os import system as run_command

import filedb

import random

request_timeout = 5

numbers_bak = {
    'first':1,
    'second':2,
    'third':3,
    'fourth':4,
    'fifth':5,
    'sixth':6,
    'seventh':7,
    'eigth':8,
    'ninth':9,
    'tenth':10,
    }
numbers_en = {
    'one':1,
    'two':2,
    'three':3,
    'four':4,
    'five':5,
    'six':6,
    'seven':7,
    'eight':8,
    'nine':9,
    'ten':10,
    }


CODE_DIR = '/home/pi/SunFounder_Pi-Mirror/'
icon_dir = CODE_DIR + 'icon/'
icon_lookup = {
    'clear-day'           : icon_dir+"Sun.png",
    'wind'                : icon_dir+"Wind.png",
    'cloudy'              : icon_dir+"Cloud.png",
    'partly-cloudy-day'   : icon_dir+"PartlySunny.png",
    'rain'                : icon_dir+"Rain.png",
    'snow'                : icon_dir+"Snow.png",
    'snow-thin'           : icon_dir+"Snow.png",
    'fog'                 : icon_dir+"Haze.png",
    'clear-night'         : icon_dir+"Moon.png",
    'partly-cloudy-night' : icon_dir+"PartlyMoon.png",
    'thunderstorm'        : icon_dir+"Storm.png",
    'tornado'             : icon_dir+"Tornado.png",
    'hail'                : icon_dir+"Hail.png",
}

CANCLE_PHRASE = ['never mind']

def get_from_url(url):
    for i in range(5):
        try:
            result = requests.get(url, timeout=request_timeout)
            return result
        except:
            continue
    raise IOError('Timeout: %s; URL: %s'%(request_timeout,url))

class Text(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.text = ''
        self.text_lable = Message(self, font=('Helvetica', conf.large_text_size), fg="white", bg="black", width=500)
        self.text_lable.pack()
        self.is_displayed = False

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self.text_lable.config(text=self.text)

    def show(self):
        self.is_displayed = True
        self.pack(anchor=N, padx=100, pady=500)

    def hide(self):
        self.is_displayed = False
        self.pack_forget()


class Screensaver(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.image = ''
        self.imageLb = Label(self, bg="black")
        self.imageLb.pack()
        self.is_displayed = False

    def set_pic(self, image):
        if image != self.image:
            self.image = image
            photo_image = Image.open(image)
            photo_image = photo_image.convert('RGB')
            photo_image = ImageTk.PhotoImage(photo_image)
            self.imageLb.config(image=photo_image)
            self.imageLb.image = photo_image

    def show(self):
        self.is_displayed = True
        self.pack()

    def hide(self):
        self.is_displayed = False
        self.pack_forget()

class Datetime(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self._time = ''
        self.time_label = Label(self, font=('Helvetica', conf.large_text_size), fg="white", bg="black")
        self.time_label.pack(side=TOP, anchor=E)
        # initialize day of week
        self._weekday = ''
        self.weekday_label = Label(self, text=self._weekday, font=('Helvetica', conf.small_text_size), fg="white", bg="black")
        self.weekday_label.pack(side=TOP, anchor=E)
        # initialize date label
        self._date = ''
        self.date_label = Label(self, text=self._date, font=('Helvetica', conf.small_text_size), fg="white", bg="black")
        self.date_label.pack(side=TOP, anchor=E)
        self.is_displayed = False

    def get_datetime(self):
        if conf.time_format == 12:
            time_tmp = time.strftime('%I:%M %p') #hour in 12h format
        else:
            time_tmp = time.strftime('%H:%M') #hour in 24h format

        weekday_tmp = time.strftime('%A')
        date_tmp = time.strftime(conf.date_format)
        # if time string has changed, update it
        if time_tmp != self._time:
            self._time = time_tmp
            self.time_label.config(text=time_tmp)
        if weekday_tmp != self._weekday:
            self._weekday = weekday_tmp
            self.weekday_label.config(text=weekday_tmp)
        if date_tmp != self._date:
            self._date = date_tmp
            self.date_label.config(text=date_tmp)

    def show(self):
        self.is_displayed = True
        self.pack(anchor=N, padx=100, pady=500)

    def hide(self):
        self.is_displayed = False
        self.pack_forget()


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', conf.xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Helvetica', conf.medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=('Helvetica', conf.small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Helvetica', conf.small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.is_displayed = False

    def available(self):
        if conf.weather_api_token == 'None':
            return False
        else:
            return True

    def get_weather(self):
        try:
            weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (conf.weather_api_token, conf.lat, conf.lon, conf.weather_lang, conf.weather_unit)
            print (weather_req_url)
            r = get_from_url(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            self.locationLbl.config(text='%s, %s'%(conf.city, conf.regionName))
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

    def show(self):
        self.is_displayed = True
        self.pack(anchor=N, padx=100, pady=500)

    def hide(self):
        self.is_displayed = False
        self.pack_forget()


class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News'
        self.newsLbl = Label(self, text=self.title, font=('Helvetica', conf.medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.detailContainer = Frame(self, bg="black")
        self.detailContainer.pack(side=TOP)
        self.is_displayed = False
        self.is_detail_displayed = False

    def get_headlines(self):
        #self.detailContainer.pack_forget()
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        try:
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
            try:
                headlines_url = "https://news.google.com/news?ned=%s&output=rss" % conf.countryCode
                print ('local news at: %s'%headlines_url)
            except:
                print ('local news not available: %s'%headlines_url)
                headlines_url = "https://news.google.com/news?ned=us&output=rss"

            feed = feedparser.parse(headlines_url)

            self.posts = feed.entries[0:conf.news_mount]
            for i in range(len(self.posts)):
                headline = self.NewsHeadline(self.headlinesContainer, '%s. %s'%(i+1, self.posts[i].title))
                headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get news." % e)

    def get_detail(self, index):
        self.headlinesContainer.pack_forget()
        self.detailContainer = Frame(self, bg="black")
        self.detailContainer.pack(side=TOP)
        detail = self.posts[index-1].summary
        detail = self.cleanhtml(detail)
        detail = detail.split('\n')[4]
        print (detail)
        detail = self.NewsDetail(self.detailContainer, detail)
        detail.pack(side=TOP, anchor=W)

    def cleanhtml(self, raw_html):
        special = {
            '&nbsp;' : ' ',
            '&amp;'  : '&',
            '&quot;' : '"',
            '&lt;'   : '<',
            '&gt;'   : '>',
            '&#39;'  : "'",
            '<br>'   : "\n",
        }

        cleantext = raw_html
        for (k,v) in special.items():
            cleantext = cleantext.replace (k, v)
     
        # clean hyer reference
        cleanr = re.compile('<a href.*?</a>')
        cleantext = re.sub(cleanr, '', cleantext)
        # clean nobr note
        cleanr = re.compile('<nobr>.*?</nobr>')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', cleantext)
        return cleantext

    class NewsHeadline(Frame):
        def __init__(self, parent, event_name=""):
            Frame.__init__(self, parent, bg='black')

            image = Image.open(icon_dir+"Newspaper.png")
            image = image.resize((25, 25), Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            self.iconLbl = Label(self, bg='black', image=photo)
            self.iconLbl.image = photo
            self.iconLbl.pack(side=LEFT, anchor=N)

            self.eventName = event_name
            self.eventNameMsg = Message(self, text=self.eventName, font=('Helvetica', conf.small_text_size), fg="white", bg="black", width=500)
            self.eventNameMsg.pack(side=LEFT, anchor=N)

    class NewsDetail(Frame):
        def __init__(self, parent, event_name=""):
            Frame.__init__(self, parent, bg='black')

            self.eventName = event_name
            self.eventNameMsg = Message(self, text=self.eventName, font=('Helvetica', conf.small_text_size), fg="white", bg="black", width=500)
            self.eventNameMsg.pack(side=LEFT, anchor=N)

    def show(self):
        self.is_displayed = True
        self.pack(anchor=N, padx=100, pady=500)

    def show_detail(self):
        self.is_detail_displayed = True
        self.pack(anchor=N, padx=100, pady=500)

    def hide(self):
        self.is_displayed = False
        #self.is_detail_displayed = False
        #self.headlinesContainer.pack_forget()
        #self.detailContainer.pack_forget()
        self.pack_forget()

class Mirror:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.mainFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.mainFrame.pack(fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=X)
        self.state = True
        self.tk.attributes("-fullscreen", True)
        self.mainFrame.config(cursor='none')
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        self.text = Text(self.mainFrame)
        self.screensaver = Screensaver(self.mainFrame)
        self.datetime = Datetime(self.mainFrame)
        self.weather = Weather(self.mainFrame)
        self.news = News(self.mainFrame)
        self.recognized = Label(self.bottomFrame, font=('Helvetica', conf.large_text_size), fg="white", bg="black")
        self.recognized.pack(anchor=E)

        self.disable_screen_sleep()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        if self.state:
            self.mainFrame.config(cursor='none')
        else:
            self.mainFrame.config(cursor='arrow')
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        self.mainFrame.config(cursor='arrow')
        return "break"

    def disable_screen_sleep(self):
        cmd = "xset s reset"
        run_command(cmd)
    def set_screen_sleep(self, sec):
        cmd = "xset s on s %s" % sec
        run_command(cmd)
    def active_screen(self):
        cmd = "xset s activate"
        run_command(cmd)


class Google_Assistant(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--credentials', type=existing_file,
                            metavar='OAUTH2_CREDENTIALS_FILE',
                            default=os.path.join(
                                os.path.expanduser('~/.config'),
                                'google-oauthlib-tool',
                                'credentials.json'
                            ),
                            help='Path to store and read OAuth2 credentials')
        args = parser.parse_args()
        with open(args.credentials, 'r') as f:
            self.credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))

        self.google_assistant = threading.Thread(target=self.main)

    def INFO(self, info):
        print("Google_Assistant: %s"%info)
    def start(self):
        self.google_assistant.start()

    def process_event(self, event):
        status = None

        self.INFO(event)
        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            if status_handler.display_status != 'NEWS':
                status_handler.display_status = 'GREETINGS'

        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
                status = self.process_status(event.args['text'])

        elif event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
            status_handler.display_status = 'CLEANUP'

        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            if status_handler.display_status == 'GREETINGS':
                status_handler.display_status = 'CLEANUP'

        if status != None:
            self.assistant.set_mic_mute(True)
            status_handler.display_status = status
            self.assistant.set_mic_mute(False)

    def process_status(self, text):
        text = text.lower()
        status = None
        if text == 'hey google' or text == 'ok google':
            status = 'GREETINGS'
        if 'show me' in text:
            if 'date' in text or 'time' in text:
                status = 'DATETIME'
            elif 'weather' in text:
                status = 'WEATHER'
            elif 'news' in text:
                status = 'NEWS'
        elif 'set screensaver to' in text:
            if 'mirror' in text:
                status = 'SCREENSAVER MIRROR'
            if 'random' in text:
                status = 'SCREENSAVER RANDOM'
        return status

    def process_news(self, text):
        text = text.lower()
        status = None
        if text in CANCLE_PHRASE:
            status = 'SCREENSAVER'
        else:
            for key in numbers_en:
                if key in text:
                    status = 'NEWS_DETAIL %d'%numbers_en[key]
                    print('Detail detect!: %s'%status)
                    return status
            for i in range(0,11):
                if str(i) in text:
                    status = 'NEWS_DETAIL %d'%i
                    print('Detail detect!: %s'%status)
                    return status
        return status
    def main(self):
        self.assistant = Assistant(self.credentials)
        for ga_event in self.assistant.start():
            status = self.process_event(ga_event)

class Status_Handler(object):
    screensaver_dir = CODE_DIR+'screensavers/'

    def __init__(self):
        self.display_status = 'SCREENSAVER'

    def start(self):
        self.status_detect = threading.Thread(target = self.status_detect_func)
        self.status_detect.start()

    def status_detect_func(self):
        while True:
            #print ("Display Status: %s"%self.display_status)
            if self.display_status == None:
                pass
            elif self.display_status == 'SCREENSAVER':
                if conf.screensaver == 'MIRROR':
                    self.random_timer_stop()
                elif conf.screensaver == 'RANDOM':
                    self.random_pic()
                    self.random_timer_stop()
                    self.random_timer_start()
                else:
                    self.random_timer_stop()
                    self.show_image(conf.screensaver)
                self.display_status = None
                    
            elif self.display_status == 'CLEANUP':
                print("cleanup")
                self.sleep_timer.cancel()
                self.sleep_timer_func()
            elif self.display_status == 'GREETINGS':
                if not mirror.text.is_displayed:
                    self.show_message('Hello')
            elif self.display_status == 'DATETIME':
                self.show_datetime()
            elif self.display_status == 'WEATHER':
                self.show_weather()
            elif self.display_status == 'NEWS':
                self.show_news()
            elif 'NEWS_DETAIL' in self.display_status:
                self.show_news_detail()
            elif 'SCREENSAVER' in self.display_status:
                temp = self.display_status.split(' ')[1]
                conf.screensaver = temp
                self.show_message('OK, screensaver set to %s'%temp)
                self.display_status = 'SCREENSAVER'
            else:
                pass
            time.sleep(1)

    def show_message(self, text):
        print("show %s"%text)
        self.close_all()
        mirror.text.set_text(text)
        mirror.text.show()
        self.sleep_timer_restart()
    def show_image(self, pic):
        print("show %s"%pic)
        pic = self.screensaver_dir + pic
        mirror.screensaver.set_pic(pic)
        mirror.screensaver.show()
    def show_datetime(self):
        mirror.datetime.get_datetime()
        if not mirror.datetime.is_displayed:
            print("show DATETIME")
            self.close_all()
            mirror.datetime.show()
            self.sleep_timer_restart()
    def show_weather(self):
        if not mirror.weather.is_displayed:
            self.show_message('Wait..')
            if mirror.weather.available():
                mirror.weather.get_weather()
                print("show WEATHER")
                self.close_all()
                mirror.weather.show()
                self.sleep_timer_restart()
            else:
                self.show_message('Weather not available')
    def show_news(self):
        if not mirror.news.is_displayed:
            self.show_message('Wait..')
            print("show NEWS")
            mirror.news.get_headlines()
            self.close_all()
            mirror.news.show()
            #google_assistant.assistant.start_conversation()
            self.sleep_timer_restart()
    def show_news_detail(self):
        if not mirror.news.is_detail_displayed:
            num = int(self.display_status.split(' ')[1])
            self.show_message('Wait..')
            print("show NEWS detail %d" % num)
            mirror.news.get_detail(num)
            self.close_all()
            mirror.news.show_detail()
            self.sleep_timer_restart()
    def random_pic(self):
        pic_list = os.listdir(self.screensaver_dir)
        mount = len(pic_list)
        pick = random.randint(1,mount) - 1
        self.show_image(pic_list[pick])

    def random_timer_stop(self):
        try:
            self.random_timer.cancel()
        except:
            pass

    def random_timer_start(self):
        self.random_timer = threading.Timer(conf.random_delay, self.random_timer_func)
        self.random_timer.start()
        print ("random_timer start!")

    def random_timer_func(self):
        print ("random!")
        self.display_status = 'SCREENSAVER'

    def sleep_timer_restart(self):
        try:
            self.sleep_timer.cancel()
        except:
            pass
        finally:
            self.sleep_timer = threading.Timer(conf.infomation_timeout, self.sleep_timer_func)
            self.sleep_timer.start()
            print ("timer start!")

    def sleep_timer_func(self):
        print ("Sleep!")
        self.close_all()
        self.display_status = 'SCREENSAVER'

    def close_all(self):
        mirror.text.hide()
        mirror.datetime.hide()
        mirror.weather.hide()
        mirror.news.hide()
        self.random_timer_stop()

conf = filedb.fileDB(db=CODE_DIR+'config/config')

def main():
    global mirror, google_assistant, status_handler
    mirror = Mirror()
    google_assistant = Google_Assistant()
    status_handler = Status_Handler()
    status_handler.start()
    google_assistant.start()
    mirror.tk.mainloop()

def destory():
    status_handler.status_detect.join()
    google_assistant.google_assistant.join()
    quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destory()