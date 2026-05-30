# TASK26 Desktop Layout Preview

This patch adds a real layout preview for the TASK26 phone-desktop style card GUI.

The earlier slot preview showed card metadata and rect text, but it did not visually place cards by x/y/width/height. This made title changes visible while position and size edits were hard to verify.

The new flow is:

JSON page config -> Python render model -> layout preview payload -> GuiFacade renderResources -> DeveloperLab DesktopLayoutPreview

Current scope:

- DeveloperLab only
- no HomePage replacement
- no TrainingPage replacement
- no real GameCanvas binding
- no source/action execution
- no QML file loading
- no dynamic Loader/Repeater/Timer

The preview scales the model page, normally 1200x800, into a visible canvas and places cards according to the numeric x/y/width/height produced by gui.desktop_model.build_page_render_model.

This directly supports the future phone-desktop goal:

- mandatory cards remain checked by contract gates
- optional cards may later be added or removed
- layout edits become visually observable
- card title/widget/action/source summaries remain visible
- required/locked cards can still be visually identified
