import re


class Message:
    def __init__(self, raw_str):
        """
        raw - исходная строка
        clear - произведены замены ',' на пробел, переведено в нижний регистр, ё->е

        command - команда
        args_str - аргументы строкой
        args - аргументы списком
        """
        self.raw = raw_str
        self.clear = self.get_cleared_message(self.raw)
        msg_split = self.clear.split(' ', 1)

        self.command = msg_split[0].lower()
        self.args_str = msg_split[1]
        self.args = self.args_str.split(' ')

    @staticmethod
    def get_cleared_message(msg):
        clear_msg = msg.lower()
        clear_msg = clear_msg.replace(',', ' ')
        clear_msg = re.sub(" +", " ", clear_msg)
        # clear_msg = re.sub(",+", ",", clear_msg)
        clear_msg = clear_msg.strip().strip(',').strip().strip(' ').strip()
        clear_msg = clear_msg.replace('ё', 'е')
        return clear_msg
