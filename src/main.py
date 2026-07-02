
import time
import signal
import os

# Tüm sinyal maskelerini temizle, init süreci her sinyali kendisi almalı
# Kernel'dan gelen sinyal karmaşasını önler
signal.pthread_sigmask(signal.SIG_SETMASK, set())
# print, stdout'a yazarken hata veriyorsa bunu kapat
try:
    print("Hello World - Init Basariyla Calisti")
except:
    pass

# Sinyalleri hiç import etme, sadece sonsuz döngüye gir
# Python'ın signal modülüyle hiç muhatap olma
while True:
    time.sleep(100)
