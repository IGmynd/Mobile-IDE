[app]
title = MobileIDE
package.name = mobileide
package.domain = org.igmund

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
# Жестко фиксируем стабильную версию Kivy, чтобы сборщик не скачал сырую бету
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# --- Настройки Android ---
# Возвращаемся на стабильные версии, которые 100% дружат с python-for-android
android.api = 33
android.minapi = 24
android.ndk = 25b

# Оставляем только нужную архитектуру
android.archs = arm64-v8a

# Разрешения
android.permissions = INTERNET

# Автоматически принимаем лицензии
android.accept_sdk_license = True