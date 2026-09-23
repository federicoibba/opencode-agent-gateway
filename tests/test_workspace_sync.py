"""Tests for the workspace_sync package.

Run from the repo root with::

    python3 -m unittest discover -s tests -v

Requires PyYAML (``mise run setup-deps``).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from workspace_sync.agents import collect_skills, load_workspaces  # noqa: E402
from workspace_sync.cli import print_plan  # noqa: E402
from workspace_sync.constants import SHARED_PROMPTS  # noqa: E402
from workspace_sync.libraries import load_prompts_dir  # noqa: E402
from workspace_sync.sync import build_model  # noqa: E402


class WorkspaceSyncTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixtures ---------------------------------------------------------- #
    def write(self, rel, content):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)

    def skill(self, rel, name, description="does a thing", body="body"):
        self.write(
            rel,
            f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n",
        )

    def mcp(self, rel, name, tool_id="server:mcp:agentgateway"):
        self.write(rel, json.dumps({"name": name, "tool_id": tool_id}))

    def agent(self, rel, body):
        self.write(rel, body)

    def load(self):
        return {agent["id"]: agent for agent in load_workspaces(self.root)}

    # -- discovery --------------------------------------------------------- #
    def test_discovers_folder_and_flat_forms(self):
        self.agent("agents/frontend/frontend.yml", "name: Frontend\nbase_model: smart\nprompt: hi\n")
        self.agent("agents/quick.yml", "name: Quick\nbase_model: fast\nprompt: hi\n")
        agents = self.load()
        self.assertEqual(set(agents), {"frontend", "quick"})
        self.assertEqual(agents["frontend"]["base_model"], "smart")

    def test_folder_without_agent_file_is_skipped(self):
        self.agent("agents/frontend/frontend.yml", "name: Frontend\nbase_model: smart\nprompt: hi\n")
        self.write("agents/empty/notes.md", "not an agent")
        self.assertEqual(set(self.load()), {"frontend"})

    def test_duplicate_agent_id_is_rejected(self):
        self.agent("agents/frontend/frontend.yml", "name: A\nbase_model: smart\nprompt: hi\n")
        self.agent("agents/frontend.yml", "name: B\nbase_model: smart\nprompt: hi\n")
        with self.assertRaises(SystemExit) as ctx:
            load_workspaces(self.root)
        self.assertIn("duplicate agent id", str(ctx.exception))

    # -- extends / spread -------------------------------------------------- #
    def test_extends_unions_lists_and_appends_prompt(self):
        self.skill("skills/accessibility/SKILL.md", "accessibility")
        self.mcp("mcps/agentgateway.json", "agentgateway")
        self.agent(
            "agents/frontend/frontend.yml",
            "name: Frontend\nbase_model: smart\ntags: [frontend]\n"
            "skills: [accessibility]\nmcps: [agentgateway]\nprompt: |\n  BASE\n",
        )
        self.agent(
            "agents/frontend-vue/frontend-vue.yml",
            "name: Frontend (Vue)\nextends: frontend\ntags: [vue]\n"
            "prompt_append: |\n  EXTRA\n",
        )
        vue = self.load()["frontend-vue"]
        self.assertEqual(vue["base_model"], "smart")
        self.assertEqual(vue["tools"], ["server:mcp:agentgateway"])
        self.assertEqual([s["id"] for s in vue["skills"]], ["accessibility"])
        self.assertEqual(vue["tags"], ["frontend", "vue"])
        self.assertLess(
            vue["instructions"].index("BASE"), vue["instructions"].index("EXTRA")
        )

    def test_child_prompt_replaces_parent(self):
        self.agent(
            "agents/base/base.yml",
            "name: Base\npublish: false\nbase_model: smart\nprompt: |\n  BASE\n",
        )
        self.agent(
            "agents/child/child.yml",
            "name: Child\nextends: base\nprompt: |\n  CHILD\n",
        )
        child = self.load()["child"]
        self.assertIn("CHILD", child["instructions"])
        self.assertNotIn("BASE", child["instructions"])

    def test_params_deep_merge(self):
        self.agent(
            "agents/base/base.yml",
            "name: Base\npublish: false\nbase_model: smart\n"
            "params:\n  temperature: 1\n  top_p: 0.5\nprompt: hi\n",
        )
        self.agent(
            "agents/child/child.yml",
            "name: Child\nextends: base\nparams:\n  top_p: 0.9\nprompt: hi\n",
        )
        child = self.load()["child"]
        self.assertEqual(child["params"], {"temperature": 1, "top_p": 0.9})

    def test_name_and_folder_are_not_inherited(self):
        self.agent(
            "agents/base/base.yml",
            "name: Base\npublish: false\nbase_model: smart\n"
            "folder: Base Folder\nprompt: hi\n",
        )
        self.agent("agents/child/child.yml", "name: Child\nextends: base\nprompt: hi\n")
        self.agent("agents/anon/anon.yml", "extends: base\nprompt: hi\n")
        agents = self.load()
        self.assertEqual(agents["child"]["name"], "Child")
        self.assertEqual(agents["child"]["folder"], "Child")
        # A child that names nothing defaults to its own id, not the parent's name.
        self.assertEqual(agents["anon"]["name"], "anon")
        self.assertEqual(agents["anon"]["folder"], "anon")

    def test_extends_cycle_is_rejected(self):
        self.agent("agents/a/a.yml", "name: A\nextends: b\nprompt: hi\n")
        self.agent("agents/b/b.yml", "name: B\nextends: a\nprompt: hi\n")
        with self.assertRaises(SystemExit) as ctx:
            load_workspaces(self.root)
        self.assertIn("cycle", str(ctx.exception))

    def test_unknown_extends_is_rejected(self):
        self.agent("agents/a/a.yml", "name: A\nextends: nope\nprompt: hi\n")
        with self.assertRaises(SystemExit) as ctx:
            load_workspaces(self.root)
        self.assertIn("unknown agent", str(ctx.exception))

    # -- libraries --------------------------------------------------------- #
    def test_local_skill_is_implicit_and_shadows_shared(self):
        self.skill("skills/shared/SKILL.md", "shared", body="shared-body")
        self.skill("agents/frontend/skills/shared/SKILL.md", "shared", body="local-body")
        self.skill("agents/frontend/skills/private/SKILL.md", "private")
        self.agent(
            "agents/frontend/frontend.yml",
            "name: F\nbase_model: smart\nskills: [shared]\nprompt: hi\n",
        )
        by_id = {s["id"]: s for s in self.load()["frontend"]["skills"]}
        self.assertEqual(set(by_id), {"shared", "private"})
        self.assertEqual(by_id["shared"]["content"], "local-body")

    def test_local_mcp_overrides_shared(self):
        self.mcp("mcps/gw.json", "gw", tool_id="server:mcp:shared")
        self.mcp("agents/a/mcps/gw.json", "gw", tool_id="server:mcp:local")
        self.agent("agents/a/a.yml", "name: A\nbase_model: smart\nmcps: [gw]\nprompt: hi\n")
        self.assertEqual(self.load()["a"]["tools"], ["server:mcp:local"])

    def test_unknown_skill_reference_is_rejected(self):
        self.agent(
            "agents/a/a.yml",
            "name: A\nbase_model: smart\nskills: [ghost]\nprompt: hi\n",
        )
        with self.assertRaises(SystemExit) as ctx:
            load_workspaces(self.root)
        self.assertIn("unknown skill", str(ctx.exception))

    def test_conflicting_local_skills_are_rejected(self):
        self.skill("agents/a/skills/x/SKILL.md", "x", body="one")
        self.skill("agents/b/skills/x/SKILL.md", "x", body="two")
        self.agent("agents/a/a.yml", "name: A\nbase_model: smart\nprompt: hi\n")
        self.agent("agents/b/b.yml", "name: B\nbase_model: smart\nprompt: hi\n")
        with self.assertRaises(SystemExit) as ctx:
            load_workspaces(self.root)
        self.assertIn("conflicting skill", str(ctx.exception))

    # -- publish ----------------------------------------------------------- #
    def test_publish_false_is_extend_only(self):
        self.skill("agents/base/skills/s/SKILL.md", "s")
        self.agent("agents/base/base.yml", "name: Base\npublish: false\nprompt: BASE\n")
        self.agent(
            "agents/child/child.yml",
            "name: Child\nextends: base\nbase_model: smart\nprompt: hi\n",
        )
        agents = self.load()
        self.assertFalse(agents["base"]["publish"])
        # The unpublished base still contributes its skill to the published child.
        self.assertEqual([s["id"] for s in collect_skills(list(agents.values()))], ["s"])

    # -- prompts ----------------------------------------------------------- #
    def test_shared_prompts_load(self):
        self.write(
            "prompts/review-ui.md",
            "---\nname: Review UI\ndescription: d\n---\n\nbody\n",
        )
        prompts = load_prompts_dir(os.path.join(self.root, SHARED_PROMPTS))
        self.assertEqual(prompts[0]["command"], "review-ui")
        self.assertEqual(prompts[0]["name"], "Review UI")

    # -- model payload ----------------------------------------------------- #
    def test_system_prompt_goes_in_params_not_meta(self):
        agent = {
            "id": "a",
            "name": "A",
            "description": "d",
            "base_model": "smart",
            "instructions": "PROMPT",
            "tags": [],
            "skills": [],
            "tools": [],
            "params": {"temperature": 0.2},
        }
        model = build_model(agent)
        self.assertEqual(model["params"]["system"], "PROMPT")
        self.assertEqual(model["params"]["temperature"], 0.2)
        self.assertNotIn("system", model["meta"])

    # -- plan -------------------------------------------------------------- #
    def test_print_plan_shows_inheritance(self):
        self.agent("agents/base/base.yml", "name: Base\npublish: false\nprompt: BASE\n")
        self.agent(
            "agents/child/child.yml",
            "name: Child\nextends: base\nbase_model: smart\nprompt: hi\n",
        )
        agents = list(load_workspaces(self.root))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            print_plan(agents, [])
        text = out.getvalue()
        self.assertIn("(extend-only)", text)
        self.assertIn("extends     : base", text)
        self.assertIn("1 agent(s)", text)


if __name__ == "__main__":
    unittest.main()
