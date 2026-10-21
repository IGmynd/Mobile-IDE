[app]
title = MobileIDE
package.name = mobileide
package.domain = org.igmynd
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2
orientation = portrait

# Жёстко фиксируем Python 3.11 и добавляем jnius
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,jnius>=1.4.0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# Отключаем байт-компиляцию для ускорения
android.no-byte-compile-python = True