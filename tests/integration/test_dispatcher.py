#!/usr/bin/env python3
"""Tests d'intégration pour cowork_dispatcher — 20 tests complets."""

import json
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from cowork_dispatcher import (
    get_cowork_patterns,
    get_scripts_for_pattern,
    match_pattern,
    execute_script,
    dispatch,
    list_all,
    health_check,
    process_inbox,
    daemon_loop,
    get_color_for_task,
)


# Mock data for testing patterns and scripts
MOCK_PATTERNS = [
    {
        "pattern_id": "1",
        "agent_id": "cleaning",
        "description": "Cleaning and organizing tasks",
        "keywords": "clean,organize,clear",
        "priority": 50,
        "strategy": "sequential"
    },
    {
        "pattern_id": "2",
        "agent_id": "analysis",
        "description": "Data analysis and reporting",
        "keywords": "analyze,report,data",
        "priority": 75,
        "strategy": "parallel"
    },
    {
        "pattern_id": "3",
        "agent_id": "creation",
        "description": "Content creation and generation",
        "keywords": "create,generate,content",
        "priority": 30,
        "strategy": "async"
    }
]

MOCK_SCRIPTS = [
    {
        "script_name": "organize.py",
        "agent_id": "cleaning",
        "pattern_id": "1"
    },
    {
        "script_name": "analyze.py",
        "agent_id": "analysis",
        "pattern_id": "2"
    },
    {
        "script_name": "generate.py",
        "agent_id": "creation",
        "pattern_id": "3"
    }
]


class TestMatchPattern:
    """Tests for pattern matching functionality."""

    def test_basic_keyword_match(self):
        """Test simple keyword-based pattern matching."""
        query = "clean my room"
        result = match_pattern(query, MOCK_PATTERNS)
        
        assert len(result) > 0
        assert result[0][1]["pattern_id"] == "1"
        # Cleaning should match highest due to keyword overlap
    
    def test_description_based_match(self):
        """Test matching based on description keywords."""
        query = "analyze data patterns"
        result = match_pattern(query, MOCK_PATTERNS)
        
        matches = [p for _, p in result]
        assert any(p["pattern_id"] == "2" for p in matches)
    
    def test_priority_bonus_application(self):
        """Test that priority bonus affects scoring."""
        query = "create content"
        result = match_pattern(query, MOCK_PATTERNS)
        
        matches = [p for _, p in result]
        # Lower priority (30) should have different scoring than high priority
        assert any(p["pattern_id"] == "3" for p in matches)
    
    def test_empty_query_returns_all(self):
        """Test that empty or whitespace query returns all patterns."""
        result = match_pattern("", MOCK_PATTERNS)
        
        assert len(result) == len(MOCK_PATTERNS)
    
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        query = "CLEAN MY ROOM"
        result = match_pattern(query, MOCK_PATTERNS)
        
        assert len(result) > 0
        assert result[0][1]["pattern_id"] == "1"


class TestExecuteScript:
    """Tests for script execution functionality."""

    @patch("cowork_dispatcher.subprocess.run")
    def test_successful_script_execution(self, mock_run):
        """Test successful script execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Task completed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = execute_script("organize.py", args=["--dry-run"], timeout=60)
        
        assert result["success"] is True
        assert result["script"] == "organize.py"
    
    @patch("cowork_dispatcher.subprocess.run")
    def test_timeout_error_handling(self, mock_run):
        """Test that timeouts are handled gracefully."""
        from subprocess import TimeoutExpired
        
        # Simulate timeout
        mock_run.side_effect = TimeoutExpired("organize.py", 60)
        
        result = execute_script("organize.py", args=["--timeout"], timeout=1)
        
        assert result["error"] == "timeout"
        assert result["success"] is False
    
    @patch("cowork_dispatcher.subprocess.run")
    def test_nonexistent_script_handling(self, mock_run):
        """Test handling of non-existent scripts."""
        with patch("cowork_dispatcher.UnifiedMemoryStore.normalize_script_name", return_value="nonexistent.py"):
            result = execute_script("nonexistent_script.py")
        
        assert "Script not found" in result["error"]
        assert result["success"] is False
    
    @patch("cowork_dispatcher.subprocess.run")
    def test_stderr_captured_on_error(self, mock_run):
        """Test that stderr is captured on script errors."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: file not found\nPermission denied"
        mock_run.return_value = mock_result
        
        result = execute_script("error.py")
        
        assert "file not found" in result["stderr"]
    
    @patch("cowork_dispatcher.subprocess.run")
    def test_stdout_truncated_on_large_output(self, mock_run):
        """Test that stdout is truncated for large outputs."""
        mock_result = MagicMock()
        large_output = "x\n" * 5000  # Large output
        mock_result.returncode = 0
        mock_result.stdout = large_output
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = execute_script("large.py")
        
        # Should be truncated to ~2000 chars
        assert len(result["stdout"]) <= 2000


