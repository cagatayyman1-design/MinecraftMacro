@echo off
title SKY Project - Klavye Tepkime Hizi
color 0d
echo Windows Klavye Gecikme (Delay) sureleri en aza indiriliyor...
Reg.exe add "HKCU\Control Panel\Keyboard" /v "KeyboardDelay" /t REG_SZ /d "0" /f
Reg.exe add "HKCU\Control Panel\Keyboard" /v "KeyboardSpeed" /t REG_SZ /d "31" /f
echo Islem basarili! Tuslara basildigindaki bekleme suresi kaldirildi. 
timeout /t 4
exit
