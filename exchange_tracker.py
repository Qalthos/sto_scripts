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
import json
from collections import defaultdict

zen_store = defaultdict(int)
dil_store = defaultdict(int)

def transact(zen, rate):
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
            if dil_store[known]:
                best = known
            if rate > known:
                break

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

if __name__ == "__main__":
    data_file = os.path.join(os.path.split(__file__)[0], 'data.json')
    if os.path.exists(data_file):
        # Load data contents to dictionaries
        with open(data_file) as data_json:
            data = json.load(data_json)
            for key in data['zen']:
                zen_store[int(key)] = data['zen'][key]
            for key in data['dil']:
                dil_store[int(key)] = data['dil'][key]
    try:
        while True:
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
                zen = int(raw_input("How much zen? "))
                rate = int(raw_input("How much dil per zen? "))
            except ValueError:
                continue
            if not transact(zen, rate):
                print("That didn't work")
    except KeyboardInterrupt:
        print()
        print(zen_store)
        print(dil_store)
        with open(data_file, 'w') as data_json:
            json.dump(dict(zen=zen_store, dil=dil_store), data_json)
