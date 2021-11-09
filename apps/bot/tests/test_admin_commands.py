from django.contrib.auth.models import Group

from apps.bot.classes.consts.Consts import Role
from apps.bot.commands.AdminCommands.Ban import Ban
from apps.bot.commands.AdminCommands.DeBan import DeBan
from apps.bot.commands.AdminCommands.Flood import Flood
from apps.bot.commands.AdminCommands.Linux import Linux
from apps.bot.commands.AdminCommands.Restart import Restart
from apps.bot.models import User
from apps.bot.tests.BotInitializer import BotInitializer


class CommandBanTestCase(BotInitializer):
    Command = Ban

    def test_ban_admin(self):
        group_admin = Group.objects.get(name=Role.ADMIN.name)
        profile_ivan = User.objects.get(user_id=2).profile
        profile_ivan.groups.add(group_admin)
        self.check_correct_pwarning()

    def test_ban_user(self):
        self.event.set_message("Бан Иван")
        self.check_correct_answer()
        role_banned = Group.objects.get(name=Role.BANNED.name)
        profile_ivan = User.objects.get(user_id=2).profile
        self.assertTrue(profile_ivan.check_role(role_banned))

    def test_no_access(self):
        group_admin = Group.objects.get(name=Role.ADMIN.name)
        self.event.sender.groups.remove(group_admin)
        self.event.sender.save()
        self.event.set_message("Бан Иван")
        self.check_correct_pwarning()

    def test_no_args(self):
        self.check_correct_pwarning()


class CommandDeBanTestCase(BotInitializer):
    Command = DeBan

    def test_deban_user(self):
        profile_ivan = User.objects.get(user_id=2).profile
        role_banned = Group.objects.get(name=Role.BANNED.name)
        profile_ivan.groups.add(role_banned)
        self.event.set_message("Бан Иван")
        self.check_correct_answer()
        self.assertFalse(profile_ivan.check_role(role_banned))

    def test_no_access(self):
        group_admin = Group.objects.get(name=Role.ADMIN.name)
        self.event.sender.groups.remove(group_admin)
        self.event.sender.save()
        self.event.set_message("Разбан Иван")
        self.check_correct_pwarning()

    def test_no_args(self):
        self.check_correct_pwarning()


class CommandFloodTestCase(BotInitializer):
    Command = Flood

    def test_flood(self):
        n = 10
        self.event.set_message(f"Флуд {n}")

        answer = self.check_correct_answer()
        if len(answer) != n:
            self.fail()


class CommandLinuxTestCase(BotInitializer):
    Command = Linux


class CommandRestartTestCase(BotInitializer):
    Command = Restart
