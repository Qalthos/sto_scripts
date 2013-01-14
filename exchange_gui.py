#!/usr/bin/env python

from gi.repository import Gtk

class ExchangeWin(Gtk.Window):
    def __init__(self):
        super(ExchangeWin, self).__init__()
        # model on left for history
        self.current = Gtk.Label()
        zen_label = Gtk.Label('Zen:')
        self.zen = Gtk.Entry()
        rate_label = Gtk.Label('Dil per Zen:')
        self.rate = Gtk.Entry()
        self.go = Gtk.Button('Transact!')

        split = Gtk.Box(homogeneous=True)
        rsplit = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        zsplit = Gtk.Box()
        dsplit = Gtk.Box()

        self.add(split)
        #split.add(model)
        split.add(rsplit)
        rsplit.add(self.current)
        rsplit.add(zsplit)
        zsplit.add(zen_label)
        zsplit.add(self.zen)
        rsplit.add(dsplit)
        dsplit.add(rate_label)
        dsplit.add(self.rate)
        rsplit.add(self.go)

        self.show_all()


if __name__ == "__main__":
    win = ExchangeWin()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()

