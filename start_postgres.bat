@echo off
echo ===================================================
echo Demarrage du service PostgreSQL 17...
echo ===================================================
powershell -Command "Start-Process cmd -ArgumentList '/c net start postgresql-17' -Verb RunAs"
echo.
echo Veuillez cliquer sur 'Oui' sur la fenetre de confirmation Windows si elle apparait.
echo Une fois demarre, vous pouvez actualiser pgAdmin !
pause
