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


# For Python 2.x & 3.x coexistence
try:
    input = raw_input
except:
    pass

def transact(zen_store, zen, dil_store, rate):
    if (rate < 0) or (zen == 0):
        # Dilithium rate cannot be negative
        return (zen_store, dil_store)

    dil = -(zen * rate)

    if zen < 0:
        # we are selling zen
        dil_store[rate] += dil

        if (not zen_store):
            return (zen_store, dil_store)

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
            return (zen_store, dil_store)

        # Remember kids, negative zen means negative dilithium!
        for known in sorted(list(dil_store.keys())):
            if dil <= -dil_store[known]:
                dil += dil_store[known]
                del dil_store[known]
            else:
                dil_store[known] += dil
                dil = 0
                break

    return (zen_store, dil_store)


def print_stores(zen_store, dil_store):
    strings = []
    for name, store in [('zen', zen_store), ('dil', dil_store)]:
        details = []
        for key in sorted(store):
            details.append("(%d, %d)" % (key, store[key]))
        strings. append(name + ': ' + ', '.join(details))
    return '\n'.join(strings)


def load_history(data_file):
    zen_store = defaultdict(int)
    dil_store = defaultdict(int)
    if os.path.exists(data_file):
        # Load data contents to dictionaries
        with open(data_file) as data_csv:
            next(data_csv)
            for line in data_csv:
                zen, dil = line.split(',')
                zen_store, dil_store = transact(zen_store, int(zen), dil_store, int(dil))
    return (zen_store, dil_store)


if __name__ == "__main__":
    data_file = os.path.join(os.path.split(__file__)[0], 'history.csv')
    load_history(data_file)
    try:
        while True:
            print(print_stores(zen_store, dil_store))
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

            zen_store, dil_store = transact(zen_store, zen, dil_store, rate)
            with open(data_file, 'a') as data_csv:
                data_csv.write('%d,%d\n' % (zen, rate))

    except KeyboardInterrupt:
        print()
