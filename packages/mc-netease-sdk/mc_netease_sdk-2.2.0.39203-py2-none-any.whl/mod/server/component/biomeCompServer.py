# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class BiomeCompServer(BaseComponent):
    def GetBiomeName(self, pos, dimId=-1):
        # type: (Tuple[int,int,int], int) -> str
        """
        获取某一位置所属的生物群系信息
        """
        pass