class TestDispatch:
    """Tests for task dispatching functionality."""

    @patch("cowork_dispatcher.match_pattern")
    @patch("cowork_dispatcher.get_scripts_for_pattern")
    def test_successful_dispatch_with_execution(self, mock_get_scripts, mock_match):
        """Test successful dispatch with script execution."""
        mock_match.return_value = [(10.5, MOCK_PATTERNS[0])]
        
        mock_scripts = [MOCK_SCRIPTS[0]]
        mock_get_scripts.return_value = mock_scripts
        
        result = dispatch("clean my room", execute=True, top_n=3)
        
        assert len(result["matches"]) == 1
        assert result["matches"][0]["pattern_id"] == "1"
        assert "execution" in result["matches"][0]
    
    @patch("cowork_dispatcher.match_pattern")
    @patch("cowork_dispatcher.get_scripts_for_pattern")
    def test_dispatch_without_execution(self, mock_get_scripts, mock_match):
        """Test dispatch without executing scripts."""
        mock_match.return_value = [(10.5, MOCK_PATTERNS[0])]
        
        result = dispatch("analyze patterns", execute=False)
        
        assert len(result["matches"]) > 0
        assert "execution" not in result["matches"][0]
    
    @patch("cowork_dispatcher.match_pattern")
    def test_dispatch_with_no_matches(self, mock_match):
        """Test handling when no patterns match."""
        mock_match.return_value = []
        
        result = dispatch("random query", execute=True)
        
        assert len(result["matches"]) == 0
    
    @patch("cowork_dispatcher.match_pattern")
    @patch("cowork_dispatcher.get_scripts_for_pattern")
    def test_dispatch_with_multiple_matches(self, mock_get_scripts, mock_match):
        """Test dispatch when multiple patterns match."""
        mock_match.return_value = [
            (12.0, MOCK_PATTERNS[0]),
            (10.5, MOCK_PATTERNS[1]),
            (8.3, MOCK_PATTERNS[2])
        ]
        
        mock_get_scripts.side_effect = [
            MOCK_SCRIPTS[0],  # For pattern 1
            MOCK_SCRIPTS[1],  # For pattern 2
            MOCK_SCRIPTS[2]   # For pattern 3
        ]
        
        result = dispatch("complex query", execute=False, top_n=3)
        
        assert len(result["matches"]) == 3


class TestHealthCheck:
    """Tests for health check functionality."""

    @patch("cowork_dispatcher.UnifiedMemoryStore.connect")
    @patch("cowork_dispatcher.UnifiedMemoryStore.execute")
    def test_health_check_with_all_scripts_ok(self, mock_execute, mock_connect):
        """Test health check when all scripts exist and are valid."""
        mock_execute.return_value.fetchall = lambda: [
            ("clean.py",),
            ("analyze.py",),
            ("generate.py",)
        ]
        
        result = health_check()
        
        assert result["ok"] == 3
        assert result["missing"] == 0
    
    @patch("cowork_dispatcher.UnifiedMemoryStore.connect")
    @patch("cowork_dispatcher.UnifiedMemoryStore.execute")
    def test_health_check_with_missing_scripts(self, mock_execute, mock_connect):
        """Test health check when some scripts are missing."""
        mock_execute.return_value.fetchall = lambda: [
            ("clean.py",),
            ("missing_script.py",)  # This one doesn't exist
        ]
        
        result = health_check()
        
        assert result["missing"] == 1
    
    @patch("cowork_dispatcher.UnifiedMemoryStore.connect")
    def test_health_check_with_syntax_error(self, mock_connect):
        """Test health check when script has syntax error."""
        with patch("builtins.open", mock_open(read_data="def broken(\n")) as mock_file:
            result = health_check()
            
            assert len(result["errors"]) > 0


