#!/usr/bin/env python
"""
exchange_tracker.py: A Star Trek Online Dilithium Exchange tracker

To use: load your exchange history, and scroll to the bottom

Caveats:
 * There is no way to add  or remove dilithium to your reserves at present.
 * You must manually add stipends by buying 500 Zen at a rate of 0.
 * Selling Zen at a rate of 0 will remove it from the pool of available Zen.
"""

from __future__ import division, print_function

import os
from collections import defaultdict
from datetime import date
from operator import mul, floordiv as div

zen_store: dict[int, int] = defaultdict(int)
dil_store: dict[int, int] = defaultdict(int)


def transact_simple(zen: int, rate: int) -> bool:
    if rate < 0:
        # Dilithium rate cannot be negative
        return False

    dil = -(zen * rate)

    if zen < 0:
        # we are selling zen
        dil_store[rate] += dil

        if not zen_store:
            return True

        # Remove (whole number) zen from each bucket until no more dilithium
        # is left to buy with
        for known in sorted(list(zen_store.keys()), reverse=True):
            if dil > known:
                # We have enough dil to buy back at leas 1 zen @ $known
                if dil > known * zen_store[known]:
                    # We can even empty this bucket.
                    dil -= known * zen_store[known]
                    zen += zen_store[known]
                    del zen_store[known]
                else:
                    # We can buy back at most ($dil // $known) zen @ $known
                    change = dil // known
                    dil -= change * known
                    zen += change
                    zen_store[known] -= change
            if zen == 0:
                break
        else:
            zen_store[0] += zen

    elif zen > 0:
        # we are buying zen
        zen_store[rate] += zen

        if dil == 0:
            # Wooooo, free Zen!
            return True

        # Remember kids, negative zen means negative dilithium!
        for known in sorted(list(dil_store.keys())):
            # if we have enough dil to eradicate this key, do so
            if dil <= -dil_store[known]:
                dil += dil_store[known]
                del dil_store[known]
            # if not, just clear out dil
            else:
                dil_store[known] += dil
                dil = 0

            if dil == 0:
                break

    return True


def transact_strict(zen: int, rate: int) -> bool:
    if rate < 0:
        # Dilithium rate cannot be negative
        return False

    dil = -(zen * rate)
    best = 0
    extra = 0

    if zen == 0:
        # nothing happens, but it still succeeds
        return True

    if zen < 0:
        # we are selling zen
        if (not zen_store) or (zen == 0):
            dil_store[rate] += dil
            return True
        for known in sorted(list(zen_store.keys())):
            if rate < known:
                break
            if zen_store[known]:
                best = known

        if (zen_store[best] < -zen) and best != 0:
            extra = zen + zen_store[best]
            zen = -zen_store[best]
            dil = -zen * rate

        zen_store[best] += zen
        if not zen_store[best]:
            del zen_store[best]
        dil_store[rate] += dil

    elif zen > 0:
        # we are buying zen
        for known in sorted(list(dil_store.keys())):
            if rate > known:
                break
            if dil_store[known]:
                best = known
        else:
            # No existing dil value is less than our rate.
            best = 0

        if (dil_store[best] < -dil) and best != 0:
            extra = -(dil + dil_store[best]) // rate
            dil = -dil_store[best]
            zen = -dil // rate

        zen_store[rate] += zen
        dil_store[best] += dil
        if not dil_store[best]:
            del dil_store[best]

    transact(extra, rate)
    return True


def print_stores() -> None:
    for name, store, func in [('Zen', zen_store, mul),
                              ('dilithium', dil_store, div)]:
        total = sum(store.values())
        value = sum(func(store[rate], rate) for rate in store if not rate == 0)
        stored_values = [str(pair) for pair in sorted(store.items())]

        if total == 0 or value == 0:
            print("{} {}".format(total, name))
        else:
            dil_per_zen = max(total, value) / min(total, value)
            print("{} {} @ {} each".format(total, name, dil_per_zen))
        print(' '.join(stored_values))


def main() -> None:
    data_file = os.path.join(os.path.split(__file__)[0], 'history.csv')
    if os.path.exists(data_file):
        # Load data contents to dictionaries
        with open(data_file) as data_csv:
            next(data_csv)
            for line in data_csv:
                zen_in, dil_in = line.split(',')[0:2]
                transact(int(zen_in), int(dil_in))
    try:
        while True:
            print_stores()
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

    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == "__main__":
    transact = transact_simple
    main()
