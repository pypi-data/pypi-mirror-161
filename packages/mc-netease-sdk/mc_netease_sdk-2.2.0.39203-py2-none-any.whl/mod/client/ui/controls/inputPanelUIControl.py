# -*- coding: utf-8 -*-

from mod.client.ui.controls.baseUIControl import BaseUIControl
from typing import Tuple

class InputPanelUIControl(BaseUIControl):
    def SetIsModal(self, isModal):
        # type: (bool) -> bool
        """
        设置当前面板是否为模态框
        """
        pass

    def GetIsModal(self):
        # type: () -> bool
        """
        判断当前面板是否为模态框
        """
        pass

    def SetOffsetDelta(self, offset_delta):
        # type: (Tuple[float,float]) -> bool
        """
        设置点击面板的拖拽偏移量
        """
        pass

    def GetOffsetDelta(self):
        # type: () -> Tuple[float,float]
        """
        获得点击面板的拖拽偏移量
        """
        pass

