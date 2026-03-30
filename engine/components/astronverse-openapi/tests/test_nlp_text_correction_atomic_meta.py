from astronverse.actionlib.atomic import atomicMg
from astronverse.openapi.openapi import OpenApi  # noqa: F401


def test_nlp_text_correction_atomic_uses_rich_form_config():
    meta = atomicMg.atomic_dict["OpenApi.nlp_text_correction"]
    params = {item.key: item for item in meta.inputList}
    outputs = {item.key: item for item in meta.outputList}

    assert "input_type" in params
    assert "is_multi" in params
    assert "src_dir" in params
    assert "is_save" in params
    assert "error_dst_file" in params
    assert "export_corrected_doc" in params
    assert "corrected_dst_file" in params

    assert params["input_type"].formType.type == "RADIO"
    assert params["input_type"].default == "text"
    assert params["text"].formType.type == "INPUT_VARIABLE_PYTHON"
    assert params["text"].limitLength == [-1, 2000]

    src_file_show = params["src_file"].dynamics[0].expression
    src_dir_show = params["src_dir"].dynamics[0].expression
    text_show = params["text"].dynamics[0].expression
    error_dst_show = params["error_dst_file"].dynamics[0].expression
    corrected_show = params["corrected_dst_file"].dynamics[0].expression

    assert "input_type.value == 'file'" in src_file_show
    assert "is_multi.value == false" in src_file_show
    assert "is_multi.value == true" in src_dir_show
    assert "input_type.value == 'text'" in text_show
    assert "is_save.value == true" in error_dst_show
    assert "export_corrected_doc.value == true" in corrected_show

    assert "error_detail_file" in outputs
    assert "corrected_file" in outputs
