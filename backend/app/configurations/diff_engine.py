"""
Configuration Diff Engine generating unified diffs, side-by-side matrices, and change statistics.
"""

from typing import List, Tuple
import difflib
from backend.app.configurations.schemas import ConfigDiffResponse, DiffLine


class ConfigDiffEngine:
    @staticmethod
    def compare_configs(source_text: str, target_text: str) -> ConfigDiffResponse:
        """Compute line-by-line unified diff and side-by-side visual matrix."""
        src_lines = source_text.splitlines()
        tgt_lines = target_text.splitlines()

        # Compute unified diff string
        unified = "\n".join(
            difflib.unified_diff(
                src_lines, tgt_lines, fromfile="running_config (before)", tofile="staged_config (after)", lineterm=""
            )
        )

        matcher = difflib.SequenceMatcher(None, src_lines, tgt_lines)
        diff_lines: List[DiffLine] = []
        additions = 0
        deletions = 0
        modifications = 0

        src_idx = 1
        tgt_idx = 1

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for line in src_lines[i1:i2]:
                    diff_lines.append(
                        DiffLine(line_number_src=src_idx, line_number_dst=tgt_idx, type="unchanged", content=line)
                    )
                    src_idx += 1
                    tgt_idx += 1
            elif tag == "replace":
                for line in src_lines[i1:i2]:
                    diff_lines.append(
                        DiffLine(line_number_src=src_idx, line_number_dst=None, type="removed", content=line)
                    )
                    src_idx += 1
                    deletions += 1
                for line in tgt_lines[j1:j2]:
                    diff_lines.append(
                        DiffLine(line_number_src=None, line_number_dst=tgt_idx, type="added", content=line)
                    )
                    tgt_idx += 1
                    additions += 1
                modifications += max(i2 - i1, j2 - j1)
            elif tag == "delete":
                for line in src_lines[i1:i2]:
                    diff_lines.append(
                        DiffLine(line_number_src=src_idx, line_number_dst=None, type="removed", content=line)
                    )
                    src_idx += 1
                    deletions += 1
            elif tag == "insert":
                for line in tgt_lines[j1:j2]:
                    diff_lines.append(
                        DiffLine(line_number_src=None, line_number_dst=tgt_idx, type="added", content=line)
                    )
                    tgt_idx += 1
                    additions += 1

        is_identical = additions == 0 and deletions == 0

        return ConfigDiffResponse(
            unified_diff=unified,
            diff_lines=diff_lines,
            additions=additions,
            deletions=deletions,
            modifications=modifications,
            is_identical=is_identical,
        )
