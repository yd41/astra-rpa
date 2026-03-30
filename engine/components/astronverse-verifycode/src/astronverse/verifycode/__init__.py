from enum import Enum

from astronverse.actionlib.atomic import atomicMg


class VerifyCodeConfig:
    @staticmethod
    def gateway_port() -> str:
        return str(atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159")

    @staticmethod
    def gateway_base_url() -> str:
        return f"http://127.0.0.1:{VerifyCodeConfig.gateway_port()}/api/rpa-ai-service"

    @staticmethod
    def jfbym_url() -> str:
        return f"{VerifyCodeConfig.gateway_base_url()}/jfbym/customApi"

    url = ""


class PictureCodeType(Enum):
    GENERAL1234 = "10110"
    GENERAL5678 = "10111"
    GENERAL1234_PLUS = "10211"


class HintPosition(Enum):
    BOTTOM = "bottom"
    TOP = "top"


class ElementGetAttributeTypeFlag(Enum):
    GetText = "getText"
    GetHtml = "getHtml"
    GetValue = "getValue"
    GetLink = "getLink"
    GetAttribute = "getAttribute"
    GetPosition = "getPosition"
    GetSelection = "getSelection"


VerifyCodeConfig.url = VerifyCodeConfig.jfbym_url()
