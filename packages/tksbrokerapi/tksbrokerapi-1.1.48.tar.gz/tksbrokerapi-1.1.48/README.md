# TKSBrokerAPI

**[TKSBrokerAPI](https://github.com/Tim55667757/TKSBrokerAPI)** — это python API для работы с Tinkoff Open API и доступа к торговому серверу брокера [Тинькофф Инвестиции](http://tinkoff.ru/sl/AaX1Et1omnH) через REST протокол. С модулем TKSBrokerAPI можно работать в консоли, используя богатую систему команд, и, как обычно, через `python import`. TKSBrokerAPI позволяет автоматизировать рутинные торговые операции и реализовать ваши торговые сценарии, либо только получать нужную информацию от брокера. Его достаточно просто встроить в системы автоматизации CI/CD.

[![Build Status](https://travis-ci.com/Tim55667757/TKSBrokerAPI.svg?branch=master)](https://travis-ci.com/Tim55667757/TKSBrokerAPI)
[![pypi](https://img.shields.io/pypi/v/TKSBrokerAPI.svg)](https://pypi.python.org/pypi/TKSBrokerAPI)
[![license](https://img.shields.io/pypi/l/TKSBrokerAPI.svg)](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/LICENSE)
[![en-doc](https://badgen.net/badge/english/readme/pink)](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/README_EN.md)
[![api-doc](https://badgen.net/badge/api-doc/TKSBrokerAPI/blue)](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html)
[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20TKSBrokerAPI&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FTKSBrokerAPI%2F&quickpay=shop&account=410015019068268)

❗ Если вам не хватает какой-то возможности программы или какого-то конкретного примера в документации для понимания работы модуля TKSBrokerAPI (в консоли или как python API), то опишите ваш случай в разделе 👉 [**Issues**](https://github.com/Tim55667757/TKSBrokerAPI/issues/new) 👈, пожалуйста. По мере возможности постараемся реализовать нужную функциональность и добавить примеры в очередном релизе.

**Полезные ссылки**

* 📚 [Документация и примеры на английском (documentation and examples in english here)](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/README_EN.md)
  * ⚙ [Автоматическая API-документация на английском для модуля TKSBrokerAPI (API documentation here)](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html)
  * 🇺🇸 [Релиз-ноты на английском](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/CHANGELOG_EN.md)
  * 🇷🇺 [Релиз-ноты на русском](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/CHANGELOG.md)
    * 💡 [Все запланированные релизы и вошедшие в них фичи](https://github.com/Tim55667757/TKSBrokerAPI/milestones?direction=desc&sort=title&state=open)
    * 📂 [Все открытые задачи в беклоге](https://github.com/Tim55667757/TKSBrokerAPI/issues?q=is%3Aissue+is%3Aopen+sort%3Acreated-asc)
* 🎁 Поддержать проект донатом на ЮМани-кошелёк: [410015019068268](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20TKSBrokerAPI&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FTKSBrokerAPI%2F&quickpay=shop&account=410015019068268)

**Содержание документации**

1. [Введение](#Введение)
   - [Основные возможности](#Основные-возможности)
2. [Как установить](#Как-установить)
3. [Аутентификация](#Аутентификация)
   - [Токен](#Токен)
   - [Идентификатор счёта пользователя](#Идентификатор-счёта-пользователя)
4. [Примеры использования](#Примеры-использования)
   - [Из командной строки](#Из-командной-строки)
     - [Получить справку по ключам](#Получить-справку-по-ключам)
     - [Получить список всех доступных для торговли инструментов](#Получить-список-всех-доступных-для-торговли-инструментов)
     - [Получить информацию по инструменту](#Получить-информацию-по-инструменту)
     - [Запросить стакан цен с заданной глубиной](#Запросить-стакан-цен-с-заданной-глубиной)
     - [Запросить таблицу последних актуальных цен для списка инструментов](#Запросить-таблицу-последних-актуальных-цен-для-списка-инструментов)
     - [Получить текущий портфель пользователя и статистику распределения активов](#Получить-текущий-портфель-пользователя-и-статистику-распределения-активов)
     - [Получить отчёт по операциям с портфелем за указанный период](#Получить-отчёт-по-операциям-с-портфелем-за-указанный-период)
     - [Совершить сделку по рынку](#Совершить-сделку-по-рынку)
     - [Открыть отложенный лимитный или стоп-ордер](#Открыть-отложенный-лимитный-или-стоп-ордер)
     - [Отменить ордера и закрыть позиции](#Отменить-ордера-и-закрыть-позиции)
   - [Как python API через импорт модуля TKSBrokerAPI](#Как-python-API-через-импорт-модуля-TKSBrokerAPI)
     - [Пример реализации абстрактного сценария](#Пример-реализации-абстрактного-сценария)


## Введение

Если вы занимаетесь одновременно инвестированием, автоматизацией и алгоритмической торговлей, то наверняка слышали про [Tinkoff Open API](https://tinkoff.github.io/investAPI/) (к нему есть неплохая [Swagger-документация](https://tinkoff.github.io/investAPI/swagger-ui/)) — это API, предоставляемое брокером Тинькофф Инвестиции для автоматизации работы биржевых торговых роботов. Если ещё не слышали, то можете завести себе аккаунт [по ссылке](http://tinkoff.ru/sl/AaX1Et1omnH) и протестировать его возможности сами.

При работе с любыми API, всегда возникают технические трудности: высокий порог вхождения, необходимость в изучении документации, написание и отладка кода для выполнения сетевых запросов по формату API. Пройдёт много времени, прежде чем у вас дойдёт дело до реализации торгового алгоритма.

**[TKSBrokerAPI](https://github.com/Tim55667757/TKSBrokerAPI)** — это более простой инструмент, который можно использовать как обычный python-модуль или запускать из командной строки, и сразу из коробки получить возможность работать со счётом у брокера Тинькофф Инвестиции: получать информацию о состоянии портфеля, включая элементарную аналитику, открывать и закрывать позиции, получать общую информацию о торгуемых на бирже инструментах, запрашивать цены и получать отчёты об операциях за указанный период. Все данные выводятся сразу в консоль: в текстовом виде или сохраняются в файлах формата Markdown.

<details>
  <summary>Пример запроса клиентского портфеля и вывод информации в консоль</summary>

```commandline
$ tksbrokerapi --overview

TKSBrokerAPI.py     L:1726 INFO    [2022-07-26 12:43:12,279] Statistics of client's portfolio:
# Client's portfolio

* **Actual date:** [2022-07-26 09:43:12] (UTC)
* **Portfolio cost:** 19835.73 RUB
* **Changes:** +415.14 RUB (+2.05%)

## Open positions

| Ticker [FIGI]               | Volume (blocked)                | Lots     | Curr. price  | Avg. price   | Current volume cost | Profit (%)
|-----------------------------|---------------------------------|----------|--------------|--------------|---------------------|----------------------
| Ruble                       |                90.96 (0.30) rub |          |              |              |                     |
|                             |                                 |          |              |              |                     |
| **Currencies:**             |                                 |          |              |              |         9159.71 RUB |
| EUR_RUB__TOM [BBG0013HJJ31] |                 6.29 (0.00) eur | 0.0063   |    59.35 rub |    56.11 rub |          373.31 rub | +22.80 rub (+5.76%)
| CNYRUB_TOM [BBG0013HRTL0]   |                23.00 (0.00) cny | 0.0230   |     8.78 rub |     8.92 rub |          201.95 rub | -3.20 rub (-1.56%)
| CHFRUB_TOM [BBG0013HQ5K4]   |                 1.00 (0.00) chf | 0.0010   |    60.54 rub |    64.00 rub |           60.54 rub | -3.46 rub (-5.41%)
| GBPRUB_TOM [BBG0013HQ5F0]   |                 2.00 (0.00) gbp | 0.0020   |    72.80 rub |    90.10 rub |          145.59 rub | -34.61 rub (-19.21%)
| TRYRUB_TOM [BBG0013J12N1]   |                 1.00 (0.00) try | 0.0010   |     3.26 rub |     4.75 rub |            3.26 rub | -1.50 rub (-31.55%)
| USD000UTSTOM [BBG0013HGFT4] |               143.03 (0.00) usd | 0.1430   |    58.50 rub |    55.88 rub |         8367.25 rub | +395.68 rub (+4.96%)
| HKDRUB_TOM [BBG0013HSW87]   |                 1.00 (0.00) hkd | 0.0010   |     7.79 rub |    11.46 rub |            7.79 rub | -3.67 rub (-32.02%)
|                             |                                 |          |              |              |                     |
| **Stocks:**                 |                                 |          |              |              |          905.80 RUB |
| POSI [TCS00A103X66]         |                           1 (1) | 1        |   905.80 rub |   906.80 rub |          905.80 rub | -1.00 rub (-0.11%)
|                             |                                 |          |              |              |                     |
| **Bonds:**                  |                                 |          |              |              |         3024.30 RUB |
| RU000A101YV8 [TCS00A101YV8] |                           3 (0) | 3        |  1008.10 rub |  1004.40 rub |         3024.30 rub | +11.10 rub (+0.37%)
|                             |                                 |          |              |              |                     |
| **Etfs:**                   |                                 |          |              |              |         6654.96 RUB |
| TGLD [BBG222222222]         |                        1600 (0) | 16       |     0.07 usd |     0.07 usd |          113.76 usd | -3.63 usd (-3.09%)
|                             |                                 |          |              |              |                     |
| **Futures:** no trades      |                                 |          |              |              |                     |

## Opened pending limit-orders: 1

| Ticker [FIGI]               | Order ID       | Lots (exec.) | Current price (% delta) | Target price  | Action    | Type      | Create date (UTC)
|-----------------------------|----------------|--------------|-------------------------|---------------|-----------|-----------|---------------------
| POSI [TCS00A103X66]         | ***********    | 1 (0)        |     905.80 rub (-9.33%) |    999.00 rub | ↓ Sell    | Limit     | 2022-07-26 12:43:05

## Opened stop-orders: 2

| Ticker [FIGI]               | Stop order ID                        | Lots   | Current price (% delta) | Target price  | Limit price   | Action    | Type        | Expire type  | Create date (UTC)   | Expiration (UTC)
|-----------------------------|--------------------------------------|--------|-------------------------|---------------|---------------|-----------|-------------|--------------|---------------------|---------------------
| POSI [TCS00A103X66]         | ********-****-****-****-************ | 1      |     905.80 rub (-9.42%) |   1000.00 rub |        Market | ↓ Sell    | Take profit | Until cancel | 2022-07-26 08:58:02 | Undefined
| IBM [BBG000BLNNH6]          | ********-****-****-****-************ | 1      |         N/A usd (0.00%) |    135.00 usd |        Market | ↓ Sell    | Take profit | Until cancel | 2022-07-26 09:38:44 | Undefined

# Analytics

* **Current total portfolio cost:** 19835.73 RUB
* **Changes:** +415.14 RUB (+2.05%)

## Portfolio distribution by assets

| Type       | Uniques | Percent | Current cost
|------------|---------|---------|-----------------
| Ruble      | 1       | 0.46%   | 90.96 rub
| Currencies | 7       | 46.18%  | 9159.71 rub
| Shares     | 1       | 4.57%   | 905.80 rub
| Bonds      | 1       | 15.25%  | 3024.30 rub
| Etfs       | 1       | 33.55%  | 6654.96 rub

## Portfolio distribution by companies

| Company                                     | Percent | Current cost
|---------------------------------------------|---------|-----------------
| All money cash                              | 46.64%  | 9250.67 rub
| [POSI] Positive Technologies                | 4.57%   | 905.80 rub
| [RU000A101YV8] Позитив Текнолоджиз выпуск 1 | 15.25%  | 3024.30 rub
| [TGLD] Тинькофф Золото                      | 33.55%  | 6654.96 rub

## Portfolio distribution by sectors

| Sector         | Percent | Current cost
|----------------|---------|-----------------
| All money cash | 46.64%  | 9250.67 rub
| it             | 19.81%  | 3930.10 rub
| other          | 33.55%  | 6654.96 rub

## Portfolio distribution by currencies

| Instruments currencies   | Percent | Current cost
|--------------------------|---------|-----------------
| [rub] Российский рубль   | 20.27%  | 4021.06 rub
| [usd] Доллар США         | 75.73%  | 15022.22 rub
| [eur] Евро               | 1.88%   | 373.33 rub
| [cny] Юань               | 1.02%   | 201.95 rub
| [chf] Швейцарский франк  | 0.31%   | 60.54 rub
| [gbp] Фунт стерлингов    | 0.73%   | 145.59 rub
| [try] Турецкая лира      | 0.02%   | 3.26 rub
| [hkd] Гонконгский доллар | 0.04%   | 7.79 rub

TKSBrokerAPI.py     L:1732 INFO    [2022-07-26 12:43:12,303] Client's portfolio is saved to file: [overview.md]
```

</details>

TKSBrokerAPI позволяет автоматизировать рутинные торговые операции и реализовать ваши торговые сценарии, либо только получать нужную информацию от брокера. Благодаря богатой системе консольных команд его достаточно просто встроить в системы автоматизации CI/CD.

В будущем, на основе этого модуля, сюда в опенсорс будут выложены готовые торговые сценарии и шаблоны для написания собственных сценариев на языке Python.

### Основные возможности

На момент последнего актуального релиза инструмент TKSBrokerAPI умеет:

- Получать с сервера брокера список всех доступных для указанного аккаунта инструментов: валют, акций, облигаций, фондов и фьючерсов;
  - ключ `--list` или `-l`;
  - API-метод: [`Listing()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Listing).
- Запрашивать у брокера информацию об инструменте, зная его тикер или идентификатор FIGI;
  - ключ `--info` или `-i`;
  - API-методы: [`SearchByTicker()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.SearchByTicker), [`SearchByFIGI()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.SearchByFIGI) и [`ShowInstrumentInfo()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.ShowInstrumentInfo).
- Запрашивать у брокера стакан актуальных биржевых цен для указанного по тикеру или FIGI инструмента, при этом можно указать глубину стакана;
  - ключ `--price` совместно с ключом `--depth`;
  - API-метод: [`GetCurrentPrices()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.GetCurrentPrices).
- Получать с сервера брокера таблицу последних цен;
  - ключ `--prices` с перечислением списка интересующих инструментов;
  - API-метод: [`GetListOfPrices()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.GetListOfPrices).
- Получать информацию о состоянии портфеля пользователя и аналитику по нему: распределение портфеля по активам, компаниям, секторам и валютам активов;
  - ключ `--overview` или `-o`;
  - API-метод: [`Overview()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Overview).
- Получать с сервера брокера информацию о совершённых сделках за указанный период и представлять её в табличном виде;
  - ключ `--deals` или `-d`;
  - API-метод: [`Deals()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Deals).
- Совершать сделки по рынку, покупая или продавая активы в стакане, удовлетворяя имеющиеся заявки от продавцов или покупателей;
  - общий ключ `--trade` и дополнительные ключи: `--buy`, `--sell`;
  - API-методы: [`Trade()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Trade), [`Buy()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Buy) и [`Sell()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Sell).
- Открывать ордера любого типа: отложенные лимитные, действующие в пределах одной торговой сессии, и стоп-ордера, которые могут действовать до отмены или до указанной даты;
  - общий ключ `--order` и дополнительные ключи: `--buy-limit`, `--sell-limit`, `--buy-stop`, `--sell-stop`;
  - API-методы: [`Order()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.Order), [`BuyLimit()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.BuyLimit), [`SellLimit()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.SellLimit), [`BuyStop()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.BuyStop) и [`SellStop()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.SellStop).
- Закрывать открытые ранее ордера или списки ордеров любого типа по их ID;
  - ключи `--close-order` или `--cancel-order`, `--close-orders` или `--cancel-orders`;
  - API-метод: [`CloseOrders()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.CloseOrders).
- Закрывать ранее открытые позиции полностью (кроме заблокированных объёмов), указав конкретный инструмент или список инструментов через их тикеры или FIGI;
  - ключ `--close-trade` или `--cancel-trade`;
  - API-метод: [`CloseTrades()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.CloseTrades).
- Отменять все открытые ранее ордера и закрывать текущие позиции по всем инструментам сразу, кроме заблокированных объёмов и позиций по валютам, которые необходимо закрывать отдельно;
  - ключ `--close-all`, также можно конкретизировать ордера, тип актива или указать через пробел сразу несколько ключевых слов после ключа `--close-all`: `orders`, `shares`, `bonds`, `etfs` или `futures`;
  - API-методы: [`CloseAll()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.CloseAll), [`CloseAllOrders()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.CloseAllOrders) и [`CloseAllTrades()`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.CloseAllTrades).


## Как установить

Проще всего использовать установку через PyPI:

```commandline
pip install tksbrokerapi
```

После этого можно проверить установку командой:

```commandline
pip show tksbrokerapi
```

Также можно использовать модуль TKSBrokerAPI, скачав его напрямую из [репозитория](https://github.com/Tim55667757/TKSBrokerAPI/) через `git clone` и взяв кодовую базу любого протестированного [релиза](https://github.com/Tim55667757/TKSBrokerAPI/releases).

В первом случае инструмент будет доступен в консоли через команду `tksbrokerapi`, а во втором случае вам придётся запускать его как обычный python-скрипт, через `python TKSBrokerAPI.py` из каталога с исходным кодом.

Далее все примеры написаны для случая, когда TKSBrokerAPI установлен через PyPI.


## Аутентификация

### Токен

Сервис TINKOFF INVEST API использует для аутентификации токен. Токен — это набор символов, в котором зашифрованы данные о владельце, правах доступ и прочая информация, необходимая для авторизации в сервисе. Токен необходимо передавать на сервер с каждым сетевым запросом.

Модуль TKSBrokerAPI берёт всю работу с токенами на себя. Есть три варианта задания токена пользователя:

- при вызове `tksbrokerapi` в консоли укажите ключ: `--token "your_token_here"`;
- либо укажите `token` при инициализации класса в python-скрипте: [`TKSBrokerAPI.TinkoffBrokerServer(token="your_token_here", ...)`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.__init__);
- или же можно заранее установить специальную переменную в пользовательском окружении: `TKS_API_TOKEN=your_token_here`.

❗ **Работа с TINKOFF INVEST API без выпуска и использования токена невозможна**. До начала работы с модулем TKSBrokerAPI, пожалуйста, откройте по ссылке [брокерский счёт в Тинькофф Инвестиции](http://tinkoff.ru/sl/AaX1Et1omnH), а затем выберете нужный вам вид токена и создайте его, как указано по ссылке [в официальной документации](https://tinkoff.github.io/investAPI/token/).

❗ **Важное замечание**: никогда и никому не передавайте свои токены, не используйте их в примерах, а также не сохраняйте их в пабликах и в коде. Токеном может воспользоваться кто угодно, но все операции у брокера будут отображаться от вашего имени. Если вы хотите использовать свои токены для автоматизации в CI/CD-системах, то обязательно пользуйтесь сокрытием переменных окружения ([пример](https://docs.travis-ci.com/user/environment-variables/#defining-variables-in-repository-settings) установки "hidden variables" для Travis CI, и [пример](https://docs.gitlab.com/ee/ci/variables/#protected-cicd-variables) установки "protected variables" для GitLab CI).

### Идентификатор счёта пользователя

Второй важный параметр для работы TKSBrokerAPI — это числовой идентификатор счёта пользователя. Он не является обязательным, но без его указания будет невозможно выполнить многие операции через API, логически завязанные на конкретного пользователя (посмотреть портфель по брокерскому счёту, выполнить торговые операции и многие другие). Вы можете найти это число в любом брокерском отчёте, которые можно заказать либо из мобильного приложения Тинькофф Инвестиции, либо в личном кабинете на их сайте. Обычно идентификатор счёта пользователя находится сверху, в "шапке" отчётов. Также можно узнать этот номер спросив в чате техподдержки Тинькофф Инвестиции.

Есть три варианта задания идентификатора счёта пользователя:

- при вызове `tksbrokerapi` в консоли укажите ключ: `--account-id your_id_number"`;
- либо укажите `accountId` при инициализации класса в python-скрипте: [`TKSBrokerAPI.TinkoffBrokerServer(token="...", accountId=your_id_number, ...)`](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html#TinkoffBrokerServer.__init__);
- или же можно заранее установить специальную переменную в пользовательском окружении: `TKS_ACCOUNT_ID=your_id_number`.


## Примеры использования

Далее рассмотрим некоторые сценарии использования модуля TKSBrokerAPI: при его запуске в консоли или как python-скрипт.

❗ По умолчанию в консоль выводится информация уровня `INFO`. В случае возникновения каких-либо ошибок, рекомендуется повысить уровень логирования до `DEBUG`. Для этого укажите вместе с командой любой из ключей: `--debug-level=10`, `--verbosity=10` или `-v 10`. После этого скопируйте логи с проблемой и создайте новый баг в разделе 👉 [**Issues**](https://github.com/Tim55667757/TKSBrokerAPI/issues/new) 👈, пожалуйста.

Также информация уровня `DEBUG` всегда выводится в служебный файл `TKSBrokerAPI.log` (он создаётся в рабочей директории, где происходит вызов `tksbrokerapi` или скрипта `python TKSBrokerAPI.py`).

### Из командной строки

При запуске программы в консоли можно указать множество параметров и выполнить одно действие. Формат любых команд следующий:

```commandline
tksbrokerapi [необязательные ключи и параметры] [одно действие]
```

❗ Для выполнения большинства команд вы должны каждый раз указывать свой токен через ключ `--token` и идентификатор пользователя через ключ `--account-id`, либо один раз установить их через переменные окружения `TKS_API_TOKEN` и `TKS_ACCOUNT_ID` (см. раздел ["Аутентификация"](#Аутентификация)).

*Примечание: в примерах ниже токен доступа и ID счёта были заранее заданы через переменные окружения `TKS_API_TOKEN` и `TKS_ACCOUNT_ID`, поэтому ключи `--token` и `--account-id` не фигурируют в логах.*

#### Получить справку по ключам

Используется ключ `--help` (`-h`), действие не указывается. В консоль будет выведен актуальный для данного релиза список ключей и их краткое описание.

<details>
  <summary>Команда для вывода внутренней справки по работе с ключами</summary>

```commandline
tksbrokerapi --help
```

Вывод:

```text
usage: python TKSBrokerAPI.py [some options] [one command]

TKSBrokerAPI is a python API to work with some methods of Tinkoff Open API
using REST protocol. It can view history, orders and market information. Also,
you can open orders and trades. See examples:
https://tim55667757.github.io/TKSBrokerAPI/#Usage-examples

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         Option: Tinkoff service's api key. If not set then
                        used environment variable `TKS_API_TOKEN`. See how to
                        use: https://tinkoff.github.io/investAPI/token/
  --account-id ACCOUNT_ID
                        Option: string with an user numeric account ID in
                        Tinkoff Broker. It can be found in any broker's
                        reports (see the contract number). Also, this variable
                        can be set from environment variable `TKS_ACCOUNT_ID`.
  --ticker TICKER, -t TICKER
                        Option: instrument's ticker, e.g. `IBM`, `YNDX`,
                        `GOOGL` etc. Use alias for `USD000UTSTOM` simple as
                        `USD`, `EUR_RUB__TOM` as `EUR`.
  --figi FIGI, -f FIGI  Option: instrument's FIGI, e.g. `BBG006L8G4H1` (for
                        `YNDX`).
  --depth DEPTH         Option: Depth of Market (DOM) can be >=1, 1 by
                        default.
  --output OUTPUT       Option: replace default paths to output files for some
                        commands. If None then used default files.
  --debug-level DEBUG_LEVEL, --verbosity DEBUG_LEVEL, -v DEBUG_LEVEL
                        Option: showing STDOUT messages of minimal debug
                        level, e.g. 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 =
                        ERROR, 50 = CRITICAL. INFO (20) by default.
  --list, -l            Action: get and print all available instruments and
                        some information from broker server. Also, you can
                        define --output key to save list of instruments to
                        file, default: instruments.md.
  --info, -i            Action: get information from broker server about
                        instrument by it's ticker or FIGI. `--ticker` key or
                        `--figi` key must be defined!
  --price               Action: show actual price list for current instrument.
                        Also, you can use --depth key. `--ticker` key or
                        `--figi` key must be defined!
  --prices PRICES [PRICES ...], -p PRICES [PRICES ...]
                        Action: get and print current prices for list of given
                        instruments (by it's tickers or by FIGIs. WARNING!
                        This is too long operation if you request a lot of
                        instruments! Also, you can define --output key to save
                        list of prices to file, default: prices.md.
  --overview, -o        Action: show all open positions, orders and some
                        statistics. Also, you can define --output key to save
                        this information to file, default: overview.md.
  --deals [DEALS [DEALS ...]], -d [DEALS [DEALS ...]]
                        Action: show all deals between two given dates. Start
                        day may be an integer number: -1, -2, -3 days ago.
                        Also, you can use keywords: `today`, `yesterday` (-1),
                        `week` (-7), `month` (-30), `year` (-365). Dates
                        format must be: `%Y-%m-%d`, e.g. 2020-02-03. Also, you
                        can define `--output` key to save all deals to file,
                        default: report.md.
  --trade [TRADE [TRADE ...]]
                        Action: universal action to open market position for
                        defined ticker or FIGI. You must specify 1-5
                        parameters: [direction `Buy` or `Sell] [lots, >= 1]
                        [take profit, >= 0] [stop loss, >= 0] [expiration date
                        for TP/SL orders, Undefined|`%Y-%m-%d %H:%M:%S`]. See
                        examples in readme.
  --buy [BUY [BUY ...]]
                        Action: immediately open BUY market position at the
                        current price for defined ticker or FIGI. You must
                        specify 0-4 parameters: [lots, >= 1] [take profit, >=
                        0] [stop loss, >= 0] [expiration date for TP/SL
                        orders, Undefined|`%Y-%m-%d %H:%M:%S`].
  --sell [SELL [SELL ...]]
                        Action: immediately open SELL market position at the
                        current price for defined ticker or FIGI. You must
                        specify 0-4 parameters: [lots, >= 1] [take profit, >=
                        0] [stop loss, >= 0] [expiration date for TP/SL
                        orders, Undefined|`%Y-%m-%d %H:%M:%S`].
  --order [ORDER [ORDER ...]]
                        Action: universal action to open limit or stop-order
                        in any directions. You must specify 4-7 parameters:
                        [direction `Buy` or `Sell] [order type `Limit` or
                        `Stop`] [lots] [target price] [maybe for stop-order:
                        [limit price, >= 0] [stop type, Limit|SL|TP]
                        [expiration date, Undefined|`%Y-%m-%d %H:%M:%S`]]. See
                        examples in readme.
  --buy-limit BUY_LIMIT BUY_LIMIT
                        Action: open pending BUY limit-order (below current
                        price). You must specify only 2 parameters: [lots]
                        [target price] to open BUY limit-order. If you try to
                        create `Buy` limit-order above current price then
                        broker immediately open `Buy` market order, such as if
                        you do simple `--buy` operation!
  --sell-limit SELL_LIMIT SELL_LIMIT
                        Action: open pending SELL limit-order (above current
                        price). You must specify only 2 parameters: [lots]
                        [target price] to open SELL limit-order. If you try to
                        create `Sell` limit-order below current price then
                        broker immediately open `Sell` market order, such as
                        if you do simple `--sell` operation!
  --buy-stop [BUY_STOP [BUY_STOP ...]]
                        Action: open BUY stop-order. You must specify at least
                        2 parameters: [lots] [target price] to open BUY stop-
                        order. In additional you can specify 3 parameters for
                        stop-order: [limit price, >= 0] [stop type,
                        Limit|SL|TP] [expiration date, Undefined|`%Y-%m-%d
                        %H:%M:%S`]. When current price will go up or down to
                        target price value then broker opens a limit order.
                        Stop loss order always executed by market price.
  --sell-stop [SELL_STOP [SELL_STOP ...]]
                        Action: open SELL stop-order. You must specify at
                        least 2 parameters: [lots] [target price] to open SELL
                        stop-order. In additional you can specify 3 parameters
                        for stop-order: [limit price, >= 0] [stop type,
                        Limit|SL|TP] [expiration date, Undefined|`%Y-%m-%d
                        %H:%M:%S`]. When current price will go up or down to
                        target price value then broker opens a limit order.
                        Stop loss order always executed by market price.
  --close-order CLOSE_ORDER, --cancel-order CLOSE_ORDER
                        Action: close only one order by it's `orderId` or
                        `stopOrderId`. You can find out the meaning of these
                        IDs using the key `--overview`
  --close-orders CLOSE_ORDERS [CLOSE_ORDERS ...], --cancel-orders CLOSE_ORDERS [CLOSE_ORDERS ...]
                        Action: close one or list of orders by it's `orderId`
                        or `stopOrderId`. You can find out the meaning of
                        these IDs using the key `--overview`
  --close-trade, --cancel-trade
                        Action: close only one position for instrument defined
                        by `--ticker` key, including for currencies tickers.
  --close-trades CLOSE_TRADES [CLOSE_TRADES ...], --cancel-trades CLOSE_TRADES [CLOSE_TRADES ...]
                        Action: close positions for list of tickers, including
                        for currencies tickers.
  --close-all [CLOSE_ALL [CLOSE_ALL ...]], --cancel-all [CLOSE_ALL [CLOSE_ALL ...]]
                        Action: close all available (not blocked) opened
                        trades and orders, excluding for currencies. Also you
                        can select one or more keywords case insensitive to
                        specify trades type: `orders`, `shares`, `bonds`,
                        `etfs` and `futures`, but not `currencies`. Currency
                        positions you must closes manually using `--buy`,
                        `--sell`, `--close-trade` or `--close-trades`
                        operations.
```

</details>

#### Получить список всех доступных для торговли инструментов

Используется ключ `--list` (`-l`). При этом запрашивается информация с сервера брокера по инструментам, доступным для текущего аккаунта. Дополнительно можно использовать ключ `--output` для указания файла, куда следует сохранить полученные данные в формате Markdown (по умолчанию `instruments.md` в текущей рабочей директории). Ключ `--debug-level=10` выведет всю отладочную информацию в консоль (можно его не указывать).

<details>
  <summary>Команда для получения списка всех инструментов</summary>

```commandline
$ tksbrokerapi --debug-level=10 --list --output ilist.md

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-26 22:04:39,571] TKSBrokerAPI module started at: [2022-07-26 19:04:39] (UTC), it is [2022-07-26 22:04:39] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-26 22:04:39,572] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-26 22:04:39,572] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-26 22:04:39,573] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-26 22:04:39,573] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-26 22:04:39,574] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 22:04:39,581] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 22:04:39,581] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 22:04:39,581] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 22:04:39,581] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 22:04:39,582] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:925  INFO    [2022-07-26 22:04:40,400] # All available instruments from Tinkoff Broker server for current user token

* **Actual on date:** [2022-07-26 19:04] (UTC)
* **Currencies:** [21]
* **Shares:** [1900]
* **Bonds:** [655]
* **Etfs:** [105]
* **Futures:** [284]


## Currencies available. Total: [21]

| Ticker       | Full name                                                      | FIGI         | Cur | Lot    | Step
|--------------|----------------------------------------------------------------|--------------|-----|--------|---------
| USDCHF_TOM   | Швейцарский франк - Доллар США                                 | BBG0013HPJ07 | chf | 1000   | 1e-05
| EUR_RUB__TOM | Евро                                                           | BBG0013HJJ31 | rub | 1000   | 0.0025
| CNYRUB_TOM   | Юань                                                           | BBG0013HRTL0 | rub | 1000   | 0.0001
| ...          | ...                                                            | ...          | ... | ...    | ...   
| RUB000UTSTOM | Российский рубль                                               | RUB000UTSTOM | rub | 1      | 0.0025
| USD000UTSTOM | Доллар США                                                     | BBG0013HGFT4 | rub | 1000   | 0.0025

[... далее идёт аналогичная информация по другим инструментам ...]

TKSBrokerAPI.py     L:931  INFO    [2022-07-26 22:04:41,211] All available instruments are saved to file: [ilist.md]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-26 22:04:41,213] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-26 22:04:41,214] TKSBrokerAPI module work duration: [0:00:01.641989]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-26 22:04:41,215] TKSBrokerAPI module finished: [2022-07-26 19:04:41] (UTC), it is [2022-07-26 22:04:41] local time
```

</details>

#### Получить информацию по инструменту

Используется ключ `--info` (`-i`), а также необходимо указать одно из двух: тикер инструмента, либо его FIGI идентификатор. Они задаются ключами `--ticker` (`-t`) и `--figi` (`-f`) соответственно. Выводимая пользователю информация при этом не отличается для обоих ключей. Разница имеется в содержании и количестве полей, отображаемых в информационной таблице, в зависимости от типа найденного инструмента: это валюта, акция, облигация, фонд или фьючерс.

<details>
  <summary>Команда для получения информации по валюте (используя алиас тикера, минимальные логи)</summary>

```commandline
$ tksbrokerapi  -t CNY -i

TKSBrokerAPI.py     L:607  INFO    [2022-07-26 23:48:31,766] Information about instrument: ticker [CNYRUB_TOM], FIGI [BBG0013HRTL0]
# Information is actual at: [2022-07-26 20:48] (UTC)

| Parameters                                              | Values
|---------------------------------------------------------|---------------------------------------------------------
| Stock ticker:                                           | CNYRUB_TOM
| Full name:                                              | Юань
| Country of instrument:                                  |
|                                                         |
| FIGI (Financial Instrument Global Identifier):          | BBG0013HRTL0
| Exchange:                                               | FX
| Class Code:                                             | CETS
|                                                         |
| Current broker security trading status:                 | Not available for trading
| Buy operations allowed:                                 | Yes
| Sale operations allowed:                                | Yes
| Short positions allowed:                                | No
|                                                         |
| Type of the instrument:                                 | Currencies
| ISO currency name:                                      | cny
| Payment currency:                                       | rub
|                                                         |
| Previous close price of the instrument:                 | 8.6894 rub
| Last deal price of the instrument:                      | 9.2 rub
| Changes between last deal price and last close  %       | 5.88%
| Current limit price, min / max:                         | 8.1891 rub / 9.3463 rub
| Actual price, sell / buy:                               | N/A rub / N/A rub
| Minimum lot to buy:                                     | 1000
| Minimum price increment (step):                         | 0.0001
```

</details>

<details>
  <summary>Команда для получения информации по акции (используя тикер, подробные логи)</summary>

```commandline
$ tksbrokerapi -v 10 --ticker IBM --info

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-26 23:49:58,496] TKSBrokerAPI module started at: [2022-07-26 20:49:58] (UTC), it is [2022-07-26 23:49:58] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-26 23:49:58,497] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-26 23:49:58,497] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-26 23:49:58,498] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-26 23:49:58,498] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-26 23:49:58,499] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 23:49:58,503] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 23:49:58,503] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 23:49:58,503] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 23:49:58,503] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-26 23:49:58,503] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-26 23:49:59,357] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:607  INFO    [2022-07-26 23:49:59,462] Information about instrument: ticker [IBM], FIGI [BBG000BLNNH6]
# Information is actual at: [2022-07-26 20:49] (UTC)

| Parameters                                              | Values
|---------------------------------------------------------|---------------------------------------------------------
| Stock ticker:                                           | IBM
| Full name:                                              | IBM
| Sector:                                                 | it
| Country of instrument:                                  | (US) Соединенные Штаты Америки
|                                                         |
| FIGI (Financial Instrument Global Identifier):          | BBG000BLNNH6
| Exchange:                                               | SPB
| ISIN (International Securities Identification Number):  | US4592001014
| Class Code:                                             | SPBXM
|                                                         |
| Current broker security trading status:                 | Normal trading
| Buy operations allowed:                                 | Yes
| Sale operations allowed:                                | Yes
| Short positions allowed:                                | No
|                                                         |
| Type of the instrument:                                 | Shares
| IPO date:                                               | 1915-11-11 00:00:00
| Payment currency:                                       | usd
|                                                         |
| Previous close price of the instrument:                 | 128.54 usd
| Last deal price of the instrument:                      | 128.2 usd
| Changes between last deal price and last close  %       | -0.26%
| Current limit price, min / max:                         | 126.54 usd / 129.86 usd
| Actual price, sell / buy:                               | 128.08 usd / 128.65 usd
| Minimum lot to buy:                                     | 1
| Minimum price increment (step):                         | 0.01

TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-26 23:49:59,471] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-26 23:49:59,471] TKSBrokerAPI module work duration: [0:00:00.974552]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-26 23:49:59,472] TKSBrokerAPI module finished: [2022-07-26 20:49:59] (UTC), it is [2022-07-26 23:49:59] local time
```

</details>

<details>
  <summary>Команда для получения информации по облигации (зная FIGI инструмента)</summary>

```commandline
$ tksbrokerapi -f TCS00A101YV8 --info

TKSBrokerAPI.py     L:607  INFO    [2022-07-26 23:57:22,581] Information about instrument: ticker [RU000A101YV8], FIGI [TCS00A101YV8]
# Information is actual at: [2022-07-26 20:57] (UTC)

| Parameters                                              | Values
|---------------------------------------------------------|---------------------------------------------------------
| Stock ticker:                                           | RU000A101YV8
| Full name:                                              | Позитив Текнолоджиз выпуск 1
| Sector:                                                 | it
| Country of instrument:                                  | (RU) Российская Федерация
|                                                         |
| FIGI (Financial Instrument Global Identifier):          | TCS00A101YV8
| Exchange:                                               | MOEX_PLUS
| ISIN (International Securities Identification Number):  | RU000A101YV8
| Class Code:                                             | TQCB
|                                                         |
| Current broker security trading status:                 | Break in trading
| Buy operations allowed:                                 | Yes
| Sale operations allowed:                                | Yes
| Short positions allowed:                                | No
|                                                         |
| Type of the instrument:                                 | Bonds
| Payment currency:                                       | rub
| State registration date:                                | 2020-07-21 00:00:00
| Placement date:                                         | 2020-07-29 00:00:00
| Maturity date:                                          | 2023-07-26 00:00:00
|                                                         |
| Previous close price of the instrument:                 | 101. rub
| Last deal price of the instrument:                      | 101. rub
| Changes between last deal price and last close  %       | 0.00%
| Current limit price, min / max:                         | 60.51 rub / 141.17 rub
| Actual price, sell / buy:                               | N/A rub / N/A rub
| Minimum lot to buy:                                     | 1
| Minimum price increment (step):                         | 0.01
```

</details>

<details>
  <summary>Команда для получения информации по фонду (зная FIGI инструмента)</summary>

```commandline
$ tksbrokerapi --figi BBG222222222 -i

TKSBrokerAPI.py     L:607  INFO    [2022-07-26 23:59:07,204] Information about instrument: ticker [TGLD], FIGI [BBG222222222]
# Information is actual at: [2022-07-26 20:59] (UTC)

| Parameters                                              | Values
|---------------------------------------------------------|---------------------------------------------------------
| Stock ticker:                                           | TGLD
| Full name:                                              | Тинькофф Золото
| Country of instrument:                                  |
|                                                         |
| FIGI (Financial Instrument Global Identifier):          | BBG222222222
| Exchange:                                               | MOEX
| ISIN (International Securities Identification Number):  | RU000A101X50
| Class Code:                                             | TQTD
|                                                         |
| Current broker security trading status:                 | Break in trading
| Buy operations allowed:                                 | Yes
| Sale operations allowed:                                | Yes
| Short positions allowed:                                | No
|                                                         |
| Type of the instrument:                                 | Etfs
| Released date:                                          | 2020-07-13 00:00:00
| Focusing type:                                          | equity
| Payment currency:                                       | usd
|                                                         |
| Previous close price of the instrument:                 | 0.07110000000000001 usd
| Last deal price of the instrument:                      | 0.07110000000000001 usd
| Changes between last deal price and last close  %       | 0.00%
| Current limit price, min / max:                         | 0.06080000000000001 usd / 0.0815 usd
| Actual price, sell / buy:                               | N/A usd / N/A usd
| Minimum lot to buy:                                     | 100
| Minimum price increment (step):                         | 0.0001
```

</details>

<details>
  <summary>Команда для получения информации по фьючерсу (зная его тикер, подробные логи)</summary>

```commandline
$ tksbrokerapi --verbosity=10 --ticker PZH2 --info

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 00:01:48,048] TKSBrokerAPI module started at: [2022-07-26 21:01:48] (UTC), it is [2022-07-27 00:01:48] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 00:01:48,049] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 00:01:48,049] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 00:01:48,049] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 00:01:48,050] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 00:01:48,050] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 00:01:48,056] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 00:01:48,056] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 00:01:48,057] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 00:01:48,057] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 00:01:48,058] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 00:01:48,968] Requesting current prices for instrument with ticker [PZH2] and FIGI [FUTPLZL03220]...
TKSBrokerAPI.py     L:607  INFO    [2022-07-27 00:01:49,075] Information about instrument: ticker [PZH2], FIGI [FUTPLZL03220]
# Information is actual at: [2022-07-26 21:01] (UTC)

| Parameters                                              | Values
|---------------------------------------------------------|---------------------------------------------------------
| Stock ticker:                                           | PZH2
| Full name:                                              | PLZL-3.22 Полюс Золото
| Sector:                                                 | SECTOR_MATERIALS
| Country of instrument:                                  |
|                                                         |
| FIGI (Financial Instrument Global Identifier):          | FUTPLZL03220
| Exchange:                                               | FORTS
| Class Code:                                             | SPBFUT
|                                                         |
| Current broker security trading status:                 | Not available for trading
| Buy operations allowed:                                 | Yes
| Sale operations allowed:                                | Yes
| Short positions allowed:                                | Yes
|                                                         |
| Type of the instrument:                                 | Futures
| Futures type:                                           | DELIVERY_TYPE_PHYSICAL_DELIVERY
| Asset type:                                             | TYPE_SECURITY
| Basic asset:                                            | PLZL
| Basic asset size:                                       | 10.0
| Payment currency:                                       | rub
| First trade date:                                       | 2021-09-02 20:59:59
| Last trade date:                                        | 2022-03-28 21:00:00
| Date of expiration:                                     | 2022-03-30 00:00:00
|                                                         |
| Previous close price of the instrument:                 | 108100. rub
| Last deal price of the instrument:                      | 108100. rub
| Changes between last deal price and last close  %       | 0.00%
| Current limit price, min / max:                         | 0. rub / 0. rub
| Actual price, sell / buy:                               | N/A rub / N/A rub
| Minimum lot to buy:                                     | 1

TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 00:01:49,085] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 00:01:49,085] TKSBrokerAPI module work duration: [0:00:01.036968]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 00:01:49,086] TKSBrokerAPI module finished: [2022-07-26 21:01:49] (UTC), it is [2022-07-27 00:01:49] local time
```

</details>

#### Запросить стакан цен с заданной глубиной

Используется ключ `--price`, а также необходимо указать одно из двух: тикер инструмента (ключ `--ticker` или `-t`), либо его FIGI идентификатор (ключ `--figi` или `-f`) соответственно. Дополнительно можно указать ключ `--depth` для задания "глубины стакана" с актуальными ценами. Фактическая отдаваемая глубина определяется политиками брокера для конкретного инструмента, она может быть значительно меньше запрашиваемой.

<details>
  <summary>Команда для получения стакана цен</summary>

```commandline
$ tksbrokerapi --ticker IBM --depth=5 --price

TKSBrokerAPI.py     L:871  INFO    [2022-07-27 00:11:35,189] Current prices in order book:

Orders book actual at [2022-07-26 21:11:35] (UTC)
Ticker: [IBM], FIGI: [BBG000BLNNH6], Depth of Market: [5]
----------------------------------------
 Orders of Buyers   | Orders of Sellers
----------------------------------------
 Sell prices (vol.) | Buy prices (vol.)
----------------------------------------
                    | 129.2 (1)
                    | 129.0 (9)
                    | 128.96 (21)
                    | 128.7 (1)
                    | 128.65 (150)
         127.67 (1) |
         127.66 (1) |
        127.65 (60) |
         127.53 (2) |
          127.5 (5) |
----------------------------------------
     Total sell: 69 | Total buy: 182
----------------------------------------
```

</details>

#### Запросить таблицу последних актуальных цен для списка инструментов

Используется ключ `--prices` (`-p`), а также необходимо перечислить тикеры инструментов или их FIGI идентификаторы, разделяя пробелом. Дополнительно можно указать ключ `--output` и задать имя файла, куда будет сохранена таблица цен в формате Markdown (по умолчанию `prices.md` в текущей рабочей директории).

<details>
  <summary>Команда для запроса цен указанных инструментов</summary>

```commandline
$ tksbrokerapi --prices EUR IBM MSFT GOOGL UNKNOWN_TICKER TCS00A101YV8 POSI BBG000000001 PTZ2 --output some-prices.md

TKSBrokerAPI.py     L:977  WARNING [2022-07-27 00:25:43,224] Instrument [UNKNOWN_TICKER] not in list of available instruments for current token!
TKSBrokerAPI.py     L:1018 INFO    [2022-07-27 00:25:43,606] Only unique instruments are shown:
# Actual prices at: [2022-07-26 21:25 UTC]

| Ticker       | FIGI         | Type       | Prev. close | Last price  | Chg. %   | Day limits min/max  | Actual sell / buy   | Curr.
|--------------|--------------|------------|-------------|-------------|----------|---------------------|---------------------|------
| EUR_RUB__TOM | BBG0013HJJ31 | Currencies |       59.22 |       61.68 |   +4.16% |       55.82 / 62.47 |           N/A / N/A | rub
| IBM          | BBG000BLNNH6 | Shares     |      128.08 |      128.36 |   +0.22% |     126.64 / 129.96 |     128.18 / 128.65 | usd
| MSFT         | BBG000BPH459 | Shares     |      251.90 |      252.23 |   +0.13% |     248.74 / 254.96 |     252.01 / 252.35 | usd
| GOOGL        | BBG009S39JX6 | Shares     |      105.02 |      108.00 |   +2.84% |       97.78 / 119.3 |     107.55 / 107.94 | usd
| RU000A101YV8 | TCS00A101YV8 | Bonds      |      101.00 |      101.00 |    0.00% |      60.51 / 141.17 |           N/A / N/A | rub
| POSI         | TCS00A103X66 | Shares     |      910.00 |      910.00 |    0.00% |      533.2 / 1243.6 |           N/A / N/A | rub
| TRUR         | BBG000000001 | Etfs       |        5.45 |        5.45 |    0.00% |          4.8 / 5.94 |           N/A / N/A | rub
| PTZ2         | FUTPLT122200 | Futures    |      940.40 |      930.00 |   -1.11% |      831.4 / 1024.2 |           N/A / N/A | rub

TKSBrokerAPI.py     L:1024 INFO    [2022-07-27 00:25:43,611] Price list for all instruments saved to file: [some-prices.md]
```

</details>


#### Получить текущий портфель пользователя и статистику распределения активов

Используется ключ `--overview` (`-o`). Дополнительно можно указать ключ `--output` и задать имя файла, куда сохранить отчёт о состоянии портфеля в формате Markdown (по умолчанию `overview.md` в текущей рабочей директории). Ключ `--verbosity=10` выведет всю отладочную информацию в консоль (можно его не указывать).

<details>
  <summary>Команда для получения портфеля пользователя</summary>

```commandline
$ tksbrokerapi --verbosity=10 --overview --output portfolio.md

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 18:03:05,365] TKSBrokerAPI module started at: [2022-07-27 15:03:05] (UTC), it is [2022-07-27 18:03:05] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 18:03:05,366] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 18:03:05,367] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 18:03:05,368] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 18:03:05,369] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 18:03:05,370] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 18:03:05,375] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 18:03:05,375] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 18:03:05,375] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 18:03:05,375] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 18:03:05,375] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:1146 DEBUG   [2022-07-27 18:03:06,455] Request portfolio of a client...
TKSBrokerAPI.py     L:1035 DEBUG   [2022-07-27 18:03:06,456] Requesting current actual user's portfolio. Wait, please...
TKSBrokerAPI.py     L:1041 DEBUG   [2022-07-27 18:03:06,659] Records about user's portfolio successfully received
TKSBrokerAPI.py     L:1052 DEBUG   [2022-07-27 18:03:06,660] Requesting current open positions in currencies and instruments. Wait, please...
TKSBrokerAPI.py     L:1058 DEBUG   [2022-07-27 18:03:06,779] Records about current open positions successfully received
TKSBrokerAPI.py     L:1069 DEBUG   [2022-07-27 18:03:06,779] Requesting current actual pending orders. Wait, please...
TKSBrokerAPI.py     L:1075 DEBUG   [2022-07-27 18:03:06,914] [1] records about pending orders successfully received
TKSBrokerAPI.py     L:1086 DEBUG   [2022-07-27 18:03:06,916] Requesting current actual stop orders. Wait, please...
TKSBrokerAPI.py     L:1092 DEBUG   [2022-07-27 18:03:07,027] [3] records about stop orders successfully received
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 18:03:07,039] Requesting current prices for instrument with ticker [RU000A101YV8] and FIGI [TCS00A101YV8]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 18:03:07,144] Requesting current prices for instrument with ticker [POSI] and FIGI [TCS00A103X66]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 18:03:07,235] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:1726 INFO    [2022-07-27 18:03:07,387] Statistics of client's portfolio:
# Client's portfolio

* **Actual date:** [2022-07-27 15:03:07] (UTC)
* **Portfolio cost:** 34501.76 RUB
* **Changes:** +168.23 RUB (+0.49%)

## Open positions

| Ticker [FIGI]               | Volume (blocked)                | Lots     | Curr. price  | Avg. price   | Current volume cost | Profit (%)
|-----------------------------|---------------------------------|----------|--------------|--------------|---------------------|----------------------
| Ruble                       |                 7.05 (0.62) rub |          |              |              |                     |
|                             |                                 |          |              |              |                     |
| **Currencies:**             |                                 |          |              |              |        11186.55 RUB |
| EUR_RUB__TOM [BBG0013HJJ31] |                 6.29 (0.00) eur | 0.0063   |    61.06 rub |    62.98 rub |          384.07 rub | -12.06 rub (-3.04%)
| CNYRUB_TOM [BBG0013HRTL0]   |               264.00 (0.00) cny | 0.2640   |     9.08 rub |     8.95 rub |         2396.99 rub | +35.51 rub (+1.50%)
| CHFRUB_TOM [BBG0013HQ5K4]   |                 1.00 (0.00) chf | 0.0010   |    60.54 rub |    64.00 rub |           60.54 rub | -3.46 rub (-5.41%)
| GBPRUB_TOM [BBG0013HQ5F0]   |                 2.00 (0.00) gbp | 0.0020   |    73.85 rub |    90.10 rub |          147.70 rub | -32.50 rub (-18.04%)
| TRYRUB_TOM [BBG0013J12N1]   |                 1.00 (0.00) try | 0.0010   |     3.34 rub |     4.75 rub |            3.34 rub | -1.41 rub (-29.65%)
| USD000UTSTOM [BBG0013HGFT4] |               135.68 (0.00) usd | 0.1357   |    60.33 rub |    59.40 rub |         8185.91 rub | +126.52 rub (+1.57%)
| HKDRUB_TOM [BBG0013HSW87]   |                 1.00 (0.00) hkd | 0.0010   |     8.00 rub |    11.46 rub |            8.00 rub | -3.46 rub (-30.19%)
|                             |                                 |          |              |              |                     |
| **Stocks:**                 |                                 |          |              |              |         8660.80 RUB |
| POSI [TCS00A103X66]         |                           1 (0) | 1        |   929.80 rub |   906.80 rub |          929.80 rub | +23.00 rub (+2.54%)
| IBM [BBG000BLNNH6]          |                           1 (0) | 1        |   128.14 usd |   128.89 usd |          128.14 usd | -0.75 usd (-0.58%)
|                             |                                 |          |              |              |                     |
| **Bonds:**                  |                                 |          |              |              |         3032.76 RUB |
| RU000A101YV8 [TCS00A101YV8] |                           3 (2) | 3        |  1010.60 rub |  1004.40 rub |         3032.76 rub | +18.60 rub (+0.62%)
|                             |                                 |          |              |              |                     |
| **Etfs:**                   |                                 |          |              |              |        11614.60 RUB |
| TGLD [BBG222222222]         |                        2700 (0) | 27       |     0.07 usd |     0.07 usd |          192.51 usd | -3.31 usd (-1.69%)
|                             |                                 |          |              |              |                     |
| **Futures:** no trades      |                                 |          |              |              |                     |

## Opened pending limit-orders: 1

| Ticker [FIGI]               | Order ID       | Lots (exec.) | Current price (% delta) | Target price  | Action    | Type      | Create date (UTC)
|-----------------------------|----------------|--------------|-------------------------|---------------|-----------|-----------|---------------------
| RU000A101YV8 [TCS00A101YV8] | ***********    | 2 (0)        |     101.13 rub (-0.85%) |    102.00 rub | ↓ Sell    | Limit     | 2022-07-27 16:10:38

## Opened stop-orders: 2

| Ticker [FIGI]               | Stop order ID                        | Lots   | Current price (% delta) | Target price  | Limit price   | Action    | Type        | Expire type  | Create date (UTC)   | Expiration (UTC)
|-----------------------------|--------------------------------------|--------|-------------------------|---------------|---------------|-----------|-------------|--------------|---------------------|---------------------
| POSI [TCS00A103X66]         | ********-****-****-****-************ | 1      |     929.80 rub (-7.02%) |   1000.00 rub |        Market | ↓ Sell    | Take profit | Until cancel | 2022-07-26 08:58:02 | Undefined
| IBM [BBG000BLNNH6]          | ********-****-****-****-************ | 1      |     128.16 usd (-1.42%) |    130.00 usd |        Market | ↓ Sell    | Take profit | Until cancel | 2022-07-26 14:46:07 | Undefined

# Analytics

* **Current total portfolio cost:** 34501.76 RUB
* **Changes:** +168.23 RUB (+0.49%)

## Portfolio distribution by assets

| Type       | Uniques | Percent | Current cost
|------------|---------|---------|-----------------
| Ruble      | 1       | 0.02%   | 7.05 rub
| Currencies | 7       | 32.42%  | 11186.55 rub
| Shares     | 2       | 25.10%  | 8660.80 rub
| Bonds      | 1       | 8.79%   | 3032.76 rub
| Etfs       | 1       | 33.66%  | 11614.60 rub

## Portfolio distribution by companies

| Company                                     | Percent | Current cost
|---------------------------------------------|---------|-----------------
| All money cash                              | 32.44%  | 11193.60 rub
| [POSI] Positive Technologies                | 2.69%   | 929.80 rub
| [IBM] IBM                                   | 22.41%  | 7731.01 rub
| [RU000A101YV8] Позитив Текнолоджиз выпуск 1 | 8.79%   | 3032.76 rub
| [TGLD] Тинькофф Золото                      | 33.66%  | 11614.61 rub

## Portfolio distribution by sectors

| Sector         | Percent | Current cost
|----------------|---------|-----------------
| All money cash | 32.44%  | 11193.60 rub
| it             | 33.89%  | 11693.57 rub
| other          | 33.66%  | 11614.61 rub

## Portfolio distribution by currencies

| Instruments currencies   | Percent | Current cost
|--------------------------|---------|-----------------
| [rub] Российский рубль   | 11.51%  | 3969.61 rub
| [usd] Доллар США         | 79.80%  | 27531.53 rub
| [eur] Евро               | 1.11%   | 384.07 rub
| [cny] Юань               | 6.95%   | 2396.99 rub
| [chf] Швейцарский франк  | 0.18%   | 60.54 rub
| [gbp] Фунт стерлингов    | 0.43%   | 147.70 rub
| [try] Турецкая лира      | 0.01%   | 3.34 rub
| [hkd] Гонконгский доллар | 0.02%   | 8.00 rub

TKSBrokerAPI.py     L:1732 INFO    [2022-07-27 18:03:07,410] Client's portfolio is saved to file: [portfolio.md]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 18:03:07,411] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 18:03:07,411] TKSBrokerAPI module work duration: [0:00:02.045574]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 18:03:07,412] TKSBrokerAPI module finished: [2022-07-27 15:03:07] (UTC), it is [2022-07-27 18:03:07] local time
```

</details>

#### Получить отчёт по операциям с портфелем за указанный период

Используется ключ `--deals` (`-d`), после которого нужно указать две даты: начальную и конечную даты отчёта. Они должны быть в формате `%Y-%m-%d` и разделены пробелом, например, `--deals 2022-07-01 2022-07-27`. В этом случае в отчёт войдут все операции с 0:00:00 часов первой даты и до 23:59:59 второй даты.

Вместо начальной даты можно указать отрицательное число — количество предыдущих дней от текущей даты (`--deals -1`, `-d -2`, `-d -3`, ...), тогда конечную дату указывать не нужно. Также вместо начальной даты можно указать одно из ключевых слов: `today`, `yesterday` (-1 день), `week` (-7 дней), `month` (-30 дней), `year` (-365 дней). Во всех этих случаях будет выдан отчёт за указанное количество предыдущих дней и вплоть до сегодняшнего числа и текущего времени.

Дополнительно можно указать ключ `--output` для указания файла, куда сохранить отчёт по операциям в формате Markdown (по умолчанию `report.md` в текущей рабочей директории).
 
<details>
  <summary>Команда для получения отчёта по операциям между двумя указанными датами</summary>

```commandline
$ tksbrokerapi --deals 2022-07-01 2022-07-28 --output deals.md

TKSBrokerAPI.py     L:1972 INFO    [2022-07-28 18:13:18,960] # Client's operations

* **Period:** from [2022-07-01] to [2022-07-28]

## Summary (operations executed only)

| 1                          | 2                             | 3                            | 4                    | 5
|----------------------------|-------------------------------|------------------------------|----------------------|------------------------
| **Actions:**               | Operations executed: 35       | Trading volumes:             |                      |
|                            |   Buy: 19 (54.3%)             |   rub, buy: -25907.12        |                      |
|                            |   Sell: 16 (45.7%)            |   rub, sell: +11873.86       |                      |
|                            |                               |   usd, buy: -664.45          |                      |
|                            |                               |   usd, sell: +281.03         |                      |
|                            |                               |                              |                      |
| **Payments:**              | Deposit on broker account:    | Withdrawals:                 | Dividends income:    | Coupons income:
|                            |   rub: +14000.00              |   —                          |   —                  |   rub: +86.01
|                            |                               |                              |                      |
| **Commissions and taxes:** | Broker commissions:           | Service commissions:         | Margin commissions:  | All taxes/corrections:
|                            |   rub: -75.85                 |   —                          |   —                  |   rub: -11.00
|                            |   usd: -0.30                  |   —                          |   —                  |   —
|                            |                               |                              |                      |

## All operations

| Date and time       | FIGI         | Ticker       | Asset      | Value     | Payment         | Status     | Operation type
|---------------------|--------------|--------------|------------|-----------|-----------------|------------|--------------------------------------------------------------------
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      +86.01 rub | √ Executed | Coupons income
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      -11.00 rub | √ Executed | Withholding personal income tax on bond coupons
|                     |              |              |            |           |                 |            |
| 2022-07-27 20:30:12 | BBG000BLNNH6 | IBM          | Shares     | 2         |               — | × Canceled | Sell securities
| 2022-07-27 20:26:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:26:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -129.28 usd | √ Executed | Buy securities
| 2022-07-27 20:25:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:25:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.89 usd | √ Executed | Sell securities
| 2022-07-27 19:18:43 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 19:18:42 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.80 usd | √ Executed | Buy securities
| 2022-07-27 19:13:29 | BBG000BLNNH6 | IBM          | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-27 16:00:39 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 16:00:38 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.01 usd | √ Executed | Sell securities
| 2022-07-27 15:56:46 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 15:56:45 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.10 usd | √ Executed | Buy securities
| 2022-07-27 13:10:38 | TCS00A101YV8 | RU000A101YV8 | Bonds      | 2         |               — | × Canceled | Sell securities
| 2022-07-27 13:06:38 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | —         |       -6.47 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:06:37 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | 241       |    -2156.28 rub | √ Executed | Buy securities
| 2022-07-27 13:05:42 | BBG222222222 | TGLD         | Etfs       | 1100      |      -78.43 usd | √ Executed | Buy securities
| 2022-07-27 13:04:26 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -35.66 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:04:25 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 200       |   -11885.50 rub | √ Executed | Buy securities
| 2022-07-27 13:03:46 | —            | —            | —          | —         |   +14000.00 rub | √ Executed | Deposit on broker account
|                     |              |              |            |           |                 |            |
| 2022-07-26 14:46:08 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-26 14:46:07 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.89 usd | √ Executed | Buy securities
| 2022-07-26 09:43:05 | TCS00A103X66 | POSI         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-26 09:37:47 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -24.57 rub | √ Executed | Operation fee deduction
| 2022-07-26 09:37:46 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 140       |    -8190.00 rub | √ Executed | Buy securities
| 2022-07-26 08:58:02 | TCS00A103X66 | POSI         | Shares     | —         |       -0.23 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:58:01 | TCS00A103X66 | POSI         | Shares     | 1         |     -906.80 rub | √ Executed | Buy securities
| 2022-07-26 08:56:25 | TCS00A103X66 | POSI         | Shares     | —         |       -1.13 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:56:24 | TCS00A103X66 | POSI         | Shares     | 5         |    +4530.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-25 08:25:59 | TCS00A103X66 | POSI         | Shares     | —         |       -1.17 rub | √ Executed | Operation fee deduction
| 2022-07-25 08:25:58 | TCS00A103X66 | POSI         | Shares     | 5         |    +4676.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-22 14:48:50 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-22 14:48:49 | BBG00JN4FXG8 | SLDB         | Shares     | 3         |       +2.14 usd | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-21 17:21:21 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:17:06 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:16:17 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:11:30 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-21 17:11:29 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       -0.74 usd | √ Executed | Buy securities
|                     |              |              |            |           |                 |            |
| 2022-07-19 07:08:11 | TCS00A103X66 | POSI         | Shares     | —         |       -0.22 rub | √ Executed | Operation fee deduction
| 2022-07-19 07:08:10 | TCS00A103X66 | POSI         | Shares     | 1         |     -864.00 rub | √ Executed | Buy securities
|                     |              |              |            |           |                 |            |
| 2022-07-15 07:00:05 | TCS00A103X66 | POSI         | Shares     | —         |       -0.22 rub | √ Executed | Operation fee deduction
| 2022-07-15 07:00:04 | TCS00A103X66 | POSI         | Shares     | 1         |     +860.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-11 07:46:13 | BBG222222222 | TGLD         | Etfs       | 300       |      -21.45 usd | √ Executed | Buy securities
| 2022-07-08 18:04:04 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-08 18:04:03 | BBG00JN4FXG8 | SLDB         | Shares     | 25        |      +16.26 usd | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-06 17:15:05 | BBG00JN4FXG8 | SLDB         | Shares     | 27        |               — | × Canceled | Sell securities
| 2022-07-06 14:58:23 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-06 14:58:22 | BBG00JN4FXG8 | SLDB         | Shares     | 3         |       +2.16 usd | √ Executed | Sell securities
| 2022-07-06 14:46:40 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-06 14:46:39 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.68 usd | √ Executed | Sell securities
| 2022-07-06 14:40:39 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-06 14:40:38 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.66 usd | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-05 14:24:15 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-05 13:26:56 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-05 13:26:55 | BBG00JN4FXG8 | SLDB         | Shares     | 6         |       -3.59 usd | √ Executed | Buy securities
| 2022-07-05 13:26:31 | BBG222222222 | TGLD         | Etfs       | 300       |      -22.29 usd | √ Executed | Buy securities
| 2022-07-05 13:24:45 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |       -5.38 rub | √ Executed | Operation fee deduction
| 2022-07-05 13:24:44 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 29        |    -1792.56 rub | √ Executed | Buy securities
| 2022-07-05 13:24:26 | BBG00V9V16J8 | GOLD         | Etfs       | —         |       -0.45 rub | √ Executed | Operation fee deduction
| 2022-07-05 13:24:25 | BBG00V9V16J8 | GOLD         | Etfs       | 1972      |    +1797.68 rub | √ Executed | Sell securities
| 2022-07-05 13:21:59 | BBG222222222 | TGLD         | Etfs       | 100       |       -7.44 usd | √ Executed | Buy securities
| 2022-07-05 10:12:22 | BBG00V9V16J8 | GOLD         | Etfs       | —         |       -0.01 rub | √ Executed | Operation fee deduction
| 2022-07-05 10:12:21 | BBG00V9V16J8 | GOLD         | Etfs       | 11        |      +10.18 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-01 19:32:46 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-01 19:32:45 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.58 usd | √ Executed | Sell securities
| 2022-07-01 18:13:04 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-01 18:13:03 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       -0.56 usd | √ Executed | Buy securities
| 2022-07-01 17:46:57 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-01 17:46:56 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-01 17:46:56 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Buy securities
| 2022-07-01 17:46:56 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.55 usd | √ Executed | Sell securities
| 2022-07-01 17:46:56 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-01 17:46:55 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.55 usd | √ Executed | Sell securities
| 2022-07-01 17:46:55 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       +0.55 usd | √ Executed | Sell securities
| 2022-07-01 09:22:15 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | —         |       -0.34 rub | √ Executed | Operation fee deduction
| 2022-07-01 09:22:14 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | 13        |     -111.98 rub | √ Executed | Buy securities
| 2022-07-01 09:20:21 | BBG222222222 | TGLD         | Etfs       | 200       |      -14.88 usd | √ Executed | Buy securities

TKSBrokerAPI.py     L:1978 INFO    [2022-07-28 18:13:18,975] History of a client's operations are saved to file: [deals.md]
```

</details>

<details>
  <summary>Команда для получения отчёта по операциям за три предыдущих дня</summary>

```commandline
$ tksbrokerapi -d -3

TKSBrokerAPI.py     L:1972 INFO    [2022-07-28 18:29:15,026] # Client's operations

* **Period:** from [2022-07-25] to [2022-07-28]

## Summary (operations executed only)

| 1                          | 2                             | 3                            | 4                    | 5
|----------------------------|-------------------------------|------------------------------|----------------------|------------------------
| **Actions:**               | Operations executed: 13       | Trading volumes:             |                      |
|                            |   Buy: 9 (69.2%)              |   rub, buy: -23138.58        |                      |
|                            |   Sell: 4 (30.8%)             |   rub, sell: +9206.00        |                      |
|                            |                               |   usd, buy: -593.50          |                      |
|                            |                               |   usd, sell: +256.90         |                      |
|                            |                               |                              |                      |
| **Payments:**              | Deposit on broker account:    | Withdrawals:                 | Dividends income:    | Coupons income:
|                            |   rub: +14000.00              |   —                          |   —                  |   rub: +86.01
|                            |                               |                              |                      |
| **Commissions and taxes:** | Broker commissions:           | Service commissions:         | Margin commissions:  | All taxes/corrections:
|                            |   rub: -69.23                 |   —                          |   —                  |   rub: -11.00
|                            |   usd: -0.18                  |   —                          |   —                  |   —
|                            |                               |                              |                      |

## All operations

| Date and time       | FIGI         | Ticker       | Asset      | Value     | Payment         | Status     | Operation type
|---------------------|--------------|--------------|------------|-----------|-----------------|------------|--------------------------------------------------------------------
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      +86.01 rub | √ Executed | Coupons income
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      -11.00 rub | √ Executed | Withholding personal income tax on bond coupons
|                     |              |              |            |           |                 |            |
| 2022-07-27 20:30:12 | BBG000BLNNH6 | IBM          | Shares     | 2         |               — | × Canceled | Sell securities
| 2022-07-27 20:26:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:26:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -129.28 usd | √ Executed | Buy securities
| 2022-07-27 20:25:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:25:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.89 usd | √ Executed | Sell securities
| 2022-07-27 19:18:43 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 19:18:42 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.80 usd | √ Executed | Buy securities
| 2022-07-27 19:13:29 | BBG000BLNNH6 | IBM          | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-27 16:00:39 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 16:00:38 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.01 usd | √ Executed | Sell securities
| 2022-07-27 15:56:46 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 15:56:45 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.10 usd | √ Executed | Buy securities
| 2022-07-27 13:10:38 | TCS00A101YV8 | RU000A101YV8 | Bonds      | 2         |               — | × Canceled | Sell securities
| 2022-07-27 13:06:38 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | —         |       -6.47 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:06:37 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | 241       |    -2156.28 rub | √ Executed | Buy securities
| 2022-07-27 13:05:42 | BBG222222222 | TGLD         | Etfs       | 1100      |      -78.43 usd | √ Executed | Buy securities
| 2022-07-27 13:04:26 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -35.66 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:04:25 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 200       |   -11885.50 rub | √ Executed | Buy securities
| 2022-07-27 13:03:46 | —            | —            | —          | —         |   +14000.00 rub | √ Executed | Deposit on broker account
|                     |              |              |            |           |                 |            |
| 2022-07-26 14:46:08 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-26 14:46:07 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.89 usd | √ Executed | Buy securities
| 2022-07-26 09:43:05 | TCS00A103X66 | POSI         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-26 09:37:47 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -24.57 rub | √ Executed | Operation fee deduction
| 2022-07-26 09:37:46 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 140       |    -8190.00 rub | √ Executed | Buy securities
| 2022-07-26 08:58:02 | TCS00A103X66 | POSI         | Shares     | —         |       -0.23 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:58:01 | TCS00A103X66 | POSI         | Shares     | 1         |     -906.80 rub | √ Executed | Buy securities
| 2022-07-26 08:56:25 | TCS00A103X66 | POSI         | Shares     | —         |       -1.13 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:56:24 | TCS00A103X66 | POSI         | Shares     | 5         |    +4530.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-25 08:25:59 | TCS00A103X66 | POSI         | Shares     | —         |       -1.17 rub | √ Executed | Operation fee deduction
| 2022-07-25 08:25:58 | TCS00A103X66 | POSI         | Shares     | 5         |    +4676.00 rub | √ Executed | Sell securities

TKSBrokerAPI.py     L:1978 INFO    [2022-07-28 18:29:15,032] History of a client's operations are saved to file: [report.md]
```

</details>

<details>
  <summary>Команда для получения отчёта по операциям за прошлую неделю</summary>

```commandline
$ tksbrokerapi -d week

TKSBrokerAPI.py     L:1972 INFO    [2022-07-28 18:29:59,035] # Client's operations

* **Period:** from [2022-07-21] to [2022-07-28]

## Summary (operations executed only)

| 1                          | 2                             | 3                            | 4                    | 5
|----------------------------|-------------------------------|------------------------------|----------------------|------------------------
| **Actions:**               | Operations executed: 15       | Trading volumes:             |                      |
|                            |   Buy: 10 (66.7%)             |   rub, buy: -23138.58        |                      |
|                            |   Sell: 5 (33.3%)             |   rub, sell: +9206.00        |                      |
|                            |                               |   usd, buy: -594.24          |                      |
|                            |                               |   usd, sell: +259.04         |                      |
|                            |                               |                              |                      |
| **Payments:**              | Deposit on broker account:    | Withdrawals:                 | Dividends income:    | Coupons income:
|                            |   rub: +14000.00              |   —                          |   —                  |   rub: +86.01
|                            |                               |                              |                      |
| **Commissions and taxes:** | Broker commissions:           | Service commissions:         | Margin commissions:  | All taxes/corrections:
|                            |   rub: -69.23                 |   —                          |   —                  |   rub: -11.00
|                            |   usd: -0.20                  |   —                          |   —                  |   —
|                            |                               |                              |                      |

## All operations

| Date and time       | FIGI         | Ticker       | Asset      | Value     | Payment         | Status     | Operation type
|---------------------|--------------|--------------|------------|-----------|-----------------|------------|--------------------------------------------------------------------
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      -11.00 rub | √ Executed | Withholding personal income tax on bond coupons
| 2022-07-28 05:00:08 | TCS00A101YV8 | RU000A101YV8 | Bonds      | —         |      +86.01 rub | √ Executed | Coupons income
|                     |              |              |            |           |                 |            |
| 2022-07-27 20:30:12 | BBG000BLNNH6 | IBM          | Shares     | 2         |               — | × Canceled | Sell securities
| 2022-07-27 20:26:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:26:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -129.28 usd | √ Executed | Buy securities
| 2022-07-27 20:25:41 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 20:25:40 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.89 usd | √ Executed | Sell securities
| 2022-07-27 19:18:43 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 19:18:42 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.80 usd | √ Executed | Buy securities
| 2022-07-27 19:13:29 | BBG000BLNNH6 | IBM          | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-27 16:00:39 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 16:00:38 | BBG000BLNNH6 | IBM          | Shares     | 1         |     +128.01 usd | √ Executed | Sell securities
| 2022-07-27 15:56:46 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-27 15:56:45 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.10 usd | √ Executed | Buy securities
| 2022-07-27 13:10:38 | TCS00A101YV8 | RU000A101YV8 | Bonds      | 2         |               — | × Canceled | Sell securities
| 2022-07-27 13:06:38 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | —         |       -6.47 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:06:37 | BBG0013HRTL0 | CNYRUB_TOM   | Currencies | 241       |    -2156.28 rub | √ Executed | Buy securities
| 2022-07-27 13:05:42 | BBG222222222 | TGLD         | Etfs       | 1100      |      -78.43 usd | √ Executed | Buy securities
| 2022-07-27 13:04:26 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -35.66 rub | √ Executed | Operation fee deduction
| 2022-07-27 13:04:25 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 200       |   -11885.50 rub | √ Executed | Buy securities
| 2022-07-27 13:03:46 | —            | —            | —          | —         |   +14000.00 rub | √ Executed | Deposit on broker account
|                     |              |              |            |           |                 |            |
| 2022-07-26 14:46:08 | BBG000BLNNH6 | IBM          | Shares     | —         |       -0.03 usd | √ Executed | Operation fee deduction
| 2022-07-26 14:46:07 | BBG000BLNNH6 | IBM          | Shares     | 1         |     -128.89 usd | √ Executed | Buy securities
| 2022-07-26 09:43:05 | TCS00A103X66 | POSI         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-26 09:37:47 | BBG0013HGFT4 | USD000UTSTOM | Currencies | —         |      -24.57 rub | √ Executed | Operation fee deduction
| 2022-07-26 09:37:46 | BBG0013HGFT4 | USD000UTSTOM | Currencies | 140       |    -8190.00 rub | √ Executed | Buy securities
| 2022-07-26 08:58:02 | TCS00A103X66 | POSI         | Shares     | —         |       -0.23 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:58:01 | TCS00A103X66 | POSI         | Shares     | 1         |     -906.80 rub | √ Executed | Buy securities
| 2022-07-26 08:56:25 | TCS00A103X66 | POSI         | Shares     | —         |       -1.13 rub | √ Executed | Operation fee deduction
| 2022-07-26 08:56:24 | TCS00A103X66 | POSI         | Shares     | 5         |    +4530.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-25 08:25:59 | TCS00A103X66 | POSI         | Shares     | —         |       -1.17 rub | √ Executed | Operation fee deduction
| 2022-07-25 08:25:58 | TCS00A103X66 | POSI         | Shares     | 5         |    +4676.00 rub | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-22 14:48:50 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-22 14:48:49 | BBG00JN4FXG8 | SLDB         | Shares     | 3         |       +2.14 usd | √ Executed | Sell securities
|                     |              |              |            |           |                 |            |
| 2022-07-21 17:21:21 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:17:06 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:16:17 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |               — | × Canceled | Sell securities
| 2022-07-21 17:11:30 | BBG00JN4FXG8 | SLDB         | Shares     | —         |       -0.01 usd | √ Executed | Operation fee deduction
| 2022-07-21 17:11:29 | BBG00JN4FXG8 | SLDB         | Shares     | 1         |       -0.74 usd | √ Executed | Buy securities

TKSBrokerAPI.py     L:1978 INFO    [2022-07-28 18:29:59,045] History of a client's operations are saved to file: [report.md]
```

</details>

#### Совершить сделку по рынку

В начале следует указать ключ `--ticker` или `--figi`, чтобы конкретизировать инструмент, для которого будет рыночный ордер. Для совершения сделки "по рынку", то есть по текущим ценам в стакане, используется общий ключ `--trade`, после которого нужно указать от 1 до 5 параметров в строгом порядке их следования:

- направление: `Buy`или `Sell` — обязательный параметр;
- необязательные параметры:
  - количество лотов инструмента, целое число >= 1, по умолчанию 1;
  - уровень тейк-профит, дробное число >= 0, по умолчанию 0 (если 0 — тейк-профит ордер установлен не будет);
  - уровень стоп-лосс, дробное число >= 0, по умолчанию 0 (если 0 — стоп-лосс ордер установлен не будет);
  - дата отмены ордеров тейк-профит и стоп-лосс, по умолчанию строка `Undefined` (в этом случае ордера будут действовать до отмены) или можно задать дату в формате `%Y-%m-%d %H:%M:%S`.

Также можно использовать более простые ключи для совершения операций покупки и продажи по рынку `--buy` или `--sell`, для которых можно задать до 4 необязательных параметров:

- количество лотов инструмента, целое число >= 1, по умолчанию 1;
- уровень тейк-профит, дробное число >= 0, по умолчанию 0 (если 0 — тейк-профит ордер установлен не будет);
- уровень стоп-лосс, дробное число >= 0, по умолчанию 0 (если 0 — стоп-лосс ордер установлен не будет);
- дата отмены ордеров тейк-профит и стоп-лосс, по умолчанию строка `Undefined` (в этом случае ордера будут действовать до отмены) или можно задать дату в формате `%Y-%m-%d %H:%M:%S`.
 
<details>
  <summary>Команда для покупки и выставления ордеров тейк-профит и стоп-лосс</summary>

```commandline
$ tksbrokerapi --ticker IBM --trade Buy 1 131.5 125.1 "2022-07-28 12:00:00"

TKSBrokerAPI.py     L:2202 INFO    [2022-07-27 18:56:49,032] [Buy] market order [447445558780] was executed: ticker [IBM], FIGI [BBG000BLNNH6], lots [1]. Total order price: [128.1000 usd] (with commission: [0.04 usd]). Average price of lot: [128.10 usd]
TKSBrokerAPI.py     L:2476 INFO    [2022-07-27 18:56:49,389] Stop-order [182892f7-9533-4817-94d9-613545a01ee1] was created: ticker [IBM], FIGI [BBG000BLNNH6], action [Sell], lots [1], target price [131.50 usd], limit price [131.50 usd], stop-order type [Take profit] and expiration date in UTC [2022-07-28 09:00:00]
TKSBrokerAPI.py     L:2476 INFO    [2022-07-27 18:56:49,683] Stop-order [4ca044e8-607a-4636-ad27-3a9139cc964a] was created: ticker [IBM], FIGI [BBG000BLNNH6], action [Sell], lots [1], target price [125.10 usd], limit price [125.10 usd], stop-order type [Stop loss] and expiration date in UTC [2022-07-28 09:00:00]
```

</details>

<details>
  <summary>Команда для продажи ранее купленного инструмента (без указания SL/TP ордеров, с подробными логами)</summary>

```commandline
$ tksbrokerapi -v 10 --ticker IBM --sell 1

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 19:00:39,673] TKSBrokerAPI module started at: [2022-07-27 16:00:39] (UTC), it is [2022-07-27 19:00:39] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 19:00:39,674] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 19:00:39,675] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 19:00:39,676] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 19:00:39,677] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 19:00:39,678] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 19:00:39,682] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 19:00:39,682] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 19:00:39,682] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 19:00:39,682] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 19:00:39,683] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 19:00:40,812] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:2184 DEBUG   [2022-07-27 19:00:40,922] Opening [Sell] market order: ticker [IBM], FIGI [BBG000BLNNH6], lots [1], TP [0.0000], SL [0.0000], expiration date of TP/SL orders [Undefined]. Wait, please...
TKSBrokerAPI.py     L:2202 INFO    [2022-07-27 19:00:41,201] [Sell] market order [447451039340] was executed: ticker [IBM], FIGI [BBG000BLNNH6], lots [1]. Total order price: [128.0100 usd] (with commission: [0.04 usd]). Average price of lot: [128.01 usd]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 19:00:41,203] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 19:00:41,204] TKSBrokerAPI module work duration: [0:00:01.530060]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 19:00:41,204] TKSBrokerAPI module finished: [2022-07-27 16:00:41] (UTC), it is [2022-07-27 19:00:41] local time
```

</details>

#### Открыть отложенный лимитный или стоп-ордер

В начале следует указать ключ `--ticker` или `--figi`, чтобы конкретизировать инструмент, для которого будет выставлен ордер. Чтобы открыть отложенный ордер любого типа, можно использовать общий ключ `--order`, после которого нужно указать от 4 до 7 параметров в строгом порядке их следования:

- направление: `Buy`или `Sell` — обязательный параметр;
- тип ордера: `Limit` (действуют до конца торговой сессии) или `Stop` (действуют до отмены, либо до указанной даты) — обязательный параметр;
- количество лотов инструмента, целое число >= 1 — обязательный параметр;
- целевая цена срабатывания начального ордера, дробное число >= 0 — обязательный параметр;
- необязательные параметры и только для стоп-ордеров: 
  - цена открываемого лимитного ордера, дробное число >= 0, по умолчанию 0 (если 0 — вместо лимитного будет немедленно выставлен рыночный ордер, при достижении цены срабатывания начального стоп-ордера);
  - тип ордера, открываемого по достижении цены срабатывания начального стоп-ордера, по умолчанию это строка `Limit` или можно указать `SL`, `TP`, для открытия стоп-лосс или тейк-профит ордера;
    - стоп-лосс ордер всегда открывается по рыночной цене;
  - дата отмены ордеров тейк-профит и стоп-лосс, по умолчанию строка `Undefined` (в этом случае ордера будут действовать до отмены) или можно задать дату в формате `%Y-%m-%d %H:%M:%S`.

Можно использовать более простые ключи для выставления отложенных лимитных ордеров (действуют до конца торговой сессии) `--buy-limit` или `--sell-limit`, для которых нужно указать только 2 обязательных параметра:

- количество лотов инструмента, целое число >= 1 — обязательный параметр;
- целевая цена срабатывания лимитного ордера, дробное число >= 0 — обязательный параметр;
  - для ордера типа `--buy-limit` целевая цена должна быть ниже текущей цены, а если она будет выше, то брокер немедленно откроет рыночный ордер на покупку, как если бы исполнилась команда `--buy`;
  - для ордера типа `--sell-limit` целевая цена должна быть выше текущей цены, а если она будет ниже, то брокер немедленно откроет рыночный ордер на продажу, как если бы исполнилась команда `--sell`.

Можно использовать более простые ключи для выставления отложенных стоп-ордеров (действуют до отмены, либо до указанной даты) `--buy-stop` (на покупку) или `--sell-stop` (на продажу), для которых нужно указать только 2 обязательных параметра и 3 необязательных:

- количество лотов инструмента, целое число >= 1 — обязательный параметр;
- целевая цена срабатывания стоп-ордера, дробное число >= 0 — обязательный параметр;
- необязательные параметры:
  - цена открываемого лимитного ордера, дробное число >= 0, по умолчанию 0 (если 0 — вместо лимитного будет немедленно выставлен рыночный ордер, при достижении цены срабатывания начального стоп-ордера);
  - тип ордера, открываемого по достижении цены срабатывания начального стоп-ордера, по умолчанию это строка `Limit` или можно указать `SL`, `TP`, для открытия стоп-лосс или тейк-профит ордера;
    - стоп-лосс ордер всегда открывается по рыночной цене;
  - дата отмены ордеров тейк-профит и стоп-лосс, по умолчанию строка `Undefined` (в этом случае ордера будут действовать до отмены) или можно задать дату в формате `%Y-%m-%d %H:%M:%S`.

<details>
  <summary>Команда для выставления стоп-ордера типа тейк-профит на продажу, с указанием даты отмены</summary>

```commandline
$ tksbrokerapi -v 10 --ticker IBM --order Sell Stop  1 130.2 130.1 TP  "2022-07-28 12:20:00"

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 22:15:20,137] TKSBrokerAPI module started at: [2022-07-27 19:15:20] (UTC), it is [2022-07-27 22:15:20] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 22:15:20,138] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 22:15:20,139] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 22:15:20,141] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 22:15:20,141] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 22:15:20,142] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:15:20,148] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:15:20,148] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:15:20,148] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:15:20,148] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:15:20,148] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 22:15:21,400] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:2443 DEBUG   [2022-07-27 22:15:21,500] Creating stop-order: ticker [IBM], FIGI [BBG000BLNNH6], action [Sell], lots [1], target price [130.20 usd], limit price [130.10 usd], stop-order type [TP] and local expiration date [2022-07-28 12:20:00]. Wait, please...
TKSBrokerAPI.py     L:2476 INFO    [2022-07-27 22:15:21,671] Stop-order [********-****-****-****-************] was created: ticker [IBM], FIGI [BBG000BLNNH6], action [Sell], lots [1], target price [130.20 usd], limit price [130.10 usd], stop-order type [Take profit] and expiration date in UTC [2022-07-28 09:20:00]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 22:15:21,673] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 22:15:21,674] TKSBrokerAPI module work duration: [0:00:01.535746]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 22:15:21,675] TKSBrokerAPI module finished: [2022-07-27 19:15:21] (UTC), it is [2022-07-27 22:15:21] local time
```

</details>

<details>
  <summary>Команда для выставления тейк-профит стоп-ордера с продажей по рыночной цене, при достижении целевого уровня</summary>

```commandline
$ tksbrokerapi -t IBM --sell-stop 2 140 0 TP

TKSBrokerAPI.py     L:2476 INFO    [2022-07-27 23:29:29,614] Stop-order [********-****-****-****-************] was created: ticker [IBM], FIGI [BBG000BLNNH6], action [Sell], lots [2], target price [140.00 usd], limit price [140.00 usd], stop-order type [Take profit] and expiration date in UTC [Undefined]
```

</details>

<details>
  <summary>Команда для выставления лимитного ордера на покупку</summary>

```commandline
$ tksbrokerapi --debug-level=10 --ticker IBM --buy-limit 1 128.8

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 22:18:41,111] TKSBrokerAPI module started at: [2022-07-27 19:18:41] (UTC), it is [2022-07-27 22:18:41] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 22:18:41,111] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 22:18:41,111] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 22:18:41,111] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 22:18:41,111] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 22:18:41,111] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:18:41,118] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:18:41,119] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:18:41,119] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:18:41,119] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 22:18:41,120] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 22:18:42,032] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:2398 DEBUG   [2022-07-27 22:18:42,134] Creating pending limit-order: ticker [IBM], FIGI [BBG000BLNNH6], action [Buy], lots [1] and the target price [128.80 usd]. Wait, please...
TKSBrokerAPI.py     L:2417 INFO    [2022-07-27 22:18:42,358] Limit-order [************] was created: ticker [IBM], FIGI [BBG000BLNNH6], action [Buy], lots [1], target price [128.80 usd]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 22:18:42,359] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 22:18:42,359] TKSBrokerAPI module work duration: [0:00:01.248221]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 22:18:42,359] TKSBrokerAPI module finished: [2022-07-27 19:18:42] (UTC), it is [2022-07-27 22:18:42] local time
```

</details>

#### Отменить ордера и закрыть позиции

Идентификаторы ордеров и тикеры инструментов, по которым открыты позиции, можно узнать в портфеле клиента, запустив команду `tksbrokerapi --overview`. Они будут нужны для операций ниже.

Для закрытия одного ордера любого типа по его ID можно использовать ключ `--close-order` (`--cancel-order`), после которого указать уникальный идентификатор ордера. Для закрытия ордеров по списку, можно использовать аналогичный ключ `--close-orders` (`--cancel-orders`), после которого перечислить все идентификаторы ордеров.

Для закрытия ранее открытой позиции (как в "лонг", так и в "шорт") используется ключ `--close-trade` (`--cancel-trade`), перед которым следует указать тикер инструмента с ключом `--ticker`. По факту открывается рыночный ордер с направлением, противоположным открытой позиции. Для закрытия позиций по нескольким инструментам, можно использовать аналогичный ключ `--close-trades` (`--cancel-trades`), после которого перечислить нужные тикеры (ключ `--ticker` уже не требуется).

Также можно использовать более общий ключ `--close-all` (`--cancel-all`). Если указать его без параметров, то будет выполнена попытка закрытия всех инструментов и ордеров, кроме заблокированных или недоступных для торгов. Сначала будут закрыты все ордера, иначе, например, лимитные ордера могут блокировать закрытие части доступных объёмов у инструментов. Затем по-порядку будут закрываться позиции по всем инструментам: акциям, облигациям, фондам и фьючерсам. Этот ключ более удобен, когда требуется экстренно закрыть все позиции, чем выполнять эти операции по очереди.

❗ Важно отметить, что в текущей версии TKSBrokerAPI открытые позиции по валютам не будут закрыты с ключом `--close-all` (`--cancel-all`). Это связано с тем, что остальные инструменты могут использовать различные базовые валюты. Кроме того, пользователь может не хотеть сокращения своих валютных позиций, чтобы покупать на эти средства другие инструменты в будущем. При необходимости позиции по валютам можно закрыть вручную, используя ключи `--buy`, `--sell`, `--close-trade` или `--close-trades`.

Для выборочного сокращения позиций, можно использовать ключ `--close-all` (`--cancel-all`), после которого перечислить один или более типов инструментов, разделённых пробелами:
- `orders` — закрыть все ордера (и лимитные, и стоп-ордера),
- `shares` — закрыть все позиции по акциям,
- `bonds` — закрыть все позиции по облигациям,
- `etfs` — закрыть все позиции по фондам,
- `futures` — закрыть все позиции по фьючерсам,
- но, нельзя указывать `currencies` — закрыть все позиции по валютам, из-за причин, описанных выше.

<details>
  <summary>Команда для отмены одного стоп-ордера по его идентификатору</summary>

```commandline
$ tksbrokerapi -v 10 --cancel-order ********-****-****-****-************

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 23:16:55,978] TKSBrokerAPI module started at: [2022-07-27 20:16:55] (UTC), it is [2022-07-27 23:16:55] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 23:16:55,979] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 23:16:55,980] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 23:16:55,981] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 23:16:55,982] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 23:16:55,983] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:16:55,989] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:16:55,989] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:16:55,989] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:16:55,989] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:16:55,989] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:1069 DEBUG   [2022-07-27 23:16:56,959] Requesting current actual pending orders. Wait, please...
TKSBrokerAPI.py     L:1075 DEBUG   [2022-07-27 23:16:57,077] [1] records about pending orders successfully received
TKSBrokerAPI.py     L:1086 DEBUG   [2022-07-27 23:16:57,078] Requesting current actual stop orders. Wait, please...
TKSBrokerAPI.py     L:1092 DEBUG   [2022-07-27 23:16:57,187] [6] records about stop orders successfully received
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:16:57,188] Cancelling stop order with ID: [********-****-****-****-************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:16:57,317] Success time marker received from server: [2022-07-27T20:16:57.288786707Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:16:57,318] Stop order with ID [********-****-****-****-************] successfully cancel
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 23:16:57,319] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 23:16:57,319] TKSBrokerAPI module work duration: [0:00:01.340621]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 23:16:57,320] TKSBrokerAPI module finished: [2022-07-27 20:16:57] (UTC), it is [2022-07-27 23:16:57] local time
```

</details>

<details>
  <summary>Команда для закрытия позиции по фонду (пример неудачной попытки, так как рынок уже закрыт)</summary>

```commandline
$ tksbrokerapi -v 10 --ticker TGLD --close-trade

TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 23:20:32,745] TKSBrokerAPI module started at: [2022-07-27 20:20:32] (UTC), it is [2022-07-27 23:20:32] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 23:20:32,746] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 23:20:32,746] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 23:20:32,746] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 23:20:32,747] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 23:20:32,747] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:20:32,751] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:20:32,751] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:20:32,752] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:20:32,752] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:20:32,752] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:1035 DEBUG   [2022-07-27 23:20:34,316] Requesting current actual user's portfolio. Wait, please...
TKSBrokerAPI.py     L:1041 DEBUG   [2022-07-27 23:20:34,468] Records about user's portfolio successfully received
TKSBrokerAPI.py     L:1052 DEBUG   [2022-07-27 23:20:34,469] Requesting current open positions in currencies and instruments. Wait, please...
TKSBrokerAPI.py     L:1058 DEBUG   [2022-07-27 23:20:34,582] Records about current open positions successfully received
TKSBrokerAPI.py     L:1069 DEBUG   [2022-07-27 23:20:34,583] Requesting current actual pending orders. Wait, please...
TKSBrokerAPI.py     L:1075 DEBUG   [2022-07-27 23:20:34,682] [1] records about pending orders successfully received
TKSBrokerAPI.py     L:1086 DEBUG   [2022-07-27 23:20:34,683] Requesting current actual stop orders. Wait, please...
TKSBrokerAPI.py     L:1092 DEBUG   [2022-07-27 23:20:34,793] [5] records about stop orders successfully received
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:34,805] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:34,907] Requesting current prices for instrument with ticker [POSI] and FIGI [TCS00A103X66]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:34,993] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:35,077] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:35,192] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:2264 DEBUG   [2022-07-27 23:20:35,285] All opened instruments by it's tickers names: ['EUR_RUB__TOM', 'CNYRUB_TOM', 'CHFRUB_TOM', 'GBPRUB_TOM', 'TRYRUB_TOM', 'USD000UTSTOM', 'HKDRUB_TOM', 'POSI', 'IBM', 'RU000A101YV8', 'TGLD']
TKSBrokerAPI.py     L:2290 DEBUG   [2022-07-27 23:20:35,286] Closing trade of instrument: ticker [TGLD], FIGI[BBG222222222], lots [2700]. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:20:35,286] Requesting current prices for instrument with ticker [TGLD] and FIGI [BBG222222222]...
TKSBrokerAPI.py     L:2184 DEBUG   [2022-07-27 23:20:35,386] Opening [Sell] market order: ticker [TGLD], FIGI [BBG222222222], lots [27.0], TP [0.0000], SL [0.0000], expiration date of TP/SL orders [Undefined]. Wait, please... TKSBrokerAPI.py     L:358  DEBUG   [2022-07-27 23:20:35,485]     - not oK status code received: [400] {"code":3,"message":"instrument is not available for trading","description":"30079"}
TKSBrokerAPI.py     L:368  ERROR   [2022-07-27 23:20:35,486] Not `oK` status received from broker server!
TKSBrokerAPI.py     L:369  ERROR   [2022-07-27 23:20:35,486]     - message: [400] {"code":3,"message":"instrument is not available for trading","description":"30079"}
TKSBrokerAPI.py     L:2206 WARNING [2022-07-27 23:20:35,487] Not `oK` status received! Market order not created. See full debug log or try again and open order later.
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 23:20:35,488] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 23:20:35,488] TKSBrokerAPI module work duration: [0:00:02.742544]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 23:20:35,488] TKSBrokerAPI module finished: [2022-07-27 20:20:35] (UTC), it is [2022-07-27 23:20:35] local time
```

</details>

<details>
  <summary>Команда для отмены всех ордеров и закрытия позиций по незаблокированным акциям</summary>

```commandline
$ tksbrokerapi --debug-level=10 --close-all orders shares
TKSBrokerAPI.py     L:2804 DEBUG   [2022-07-27 23:25:36,481] TKSBrokerAPI module started at: [2022-07-27 20:25:36] (UTC), it is [2022-07-27 23:25:36] local time
TKSBrokerAPI.py     L:198  DEBUG   [2022-07-27 23:25:36,482] Bearer token for Tinkoff OpenApi set up from environment variable `TKS_API_TOKEN`. See https://tinkoff.github.io/investAPI/token/
TKSBrokerAPI.py     L:210  DEBUG   [2022-07-27 23:25:36,483] String with user's numeric account ID in Tinkoff Broker set up from environment variable `TKS_ACCOUNT_ID`
TKSBrokerAPI.py     L:240  DEBUG   [2022-07-27 23:25:36,484] Broker API server: https://invest-public-api.tinkoff.ru/rest
TKSBrokerAPI.py     L:411  DEBUG   [2022-07-27 23:25:36,485] Requesting all available instruments from broker for current user token. Wait, please...
TKSBrokerAPI.py     L:412  DEBUG   [2022-07-27 23:25:36,485] CPU usages for parallel requests: [7]
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:25:36,492] Requesting available [Currencies] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:25:36,492] Requesting available [Shares] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:25:36,492] Requesting available [Bonds] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:25:36,492] Requesting available [Etfs] list. Wait, please...
TKSBrokerAPI.py     L:389  DEBUG   [2022-07-27 23:25:36,492] Requesting available [Futures] list. Wait, please...
TKSBrokerAPI.py     L:1035 DEBUG   [2022-07-27 23:25:37,568] Requesting current actual user's portfolio. Wait, please...
TKSBrokerAPI.py     L:1041 DEBUG   [2022-07-27 23:25:37,742] Records about user's portfolio successfully received
TKSBrokerAPI.py     L:1052 DEBUG   [2022-07-27 23:25:37,743] Requesting current open positions in currencies and instruments. Wait, please...
TKSBrokerAPI.py     L:1058 DEBUG   [2022-07-27 23:25:37,831] Records about current open positions successfully received
TKSBrokerAPI.py     L:1069 DEBUG   [2022-07-27 23:25:37,832] Requesting current actual pending orders. Wait, please...
TKSBrokerAPI.py     L:1075 DEBUG   [2022-07-27 23:25:37,934] [1] records about pending orders successfully received
TKSBrokerAPI.py     L:1086 DEBUG   [2022-07-27 23:25:37,934] Requesting current actual stop orders. Wait, please...
TKSBrokerAPI.py     L:1092 DEBUG   [2022-07-27 23:25:38,049] [5] records about stop orders successfully received
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:25:38,058] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:25:38,165] Requesting current prices for instrument with ticker [POSI] and FIGI [TCS00A103X66]...
TKSBrokerAPI.py     L:2663 DEBUG   [2022-07-27 23:25:38,534] Closing all available ['orders', 'shares']. Currency positions you must closes manually using buy or sell operations! Wait, please...
TKSBrokerAPI.py     L:1069 DEBUG   [2022-07-27 23:25:38,535] Requesting current actual pending orders. Wait, please...
TKSBrokerAPI.py     L:1075 DEBUG   [2022-07-27 23:25:38,639] [1] records about pending orders successfully received
TKSBrokerAPI.py     L:1086 DEBUG   [2022-07-27 23:25:38,639] Requesting current actual stop orders. Wait, please...
TKSBrokerAPI.py     L:1092 DEBUG   [2022-07-27 23:25:38,774] [5] records about stop orders successfully received
TKSBrokerAPI.py     L:2636 INFO    [2022-07-27 23:25:38,775] Found: [1] opened pending and [5] stop orders. Let's trying to cancel it all. Wait, please...
TKSBrokerAPI.py     L:2591 DEBUG   [2022-07-27 23:25:38,776] Cancelling pending order with ID: [************]. Wait, please...
TKSBrokerAPI.py     L:2599 DEBUG   [2022-07-27 23:25:38,939] Success time marker received from server: [2022-07-27T20:25:38.908221Z] (UTC)
TKSBrokerAPI.py     L:2600 INFO    [2022-07-27 23:25:38,940] Pending order with ID [************] successfully cancel
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:25:38,941] Cancelling stop order with ID: [********-****-****-****-************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:25:39,201] Success time marker received from server: [2022-07-27T20:25:39.171270508Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:25:39,202] Stop order with ID [********-****-****-****-************] successfully cancel
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:25:39,202] Cancelling stop order with ID: [********-****-****-****-************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:25:39,336] Success time marker received from server: [2022-07-27T20:25:39.306369844Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:25:39,337] Stop order with ID [********-****-****-****-************] successfully cancel
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:25:39,337] Cancelling stop order with ID: [********-****-****-****-************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:25:39,438] Success time marker received from server: [2022-07-27T20:25:39.410229318Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:25:39,439] Stop order with ID [********-****-****-****-************] successfully cancel
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:25:39,439] Cancelling stop order with ID: [********-****-****-****-************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:25:39,565] Success time marker received from server: [2022-07-27T20:25:39.534114123Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:25:39,566] Stop order with ID [********-****-****-****-************] successfully cancel
TKSBrokerAPI.py     L:2606 DEBUG   [2022-07-27 23:25:39,567] Cancelling stop order with ID: [************]. Wait, please...
TKSBrokerAPI.py     L:2614 DEBUG   [2022-07-27 23:25:39,745] Success time marker received from server: [2022-07-27T20:25:39.714517992Z] (UTC)
TKSBrokerAPI.py     L:2615 INFO    [2022-07-27 23:25:39,746] Stop order with ID [************] successfully cancel
TKSBrokerAPI.py     L:2325 DEBUG   [2022-07-27 23:25:39,747] Instrument tickers with type [Shares] that will be closed: ['POSI', 'IBM']
TKSBrokerAPI.py     L:2264 DEBUG   [2022-07-27 23:25:39,747] All opened instruments by it's tickers names: ['EUR_RUB__TOM', 'CNYRUB_TOM', 'CHFRUB_TOM', 'GBPRUB_TOM', 'TRYRUB_TOM', 'USD000UTSTOM', 'HKDRUB_TOM', 'POSI', 'IBM', 'RU000A101YV8', 'TGLD']
TKSBrokerAPI.py     L:2290 DEBUG   [2022-07-27 23:25:39,748] Closing trade of instrument: ticker [POSI], FIGI[TCS00A103X66], lots [1]. Wait, please...
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:25:39,749] Requesting current prices for instrument with ticker [POSI] and FIGI [TCS00A103X66]...
TKSBrokerAPI.py     L:2184 DEBUG   [2022-07-27 23:25:39,855] Opening [Sell] market order: ticker [POSI], FIGI [TCS00A103X66], lots [1.0], TP [0.0000], SL [0.0000], expiration date of TP/SL orders [Undefined]. Wait, please...
TKSBrokerAPI.py     L:358  DEBUG   [2022-07-27 23:25:39,947]     - not oK status code received: [400] {"code":3,"message":"instrument is not available for trading","description":"30079"}
TKSBrokerAPI.py     L:368  ERROR   [2022-07-27 23:25:39,948] Not `oK` status received from broker server!
TKSBrokerAPI.py     L:369  ERROR   [2022-07-27 23:25:39,948]     - message: [400] {"code":3,"message":"instrument is not available for trading","description":"30079"}
TKSBrokerAPI.py     L:2206 WARNING [2022-07-27 23:25:39,949] Not `oK` status received! Market order not created. See full debug log or try again and open order later.
TKSBrokerAPI.py     L:2290 DEBUG   [2022-07-27 23:25:39,949] Closing trade of instrument: ticker [IBM], FIGI[BBG000BLNNH6], lots [2], blocked [1]. Wait, please...
TKSBrokerAPI.py     L:2300 WARNING [2022-07-27 23:25:39,950] Just for your information: there are [1] lots blocked for instrument [IBM]! Available only [1.0] lots to closing trade.
TKSBrokerAPI.py     L:798  DEBUG   [2022-07-27 23:25:39,950] Requesting current prices for instrument with ticker [IBM] and FIGI [BBG000BLNNH6]...
TKSBrokerAPI.py     L:2184 DEBUG   [2022-07-27 23:25:40,042] Opening [Sell] market order: ticker [IBM], FIGI [BBG000BLNNH6], lots [1.0], TP [0.0000], SL [0.0000], expiration date of TP/SL orders [Undefined]. Wait, please...
TKSBrokerAPI.py     L:2202 INFO    [2022-07-27 23:25:40,685] [Sell] market order [447747151970] was executed: ticker [IBM], FIGI [BBG000BLNNH6], lots [1.0]. Total order price: [128.8900 usd] (with commission: [0.04 usd]). Average price of lot: [128.89 usd]
TKSBrokerAPI.py     L:3034 DEBUG   [2022-07-27 23:25:40,686] All operations with Tinkoff Server using Open API are finished success (summary code is 0).
TKSBrokerAPI.py     L:3039 DEBUG   [2022-07-27 23:25:40,686] TKSBrokerAPI module work duration: [0:00:04.204806]
TKSBrokerAPI.py     L:3042 DEBUG   [2022-07-27 23:25:40,687] TKSBrokerAPI module finished: [2022-07-27 20:25:40] (UTC), it is [2022-07-27 23:25:40] local time
```

</details>

### Как python API через импорт модуля TKSBrokerAPI

Полная документация по всем доступным свойствам и методам класса `TKSBrokerAPI.TinkoffBrokerServer()` находится [по ссылке](https://tim55667757.github.io/TKSBrokerAPI/docs/tksbrokerapi/TKSBrokerAPI.html). Соответствие ключей и методов также можно посмотреть в разделе ["Основные возможности"](#Основные-возможности).

С помощью модуля TKSBrokerAPI вы можете реализовать на языке Python любой торговый сценарий. Чтобы не использовалось в качестве основной системы принятия торговых решений о покупке или продаже (технический анализ, нейросети, парсинг отчётов или слежение за сделками других трейдеров), всё равно вам потребуется выполнять торговые операции: выставлять ордера, открывать и закрывать сделки. Модуль `TKSBrokerAPI` будет выступать как посредник между кодом с логикой торгов и инфраструктурой брокера Тинькофф Инвестиции, а также выполнять рутинные задачи от вашего имени в [брокерском аккаунте](http://tinkoff.ru/sl/AaX1Et1omnH).

❗ **Важное замечание**: модуль TKSBrokerAPI не предназначен для высокочастотной (HFT) торговли, из-за системы динамического формирования лимитов для пользователей TINKOFF INVEST API (подробнее [по ссылке](https://tinkoff.github.io/investAPI/limits/)). В среднем, это 50-300 запросов в секунду, в зависимости от их типа, что очень мало для требований к скоростям HFT (есть [несколько рекомендаций](https://tinkoff.github.io/investAPI/speedup/) по ускорению исполнения поручений). Однако вы вполне можете использовать его для автоматизации своих интрадей, кратко-, средне- и долгосрочных торговых стратегий.

#### Пример реализации абстрактного сценария

В данной документации не хочется акцентировать внимание на конкретных торговых сценариях, а только лишь указать возможности для их автоматизации. Поэтому, давайте рассмотрим один простой, но полностью вымышленный сценарий, и реализуем его при помощи модуля TKSBrokerAPI. Действия будут следующие:

- запрос текущего портфолио клиента и определение доступных для торговли средств;
- запрос стакана цен с глубиной 20 для выбранного инструмента, например, акции с тикером `IBM`;
- если ранее инструмент куплен не был, то проверить:
  - если в стакане объёмы на покупку больше объёмов на продажу хотя бы на 50%, то купить 1 акцию по рынку и выставить тейк-профит как стоп-ордер на 5% выше текущей цены покупки со сроком действия до отмены;
- если инструмент имеется в списке открытых позиций, то проверить:
   - если текущая цена выше средней цены позиции на 3%, то выставить тейк-профит как отложенный лимитный ордер ещё на 0.05% выше текущей цены, чтобы позиция закрылась с профитом с большой вероятностью в течении текущей сессии.
- напечатать пользователю в консоль текущее состояние портфеля.

Для понимания примера сохраните и запустите скрипт под спойлером ниже. Не забудьте перед этим получить token и узнать свой accountId (см. раздел ["Аутентификация"](#Аутентификация)).

<details>
  <summary>Торговый сценарий на python с использованием модуля TKSBrokerAPI</summary>

```python

```
</details>

<details>
  <summary>Результаты запуска сценария</summary>

```commandline

```

</details>


На этом всё, вопросы задавайте в разделе 👉 [**Issues**](https://github.com/Tim55667757/TKSBrokerAPI/issues/new) 👈, пожалуйста.

🚀 Успехов вам в автоматизации биржевой торговли! И профита!

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20TKSBrokerAPI&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FTKSBrokerAPI%2F&quickpay=shop&account=410015019068268)
