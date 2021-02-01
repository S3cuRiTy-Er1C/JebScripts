# -*- coding: utf-8 -*-  
"""
Deobscure class name(use debug directives as source name) for PNF Software's JEB2.
"""
__author__ = 'Ericli & rf.w'

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

        # dict save {sourceStr, {parent_pkg_path, [unit, classs]}
        dic = {}

        for unit in units:
            classes = unit.getClasses()
            if classes:
                for clazz in classes:
                    # print(clazz.getName(True), clazz)
                    sourceIndex = clazz.getSourceStringIndex()
                    clazzAddress = clazz.getAddress()
                    # flag = clazz.getGenericFlags()

                    if sourceIndex == -1 or '$' in clazzAddress:# Do not rename inner class
                        # print('without have source field', clazz.getName(True))
                        continue

                    sourceStr = str(unit.getString(sourceIndex))
                    if '.java' in sourceStr:
                        sourceStr = sourceStr[:-5]
                    else:
                        # @rf.w 20210120
                        continue

                    # print(clazz.getName(True), sourceIndex, sourceStr, clazz)
                    if clazz.getName(True) != sourceStr:
                        # @rf.w 20210122
                        index = 1
                        source_format = sourceStr + '_{0}'

                        source_key = sourceStr
                        parent_pkg_name = self.get_parent_pkg_name(clazz.getSignature())

                        if source_key not in dic.keys():
                            dic[source_key] = {}
                            dic[source_key][parent_pkg_name] = [unit, clazz]
                            #print('ADD %s => %s(%s)' % (clazz.getSignature(), source_key, (parent_pkg_name +"/" + source_key)))
                            continue
                        else:
                            while source_key in dic.keys():
                                inner_dic = dic[source_key]

                                if parent_pkg_name in inner_dic.keys():
                                    #print('found repeated: %s' % (parent_pkg_name +"/" + source_key), clazz)
                                    source_key = source_format.format(str(index))
                                    index += 1
                                    continue
                                else:
                                    inner_dic[parent_pkg_name] = [unit, clazz]
                                    break

                            dic[source_key] = {}
                            dic[source_key][parent_pkg_name] = [unit, clazz]
                            #print('ADD %s => %s(%s)' % (clazz.getSignature(), source_key, (parent_pkg_name +"/" + source_key)))

        for key in dic.keys():
            inner_dic = dic[key]
            for inner_key in inner_dic.keys():
                array = inner_dic[inner_key]
                unit = array[0]
                clazz = array[1]
                print("RENAME %s <= %s!" % (key, clazz.getAddress()))
                self.comment_class(unit, clazz, clazz.getName(True))  # Backup origin clazz name to comment
                self.rename_class(unit, clazz, key, True)  # Rename to source name

    def rename_class(self, unit, originClazz, sourceName, isBackup):
        actCtx = ActionContext(unit, Actions.RENAME, originClazz.getItemId(), originClazz.getAddress())
        actData = ActionRenameData()
        actData.setNewName(sourceName)

        if unit.prepareExecution(actCtx, actData):
            try:
                result = unit.executeAction(actCtx, actData)
                if not result:
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
                if not result:
                    print('comment to %s failed!' % commentStr)
            except Exception, e:
                print (Exception, e)


    def get_parent_pkg_name(self, class_signature):
        if len(class_signature) <= 0:
            return ""

        index = class_signature.rfind('/')
        return class_signature[0:index]