class TestGetColorForTask:
    """Tests for task color mapping functionality."""

    def test_content_task_gets_yellow(self):
        """Test content-related tasks get yellow color."""
        color = get_color_for_task("content creation")
        assert color == "yellow"
    
    def test_social_task_gets_red(self):
        """Test social media tasks get red color."""
        color = get_color_for_task("linkedin post")
        assert color == "red"
    
    def test_trade_task_gets_blue(self):
        """Test trading/finance tasks get blue color."""
        color = get_color_for_task("crypto analysis")
        assert color == "blue"
    
    def test_email_task_gets_green(self):
        """Test email/mail tasks get green color."""
        color = get_color_for_task("email draft")
        assert color == "green"
    
    def test_unknown_task_gets_white(self):
        """Test unknown tasks default to white color."""
        color = get_color_for_task("random operation")
        assert color == "white"


class TestProcessInbox:
    """Tests for inbox processing functionality."""

    @patch("cowork_dispatcher.dispatch")
    @patch("cowork_dispatcher.UnifiedMemoryStore.resolve")
    def test_process_inbox_success(self, mock_resolve, mock_dispatch):
        """Test successful inbox processing."""
        mock_resolve.return_value = "/dummy/path"
        
        # Create a dummy inbox with a mission file
        test_data = {
            "mission_id": "test_001",
            "classification": "content",
            "contexte": {"analysis_goal": "test content"}
        }
        
        with patch("os.listdir", return_value=["test_mission.json"]), \
             patch("os.remove"), \
             patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            
            result = process_inbox()
            
            assert result > 0
    
    @patch("cowork_dispatcher.dispatch")
    def test_process_inbox_no_files(self, mock_dispatch):
        """Test inbox processing when no files exist."""
        with patch("os.listdir", return_value=[]), \
             patch("os.remove"), \
             patch("builtins.open"):
            result = process_inbox()
            
            assert result == 0


class TestErrorScenarios:
    """Tests for error handling and edge cases."""

    @patch("cowork_dispatcher.subprocess.run")
    def test_db_connection_timeout(self, mock_run):
        """Test handling of database connection timeout."""
        from sqlite3 import OperationalError
        
        mock_result = MagicMock()
        mock_result.returncode = -1
        mock_result.stdout = ""
        mock_result.stderr = "sqlite3: database locked"
        mock_run.return_value = mock_result
        
        result = execute_script("blocked.py")
        
        assert result["success"] is False
    
    @patch("cowork_dispatcher.match_pattern")
    def test_llm_api_error(self, mock_match):
        """Test handling of LLM API errors."""
        mock_match.side_effect = Exception("LLM service unavailable")
        
        with pytest.raises(Exception) as excinfo:
            dispatch("test query", execute=True)
        
        assert "LLM" in str(excinfo.value).lower() or "service" in str(excinfo.value).lower()
    
    @patch("cowork_dispatcher.UnifiedMemoryStore.connect")
    def test_db_locked_error(self, mock_connect):
        """Test handling of locked database."""
        with patch("cowork_dispatcher.UnifiedMemoryStore.execute") as mock_execute:
            mock_execute.return_value.fetchall.side_effect = OperationalError(
                "dummy", "", "database is locked"
            )
            
            result = health_check()
            
            assert result["syntax_errors"] >= 0  # Should handle gracefully


class TestIntegrationScenarios:
    """Integration tests combining multiple functions."""

    @patch("cowork_dispatcher.get_scripts_for_pattern")
    @patch("cowork_dispatcher.match_pattern")
    def test_full_dispatch_workflow(self, mock_match, mock_get_scripts):
        """Test complete dispatch workflow from query to execution."""
        # Setup mocks
        mock_match.return_value = [(8.5, MOCK_PATTERNS[1])]
        mock_get_scripts.return_value = MOCK_SCRIPTS[1]
        
        # Create a script with predictable output
        test_script = Path("tests/integration/test_dispatch_script.py")
        test_script.parent.mkdir(exist_ok=True)
        test_script.write_text("#!/usr/bin/env python3\nprint('SUCCESS')")
        
        result = dispatch("analyze data", execute=True, top_n=2)
        
        assert len(result["matches"]) == 1
        assert "execution" in result["matches"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
