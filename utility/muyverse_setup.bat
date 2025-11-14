@echo off
:: Step 1: Clean up downloaded files
echo Running cleanup script...
python "C:\Users\Muy\Muyverse Downloads\cleanup_muyverse_downloads.py" --path "C:\Users\Muy\Muyverse Downloads" --yes

:: Step 2: Create Long folders (1–10)
echo Creating Long folders...
cd "C:\Users\Muy\Muyverse Downloads\Long"
for /L %%i in (1,1,10) do mkdir "%%i"

:: Step 3: Create Shorts folders (1–10)
echo Creating Shorts folders...
cd "C:\Users\Muy\Muyverse Downloads\Shorts"
for /L %%i in (1,1,10) do mkdir "%%i"

echo All tasks completed successfully!
pause
