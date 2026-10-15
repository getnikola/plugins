# -*- coding: utf-8 -*-
"""Tests for the ai_chatbot plugin, in the layout of the getnikola/plugins repo.

Each test makes a real Nikola site object, loads the plugin from v8/ai_chatbot
and reads the BODY_END setting that every theme prints before </body>.
"""

import os

import pytest

from nikola import Nikola

from v8.ai_chatbot.ai_chatbot import DEFAULT_SCRIPT_URL, build_tag

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v8", "ai_chatbot")
WIDGET_ID = "asyntai_1a2b3c4d5e6f"
TAG = build_tag(WIDGET_ID, DEFAULT_SCRIPT_URL)


def make_site(**config):
    config.setdefault("EXTRA_PLUGINS_DIRS", [PLUGIN_DIR])
    site = Nikola(**config)
    site.init_plugins()
    return site


@pytest.fixture(autouse=True)
def in_tmp_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_tag_shape():
    assert TAG == (
        '<script async src="https://widget.asyntai.com/static/js/chat-widget.js" '
        'data-asyntai-id="asyntai_1a2b3c4d5e6f"></script>'
    )


def test_adds_tag_to_body_end():
    site = make_site(ASYNTAI_WIDGET_ID=WIDGET_ID)
    assert site.config["BODY_END"]("en").count(TAG) == 1
    assert site.GLOBAL_CONTEXT["body_end"]("en").count(TAG) == 1


def test_keeps_existing_body_end():
    site = make_site(ASYNTAI_WIDGET_ID=WIDGET_ID, BODY_END="<script>var a = 1;</script>")
    body_end = site.config["BODY_END"]("en")
    assert body_end.startswith("<script>var a = 1;</script>")
    assert body_end.endswith(TAG)


def test_every_language():
    site = make_site(
        ASYNTAI_WIDGET_ID=WIDGET_ID,
        TRANSLATIONS={"en": "", "cs": "./cs"},
        BODY_END={"en": "<i>en</i>", "cs": "<i>cs</i>"},
    )
    assert site.config["BODY_END"]("en") == "<i>en</i>\n" + TAG
    assert site.config["BODY_END"]("cs") == "<i>cs</i>\n" + TAG


@pytest.mark.parametrize("widget_id", ["", "1a2b3c4d5e6f", "asyntai_bad id"])
def test_missing_or_bad_id_adds_nothing(widget_id):
    site = make_site(ASYNTAI_WIDGET_ID=widget_id)
    assert "data-asyntai-id" not in site.config["BODY_END"]("en")


def test_no_second_widget_when_snippet_already_pasted():
    pasted = '<script async src="x.js" data-asyntai-id="asyntai_pasted99"></script>'
    site = make_site(ASYNTAI_WIDGET_ID=WIDGET_ID, BODY_END=pasted)
    assert site.config["BODY_END"]("en") == pasted


def test_custom_script_url():
    site = make_site(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SCRIPT_URL="https://cdn.example.com/w.js")
    assert 'src="https://cdn.example.com/w.js"' in site.config["BODY_END"]("en")
