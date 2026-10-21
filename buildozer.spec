[app]
title = MobileIDE
package.name = mobileide
package.domain = org.igmynd
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.3

# Возвращаем стабильную связку Python 3.11
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,jnius>=1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

android.no-byte-compile-python = True
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE