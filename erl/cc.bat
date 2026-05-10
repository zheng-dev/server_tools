@echo off
::设置为utf8
chcp 65001
set p=%cd%
::"C:\Program Files\erl10.7\bin\erlc" z_compile.erl sync.erl cmd_tool.erl
::erl -s z_compile cfg_check "F:\snk_work\server_code\alpha\game_alpha\plugin\cfg\.cfg" ".cfg,.a," -s init stop
echo ===done===
erl -s cmd_tool main export_record "F:\snk_work\server_code\alpha\game_alpha\plugin\app\.ebin" -s init stop
xcopy /y /f .\record.js "F:\snk_work\dev_doc\战斗配置说明\后台\record查看\record.js"
TortoiseProc.exe/command:commit /path:"F:\snk_work\dev_doc\战斗配置说明\后台\record查看" /closeonend:2  /logmsg:"new record x"
pause