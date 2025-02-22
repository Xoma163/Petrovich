from datetime import datetime

from apps.bot.api.timezonedb import TimezoneDB
from apps.bot.api.yandex.geo import YandexGeo
from apps.bot.classes.bots.tg_bot import TgBot
from apps.bot.classes.command import Command
from apps.bot.classes.const.consts import Platform, Role
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.classes.help_text import HelpText, HelpTextItem, HelpTextArgument
from apps.bot.classes.messages.attachments.photo import PhotoAttachment
from apps.bot.classes.messages.response_message import ResponseMessage, ResponseMessageItem
from apps.bot.models import Profile as ProfileModel
from apps.service.models import City, TimeZone


class Profile(Command):
    name = "профиль"

    help_text = HelpText(
        commands_text="позволяет управлять вашим профилем",
        help_texts=[
            HelpTextItem(Role.USER, [
                HelpTextArgument(None, "присылает информацию по вашему профилю"),
                HelpTextArgument(
                    "(имя, фамилия, логин/id, никнейм)",
                    "присылает информацию по профилю человека в конфе"),
                HelpTextArgument("город (название города)", "устанавливает новый город"),
                HelpTextArgument("город добавить (название города)", "добавляет новый город в базу"),
                HelpTextArgument("др (дата)", "устанавливает новый др"),
                HelpTextArgument("имя (имя)", "устанавливает новое имя"),
                HelpTextArgument("фамилия (фамилия)", "устанавливает новую фамилию"),
                HelpTextArgument("никнейм (никнейм)", "устанавливает новый никнейм"),
                HelpTextArgument("пол (мужской/женский)", "устанавливает новый пол"),
                HelpTextArgument("аватар", "обновляет аватар"),
                HelpTextArgument("аватар (изображение)", "обновляет аватар из вложения")
            ])
        ]
    )

    platforms = [Platform.TG]

    bot: TgBot

    def start(self) -> ResponseMessage:
        if self.event.message.args:
            arg0 = self.event.message.args[0]
        else:
            arg0 = None

        menu = [
            [["город"], self.menu_city],
            [["др", "дата"], self.menu_bd],
            [['ник', 'никнейм'], self.menu_nickname],
            [['имя'], self.menu_name],
            [['фамилия'], self.menu_surname],
            [['пол'], self.menu_gender],
            [['аватар'], self.menu_avatar],
            [['default'], self.menu_default],
        ]
        method = self.handle_menu(menu, arg0)
        rmi = method()
        return ResponseMessage(rmi)

    def menu_city(self) -> ResponseMessageItem:
        self.check_args(2)
        arg1 = self.event.message.args_case[1]
        if arg1 == 'добавить':
            city_name = " ".join(self.event.message.args_case[2:])
            city = self.add_city_to_db(city_name)
            answer = f"Добавил новый город - {city.name}"
            return ResponseMessageItem(text=answer)
        else:
            city_name = " ".join(self.event.message.args_case[1:])
            city = City.objects.filter(synonyms__icontains=city_name).first()
            if not city:
                raise PWarning(
                    "Не нашёл такого города.\n"
                    f"{self.bot.get_formatted_text_line('/профиль город добавить (название)')}"
                )
            self.event.sender.city = city
            self.event.sender.save()
            answer = f"Изменил город на {self.event.sender.city.name}"
            return ResponseMessageItem(text=answer)

    def menu_bd(self) -> ResponseMessageItem:
        self.check_args(2)
        birthday = self.event.message.args[1]

        show_birthday_year = True
        if birthday.count(".") == 1:
            birthday += ".1900"
            show_birthday_year = False
        try:
            date_time_obj = datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            raise PWarning("Не смог распарсить дату. Формат ДД.ММ.ГГГГ")

        self.event.sender.birthday = date_time_obj.date()
        self.event.sender.settings.show_birthday_year = show_birthday_year
        self.event.sender.save()

        new_bday = self.event.sender.birthday.strftime(
            '%d.%m.%Y') if show_birthday_year else self.event.sender.birthday.strftime('%d.%m')
        answer = f"Изменил дату рождения на {new_bday}"
        return ResponseMessageItem(text=answer)

    def menu_nickname(self) -> ResponseMessageItem:
        self.check_args(2)
        nickname = " ".join(self.event.message.args_case[1:])
        self.event.sender.nickname_real = nickname
        self.event.sender.save()
        answer = f"Изменил никнейм на {self.event.sender.nickname_real}"
        return ResponseMessageItem(text=answer)

    def menu_name(self) -> ResponseMessageItem:
        self.check_args(2)
        name = " ".join(self.event.message.args_case[1:])
        self.event.sender.name = name
        self.event.sender.save()
        answer = f"Изменил имя на {self.event.sender.name}"

        return ResponseMessageItem(text=answer)

    def menu_surname(self) -> ResponseMessageItem:
        self.check_args(2)
        surname = " ".join(self.event.message.args_case[1:])
        self.event.sender.surname = surname
        self.event.sender.save()
        answer = f"Изменил фамилию на {self.event.sender.surname}"
        return ResponseMessageItem(text=answer)

    def menu_gender(self) -> ResponseMessageItem:
        self.check_args(2)
        gender = self.event.message.args[1]
        if gender in ['мужской', 'м', 'муж']:
            gender_code = self.event.sender.GENDER_MALE
        elif gender in ['женский', 'ж', 'жен']:
            gender_code = self.event.sender.GENDER_FEMALE
        else:
            gender_code = self.event.sender.GENDER_NONE
        self.event.sender.gender = gender_code
        self.event.sender.save()
        answer = f"Изменил пол на {self.event.sender.get_gender_display()}"
        return ResponseMessageItem(text=answer)

    def menu_avatar(self) -> ResponseMessageItem:
        images = self.event.get_all_attachments([PhotoAttachment])
        if len(images) > 0:
            self.event.sender.set_avatar(images[0])
        else:
            if self.event.platform not in [Platform.TG]:
                raise PWarning("Обновление аватара по пользователю доступно только для ВК/ТГ")
            self.bot.update_profile_avatar(self.event.sender, self.event.user.user_id)
        answer = "Изменил аватарку"
        return ResponseMessageItem(text=answer)

    def menu_default(self) -> ResponseMessageItem:
        if self.event.message.args:
            self.check_conversation()
            profile = self.bot.get_profile_by_name(self.event.message.args, filter_chat=self.event.chat)
            return self.get_profile_info(profile)
        profile = self.event.sender
        return self.get_profile_info(profile)

    def get_profile_info(self, profile: ProfileModel) -> ResponseMessageItem:
        not_defined = "Не установлено"

        _city = profile.city or not_defined
        _bd = profile.birthday
        if profile.settings.celebrate_bday:
            if _bd:
                if not profile.settings.show_birthday_year:
                    _bd = _bd.strftime('%d.%m')
                else:
                    _bd = _bd.strftime('%d.%m.%Y')
            else:
                _bd = not_defined
        else:
            _bd = "Скрыто"
        _nickname = profile.nickname_real or not_defined
        _name = profile.name or not_defined
        _surname = profile.surname or not_defined

        roles = []
        for group in profile.groups.all():
            roles.append(Role[group.name])
        roles = sorted(roles)
        roles_str = ", ".join(roles)

        answer = \
            f"Имя: {_name}\n" \
            f"Фамилия: {_surname}\n" \
            f"Никнейм: {_nickname}\n" \
            f"Дата рождения: {_bd}\n" \
            f"Город: {_city}\n" \
            f"Пол: {profile.get_gender_display().capitalize()}\n\n" \
            f"Роли: {roles_str}"
        rmi = ResponseMessageItem(text=answer)

        if profile.avatar:
            attachment = self.bot.get_photo_attachment(profile.avatar.path, peer_id=self.event.peer_id,
                                                       filename="petrovich_user_avatar.png")
            rmi.attachments = [attachment]

        return rmi

    def add_city_to_db(self, city_name: str):
        city_name = city_name.capitalize()
        yandexgeo_api = YandexGeo(log_filter=self.event.log_filter)
        city_info = yandexgeo_api.get_city_info_by_name(city_name)
        if not city_info:
            raise PWarning("Не смог найти координаты для города")
        city_info['name'] = city_info['name'].replace('ё', 'е')
        city = City.objects.filter(name=city_info['name'])
        if len(city) != 0:
            return city.first()
        city_info['synonyms'] = city_info['name'].lower()
        timezonedb_api = TimezoneDB(log_filter=self.event.log_filter)
        timezone_name = timezonedb_api.get_timezone_by_coordinates(city_info['lat'], city_info['lon'])
        if not timezone_name:
            raise PWarning("Не смог найти таймзону для города")
        timezone_obj, _ = TimeZone.objects.get_or_create(name=timezone_name)

        city_info['timezone'] = timezone_obj
        city = City(**city_info)
        city.save()
        return city
