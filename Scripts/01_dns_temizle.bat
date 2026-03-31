@echo off
title SKY Project - Ag ve DNS Temizleyici
color 0b
echo Ag baglantilari ve DNS onbellegi temizleniyor...
ipconfig /flushdns
ipconfig /release
ipconfig /renew
netsh winsock reset
echo.
echo Temizlik Tamamlandi. Aginiz daha stabil hale getirildi.
timeout /t 4
exit
