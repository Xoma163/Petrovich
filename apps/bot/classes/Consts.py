from enum import Enum


class Role(Enum):
    ADMIN = "администратор"
    CONFERENCE_ADMIN = "админ конфы"
    MODERATOR = "модератор"
    MINECRAFT = "майнкрафт"
    TERRARIA = "террария"
    STUDENT = "студент"
    MINECRAFT_NOTIFY = "уведомления майна"
    USER = "пользователь"
    BANNED = "забанен"
    TRUSTED = "доверенный"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


WEEK_TRANSLATOR = {
    'понедельник': 1, 'пн': 1,
    'вторник': 2, 'вт': 2,
    'среда': 3, 'ср': 3,
    'четверг': 4, 'чт': 4,
    'пятница': 5, 'пт': 5,
    'суббота': 6, 'сб': 6,
    'воскресенье': 7, 'воскресение': 7, 'вс': 7,
}

WEEK_TRANSLATOR_REVERT = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среда',
    4: 'четверг',
    5: 'пятница',
    6: 'суббота',
    7: 'воскресенье'
}

ON_OFF_TRANSLATOR = {
    'вкл': True,
    'on': True,
    '1': True,
    'true': True,
    'включить': True,
    'включи': True,
    'вруби': True,
    'подключи': True,

    'выкл': False,
    'off': False,
    '0': False,
    'false': False,
    'выключить': False,
    'выключи': False,
    'выруби': False,
    'отключи': False
}

TRUE_FALSE_TRANSLATOR = {
    True: 'вкл ✅',
    False: 'выкл ⛔'
}

WEATHER_TRANSLATOR = {
    'clear': 'Ясно ☀',
    'partly-cloudy': 'Малооблачно ⛅',
    'cloudy': 'Облачно с прояснениями 🌥',
    'overcast': 'Пасмурно ☁',
    'partly-cloudy-and-light-rain': 'Небольшой дождь 🌧',
    'partly-cloudy-and-rain': 'Дождь 🌧',
    'overcast-and-rain': 'Сильный дождь 🌧🌧',
    'overcast-thunderstorms-with-rain': 'Сильный дождь, гроза 🌩',
    'cloudy-and-light-rain': 'Небольшой дождь 🌧',
    'overcast-and-light-rain': 'Небольшой дождь 🌧',
    'cloudy-and-rain': 'Дождь 🌧',
    'overcast-and-wet-snow': 'Дождь со снегом 🌨',
    'partly-cloudy-and-light-snow': 'Небольшой снег 🌨',
    'partly-cloudy-and-snow': 'Снег 🌨',
    'overcast-and-snow': 'Снегопад 🌨',
    'cloudy-and-light-snow': 'Небольшой снег 🌨',
    'overcast-and-light-snow': 'Небольшой снег 🌨',
    'cloudy-and-snow': 'Снег 🌨'}

DAY_TRANSLATOR = {
    'night': 'ночь',
    'morning': 'утро',
    'day': 'день',
    'evening': 'вечер',
}

ATTACHMENT_TRANSLATOR = {
    'audio': 'аудио',
    'video': 'видео',
    'photo': 'фото',
    'doc': 'документ',
    'audio_message': 'голосовое'
}

BAD_ANSWERS = ['как же вы меня затрахали...',
               'ты обижаешь бота?',
               'тебе заняться нечем?',
               '...',
               'о боже, опять ты',
               'тебе не стыдно?',
               'зачем ты так?',
               'что я тебе сделал?',
               'чего ты добился?']
