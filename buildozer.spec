[app]
title = MobileIDE
package.name = mobileide
package.domain = org.igmynd
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.3

# Стабильная связка: Python 3.9 и явное указание jnius
requirements = python3==3.9.18,hostpython3==3.9.18,kivy==2.3.0,jnius>=1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

# Отключаем байт-компиляцию для ускорения
android.no-byte-compile-python = True

# Разрешения для экспорта/импорта
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE