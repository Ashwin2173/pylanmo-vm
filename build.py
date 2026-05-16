import os
import sys

print("Starting to build...")

if os.name == 'nt':
    is_success = os.system("pyinstaller --onefile lanmo.py")
    if is_success == 0:
        os.system(r'xcopy "dist\lanmo.exe" "C:\Program Files (x86)\Lasm\bin\" /I /Y')
        print("[ INFO ] Build successfully...")
else:
    print("Build in only supported for windows for now")
    sys.exit(1)
