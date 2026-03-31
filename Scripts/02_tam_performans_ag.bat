@echo off
title SKY Project - Oyun Ag Optimizasyonu
color 0a
echo Windows Ag Kisitlamalari (Network Throttling) devredisi birakiliyor...
Reg.exe add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d "4294967295" /f
Reg.exe add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d "0" /f
echo TCP Ayarlari oyunlar icin optimize ediliyor...
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global ecncapability=disabled
echo Islem tamamlandi. Ping degerleri stabilize edildi. (Degisiklik icin yeniden baslatma gerekebilir)
timeout /t 4
exit
