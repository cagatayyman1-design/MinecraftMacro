@echo off
title SKY Project - Saf Fare (Raw Input)
color 0c
echo Windows Fare Ivmesi (Enhance Pointer Precision) devredisi birakiliyor...
Reg.exe add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f
Reg.exe add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f
Reg.exe add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f
echo Isaretci hassasiyeti sifrlandi. Fare hiziniz artik %100 saf el hizinizdir.
timeout /t 4
exit
