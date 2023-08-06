# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class ActorRenderCompClient(BaseComponent):
    def GetNotRenderAtAll(self):
        # type: () -> bool
        """
        获取实体是否不渲染
        """
        pass

    def SetNotRenderAtAll(self, notRender):
        # type: (bool) -> bool
        """
        设置是否关闭实体渲染
        """
        pass

    def AddPlayerRenderMaterial(self, materialKey, materialName):
        # type: (str, str) -> bool
        """
        增加玩家渲染需要的材质
        """
        pass

    def AddPlayerRenderController(self, renderControllerName, condition=''):
        # type: (str, str) -> bool
        """
        增加玩家渲染控制器
        """
        pass

    def RemovePlayerRenderController(self, renderControllerName):
        # type: (str) -> bool
        """
        删除玩家渲染控制器
        """
        pass

    def RemovePlayerGeometry(self, geometryKey):
        # type: (str) -> bool
        """
        删除玩家渲染几何体
        """
        pass

    def AddPlayerGeometry(self, geometryKey, geometryName):
        # type: (str, str) -> bool
        """
        增加玩家渲染几何体
        """
        pass

    def AddPlayerTexture(self, geometryKey, geometryName):
        # type: (str, str) -> bool
        """
        增加玩家渲染贴图
        """
        pass

    def AddPlayerAnimation(self, animationKey, animationName):
        # type: (str, str) -> bool
        """
        增加玩家渲染动画
        """
        pass

    def AddPlayerAnimationController(self, animationControllerKey, animationControllerName):
        # type: (str, str) -> bool
        """
        增加玩家渲染动画控制器
        """
        pass

    def RemovePlayerAnimationController(self, animationControllKey):
        # type: (str) -> bool
        """
        移除玩家渲染动画控制器
        """
        pass

    def AddActorAnimationController(self, actorIdentifier, animationControllerKey, animationControllerName):
        # type: (str, str, str) -> bool
        """
        增加生物渲染动画控制器
        """
        pass

    def RemoveActorAnimationController(self, actorIdentifier, animationControllKey):
        # type: (str, str) -> bool
        """
        移除生物渲染动画控制器
        """
        pass

    def RebuildPlayerRender(self):
        # type: () -> bool
        """
        重建玩家的数据渲染器
        """
        pass

    def AddActorRenderMaterial(self, actorIdentifier, materialKey, materialName):
        # type: (str, str, str) -> bool
        """
        增加生物渲染需要的材质
        """
        pass

    def AddActorRenderController(self, actorIdentifier, renderControllerName, condition=''):
        # type: (str, str, str) -> bool
        """
        增加生物渲染控制器
        """
        pass

    def RemoveActorRenderController(self, actorIdentifier, renderControllerName):
        # type: (str, str) -> bool
        """
        删除生物渲染控制器
        """
        pass

    def RebuildActorRender(self, actorIdentifier):
        # type: (str) -> bool
        """
        重建生物的数据渲染器（该接口不支持玩家，玩家请使用RebuildPlayerRender）
        """
        pass

    def ChangeArmorTextures(self, armorIdentifier, texturesDict, uiIconTexture):
        # type: (str, dict, str) -> bool
        """
        修改盔甲在场景中显示和在UI中显示的贴图
        """
        pass

    def AddPlayerParticleEffect(self, effectKey, effectName):
        # type: (str, str) -> bool
        """
        增加玩家特效资源
        """
        pass

    def AddActorParticleEffect(self, actorIdentifier, effectKey, effectName):
        # type: (str, str, str) -> bool
        """
        增加生物特效资源
        """
        pass

    def AddPlayerSoundEffect(self, soundKey, soundName):
        # type: (str, str) -> bool
        """
        增加玩家音效资源
        """
        pass

    def AddActorSoundEffect(self, actorIdentifier, soundKey, soundName):
        # type: (str, str, str) -> bool
        """
        增加生物音效资源
        """
        pass

    def AddPlayerAnimationIntoState(self, animationControllerName, stateName, animationName, condition=''):
        # type: (str, str, str, str) -> bool
        """
        在玩家的动画控制器中的状态添加动画
        """
        pass

    def AddActorScriptAnimate(self, actorIdentifier, animateName, condition='', autoReplace=False):
        # type: (str, str, str, bool) -> bool
        """
        在生物的客户端实体定义（minecraft:client_entity）json中的scripts/animate节点添加动画/动画控制器
        """
        pass

    def AddActorAnimation(self, actorIdentifier, animationKey, animationName):
        # type: (str, str, str) -> bool
        """
        增加生物渲染动画
        """
        pass

    def AddActorRenderControllerArray(self, actorIdentifier, renderControllerName, arrayType, arrayName, expression):
        # type: (str, str, int, str, str) -> bool
        """
        增加生物渲染控制器列表中字典arrays元素
        """
        pass

    def AddActorBlockGeometry(self, geometryName, offset=(0, 0, 0), rotation=(0, 0, 0)):
        # type: (str, Tuple[float,float,float], Tuple[float,float,float]) -> bool
        """
        为实体添加方块几何体模型。
        """
        pass

    def DeleteActorBlockGeometry(self, geometryName):
        # type: (str) -> bool
        """
        删除实体中指定方块几何体模型。
        """
        pass

    def ClearActorBlockGeometry(self):
        # type: () -> bool
        """
        删除实体中所有的方块几何体模型。
        """
        pass

    def SetActorBlockGeometryVisible(self, geometryName, visible):
        # type: (str, bool) -> bool
        """
        设置实体中指定的方块几何体模型是否显示。
        """
        pass

    def SetActorAllBlockGeometryVisible(self, visible):
        # type: (bool) -> bool
        """
        设置实体中所有的方块几何体模型是否显示。
        """
        pass

    def SetActorBlockGeometryOffset(self, geometryName, offset=(0, 0, 0)):
        # type: (str, Tuple[float,float,float]) -> bool
        """
        设置实体的方块几何体模型的位置偏移。
        """
        pass

    def SetActorBlockGeometryRotation(self, geometryName, rotation=(0, 0, 0)):
        # type: (str, Tuple[float,float,float]) -> bool
        """
        设置实体的方块几何体模型的旋转角度。
        """
        pass

    def EnableActorBlockGeometryTransparent(self, geometryName, enable):
        # type: (str, bool) -> bool
        """
        设置是否允许实体的方块几何体模型产生透明度，允许开启后通过调节方块几何体的透明度将会使得方块几何体模型变得透明。
        """
        pass

    def SetActorBlockGeometryTransparency(self, geometryName, transparent):
        # type: (str, float) -> bool
        """
        设置实体的方块几何体模型的透明度。注意，只有调用接口EnableActorBlockGeometryTransparent开启了方块几何体模型的透明度后该接口才会生效。
        """
        pass

