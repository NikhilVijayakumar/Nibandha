import pytest
from pathlib import Path
import json
from nibandha.reporting.shared.rendering.template_engine import TemplateEngine

@pytest.fixture
def template_dir(tmp_path):
    d = tmp_path / "templates"
    d.mkdir()
    return d

@pytest.fixture
def sample_template(template_dir):
    f = template_dir / "simple.md"
    f.write_text("# Report\nValue: {{ value }}\nList:\n{{ items }}", encoding="utf-8")
    return "simple.md"

@pytest.fixture
def engine(template_dir):
    return TemplateEngine(template_dir)

def test_render_success(engine, sample_template):
    data = {"value": "123", "items": "- A\n- B"}
    result = engine.render(sample_template, data)
    assert "Value: 123" in result
    assert "- A" in result

def test_render_missing_key(engine, sample_template):
    from jinja2.exceptions import UndefinedError
    data = {"value": "123"} # Missing 'items'
    with pytest.raises(UndefinedError):
        engine.render(sample_template, data)

def test_template_not_found(engine):
    from jinja2.exceptions import TemplateNotFound
    with pytest.raises(TemplateNotFound):
        engine.render("non_existent.md", {})

def test_render_save_output(engine, sample_template, tmp_path):
    data = {"value": "test", "items": ""}
    out_file = tmp_path / "out" / "report.md"
    content = engine.render(sample_template, data, output_path=out_file)
    
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == content

def test_save_data(engine, tmp_path):
    data = {"foo": "bar", "num": 1}
    json_path = tmp_path / "data.json"
    engine.save_data(data, json_path)
    
    assert json_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded == data
