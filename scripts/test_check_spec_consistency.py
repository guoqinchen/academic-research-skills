"""Unit tests for check_spec_consistency.py."""
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts._test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_spec_consistency.py"


def _run() -> subprocess.CompletedProcess:
    return run_script(SCRIPT)


class TestSpecConsistencyIntegration(unittest.TestCase):
    """Integration tests: run script against the real codebase."""

    def test_passes_against_real_codebase(self) -> None:
        result = _run()
        self.assertEqual(result.returncode, 0, msg=result.stderr)


class TestCheckRelativeMarkdownLinks(unittest.TestCase):
    """Unit tests for the check_relative_markdown_links function."""

    def test_broken_link_detected(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            doc = Path(tmp) / "doc.md"
            doc.write_text("[foo](nonexistent.md)", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_relative_markdown_links("doc.md")

                self.assertTrue(
                    any("nonexistent.md" in e for e in errors),
                    f"Expected broken link error, got: {errors}",
                )

    def test_http_link_skipped(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            doc = Path(tmp) / "doc.md"
            doc.write_text("[Google](https://google.com)", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_relative_markdown_links("doc.md")

                self.assertEqual(errors, [])

    def test_anchor_link_skipped(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            doc = Path(tmp) / "doc.md"
            doc.write_text("[section](#section-name)", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_relative_markdown_links("doc.md")

                self.assertEqual(errors, [])

    def test_valid_relative_link_passes(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            subdir = Path(tmp) / "sub"
            subdir.mkdir()
            doc = subdir / "doc.md"
            target = subdir / "target.md"
            target.write_text("# Target", encoding="utf-8")
            doc.write_text("[target](target.md)", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_relative_markdown_links("sub/doc.md")

                self.assertEqual(errors, [])


class TestExtractSection(unittest.TestCase):
    """Unit tests for the extract_section helper."""

    def test_missing_start_reports_error(self) -> None:
        import check_spec_consistency as csc

        csc.ERRORS.clear()
        result = csc.extract_section("no marker here", "[START]", "[END]")
        self.assertEqual(result, "")
        self.assertTrue(any("missing section start" in e for e in csc.ERRORS))

    def test_missing_end_returns_to_end_of_text(self) -> None:
        import check_spec_consistency as csc

        csc.ERRORS.clear()
        text = "[START]content[END]after"
        result = csc.extract_section(text, "[START]", "[MISSING]")
        self.assertEqual(result, "[START]content[END]after")
        # No new error reported for missing end (legacy behavior)

    def test_both_present_returns_slice(self) -> None:
        import check_spec_consistency as csc

        csc.ERRORS.clear()
        text = "prefix[START]middle[END]suffix"
        result = csc.extract_section(text, "[START]", "[END]")
        # text[start_idx:end_idx] is exclusive of end, so we get [START] + content up to but not including [END]
        self.assertEqual(result, "[START]middle")


class TestModeRegistryChecks(unittest.TestCase):
    """Unit tests for mode-registry-specific validation."""

    def test_mode_registry_heading_missing_fails(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            registry = Path(tmp) / "MODE_REGISTRY.md"
            registry.write_text("no headings here", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_mode_registry()

                self.assertTrue(
                    any("missing mode heading" in e for e in errors),
                    f"Expected missing heading error, got: {errors}",
                )

    def test_mode_registry_stale_version_fails(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            registry = Path(tmp) / "MODE_REGISTRY.md"
            registry.write_text("Last updated: v3.3.0 (2026-01-01)", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_mode_registry()

                self.assertTrue(
                    any("missing expected text" in e for e in errors),
                    f"Expected stale version error, got: {errors}",
                )


class TestReviewerVersionBlock(unittest.TestCase):
    """Unit tests for reviewer version block consistency."""

    def test_version_mismatch_fails(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            skill = Path(tmp) / "academic-paper-reviewer" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text(
                '---\nname: academic-paper-reviewer\nmetadata:\n  version: "1.4"\n  last_updated: "2026-04-15"\n---\n# Header\n| Skill Version | 99.9 |\n| Last Updated | 2026-04-15 |\n',
                encoding="utf-8",
            )

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_reviewer_version_block()

                self.assertTrue(
                    any("does not match" in e for e in errors),
                    f"Expected version mismatch error, got: {errors}",
                )


class TestReadmeSectionChecks(unittest.TestCase):
    """Unit tests for README section validation."""

    def test_missing_version_heading_fails(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text("no version heading", encoding="utf-8")

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_readme_sections()

                self.assertTrue(
                    any("missing heading" in e for e in errors),
                    f"Expected missing heading error, got: {errors}",
                )

    def test_forbidden_text_fails(self) -> None:
        import check_spec_consistency as csc

        with TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text(
                "#### Academic Paper (10 modes)\nout-of-scope content\n"
                "#### Academic Paper Reviewer (6 modes)\n6th independent reviewer\n",
                encoding="utf-8",
            )

            with patch.object(csc, "ROOT", Path(tmp)):
                errors: list[str] = []
                with patch.object(csc, "fail", errors.append):
                    csc.check_readme_sections()

                self.assertTrue(
                    any("6th independent reviewer" in e for e in errors),
                    f"Expected forbidden text error, got: {errors}",
                )


if __name__ == "__main__":
    unittest.main()
