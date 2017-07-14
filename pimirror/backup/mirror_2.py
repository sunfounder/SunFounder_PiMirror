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

CENTER = (640,400)

def get_from_url(url):
    for i in range(5):
        try:
            result = requests.get(url, timeout=request_timeout)
            return result
        except:
            continue
    raise IOError('Timeout: %s; URL: %s'%(request_timeout,url))

class Message(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self._text = ''
        self.msg_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=('Helvetica', conf.xlarge_text_size),
            state='hidden'
        )
        self.is_displayed = False

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, text):
        if text != self._text:
            self._text = text
            self.canvas.itemconfig(self.msg_item, text=self._text)

    def show(self):
        self.is_displayed = True
        self.canvas.itemconfig(self.msg_item, state='normal')

    def hide(self):
        self.is_displayed = False
        self.canvas.itemconfig(self.msg_item, state='hidden')


class ScreenSaver(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self._image = ''
        self.image_item = self.canvas.create_image((640,400), state=HIDDEN)
        self.is_displayed = False

    def set_image(self, image):
        if image != self._image:
            self._image = image
            temp = Image.open(self._image)
            temp = temp.convert('RGB')
            temp = ImageTk.PhotoImage(temp)
            self.canvas.itemconfig(self.image_item, image=temp)

    def show(self):
        self.is_displayed = True
        self.canvas.itemconfig(self.image_item, state='normal')

    def hide(self):
        self.is_displayed = False
        self.canvas.itemconfig(self.image_item, state='hidden')


class Datetime(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self._time = ''
        self._date = ''
        self._weekday = ''
        self.time_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.large_text_size
                ),
            state='hidden',
            tag='datetime'
            )
        self.date_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.small_text_size
                ),
            state='hidden',
            tag='datetime'
            )
        self.weekday_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.small_text_size
                ),
            state='hidden',
            tag='datetime'
            )
        self.is_displayed = False

    def reflash(self):
        if conf.time_format == 12:
            temp_time = time.strftime('%I:%M %p') #hour in 12h format
        else:
            temp_time = time.strftime('%H:%M') #hour in 24h format
        temp_weekday = time.strftime('%A')
        temp_date = time.strftime(conf.date_format)

        if temp_time != self._time:
            self._time = temp_time
            self.canvas.itemconfig(self.time_item, text=self._time)
        if temp_date != self._date:
            self._date = temp_date
            self.canvas.itemconfig(self.date_item, text=self._date)
        if temp_weekday != self._weekday:
            self._weekday = temp_weekday
            self.canvas.itemconfig(self.weekday_item, text=self._weekday)

    def show(self):
        self.is_displayed = True
        self.canvas.itemconfig(self.time_item, state='normal')
        self.canvas.itemconfig(self.date_item, state='normal')
        self.canvas.itemconfig(self.weekday_item, state='normal')

    def hide(self):
        self.is_displayed = False
        self.canvas.itemconfig(self.time_item, state='hidden')
        self.canvas.itemconfig(self.date_item, state='hidden')
        self.canvas.itemconfig(self.weekday_item, state='hidden')


class Weather(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.temperature = ''
        self.forecast = ''
        self.currently = ''
        self.icon = ''
        self.location = ''
        self.regionName = ''
        self.temperature_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.xlarge_text_size
                ),
            state='hidden'
            )
        self.icon_item = self.canvas.create_image(
            (640,400),
            state='hidden'
            )
        self.currently_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.medium_text_size
                ),
            state='hidden'
            )
        self.forecast_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.small_text_size
                ),
            state='hidden'
            )
        self.location_item = self.canvas.create_text(
            CENTER,
            fill='white',
            font=(
                'Helvetica',
                conf.small_text_size
                ),
            state='hidden'
            )
        self.is_displayed = False

    def available(self):
        if conf.weather_api_token == 'None':
            return False
        else:
            return True

    def reflash(self):
        try:
            weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (conf.weather_api_token, conf.lat, conf.lon, conf.weather_lang, conf.weather_unit)
            print (weather_req_url)
            r = get_from_url(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently = weather_obj['currently']['summary']
            forecast = weather_obj["hourly"]["summary"]

            location = '%s, %s'%(conf.city, conf.regionName)

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
                    self.canvas.itemconfig(icon_item, image=photo)
            else:
                self.canvas.itemconfig(icon_item, image='')

            if self.currently != currently:
                self.currently = currently
                self.canvas.itemconfig(currently_item, text=self.currently)
            if self.forecast != forecast:
                self.forecast = forecast
                self.canvas.itemconfig(forecast_item, text=self.forecast)
            if self.temperature != temperature:
                self.temperature = temperature
                self.canvas.itemconfig(temperature_item, text=self.temperature)
            if self.location != location:
                self.location = location
                self.canvas.itemconfig(location_item, text=self.location)
            return True
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)
            return False

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

    def show(self):
        self.is_displayed = True
        self.canvas.itemconfig(self.temperature_item, state='normal')
        self.canvas.itemconfig(self.icon_item, state='normal')
        self.canvas.itemconfig(self.currently_item, state='normal')
        self.canvas.itemconfig(self.forecast_item, state='normal')
        self.canvas.itemconfig(self.location_item, state='normal')

    def hide(self):
        self.is_displayed = False
        self.canvas.itemconfig(self.temperature_item, state='hidden')
        self.canvas.itemconfig(self.icon_item, state='hidden')
        self.canvas.itemconfig(self.currently_item, state='hidden')
        self.canvas.itemconfig(self.forecast_item, state='hidden')
        self.canvas.itemconfig(self.location_item, state='hidden')

