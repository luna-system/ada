"""Tests for MCP resource handlers."""

import pytest
from pathlib import Path

from ada_mcp.resources import RESOURCES, URI_TO_PATH, read_resource, get_resource_by_uri


class TestResourceDefinitions:
    """Test resource metadata and definitions."""

    def test_all_resources_defined(self):
        """Verify expected resources are present."""
        expected_uris = [
            "ada://docs/context",
            "ada://docs/codebase-map",
            "ada://docs/specialist-registry",
            "ada://docs/conventions",
            "ada://docs/quickstart",
            "ada://docs/gotchas",
            "ada://docs/testing",
        ]
        
        # Convert AnyUrl to strings for comparison
        resource_uris = [str(r.uri) for r in RESOURCES]
        assert set(resource_uris) == set(expected_uris)

    def test_resources_have_metadata(self):
        """Verify all resources have required metadata."""
        for resource in RESOURCES:
            assert resource.uri
            assert resource.name
            assert resource.description
            assert resource.mimeType
            assert "annotations" in resource.model_dump()

    def test_resources_have_priority(self):
        """Verify all resources have priority annotations."""
        for resource in RESOURCES:
            annotations = resource.model_dump().get("annotations", {})
            assert "priority" in annotations
            priority = annotations["priority"]
            assert 0.0 <= priority <= 1.0

    def test_resources_have_audience(self):
        """Verify all resources specify assistant audience."""
        for resource in RESOURCES:
            annotations = resource.model_dump().get("annotations", {})
            assert "audience" in annotations
            assert "assistant" in annotations["audience"]


class TestResourcePaths:
    """Test resource file path mappings."""

    def test_all_uris_mapped(self):
        """Verify all resource URIs have file path mappings."""
        for resource in RESOURCES:
            # Convert AnyUrl to string for comparison
            assert str(resource.uri) in URI_TO_PATH

    def test_all_files_exist(self):
        """Verify all mapped files exist in the .ai/ directory."""
        for uri, path in URI_TO_PATH.items():
            assert path.exists(), f"File not found for {uri}: {path}"

    def test_json_files_are_valid(self):
        """Verify JSON files are valid JSON."""
        import json
        
        for uri, path in URI_TO_PATH.items():
            if path.suffix == ".json":
                with open(path, "r") as f:
                    data = json.load(f)
                    assert isinstance(data, dict)

    def test_markdown_files_are_readable(self):
        """Verify Markdown files can be read."""
        for uri, path in URI_TO_PATH.items():
            if path.suffix == ".md":
                content = path.read_text(encoding="utf-8")
                assert len(content) > 0


class TestResourceReading:
    """Test resource reading functionality."""

    @pytest.mark.asyncio
    async def test_read_markdown_resource(self):
        """Test reading a Markdown resource."""
        contents = await read_resource("ada://docs/context")
        
        assert len(contents) == 1
        assert contents[0].type == "text"
        assert "# Ada" in contents[0].text or "Ada" in contents[0].text

    @pytest.mark.asyncio
    async def test_read_json_resource(self):
        """Test reading a JSON resource."""
        import json
        
        contents = await read_resource("ada://docs/codebase-map")
        
        assert len(contents) == 1
        assert contents[0].type == "text"
        
        # Verify it's valid JSON
        data = json.loads(contents[0].text)
        assert "modules" in data or "version" in data

    @pytest.mark.asyncio
    async def test_read_unknown_resource(self):
        """Test reading an unknown resource raises error."""
        with pytest.raises(ValueError, match="Unknown resource URI"):
            await read_resource("ada://docs/nonexistent")

    @pytest.mark.asyncio
    async def test_all_resources_readable(self):
        """Verify all defined resources can be read."""
        for resource in RESOURCES:
            contents = await read_resource(resource.uri)
            assert len(contents) > 0
            assert contents[0].type == "text"
            assert len(contents[0].text) > 0


class TestResourceLookup:
    """Test resource lookup functionality."""

    def test_get_resource_by_uri(self):
        """Test looking up resource by URI."""
        resource = get_resource_by_uri("ada://docs/context")
        
        assert resource is not None
        # Convert AnyUrl to string for comparison
        assert str(resource.uri) == "ada://docs/context"
        assert resource.name == "Architecture Context"

    def test_get_unknown_resource(self):
        """Test looking up unknown resource returns None."""
        resource = get_resource_by_uri("ada://docs/nonexistent")
        assert resource is None

    def test_get_all_resources(self):
        """Test looking up all resources."""
        for expected in RESOURCES:
            found = get_resource_by_uri(expected.uri)
            assert found is not None
            assert found.uri == expected.uri
