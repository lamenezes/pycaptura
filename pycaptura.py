# -*- encoding:utf-8 -*-

import ctypes
from ctypes import cdll
from ctypes.util import find_library
import time
from threading import Thread

x11 = cdll.LoadLibrary(find_library('X11'))
display = x11.XOpenDisplay()
keys_return = ctypes.create_string_buffer(32)


class KeyboardCapture(Thread):
    acentos = {
        (15, 1): '^',
        (49, 0): '`',
        (49, 1): '~',
        (48, 0): '´',
        (48, 1): '¨',
    }

    modifier_keys = {
        'ctrl': [37, 105],
        'shift': [50, 62],
        'caps_lock': 66,
        'alt': [64, 108],
        'alt_Gr': 108,
        'super': 133,
    }

    def __init__(self, sleep_interval=0.005):
        super(KeyboardCapture, self).__init__()

        self.sleep_interval = sleep_interval
        self.last_pressed = 0
        self.last_raw_pressed = []
        self.caps_lock = False

    def parse_keys(self, keys):
        """
        Parses the result of the function x11.XQueryKeymap

        The function returns a list with 32 integers and each integer represents
        a byte. For example let's suppose the function returns the following list:

            >>> keymap_return = [8] + ([0] * 31)
            >>> bin(keymap_return[0])
            '0b100'

        This means the 3rd key of the keyboard logical representation (this is
        called keycode) has been pressed. The keycode value is 2 (starting from 0)

        Now another example, just to things be real clear:

            >>> keymap_return = [0, 0, 0, 128] + ([0] * 28)
            >>> bin(keymap_return[3])
            '0b100000000'

        This time the 31st key has been pressed, we can see that because the
        first 3 bytes aren't flagged, but the 7th bit of the 4th byte is.

        (Obvious) Note: multiple keys can be pressed at the same time
        """

        keys = [ord(key) for key in keys]
        modifier = 0
        mod_pressed = {
            'ctrl': False, 'shift': False, 'alt': False, 'alt_Gr': False, 'super': False
        }
        keys_pressed = []
        raw_pressed = []

        for i, num in enumerate(keys):
            if not num:
                continue

            binary = bin(num)[2:][::-1]
            for j, bit in enumerate(binary):
                if bit == '1':
                    raw_pressed.append((8 * i) + j)

        # FIXME: the following does not record multiple occurrence of the same key
        #        when it has been pressed down for a long time
        pressed = list(set(raw_pressed).difference(self.last_raw_pressed))
        has_pressed = bool(pressed)
        self.last_raw_pressed = raw_pressed

        if has_pressed:
            if self.modifier_keys['caps_lock'] in raw_pressed:
                self.caps_lock = not self.caps_lock

        if self.caps_lock:
            modifier = 1
        else:
            modifier = 0

        if self.modifier_keys['alt_Gr'] in raw_pressed:
            mod_pressed['alt_Gr'] = True

        if self.modifier_keys['super'] in raw_pressed:
            mod_pressed['super'] = True

        for key in raw_pressed:
            if key in self.modifier_keys['shift']:
                if modifier == 1:
                    modifier = 0
                elif modifier == 0:
                    modifier = 1
                mod_pressed['shift'] = True

            if key in self.modifier_keys['ctrl']:
                mod_pressed['ctrl'] = True

            if key in self.modifier_keys['alt']:
                mod_pressed['alt'] = True

        for keycode in pressed:
            key = self.keycode_to_string(keycode, modifier)
            if not key:
                if self.caps_lock and modifier == 1:
                    modifier = 0
                elif self.caps_lock and modifier == 0:
                    modifier = 1
                key = self.acentos.get((keycode, modifier))
                if not key:
                    key = (keycode, modifier)
            keys_pressed.append(key)

        self.last_pressed = keys_pressed

        return has_pressed, keys_pressed, mod_pressed

    def keycode_to_string(self, keycode, modifier):
        keycode = ctypes.c_ubyte(keycode)
        modifier = ctypes.c_int(modifier)
        keysym = ctypes.c_ulong()
        keysym = x11.XKeycodeToKeysym(display, keycode, modifier)
        keysym_to_string = x11.XKeysymToString
        keysym_to_string.restype = ctypes.c_char_p
        return keysym_to_string(keysym)

    def run(self):
        while True:
            x11.XQueryKeymap(display, keys_return)
            has_pressed, pressed, mods = self.parse_keys(keys_return)
            if has_pressed:
                print u') A tecla [%s] foi apertada [%s]' % (pressed, mods)

            time.sleep(self.sleep_interval)


if __name__ == "__main__":
    capture = KeyboardCapture()
    capture.start()