'''
class News(object):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News' # 'News' is more internationally generic
        self.newsLbl = Label(self, text=self.title, font=('Helvetica', conf.medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.detailContainer = Frame(self, bg="black")
        self.detailContainer.pack(side=TOP)
        self.is_displayed = False
        self.is_detail_displayed = False

    def get_headlines(self):
        self.detailContainer.pack_forget()
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
            for post in self.posts:
                headline = self.NewsHeadline(self.headlinesContainer, post.title)
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
'''
class Mirror:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(bg='black')
        self.state = True
        self.tk.attributes("-fullscreen", True)
        self.canvas = Canvas(self.tk, bd=0, highlightthickness=0, bg='black')
        self.canvas.pack(fill=BOTH, expand = YES)
        self.canvas.config(cursor='none')
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        self.message = Message(self.canvas)
        self.screensaver = ScreenSaver(self.canvas)
        self.datetime = Datetime(self.canvas)
        self.weather = Weather(self.canvas)
        #self.news = News(self.canvas)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
        self.disable_screen_sleep()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        if self.state:
            self.canvas.config(cursor='none')
        else:
            self.canvas.config(cursor='arrow')
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        self.canvas.config(cursor='arrow')
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

        #self.assistant.set_mic_mute(False)

        self.INFO(event)
        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            status_handler.display_status = status_handler.GREETINGS

        if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            status = self.process_status(event.args['text'])

        if event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            if status_handler.display_status == status_handler.GREETINGS:
                status_handler.display_status = status_handler.CLEANUP

        if status != None:
            self.assistant.set_mic_mute(True)
            status_handler.display_status = status
            self.assistant.set_mic_mute(False)

    def process_status(self, text):
        text = text.lower()
        status = None
        if 'show me' in text:
            if 'date' in text or 'time' in text:
                status = 'DATETIME'
            elif 'weather' in text:
                status = 'WEATHER'
            elif 'detail' in text:
                if 'first' in text:
                    status = 'NEWS_DETAIL_1'
                elif 'second' in text:
                    status = 'NEWS_DETAIL_2'
                elif 'third' in text:
                    status = 'NEWS_DETAIL_3'
                elif 'fourth' in text:
                    status = 'NEWS_DETAIL_4'
                elif 'fifth' in text:
                    status = 'NEWS_DETAIL_5'
            elif 'news' in text:
                status = 'NEWS'
        return status

    def main(self):
        self.assistant = Assistant(self.credentials)
        for ga_event in self.assistant.start():
            status = self.process_event(ga_event)

class Status_Handler(object):
    screensaver_dir = CODE_DIR+'screen-savers/'

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
                    self.show_pic(conf.screensaver)
                self.display_status = None
                    
            elif self.display_status == 'CLEANUP':
                print("cleanup")
                self.sleep_timer.cancel()
                self.sleep_timer_func()
            elif self.display_status == 'GREETINGS':
                if not mirror.text.is_displayed:
                    self.show_text('Hello')
            elif self.display_status == 'DATETIME':
                self.show_datetime()
            elif self.display_status == 'WEATHER':
                self.show_weather()
            elif self.display_status == 'NEWS':
                self.show_news()
            elif 'NEWS_DETAIL' in self.display_status:
                if not mirror.news.is_detail_displayed:
                    num = int(self.display_status[-1])
                    self.show_text('Wait..')
                    print("show NEWS detail %d" % num)
                    mirror.news.get_detail(num)
                    self.close_all()
                    mirror.news.is_detail_displayed = True
                    mirror.news.pack(anchor=N, padx=100, pady=500)
                    self.sleep_timer_restart()
            else:
                pass
            time.sleep(1)

    def show_message(self, text):
        print("show %s"%text)
        self.close_all()
        mirror.text.text = text
        mirror.text.show()
        self.sleep_timer_restart()
    def show_screensaver(self, pic):
        print("show %s"%pic)
        pic = self.screensaver_dir + pic
        mirror.screensaver.set_image(pic)
        mirror.screensaver.show()
    def show_datetime(self):
        mirror.datetime.reflash()
        if not mirror.datetime.is_displayed:
            print("show DATETIME")
            self.close_all()
            mirror.datetime.show()
            self.sleep_timer_restart()
    def show_weather(self):
        if not mirror.weather.is_displayed:
            self.show_message('Wait..')
            if mirror.weather.available():
                mirror.weather.reflash()
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
            mirror.news.is_displayed = True
            mirror.news.pack(anchor=N, padx=100, pady=500)
            self.sleep_timer_restart()

    def random_pic(self):
        pic_list = os.listdir(self.screensaver_dir)
        mount = len(pic_list)
        pick = random.randint(1,mount) - 1
        self.show_screensaver(pic_list[pick])

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
        mirror.message.hide()
        mirror.screensaver.hide()
        mirror.datetime.hide()
        mirror.weather.hide()
        #mirror.news.hide()
        self.random_timer_stop()

conf = filedb.fileDB(db=CODE_DIR+'config/config')

def main():
    global mirror, gooole_assistant, status_handler
    mirror = Mirror()
    gooole_assistant = Google_Assistant()
    status_handler = Status_Handler()
    status_handler.start()
    gooole_assistant.start()
    mirror.tk.mainloop()

def destory():
    status_handler.status_detect.join()
    gooole_assistant.google_assistant.join()
    quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destory()