"""Интерфейс командной строки"""

import shlex

from prettytable import PrettyTable

from valutatrade_hub.core.exceptions import ValutaTradeError
from valutatrade_hub.core.usecases import buy, get_rate, login, register, sell
from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.parser_service.updater import RatesUpdater

HELP = """Команды:
  register <name> <password>
  login <name> <password>
  show-portfolio
  buy <currency> <amount>
  sell <currency> <amount>
  get-rate <from> <to>
  update-rates
  show-rates
  help
  exit"""


class Interface:
    """Обрабатывает команды пользователя"""

    def __init__(self):
        self.user = None

    def run(self) -> None:
        """Запускает интерактивный режим"""
        print("ValutaTrade Hub")
        print('Введите "help" для списка команд')

        while True:
            try:
                raw = input("valuta> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return

            if raw:
                self.execute(raw)

    def execute(self, raw: str) -> None:
        """Выполняет одну команду"""
        try:
            args = shlex.split(raw)
            command = args.pop(0).lower()
            handler = getattr(self, f"cmd_{command.replace('-', '_')}", None)

            if handler is None:
                print('Неизвестная команда. Введите "help"')
                return

            handler(args)
        except (ValutaTradeError, ValueError) as error:
            print(f"Ошибка: {error}")

    def cmd_register(self, args: list[str]) -> None:
        """Регистрирует пользователя"""
        self._need_args(args, 2, "register <name> <password>")
        user = register(args[0], args[1])
        print(f"Пользователь {user.username} зарегистрирован")

    def cmd_login(self, args: list[str]) -> None:
        """Выполняет вход"""
        self._need_args(args, 2, "login <name> <password>")
        self.user = login(args[0], args[1])
        print(f"Вход выполнен: {self.user.username}")

    def cmd_show_portfolio(self, args: list[str]) -> None:
        """Показывает портфель"""
        self._need_args(args, 0, "show-portfolio")
        portfolio = self._portfolio()

        table = PrettyTable(["Валюта", "Баланс"])
        for code, wallet in sorted(portfolio.wallets.items()):
            table.add_row([code, f"{wallet.balance:.8g}"])
        print(table)

        try:
            total = portfolio.get_total_value()
            print(f"Итого: ${total:.2f}")
        except ValueError as error:
            print(f"Итого не рассчитано: {error}")

    def cmd_buy(self, args: list[str]) -> None:
        """Покупает валюту"""
        self._need_args(args, 2, "buy <currency> <amount>")
        cost = buy(self._portfolio(), args[0], float(args[1]))
        print(f"Покупка выполнена, списано ${cost:.2f}")

    def cmd_sell(self, args: list[str]) -> None:
        """Продаёт валюту"""
        self._need_args(args, 2, "sell <currency> <amount>")
        revenue = sell(self._portfolio(), args[0], float(args[1]))
        print(f"Продажа выполнена, получено ${revenue:.2f}")

    def cmd_get_rate(self, args: list[str]) -> None:
        """Показывает курс валют"""
        self._need_args(args, 2, "get-rate <from> <to>")
        rate, stale = get_rate(args[0], args[1])
        print(f"1 {args[0].upper()} = {rate:.8g} {args[1].upper()}")

        if stale:
            print("Кэш устарел, рекомендуется update-rates")

    def cmd_update_rates(self, args: list[str]) -> None:
        """Обновляет кэш курсов"""
        self._need_args(args, 0, "update-rates")
        result = RatesUpdater().run_update()
        print(f"Курсы обновлены: {len(result['data']['rates'])}")

        for error in result["errors"]:
            print(f"Источник пропущен: {error}")

    def cmd_show_rates(self, args: list[str]) -> None:
        """Показывает курсы из кэша"""
        self._need_args(args, 0, "show-rates")
        data = DatabaseManager().load_rates()

        table = PrettyTable(["Валюта", "За 1 USD"])
        for code, rate in sorted(data.get("rates", {}).items()):
            table.add_row([code, f"{float(rate):.8g}"])
        print(table)
        print(f"Обновлено: {data.get('updated_at') or 'ещё не обновлялось'}")

    def cmd_help(self, args: list[str]) -> None:
        """Показывает список команд"""
        self._need_args(args, 0, "help")
        print(HELP)

    def cmd_exit(self, args: list[str]) -> None:
        """Завершает программу"""
        self._need_args(args, 0, "exit")
        raise SystemExit

    def _portfolio(self):
        if self.user is None:
            raise ValueError("Сначала выполните login")
        return DatabaseManager().load_portfolio(self.user)

    @staticmethod
    def _need_args(args: list[str], count: int, usage: str) -> None:
        if len(args) != count:
            raise ValueError(f"Использование: {usage}")
