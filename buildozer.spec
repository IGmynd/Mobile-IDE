[app]

# (str) Title of your application
title = MobileIDE

# (str) Package name
package.name = mobileide

# (str) Package domain (needed for android/ios packaging)
package.domain = org.igmynd

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0

# (str) The Android API version to run on
android.api = 33

# (int) The minimum API version to run on
android.minapi = 24

# (int) The Android NDK version to build with
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Accept SDK licenses automatically
android.accept_sdk_license = True

# (str) Path to the python-for-android repository (fixes the timeout)
p4a.source_dir = ./python-for-android

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (list) Permissions
# android.permissions = INTERNET

# (list) Pattern to whitelist for the android application
# android.whitelist =

# (str) Android logcat filters
# android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
# android.add_src = foo.java,bar.java,path/to/more

# (str) python-for-android branch to use, defaults to master
# p4a.branch = develop

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes = 

# (str) Filename to the hook for p4a
# p4a.hook = 

# (str) Provide the path to the library dependencies
# p4a.stl = gnustl

# (str) Android NDK version to use
# android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support.
# android.ndk_api = 21