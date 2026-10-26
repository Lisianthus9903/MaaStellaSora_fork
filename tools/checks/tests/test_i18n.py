import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.checks.check_i18n import check  # noqa: E402


class PipelineI18nTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "assets" / "interface" / "tasks").mkdir(parents=True)
        (self.root / "assets" / "resource" / "base").mkdir(parents=True)
        (self.root / "assets" / "i18n").mkdir(parents=True)

        self.interface = {
            "languages": {"zh_cn": "i18n/zh_cn.json"},
            "import": ["interface/tasks/tasks.json"],
        }
        self.task = {
            "option": {
                "Example": {
                    "pipeline_override": {
                        "OverrideNode": {
                            "focus": {
                                "Node.Action.Succeeded": {
                                    "content": "$interface.task.option.Example.pipeline_override.OverrideNode.focus.Node.Action.Succeeded",
                                    "display": "log",
                                }
                            }
                        }
                    }
                }
            }
        }
        self.pipeline = {
            "PipelineNode": {
                "focus": {
                    "Node.Action.Succeeded": "$pipeline.PipelineNode.focus.Node.Action.Succeeded"
                }
            }
        }
        self.translations = {
            "interface.task.option.Example.pipeline_override.OverrideNode.focus.Node.Action.Succeeded": "覆盖完成",
            "pipeline.PipelineNode.focus.Node.Action.Succeeded": "节点完成",
        }
        self._write_json("assets/interface.json", self.interface)
        self._write_json("assets/interface/tasks/tasks.json", self.task)
        self._write_json("assets/resource/base/pipeline.json", self.pipeline)
        self._write_json("assets/i18n/zh_cn.json", self.translations)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_json(self, relative_path, value):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_scans_normal_pipeline_and_override_focus_templates(self):
        self.assertEqual(check(self.root), [])

    def test_reports_hardcoded_chinese_focus_content(self):
        self.task["option"]["Example"]["pipeline_override"]["OverrideNode"]["focus"][
            "Node.Action.Succeeded"
        ]["content"] = "硬编码文案"
        self._write_json("assets/interface/tasks/tasks.json", self.task)

        findings = check(self.root)

        self.assertTrue(
            any("hardcoded Chinese in a Pipeline focus message" in item.message for item in findings)
        )

    def test_ignores_language_specific_pipeline_files(self):
        self._write_json(
            "assets/interface/tasks/tasks_en.json",
            {
                "option": {
                    "Localized": {
                        "pipeline_override": {
                            "Node": {"focus": {"Node.Action.Succeeded": "硬编码文案"}}
                        }
                    }
                }
            },
        )
        self.interface["import"].append("interface/tasks/tasks_en.json")
        self._write_json("assets/interface.json", self.interface)
        self._write_json(
            "assets/resource/en/pipeline_en.json",
            {"LocalizedNode": {"focus": {"Node.Action.Succeeded": "硬编码文案"}}},
        )

        self.assertEqual(check(self.root), [])


if __name__ == "__main__":
    unittest.main()
