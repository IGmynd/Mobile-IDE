[app]
title = MobileIDE
package.name = mobileide
package.domain = org.igmynd
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Явно фиксируем Python 3.11 — стабильная версия для Kivy 2.3.0
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.source_dir = ./python-for-android