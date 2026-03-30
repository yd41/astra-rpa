import time

import pyautogui
from PIL import Image
from astronverse.actionlib import AtomicLevel, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import WebPick
from astronverse.baseline.logger.logger import logger
from astronverse.browser.browser import Browser
from astronverse.browser.browser_element import BrowserElement
from astronverse.locator import smooth_move
from astronverse.locator.locator import locator
from astronverse.verifycode import HintPosition, PictureCodeType
from astronverse.verifycode.core import VerifyCodeCore
from astronverse.verifycode.error import *
from astronverse.verifycode.jfbym import jfbym_custom_api as run_jfbym_custom_api

VerifyCodeCore = VerifyCodeCore()
Locator = locator


class VerifyCode:
    @staticmethod
    def _capture_element(browser_obj: Browser, picture_pick: WebPick):
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        image = pyautogui.screenshot(region=(int(rect.left), int(rect.top), int(rect.width()), int(rect.height())))
        return image, rect

    @staticmethod
    def _capture_element_base64(browser_obj: Browser, picture_pick: WebPick) -> str:
        _, rect = VerifyCode._capture_element(browser_obj, picture_pick)
        return VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

    @staticmethod
    def _parse_coordinate_list(raw_result: str) -> list[tuple[int, int]]:
        if not raw_result:
            raise BaseException(MSG_EMPTY_FORMAT, "")
        return [tuple(map(int, pos.split(","))) for pos in raw_result.split("|")]

    @staticmethod
    def _parse_int_result(raw_result: str) -> int:
        if raw_result in (None, ""):
            raise BaseException(MSG_EMPTY_FORMAT, "")
        return int(round(float(raw_result)))

    @staticmethod
    def _merge_images_vertically(top_image: Image.Image, bottom_image: Image.Image) -> Image.Image:
        width = max(top_image.width, bottom_image.width)
        merged = Image.new("RGB", (width, top_image.height + bottom_image.height), color="white")
        merged.paste(top_image, (0, 0))
        merged.paste(bottom_image, (0, top_image.height))
        return merged

    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        from io import BytesIO
        import base64

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "input_box",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_box.show",
                        expression="return  $this.input_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("code_result", types="Str"),
        ],
    )
    def picture_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        code_type: PictureCodeType = PictureCodeType.GENERAL1234,
        input_flag: bool = False,
        input_box: WebPick = None,
    ) -> str:
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        code_result = VerifyCodeCore.get_api_result(api_type=code_type.value, pic_element_base64=image_base64)
        logger.info("验证码返回值: {}".format(code_result))
        if not code_result:
            raise BaseException(MSG_EMPTY_FORMAT, "")

        if input_flag:
            BrowserElement.input(browser_obj=browser_obj, element_data=input_box, fill_input=code_result)

        return code_result

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "move_pic_pick",
                dynamics=[
                    DynamicsItem(
                        key="$this.move_pic_pick.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "mini_step",
                dynamics=[
                    DynamicsItem(
                        key="$this.mini_step.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
            atomicMg.param("offset", level=AtomicLevel.ADVANCED, required=False),
        ],
        outputList=[atomicMg.param("drag_distance", types="Int")],
    )
    def slider_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        slider_pick: WebPick = None,
        unmatched_flag: bool = False,
        move_pic_pick: WebPick = None,
        mini_step: int = 5,
        offset: int = 0,
    ) -> int:
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        drag_distance = int(VerifyCodeCore.get_api_result(api_type="22222", pic_element_base64=image_base64))
        logger.info("验证码返回值: {}".format(drag_distance))
        drag_distance = drag_distance + offset
        logger.info("加入偏移量之后的移动量: {}".format(drag_distance))
        if not drag_distance:
            raise BaseException(MSG_EMPTY_FORMAT, "")

        slider_element = Locator.locator(slider_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        if isinstance(slider_element.rect(), list):
            raise Exception("浏览器元素定位不唯一，请检查！")
        start_pos = slider_element.point()
        if not unmatched_flag:
            end_pos = (start_pos.x + drag_distance, start_pos.y)
            VerifyCodeCore.html_drag_plus(start_pos, end_pos)

        else:
            smooth_move(start_pos.x, start_pos.y, duration=0.5)
            pyautogui.mouseDown()
            smooth_move(start_pos.x + drag_distance * 0.85, start_pos.y, duration=0.5)
            time.sleep(0.5)
            delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
            logger.info(delta)
            while abs(delta) > mini_step:
                if delta > 0:
                    smooth_move(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                else:
                    smooth_move(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                time.sleep(0.5)
                delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
                logger.info(delta)
            # 释放滑块
            pyautogui.mouseUp()

        return drag_distance

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def click_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        hint_position: HintPosition = HintPosition.BOTTOM,
    ):
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 86,94|255,62|170,92
        click_result = VerifyCodeCore.get_api_result(
            api_type="30332",
            pic_element_base64=image_base64,
            direction=hint_position.value,
        )
        logger.info("验证码返回值: {}".format(click_result))
        if not click_result:
            raise BaseException(MSG_EMPTY_FORMAT, "")
        click_positions = click_result.split("|")
        click_positions = [tuple(map(int, pos.split(","))) for pos in click_positions]

        # 开始点击
        for pos in click_positions:
            pos = (pos[0] + rect.left, pos[1] + rect.top)
            smooth_move(*pos, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        return click_positions

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("data", types="Dict")],
    )
    def jfbym_custom_api(type: str, image: str, direction: str = "bottom", **kwargs) -> dict:
        return run_jfbym_custom_api(type=type, image=image, direction=direction)

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("drag_distance", types="Int")],
    )
    def jfbym_aliyun_slider(
        browser_obj: Browser = None,
        extra: WebPick = None,
        refresh_pick: WebPick = None,
        slider_pick: WebPick = None,
        picture_pick: WebPick = None,
        **kwargs,
    ) -> int:
        return VerifyCode.slider_code(
            browser_obj=browser_obj,
            picture_pick=picture_pick,
            slider_pick=slider_pick,
        )

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def jfbym_click_order(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        confirm_pick: WebPick = None,
        **kwargs,
    ) -> list:
        return VerifyCode.click_code(
            browser_obj=browser_obj,
            picture_pick=picture_pick,
            hint_position=HintPosition.BOTTOM,
        )

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def jfbym_spatial_reasoning_click(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        confirm_pick: WebPick = None,
        **kwargs,
    ) -> list:
        return VerifyCode.click_code(
            browser_obj=browser_obj,
            picture_pick=picture_pick,
            hint_position=HintPosition.BOTTOM,
        )

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def jfbym_tencent_grid(
        browser_obj: Browser = None,
        extra: WebPick = None,
        picture_pick: WebPick = None,
        confirm_pick: WebPick = None,
        **kwargs,
    ) -> list:
        return VerifyCode.click_code(
            browser_obj=browser_obj,
            picture_pick=picture_pick,
            hint_position=HintPosition.BOTTOM,
        )

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("rotate_angle", types="Int")],
    )
    def jfbym_rotate(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        slider_pick: WebPick = None,
        bar_pick: WebPick = None,
        max_angle: str = "360",
        **kwargs,
    ) -> int:
        image_base64 = VerifyCode._capture_element_base64(browser_obj, picture_pick)
        rotate_angle = VerifyCodeCore.get_api_result(api_type="900011", pic_element_base64=image_base64)
        return VerifyCode._parse_int_result(rotate_angle)

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("rotate_angle", types="Int")],
    )
    def jfbym_double_rotate(
        browser_obj: Browser = None,
        out_ring_pick: WebPick = None,
        inner_circle_pick: WebPick = None,
        slider_pick: WebPick = None,
        bar_pick: WebPick = None,
        max_angle: str = "360",
        **kwargs,
    ) -> int:
        out_image, _ = VerifyCode._capture_element(browser_obj, out_ring_pick)
        inner_image, _ = VerifyCode._capture_element(browser_obj, inner_circle_pick)
        merged_image = VerifyCode._merge_images_vertically(out_image, inner_image)
        image_base64 = VerifyCode._image_to_base64(merged_image)
        rotate_angle = VerifyCodeCore.get_api_result(api_type="411115", pic_element_base64=image_base64)
        return VerifyCode._parse_int_result(rotate_angle)

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("track_coordinates", types="List")],
    )
    def jfbym_track(browser_obj: Browser = None, picture_pick: WebPick = None, **kwargs) -> list:
        image_base64 = VerifyCode._capture_element_base64(browser_obj, picture_pick)
        track_coordinates = VerifyCodeCore.get_api_result(api_type="100016", pic_element_base64=image_base64)
        return VerifyCode._parse_coordinate_list(track_coordinates)

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "input_pick",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_pick.show",
                        expression="return $this.fill_input.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("calculation_result", types="Str")],
    )
    def jfbym_math_digit(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        fill_input: bool = False,
        input_pick: WebPick = None,
        **kwargs,
    ) -> str:
        image_base64 = VerifyCode._capture_element_base64(browser_obj, picture_pick)
        code_result = VerifyCodeCore.get_api_result(api_type="50100", pic_element_base64=image_base64)
        if fill_input:
            BrowserElement.input(browser_obj=browser_obj, element_data=input_pick, fill_input=code_result)
        return code_result

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "input_pick",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_pick.show",
                        expression="return $this.fill_input.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("calculation_result", types="Str")],
    )
    def jfbym_math_chinese(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        fill_input: bool = False,
        input_pick: WebPick = None,
        **kwargs,
    ) -> str:
        image_base64 = VerifyCode._capture_element_base64(browser_obj, picture_pick)
        code_result = VerifyCodeCore.get_api_result(api_type="50101", pic_element_base64=image_base64)
        if fill_input:
            BrowserElement.input(browser_obj=browser_obj, element_data=input_pick, fill_input=code_result)
        return code_result
