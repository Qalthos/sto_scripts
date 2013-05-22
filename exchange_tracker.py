#!/usr/bin/env python
# exchange_tracker.py: A Star Trek Online Dilithium Exchange tracker
#
# To use: load your exchange history, and scroll to the bottom
#
# Caveats:
#  * There is no way to add  or remove dilithium to your reserves at present.
#  * You must manually add stipends by buying 500 Zen at a rate of 0.
#  * Selling Zen at a rate of 0 will remove it from the pool of available Zen.

from __future__ import division

import os
from collections import defaultdict
from datetime import date

zen_store = defaultdict(int)
dil_store = defaultdict(int)

# For Python 2.x & 3.x coexistence
try:
    input = raw_input
except:
    pass

def transact_simple(zen, rate):
    if (rate < 0):
        # Dilithium rate cannot be negative
        return False

    dil = -(zen * rate)

    if zen < 0:
        # we are selling zen
        dil_store[rate] += dil

        if (not zen_store):
            return True

        # Remove (whole number) zen from each bucket until no more dilithium
        # is left to buy with
        for known in sorted(list(zen_store.keys()), reverse=True):
            if dil > known:
                if dil > known * zen_store[known]:
                    dil -= known * zen_store[known]
                    zen += zen_store[known]
                    del zen_store[known]
                else:
                    change = dil / known
                    dil -= change * known
                    zen += change
                    zen_store[known] -= change
            if zen >= 0 or dil == 0:
                break
        if dil > rate:
            change = dil / rate
            zen += change
            zen_store[0] -= change
            dil -= rate * change

        # zen_store[0] gets any leftover (or unpaid) zen
        if zen:
            zen_store[0] += zen
        if dil:
            dil_store[0] += dil

    elif zen > 0:
        # we are buying zen
        zen_store[rate] += zen

        if dil == 0:
            # Wooooo, free Zen!
            return True

        # Remember kids, negative zen means negative dilithium!
        for known in sorted(list(dil_store.keys())):
            if dil <= -dil_store[known]:
                dil += dil_store[known]
                del dil_store[known]
            else:
                dil_store[known] += dil
                dil = 0
                break

    return True

    
def transact_strict(zen, rate):
    if (rate < 0):
        # Dilithium rate cannot be negative
        return False

    dil = -(zen * rate)
    best = 0
    extra = 0

    if zen == 0:
        # nothing happens, but it still succeeds
        return True
    elif zen < 0:
        # we are selling zen
        if (not zen_store) or (zen == 0):
            dil_store[rate] += dil
            return True
        for known in sorted(list(zen_store.keys())):
            if rate < known:
                break
            if zen_store[known]:
                best = known

        if (zen_store[best] < -zen) and not (best == 0):
            extra = zen + zen_store[best]
            zen = -zen_store[best]
            dil = -zen * rate

        zen_store[best] += zen
        if not zen_store[best]:
            del zen_store[best]
        dil_store[rate] += dil

    elif zen > 0:
        # we are buying zen
        if (not dil_store) or (dil == 0):
            zen_store[rate] += zen
            return True
        for known in sorted(list(dil_store.keys())):
            if rate > known:
                break
            if dil_store[known]:
                best = known

        if (dil_store[best] < -dil) and not (best == 0):
            extra = -(dil + dil_store[best]) / rate
            dil = -dil_store[best]
            zen = -dil / rate

        zen_store[rate] += zen
        dil_store[best] += dil
        if not dil_store[best]:
            del dil_store[best]

    transact(extra, rate)
    return True


def print_stores():
    for name, store in [('zen', zen_store), ('dil', dil_store)]:
        stored_value = map(lambda key: str((key, store[key])), sorted(store))
        print(name + ': ' + ' '.join(stored_value))


if __name__ == "__main__":
    data_file = os.path.join(os.path.split(__file__)[0], 'history.csv')
    transact = transact_simple
    if os.path.exists(data_file):
        # Load data contents to dictionaries
        with open(data_file) as data_csv:
            next(data_csv)
            for line in data_csv:
                zen, dil = line.split(',')[0:2]
                transact(int(zen), int(dil))
    try:
        while True:
            print_stores()
            curr = 0
            total = 0
            for rate, zen in zen_store.items():
                curr += float(zen)
                total += float(rate)*float(zen)
            print("%d Zen @ %f" % (curr, total/curr if not curr == 0 else 0))
            curr = 0
            total = 0
            for rate, dil in dil_store.items():
                curr += float(dil)
                if not float(rate) == 0:
                    total += float(dil)/float(rate)
            print("%d dilithium @ %f" % (curr, curr/total if not total == 0 else 0))
            try:
                zen = int(input("How much zen? "))
                rate = int(input("How much dil per zen? "))
            except ValueError:
                continue

            if transact(zen, rate):
                with open(data_file, 'a') as data_csv:
                    today = date.today().isoformat()
                    data_csv.write('%d,%d,%s\n' % (zen, rate, today))
            else:
                print("That didn't work")

    except KeyboardInterrupt:
        print()
