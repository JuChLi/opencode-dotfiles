(
echo # Java/Python/NET Settings
echo node_modules/
echo target/
echo .gradle/
echo __pycache__/
echo .vs/
echo bin/
echo obj/
echo .idea/
echo .vscode/
echo .settings/
echo *.class
echo *.exe
echo *.dll
echo *.pdb
echo .env
echo .git/
) > "%USERPROFILE%\.opencode_global_ignore"

setx OPENCODE_IGNORE_PATH "%USERPROFILE%\.opencode_global_ignore"

echo ✅ CMD 設定完成！
