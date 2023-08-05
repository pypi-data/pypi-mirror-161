# NYSE Calendar

This is a small library that calculates New York Stock Exchange's holiday. 

## Example (0)  List all NYSE holidays in 2022

```Python
from nysecalendar import NYSE_holidays

holidays = list(NYSE_holidays(datetime.date(
        2022, 1, 1), datetime.date(2022, 12, 31)))
```

## Example (1) List all NYSE tradingdays in 2022

```Python
from nysecalendar import NYSE_tradingdays

tradingdays = list(NYSE_tradingdays(datetime.date(
        2022, 1, 1), datetime.date(2022, 12, 31)))
```