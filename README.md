# PyCaptura: Um keylogger para o X Window System

## Como usar
O PyCaptura já vem com um simples keylogger, que imprime na tela tudo o que é digitado. Para rodá-lo digite:
    `python pycaptura.py`

***

Caso deseje fazer algo além imprimir a captura do teclado na tela basta criar sua própria classe de keylogger, sobrescrever o KeyboardCapture:
```python
from pycaptura import MyKeylogger


class MyKeylogger(KeyboardCapture):
    def log_keys(self, has_pressed, pressed_keys, key_modifiers):
        # send keys via email, log to file etc.
        ...
```
