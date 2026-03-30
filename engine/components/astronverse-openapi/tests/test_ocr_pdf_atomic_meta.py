from astronverse.actionlib.atomic import atomicMg
from astronverse.openapi.openapi import OpenApi  # noqa: F401


def test_ocr_pdf_atomic_uses_rich_form_config():
    meta = atomicMg.atomic_dict["OpenApi.ocr_pdf"]
    params = {item.key: item for item in meta.inputList}

    assert "input_type" in params
    assert "is_multi" in params
    assert "src_dir" in params
    assert "page_mode" in params
    assert "page_ranges" in params

    assert params["input_type"].formType.type == "RADIO"
    assert params["export_format"].default == "word"

    src_file_show = params["src_file"].dynamics[0].expression
    src_dir_show = params["src_dir"].dynamics[0].expression
    page_ranges_show = params["page_ranges"].dynamics[0].expression

    assert "input_type.value == 'file'" in src_file_show
    assert "is_multi.value == false" in src_file_show
    assert "is_multi.value == true" in src_dir_show
    assert "page_mode.value == 'custom'" in page_ranges_show
