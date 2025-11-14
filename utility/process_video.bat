@echo off
setlocal

:: --- Configuration Section ---
set "base_dir=C:\Users\Muy\OneDrive\socials\muyverse"
set "source_dir=%base_dir%\maths_input_video"

:: --- Ask for video number dynamically ---
set /p video_num=Enter video number (e.g. 6): 

:: --- Define file paths ---
set "input_video=%base_dir%\input_video.mp4"
set "source_video=%source_dir%\%video_num%.mp4"

echo --------------------------------------------------
echo Deleting old input_video.mp4 ...
if exist "%input_video%" del "%input_video%"

echo Copying "%video_num%.mp4" to input_video.mp4 ...
copy "%source_video%" "%input_video%"

echo Checking video length ...
powershell -Command " $shell = New-Object -ComObject Shell.Application; $folder = $shell.Namespace('%base_dir%'); $file = $folder.ParseName('input_video.mp4'); Write-Host 'Video length:' ($folder.GetDetailsOf($file, 27)) "

echo --------------------------------------------------
echo Task completed successfully!
pause
