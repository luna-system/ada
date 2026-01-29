"""
Code Analysis Tools 🔍

AST-grep and UBS tools for code analysis.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import subprocess


def register_code_analysis_tools(mcp, get_path_context, format_path_context):
    """Register code analysis tools (AST-grep and UBS)."""

    @mcp.tool()
    def ast_grep_search(
        pattern: str,
        language: str,
        paths: str = ".",
        cwd: str = None,
        context: int = 0,
        json_output: bool = False,
    ) -> str:
        """Search code using AST-based pattern matching."""
        path_context = get_path_context(cwd)
        working_dir = path_context["full_path"]

        output = format_path_context(path_context) + "\n"
        output += f"🔍 AST-grep search\n"
        output += f"📝 Pattern: {pattern}\n"
        output += f"🗣️  Language: {language}\n\n"

        try:
            cmd = ["ast-grep", "run", "--pattern", pattern, "--lang", language]
            if json_output:
                cmd.append("--json")
            if context > 0:
                cmd.extend(["--context", str(context)])
            if paths != ".":
                cmd.append(paths)

            result = subprocess.run(
                cmd, cwd=working_dir, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                if result.stdout:
                    return result.stdout if json_output else output + "--- Matches ---\n" + result.stdout
                else:
                    return output + "✨ No matches found\n"
            else:
                return output + f"❌ Error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return output + "❌ Search timed out after 30s"
        except Exception as e:
            return output + f"❌ Error: {str(e)}"

    @mcp.tool()
    def ast_grep_rewrite(
        pattern: str,
        rewrite: str,
        language: str,
        paths: str = ".",
        cwd: str = None,
        dry_run: bool = True,
    ) -> str:
        """Rewrite code using AST-based pattern matching."""
        path_context = get_path_context(cwd)
        working_dir = path_context["full_path"]

        output = format_path_context(path_context) + "\n"
        output += f"🔧 AST-grep rewrite\n"
        output += f"📝 Pattern: {pattern}\n"
        output += f"✨ Rewrite: {rewrite}\n\n"

        try:
            cmd = ["ast-grep", "run", "--pattern", pattern, "--rewrite", rewrite, "--lang", language]
            if not dry_run:
                cmd.append("--update-all")
                output += "⚠️  WARNING: Files will be modified!\n\n"
            if paths != ".":
                cmd.append(paths)

            result = subprocess.run(
                cmd, cwd=working_dir, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                if result.stdout:
                    output += "--- Changes ---\n" + result.stdout
                    if dry_run:
                        output += "\n\n💡 To apply these changes, call again with dry_run=False"
                    else:
                        output += "\n\n✅ Changes applied!"
                else:
                    output += "✨ No matches found\n"
            else:
                output += f"❌ Error: {result.stderr}"

            return output

        except subprocess.TimeoutExpired:
            return output + "❌ Rewrite timed out after 60s"
        except Exception as e:
            return output + f"❌ Error: {str(e)}"

    @mcp.tool()
    def ast_grep_dump_ast(code: str, language: str) -> str:
        """Dump the AST for a code snippet."""
        output = f"🌳 AST Dump for {language}\n"
        output += f"📝 Code:\n{code}\n\n"

        try:
            result = subprocess.run(
                ["ast-grep", "run", "--debug-query", "--pattern", code, "--lang", language],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.stdout:
                output += "--- AST Structure ---\n" + result.stdout
            elif result.stderr:
                output += result.stderr
            else:
                output += "✨ No AST output\n"

            return output

        except Exception as e:
            return output + f"❌ Error: {str(e)}"

    @mcp.tool()
    def ast_grep_scan(cwd: str = None) -> str:
        """Scan codebase with configured ast-grep rules."""
        path_context = get_path_context(cwd)
        working_dir = path_context["full_path"]

        output = format_path_context(path_context) + "\n"
        output += "🔍 AST-grep scan\n\n"

        try:
            result = subprocess.run(
                ["ast-grep", "scan"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                if result.stdout:
                    output += "--- Scan Results ---\n" + result.stdout
                else:
                    output += "✨ No issues found!\n"
            else:
                if "sgconfig.yml" in result.stderr:
                    output += "⚠️  No sgconfig.yml found.\n"
                else:
                    output += f"❌ Error: {result.stderr}"

            return output

        except subprocess.TimeoutExpired:
            return output + "❌ Scan timed out after 60s"
        except Exception as e:
            return output + f"❌ Error: {str(e)}"

    @mcp.tool()
    def ubs_scan(
        project_dir: str = ".",
        fail_on_warning: bool = False,
        format: str = "json",
        category: str = None,
        staged: bool = False,
        git_diff: bool = False,
        cwd: str = None,
        timeout: int = 60,
    ) -> str:
        """Run Ultimate Bug Scanner on a project."""
        path_context = get_path_context(cwd)
        working_dir = path_context["full_path"]

        output = format_path_context(path_context) + "\n"
        output += f"🔬 Ultimate Bug Scanner\n"
        output += f"📂 Project: {project_dir}\n\n"

        try:
            cmd = ["ubs", project_dir, f"--format={format}"]
            if fail_on_warning:
                cmd.append("--fail-on-warning")
            if category:
                cmd.append(f"--category={category}")
            if staged:
                cmd.append("--staged")
            elif git_diff:
                cmd.append("--git-diff")

            result = subprocess.run(
                cmd, cwd=working_dir, capture_output=True, text=True, timeout=timeout
            )

            if format == "json" or format == "jsonl":
                if result.stdout:
                    return result.stdout
                else:
                    return '{"totals": {"critical": 0, "warning": 0, "info": 0, "files": 0}}'
            else:
                if result.stdout:
                    output += "--- Scan Results ---\n" + result.stdout
                if result.stderr:
                    output += "\n--- Diagnostics ---\n" + result.stderr
                output += f"\n\nExit Code: {result.returncode}"
                if result.returncode == 0:
                    output += " ✅ (No critical issues)"
                elif result.returncode == 1:
                    output += " ⚠️  (Issues found)"
                else:
                    output += " ❌ (Scanner error)"

            return output

        except subprocess.TimeoutExpired:
            return output + f"❌ Scan timed out after {timeout}s"
        except FileNotFoundError:
            return output + "❌ UBS not found"
        except Exception as e:
            return output + f"❌ Error: {str(e)}"
