# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class ActorMotionComponentServer(BaseComponent):
    def SetMotion(self, motion):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置生物（不含玩家）的瞬时移动方向向量
        """
        pass

    def GetMotion(self):
        # type: () -> Tuple[int,int,int]
        """
        获取生物（含玩家）的瞬时移动方向向量
        """
        pass

    def ResetMotion(self):
        # type: () -> bool
        """
        重置生物（不含玩家）的瞬时移动方向向量
        """
        pass

