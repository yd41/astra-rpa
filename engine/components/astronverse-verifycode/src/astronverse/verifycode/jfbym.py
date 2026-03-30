import requests

from astronverse.verifycode import VerifyCodeConfig


def jfbym_custom_api(type: str, image: str, direction: str = "bottom") -> dict:
    payload = {
        "type": str(type),
        "image": image,
    }
    if direction:
        payload["direction"] = direction

    response = requests.post(
        VerifyCodeConfig.jfbym_url(),
        headers={"Content-Type": "application/json"},
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def extract_jfbym_result(response: dict) -> str:
    return response["data"]["data"]


def jfbym_aliyun_slider(image: str) -> dict:
    return jfbym_custom_api(type="20226", image=image)


def jfbym_click_order(image: str, direction: str = "bottom") -> dict:
    return jfbym_custom_api(type="30116", image=image, direction=direction)


def jfbym_spatial_reasoning_click(image: str) -> dict:
    return jfbym_custom_api(type="30101", image=image)


def jfbym_tencent_grid(image: str) -> dict:
    return jfbym_custom_api(type="30221", image=image)


def jfbym_rotate(image: str) -> dict:
    return jfbym_custom_api(type="900011", image=image)


def jfbym_double_rotate(image: str) -> dict:
    return jfbym_custom_api(type="411115", image=image)


def jfbym_track(image: str) -> dict:
    return jfbym_custom_api(type="100016", image=image)


def jfbym_math_digit(image: str) -> dict:
    return jfbym_custom_api(type="50100", image=image)


def jfbym_math_chinese(image: str) -> dict:
    return jfbym_custom_api(type="50101", image=image)
