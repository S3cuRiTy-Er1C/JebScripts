# JebScripts

## `JEB2DeobscureClass.py`

  使用Smali中`.source`字段(`JEB中称为Debug Directives`)作为源文件名进行反混淆：

  1. 不会反混淆内部类
  2. 字段值为空时不起作用，字段值不包含`*.java`时不起作用
  3. 只有Smali中保留了源代码信息时脚本才能使用(`proguar-rules.pro`中设置 `-keepattributes SourceFile`)
  4. 支持多个文件混淆成同一个source字段值的情况（修改记录见：[JEB2Deobsecure反混淆脚本修改记录](https://wuruofan.com/2021/02/01/jeb2deobsureclass-deobfuscation-script-modification-record/)）

