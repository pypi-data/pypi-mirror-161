from dateutil import rrule
import datetime

# Generate ruleset for holiday observances on the NYSE


def NYSE_holidays(
        a=datetime.date.today(),
        b=datetime.date.today()+datetime.timedelta(days=365),
        includeing_weekend=False):
    rs = rrule.rruleset()
    # Include all potential holiday observances

    if includeing_weekend:
        rs.rrule(rrule.rrule(
            rrule.DAILY,
            dtstart=a,
            until=b,
            byweekday=(rrule.SA, rrule.SU)
        ))

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=1,
        bymonthday=1))        # New Years Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=1,
        bymonthday=2,
        byweekday=rrule.MO))  # New Years Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=1,
        byweekday=rrule.MO(3)))  # Martin Luther King Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=2,
        byweekday=rrule.MO(3)))  # Washington's Birthday

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        byeaster=-2))   # Good Friday

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=5,
        byweekday=rrule.MO(-1)))  # Memorial Day

    if a >= datetime.date(2022, 6, 19) or b >= datetime.date(2022, 6, 19):
        rs.rrule(rrule.rrule(
            rrule.YEARLY,
            dtstart=a,
            until=b,
            bymonth=6,
            bymonthday=20,
            byweekday=rrule.MO))  # Juneteenth

        rs.rrule(rrule.rrule(
            rrule.YEARLY,
            dtstart=a,
            until=b,
            bymonth=6,
            bymonthday=19))  # Juneteenth

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=7,
        bymonthday=3,
        byweekday=rrule.FR))  # Independence Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=7,
        bymonthday=4))  # Independence Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=7,
        bymonthday=5,
        byweekday=rrule.MO))  # Independence Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=9,
        byweekday=rrule.MO(1)))  # Labor Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=11,
        byweekday=rrule.TH(4)))  # Thanksgiving Day

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=12,
        bymonthday=24,
        byweekday=rrule.FR))  # Christmas

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b, bymonth=12,
        bymonthday=25))       # Christmas

    rs.rrule(rrule.rrule(
        rrule.YEARLY,
        dtstart=a,
        until=b,
        bymonth=12,
        bymonthday=26,
        byweekday=rrule.MO))  # Christmas

    if a <= datetime.date(2018, 12, 5) and b >= datetime.date(2018, 12, 5):
        rs.rrule(rrule.rrule(
            rrule.YEARLY,
            dtstart=datetime.date(2018, 12, 5),
            until=datetime.date(2018, 12, 5),
            bymonth=12,
            bymonthday=5))  # George H.W. Bush

    if a <= datetime.date(2012, 10, 29) and b >= datetime.date(2012, 10, 30):
        rs.rrule(rrule.rrule(
            rrule.YEARLY,
            dtstart=datetime.date(2012, 10, 29),
            until=datetime.date(2012, 10, 30),
            bymonth=10,
            bymonthday=29))  # Hurricane Sandy

        rs.rrule(rrule.rrule(
            rrule.YEARLY,
            dtstart=datetime.date(2012, 10, 29),
            until=datetime.date(2012, 10, 30),
            bymonth=10,
            bymonthday=30))  # Hurricane Sandy

    # Exclude potential holidays that fall on weekends
    if not includeing_weekend:
        rs.exrule(rrule.rrule(
            rrule.WEEKLY,
            dtstart=a,
            until=b,
            byweekday=(rrule.SA, rrule.SU)))

    return rs

# Generate ruleset for NYSE trading days
def NYSE_tradingdays(
        a=datetime.date.today(),
        b=datetime.date.today()+datetime.timedelta(days=365)):
    rs = rrule.rruleset()
    rs.rrule(rrule.rrule(rrule.DAILY, dtstart=a, until=b))

    # Exclude weekends and holidays
    rs.exrule(rrule.rrule(
        rrule.WEEKLY,
        dtstart=a,
        byweekday=(rrule.SA, rrule.SU)))
    rs.exrule(NYSE_holidays(a, b))

    return rs


if __name__ == '__main__':
    # Examples
    # List all NYSE holiday observances for 2022
    print("\nNYSE Holidays in 2022")
    for dy in NYSE_holidays(datetime.date(2022, 1, 1), datetime.date(2022, 12, 31)):
        print(dy.strftime('%b %d %Y'))
    print("\n")

    print("\nNYSE Holidays in 2022 includeing weekends")
    for dy in NYSE_holidays(datetime.date(2022, 1, 1), datetime.date(2022, 12, 31), includeing_weekend=True):
        print(dy.strftime('%b %d %Y'))
    print("\n")

    # List all NYSE trading days in 2022
    trading_days = sorted(list(NYSE_tradingdays(
        datetime.date(2022, 1, 1),
        datetime.date(2022, 12, 31))),
        reverse=False)

    for trading_day in trading_days:
        print(trading_day.strftime("%Y-%m-%d %A"))

    # Ten trade days before 2022-07-28
    print(list(NYSE_tradingdays(datetime.date(2021, 7, 28), datetime.date(2022, 7, 28)))[-11])

    # Ten trade days after 2022-07-28
    print(list(NYSE_tradingdays(datetime.date(2022, 7, 28), datetime.date(2023, 7, 28)))[10])

# Count NYSE trading days
#    print("\n\nTrading Days\n")
#    for yr in range(2015, 2022):
#        tdays = len(list(NYSE_tradingdays(datetime.datetime(
#            yr, 1, 1), datetime.datetime(yr, 12, 31))))
#        print("{0}  {1}".format(yr, tdays))

#    print(sorted(list(NYSE_tradingdays(
#        datetime.datetime(2008, 1, 1),
#        datetime.datetime(2022, 12, 31))),
#        reverse=True))
