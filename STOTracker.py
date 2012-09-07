#!/usr/bin/env python

from datetime import date, datetime, timedelta

# Functions to determine when events happen
def type_1(now, reference, duration, repeat):
    delta = now.date() - reference

    # This event will next start on this hour
    start_hour = 7 - (delta.days % repeat)
    while start_hour + duration - 1 < now.hour:
        start_hour += repeat

    if start_hour > 23:
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0,
                                                     second=0, microsecond=0)
        consumed = tomorrow - now
        (running, time) = type_1(tomorrow, reference, duration, repeat)
        return (running, time+consumed)
    if now.hour in range(start_hour, start_hour+duration):
        end = now.replace(hour=start_hour+duration, minute=0,
                          second=0, microsecond=0)
        return (True, end-now)
    else:
        start = now.replace(hour=start_hour, minute=0,
                          second=0, microsecond=0)
        return (False, start-now)


events = [{'name': 'Vault', 'ref': date(2012, 9, 3), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=8)},
          {'name': 'Fleet Marks', 'ref': date(2012, 9, 4), 'pattern': type_1,
           'arguments': dict(duration=2, repeat=8)},
          {'name': 'Mirror', 'ref': date(2012, 9, 5), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=8)},
          {'name': 'Academy', 'ref': date(2012, 9, 6), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=8)},
          {'name': 'Crafting', 'ref': date(2012, 9, 7), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
          {'name': 'Path to 2409', 'ref': date(2012, 8, 31), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
          {'name': 'Officer Reports', 'ref': date(2012, 9, 8), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
          {'name': 'Mining', 'ref': date(2012, 9, 1), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
          {'name': 'Tour the Universe', 'ref': date(2012, 9, 9), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
          {'name': 'Multiphasic', 'ref': date(2012, 9, 2), 'pattern': type_1,
           'arguments': dict(duration=1, repeat=16)},
         ]

active = []
inactive = []

now = datetime.now().replace(microsecond=0)
for event in events:
    details = event['pattern'](now, event['ref'], **event['arguments'])
    if details[0]:
        active.append(dict(name=event['name'], end=details[1]))
    else:
        inactive.append(dict(name=event['name'], start=details[1]))

active.sort(key=lambda x: x['end'])
inactive.sort(key=lambda x: x['start'])

print('Active Events')
for event in active:
    print("\t%s (%s left)" % (event['name'], event['end']))
print('Upcoming Events')
for event in inactive:
    print("\t%s (%s)" % (event['name'], event['start']))
