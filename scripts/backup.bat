:: filepath: /scripts/backup.bat
@echo off
set BACKUP_PATH=C:\backups\rds
set MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin
set DB_USER=backup_user
set DB_PASS=your_password
set DB_NAME=rds_db

:: Create backup directory if not exists
if not exist "%BACKUP_PATH%" mkdir "%BACKUP_PATH%"

:: Create backup filename with timestamp
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_FILE=%BACKUP_PATH%\rds_%TIMESTAMP%.sql

:: Create MySQL backup
"%MYSQL_PATH%\mysqldump" -u%DB_USER% -p%DB_PASS% %DB_NAME% > "%BACKUP_FILE%"

:: Compress backup
powershell Compress-Archive -Path "%BACKUP_FILE%" -DestinationPath "%BACKUP_FILE%.zip"
del "%BACKUP_FILE%"

:: Delete backups older than 30 days
forfiles /p "%BACKUP_PATH%" /s /m *.zip /d -30 /c "cmd /c del @path"