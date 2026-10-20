[app]

title = MobileIDE
package.name = mobileide
package.domain = org.igmunt
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf
version = 0.1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 25b
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 0