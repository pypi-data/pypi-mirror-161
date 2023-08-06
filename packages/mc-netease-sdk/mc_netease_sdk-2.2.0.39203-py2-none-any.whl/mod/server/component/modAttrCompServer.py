# -*- coding: utf-8 -*-

from typing import Any
from mod.common.component.baseComponent import BaseComponent

class ModAttrComponentServer(BaseComponent):
    def SetAttr(self, paramName, paramValue):
        # type: (str, Any) -> None
        """
        设置属性值
        """
        pass

    def GetAttr(self, paramName, defaultValue=None):
        # type: (str, Any) -> Any
        """
        获取属性值
        """
        pass

