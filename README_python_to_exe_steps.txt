Steps to convert python project to Windows exe file.

Before proper steps make sure you've installed "pyinstaller" by for example command "pip install pyinstaller".

INFO: remember to always use relative paths to loaded files, like in case of use method 'resource_path';
1. open terminal and make sure your location is project directory;
2. provide command "pyinstaller --onefile main.py" (it creates "build" and "dist" directory, and file "main.spec");
3. in created file main.spec add "('img/*','img')" to "Analysis" element "datas" so it looks "datas=[('img/*','img')]";
4. provide command "pyinstaller main.spec";
5. if all previous steps end with success in "dist" directory you can find prepared "main.exe" file;
INFO: if you run "main.exe" directly from "dist" directory without providing necessary files
      like "img" directory or "simulator.ini", executable file won't work;