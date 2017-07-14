'''
**********************************************************************
* Filename    : filedb.py
* Description : A simple file based database.
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
**********************************************************************
'''
from os import system as run
from requests import get as request
class fileDB(object):
    """A file based database.

    A file based database, read and write arguements in the specific file.
    """
    def __init__(self, db=None):
        '''Init the db_file is a file to save the datas.'''

        # Check if db_file is defined
        if db != None:
            self.db = db
        else:
            self.db = "config"

        if not self.exist:
            run('touch %s'%self.db)
            run('sudo chmod 777 %s'%self.db)

    @property
    def exist(self):
        try:
            conf = open(self.db,'r')
            conf.close()
            return True
        except :
            return False

    def get(self, name, default_value=None):
        """Get value by data's name. Default value is for the arguemants do not exist"""
        try:
            conf = open(self.db,'r')
            lines=conf.readlines()
            conf.close()
            file_len=len(lines)-1
            flag = False
            # Find the arguement and set the value
            for i in range(file_len):
                if lines[i][0] != '#':
                    if lines[i].split('=')[0].strip() == name:
                        value = lines[i].split('=')[1].strip(' ').strip()
                        flag = True
            if flag:
                return value
            else:
                return default_value
        except :
            self.set(name, default_value)
            return default_value
    
    def set(self, name, value):
        """Set value by data's name. Or create one if the arguement does not exist"""

        # Read the file
        conf = open(self.db,'r')
        lines=conf.readlines()
        conf.close()
        file_len=len(lines)-1
        flag = False
        # Find the arguement and set the value
        for i in range(file_len):
            if lines[i][0] != '#':
                if lines[i].split('=')[0].strip() == name:
                    lines[i] = '%s = %s\n' % (name, value)
                    flag = True
        # If arguement does not exist, create one
        if not flag:
            lines.append('%s = %s\n\n' % (name, value))

        # Save the file
        conf = open(self.db,'w')
        conf.writelines(lines)
        conf.close()

    def get_ip_location(self):
        print('Getting ip informations...',end='')
        url = "http://ip-api.com/json"
        result = self.get_from_url(url)
        location = json.loads(result.text)
        print ('done.')
        return location
    def get_from_url(self, url):
        for i in range(5):
            try:
                result = request(url, timeout=5)
                return result
            except:
                continue
        raise IOError('Timeout: %s; URL: %s'%(5,url))
    def get_location(self):
        location = get_ip_location
        self.city = location['city']
        self.region = location['region']
        self.regionName = location['regionName']
        self.country = location['country']
        self.countryCode = location['countryCode'].lower()
        self.lat = location['lat']
        self.lon = location['lon']
        self.ip = location['query']
        self.timezone = location['timezone']

    @property
    def random_delay(self):
        self._random_delay = int(self.get('random_delay', 5))
        return self._random_delay
    @random_delay.setter
    def random_delay(self, value):
        self._random_delay = value
        self.set('random_delay', value)

    @property
    def infomation_timeout(self):
        self._infomation_timeout = int(self.get('infomation_timeout', 30))
        return self._infomation_timeout
    @infomation_timeout.setter
    def infomation_timeout(self, value):
        self._infomation_timeout = value
        self.set('infomation_timeout', value)

    @property
    def screensaver(self):
        self._screensaver = self.get('screensaver', 'MIRROR')
        return self._screensaver
    @screensaver.setter
    def screensaver(self, value):
        self._screensaver = value
        self.set('screensaver', value)

    @property
    def news_mount(self):
        self._news_mount = int(self.get('news_mount', 5))
        return self._news_mount
    @news_mount.setter
    def news_mount(self, value):
        self._news_mount = value
        self.set('news_mount', value)

    @property
    def time_format(self):
        self._time_format = int(self.get('time_format', 12))
        return self._time_format
    @time_format.setter
    def time_format(self, value):
        self._time_format = value
        self.set('time_format', value)

    @property
    def date_format(self):
        self._date_format = self.get('date_format', '%b %d, %Y')
        return self._date_format
    @date_format.setter
    def date_format(self, value):
        self._date_format = value
        self.set('date_format', value)

    @property
    def weather_api_token(self):
        self._weather_api_token = self.get('weather_api_token', None)
        return self._weather_api_token
    @weather_api_token.setter
    def weather_api_token(self, value):
        self._weather_api_token = value
        self.set('weather_api_token', value)

    @property
    def weather_lang(self):
        self._weather_lang = self.get('weather_lang', 'en')
        return self._weather_lang
    @weather_lang.setter
    def weather_lang(self, value):
        self._weather_lang = value
        self.set('weather_lang', value)

    @property
    def weather_unit(self):
        self._weather_unit = self.get('weather_unit', 'auto')
        return self._weather_unit
    @weather_unit.setter
    def weather_unit(self, value):
        self._weather_unit = value
        self.set('weather_unit', value)

    @property
    def xlarge_text_size(self):
        self._xlarge_text_size = int(self.get('xlarge_text_size', 40))
        return self._xlarge_text_size
    @xlarge_text_size.setter
    def xlarge_text_size(self, value):
        self._xlarge_text_size = value
        self.set('xlarge_text_size', value)

    @property
    def large_text_size(self):
        self._large_text_size = int(self.get('large_text_size', 30))
        return self._large_text_size
    @large_text_size.setter
    def large_text_size(self, value):
        self._large_text_size = value
        self.set('large_text_size', value)

    @property
    def medium_text_size(self):
        self._medium_text_size = int(self.get('medium_text_size', 20))
        return self._medium_text_size
    @medium_text_size.setter
    def medium_text_size(self, value):
        self._medium_text_size = value
        self.set('medium_text_size', value)

    @property
    def small_text_size(self):
        self._small_text_size = int(self.get('small_text_size', 10))
        return self._small_text_size
    @small_text_size.setter
    def small_text_size(self, value):
        self._small_text_size = value
        self.set('small_text_size', value)

    @property
    def city(self):
        self._city = self.get('city', None)
        if self._city == None:
            self.get_location()
            self._city = self.get('city', None)
        return self._city
    @city.setter
    def city(self, value):
        self._city = value
        self.set('city', value)

    @property
    def region(self):
        self._region = self.get('region', None)
        if self._region == None:
            self.get_location()
            self._region = self.get('region', None)
        return self._region
    @region.setter
    def region(self, value):
        self._region = value
        self.set('region', value)

    @property
    def regionName(self):
        self._regionName = self.get('regionName', None)
        if self._regionName == None:
            self.get_location()
            self._regionName = self.get('regionName', None)
        return self._regionName
    @regionName.setter
    def regionName(self, value):
        self._regionName = value
        self.set('regionName', value)

    @property
    def country(self):
        self._country = self.get('country', None)
        if self._country == None:
            self.get_location()
            self._country = self.get('country', None)
        return self._country
    @country.setter
    def country(self, value):
        self._country = value
        self.set('country', value)

    @property
    def countryCode(self):
        self._countryCode = self.get('countryCode', None)
        if self._countryCode == None:
            self.get_location()
            self._countryCode = self.get('countryCode', None)
        return self._countryCode
    @countryCode.setter
    def countryCode(self, value):
        self._countryCode = value
        self.set('countryCode', value)

    @property
    def lat(self):
        self._lat = self.get('lat', None)
        if self._lat == None:
            self.get_location()
            self._lat = self.get('lat', None)
        return self._lat
    @lat.setter
    def lat(self, value):
        self._lat = value
        self.set('lat', value)

    @property
    def lon(self):
        self._lon = self.get('lon', None)
        if self._lon == None:
            self.get_location()
            self._lon = self.get('lon', None)
        return self._lon
    @lon.setter
    def lon(self, value):
        self._lon = value
        self.set('lon', value)

    @property
    def ip(self):
        self._ip = self.get('ip', None)
        if self._ip == None:
            self.get_location()
            self._ip = self.get('ip', None)
        return self._ip
    @ip.setter
    def ip(self, value):
        self._ip = value
        self.set('ip', value)

    @property
    def timezone(self):
        self._timezone = self.get('timezone', None)
        if self._timezone == None:
            self.get_location()
            self._timezone = self.get('timezone', None)
        return self._timezone
    @timezone.setter
    def timezone(self, value):
        self._timezone = value
        self.set('timezone', value)
