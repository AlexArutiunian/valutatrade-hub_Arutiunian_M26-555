# ValutaTrade Hub

Учебный консольный сервис для работы с валютным портфелем. Здесь есть регистрация и вход, покупка и продажа валют, просмотр портфеля, кэш курсов и отдельный сервис их обновления.

## Установка

```bash
uv sync
```

Для ExchangeRate-API задайте ключ:

```bash
export EXCHANGE_RATE_API_KEY="ваш_ключ"
```

Если ключа нет, приложение всё равно запускается. При обновлении этот источник будет пропущен, а остальные продолжат работу.

## Запуск

```bash
uv run valuta
```

или

```bash
make run
```

## Команды

```text
register <name> <password>
login <name> <password>
show-portfolio
buy <currency> <amount>
sell <currency> <amount>
get-rate <from> <to>
update-rates
show-rates
help
exit
```

Новый пользователь получает учебный баланс `1000 USD`. Значение можно поменять через `START_BALANCE_USD`.

Пример работы:

```text
register alex password123
login alex password123
show-portfolio
update-rates
get-rate USD BTC
buy BTC 0.0001
show-portfolio
sell BTC 0.00002
show-portfolio
```

Кэш курсов имеет TTL 3600 секунд по умолчанию. TTL можно изменить переменной окружения `RATES_TTL_SECONDS`. После истечения TTL операции `buy` и `sell` требуют выполнить `update-rates`. Свежесть хранится отдельно для каждой валюты, поэтому обновление одного источника не обновляет TTL остальных курсов.

## Курсы

`update-rates` использует ExchangeRate-API для обычных валют и CoinGecko для криптовалют. Текущие значения пишутся в `data/rates.json`, история - в `data/exchange_rates.json`.

Падение одного источника не останавливает остальные. Запись курсов идёт через временный файл с последующей заменой.

## Структура

```text
src/valutatrade_hub/
├── core/
│   ├── exceptions.py
│   ├── models.py
│   └── usecases.py
├── infra/
│   ├── database.py
│   ├── decorators.py
│   ├── logging_config.py
│   └── settings.py
├── parser_service/
│   ├── api_clients.py
│   ├── config.py
│   ├── storage.py
│   └── updater.py
├── cli/
│   └── interface.py
└── main.py

data/
├── users.json
├── portfolios.json
├── rates.json
└── exchange_rates.json
```

## Проверка

```bash
make lint
```

Короткий тест CLI:

```bash
./demo.sh
```

## Демонстрация

[Запись работы в Asciinema](https://asciinema.org/a/qMj3uPnjX26Z9yUk)
