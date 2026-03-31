@echo off
color 0b
title Sekmeme ^& Ping Optimizer - SKY PROJECT
echo [!] SonOyuncu Sekmeme ^& Ping Optimizer Calistiriliyor...
echo.
echo [1/4] Winsock Katalogu Sifirlaniyor...
netsh winsock reset >nul
echo [2/4] IP Protokolleri Sifirlaniyor...
netsh int ip reset >nul
echo [3/4] DNS Onbellesi Temizleniyor...
ipconfig /flushdns >nul
echo [4/4] TCP Otomatik Ayarlama Devre Disi Birakiliyor (Stabil Ping)...
netsh int tcp set global autotuninglevel=disabled >nul
netsh int tcp set global rss=enabled >nul
echo.
echo [TAMAM] Optimizasyonlar Uygulandi! 
echo Not: Etkiyi gormek icin Minecraft'i yeniden baslatin.
echo.
pause
