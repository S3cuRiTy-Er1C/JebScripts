# -*- coding: utf-8 -*-  
"""
Deobscure class name(use debug directives as source name) for PNF Software's JEB2.
"""
__author__ = 'Ericli'

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData, ActionRenameData
from java.lang import Runnable


class JEB2DeobscureClass(IScript):
    def run(self, ctx):
        ctx.executeAsync("Running deobscure class ...", JEB2AutoRename(ctx))
        print('Done')


class JEB2AutoRename(Runnable):
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        ctx = self.ctx
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        prj = projects[0]

        units = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)

        for unit in units:
            classes = unit.getClasses()
            if classes:
                for clazz in classes:
                    # print(clazz.getName(True), clazz)
                    sourceIndex = clazz.getSourceStringIndex()
                    clazzAddress = clazz.getAddress()
                    if sourceIndex == -1 or '$' in clazzAddress:# Do not rename inner class
                        # print('without have source field', clazz.getName(True))
                        continue

                    sourceStr = str(unit.getString(sourceIndex))
                    if '.java' in sourceStr:
                        sourceStr = sourceStr[:-5]

                    # print(clazz.getName(True), sourceIndex, sourceStr, clazz)
                    if clazz.getName(True) != sourceStr:
                        self.comment_class(unit, clazz, clazz.getName(True))  # Backup origin clazz name to comment
                        self.rename_class(unit, clazz, sourceStr, True)  # Rename to source name

    def rename_class(self, unit, originClazz, sourceName, isBackup):
        actCtx = ActionContext(unit, Actions.RENAME, originClazz.getItemId(), originClazz.getAddress())
        actData = ActionRenameData()
        actData.setNewName(sourceName)

        if unit.prepareExecution(actCtx, actData):
            try:
                result = unit.executeAction(actCtx, actData)
                if result:
                    print('rename to %s success!' % sourceName)
                else:
                    print('rename to %s failed!' % sourceName)
            except Exception, e:
                print (Exception, e)

    def comment_class(self, unit, originClazz, commentStr):
        actCtx = ActionContext(unit, Actions.COMMENT, originClazz.getItemId(), originClazz.getAddress())
        actData = ActionCommentData()
        actData.setNewComment(commentStr)

        if unit.prepareExecution(actCtx, actData):
            try:
                result = unit.executeAction(actCtx, actData)
                if result:
                    print('comment to %s success!' % commentStr)
                else:
                    print('comment to %s failed!' % commentStr)
            except Exception, e:
                print (Exception, e)
