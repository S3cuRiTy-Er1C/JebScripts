# JebScripts

* JEB2DeobscureClass.py

  使用Smali中`.source`字段(`JEB中称为Debug Directives`)作为源文件名进行反混淆.

  > 1)不会反混淆内部类.
  >
  > 2)字段值为空时不起作用.
  >
  > 3)只有Smali中保留了源代码信息时脚本才能使用(`proguar-rules.pro`中设置 `-keepattributes SourceFile`)

