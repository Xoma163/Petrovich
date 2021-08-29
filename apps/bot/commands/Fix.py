from apps.bot.classes.Consts import Platform
from apps.bot.classes.Exceptions import PWarning
from apps.bot.classes.common.CommonCommand import CommonCommand

_eng_chars = u"~`!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?"
_rus_chars = u"ёё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"
_trans_table = dict(zip(_eng_chars, _rus_chars))
_trans_table_reverse = dict(zip(_rus_chars, _eng_chars))


def fix_layout(s):
    new_s = ""
    for letter in s:
        if letter in _trans_table:
            new_s += _trans_table[letter]
        elif letter in _trans_table_reverse:
            new_s += _trans_table_reverse[letter]
        else:
            new_s += letter
    return new_s


class Fix(CommonCommand):
    name = "фикс"
    names = ["раскладка"]
    help_text = "исправляет раскладку текста"
    help_texts = [
        "(Пересылаемые сообщения) - исправляет раскладку текста",
        "(текст) - исправляет раскладку текста"
    ]
    platforms = [Platform.VK, Platform.TG]
    args_or_fwd = 1

    def start(self):
        if self.event.args:
            msgs = fix_layout(self.event.original_args)
        else:
            msgs = ""
            for msg in self.event.fwd:
                if msg['text']:
                    msgs += f"{fix_layout(msg['text'])}"
            if not msgs:
                raise PWarning("Нет текста в сообщении или пересланных сообщениях")
        return msgs
