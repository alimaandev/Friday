import os

import pytest

from core.knowledge import KnowledgeGraph


@pytest.fixture
def graph(tmp_path):
    return KnowledgeGraph(os.path.join(tmp_path, "knowledge.json"))


def test_store_and_query_entities(graph):
    graph.store("I am building the Friday app and working with Sarah on the API.")
    results = graph.query("friday")
    assert results, "expected entities to be extracted"
    assert any(r["type"] == "project" for r in results)

    people = graph.query("sarah")
    assert people and people[0]["type"] == "person"


def test_mentions_increment_on_repeated_store(graph):
    graph.store("the Friday app")
    graph.store("the Friday app again")
    node = graph.query("friday")[0]
    assert node["mentions"] >= 2


def test_continuity_returns_known_topics(graph):
    graph.store("working on the hologram engine")
    continuity = graph.continuity()
    assert "hologram" in continuity.lower()


def test_continuity_empty_when_no_entities(graph):
    assert graph.continuity() == ""


def test_persistence_roundtrip(tmp_path):
    path = os.path.join(tmp_path, "knowledge.json")
    g1 = KnowledgeGraph(path)
    g1.store("the beta orb")
    g2 = KnowledgeGraph(path)
    assert g2.query("beta")


def test_connections_finds_existing_mentions(graph):
    graph.store("the Friday app and Sarah")
    hits = graph.connections("I need help with Friday, and Sarah said hi.")
    assert any(h["name"].lower() == "friday" for h in hits)
    assert any(h["name"].lower() == "sarah" for h in hits)
