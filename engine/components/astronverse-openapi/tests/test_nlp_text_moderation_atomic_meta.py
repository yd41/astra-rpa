from astronverse.actionlib.atomic import atomicMg
from astronverse.openapi.openapi import OpenApi  # noqa: F401


def test_nlp_text_moderation_atomic_uses_rich_form_config():
    meta = atomicMg.atomic_dict["OpenApi.nlp_text_moderation"]
    params = {item.key: item for item in meta.inputList}
    outputs = {item.key: item for item in meta.outputList}

    assert "input_type" in params
    assert "is_multi" in params
    assert "src_dir" in params
    assert "categories" in params

    assert params["input_type"].formType.type == "RADIO"
    assert params["input_type"].default == "text"
    assert params["content"].limitLength == [-1, 5000]
    assert params["categories"].formType.type == "SELECT"
    assert params["categories"].formType.params["multiple"] is True
    assert params["is_save"].default is True

    src_file_show = params["src_file"].dynamics[0].expression
    src_dir_show = params["src_dir"].dynamics[0].expression
    content_show = params["content"].dynamics[0].expression
    dst_show = params["dst_file"].dynamics[0].expression

    assert "input_type.value == 'file'" in src_file_show
    assert "is_multi.value == false" in src_file_show
    assert "is_multi.value == true" in src_dir_show
    assert "input_type.value == 'text'" in content_show
    assert "is_save.value == true" in dst_show

    assert "saved_file" in outputs
