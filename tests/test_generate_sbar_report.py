from src.utils.generate_sbar_report import (
    SBARSnapshot,
    build_markdown_body,
    render_markdown,
)


def test_build_markdown_body_formats_updates():
    initial = {"situation": None, "background": None, "assessment": None, "recommendation": None}
    snapshots = [
        SBARSnapshot(
            index=1,
            t_start=5.0,
            event_text="sat dropping ninety two",
            sbar={"situation": "sat dropping ninety two", "background": None, "assessment": None, "recommendation": None},
        )
    ]

    body = build_markdown_body(initial, snapshots)

    assert "# SBAR Evolution Report" in body
    assert "Update 1" in body
    assert "sat dropping ninety two" in body


def test_render_markdown_appends_critique_section():
    initial = {"situation": None, "background": None, "assessment": None, "recommendation": None}
    body = render_markdown(initial, [], "Critique text.")
    assert "## LLM Critique" in body
    assert "Critique text." in body
