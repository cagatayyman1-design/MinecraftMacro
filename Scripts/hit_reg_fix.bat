@echo off
color 0d
title TCP Hit Registration Fix - SKY PROJECT
echo [!] Hit Iyilestirme ^& Paket Stabilizasyonu Baslatiliyor...
echo.
echo [1/3] Nagle Algoritmasi Optimizasyonu...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /v TcpAckFrequency /t REG_DWORD /d 1 /f >nul 2>nul
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /v TcpNoDelay /t REG_DWORD /d 1 /f >nul 2>nul
echo [2/3] Netsh Arayuzu TCP Ayarlari...
netsh interface tcp set global sack=enabled >nul 2>nul
netsh interface tcp set global ecncapability=disabled >nul 2>nul
netsh interface tcp set global timestamps=disabled >nul 2>nul
echo [3/3] Winsock Katalogu Yenileniyor...
netsh winsock reset catalog >nul 2>nul
echo.
echo [TAMAM] Hit Kayitlari Iyilestirildi!
echo Not: Kayit defteri degisiklikleri icin bilgisayari baslatmaniz onerilir.
echo.
pause
