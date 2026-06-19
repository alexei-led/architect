"""Thin Python helpers for the architect extension.

Helpers do only what an LLM should not do by hand: tool-availability checks,
report validation, and report comparison. They never wrap evidence tools such
as ast-grep, codegraph, GitNexus, LSP, or tree-sitter; agents call those
directly.
"""

__version__ = "0.4.0"
