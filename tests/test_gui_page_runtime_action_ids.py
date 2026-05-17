from pathlib import Path


def test_runtime_action_ids_present_in_pages() -> None:
    checks = {
        'ui_qml/pages/UserPage.qml': ['user.list','user.create','user.load'],
        'ui_qml/pages/CalibrationPage.qml': ['calibration.list','calibration.latest','calibration.show'],
        'ui_qml/pages/ReportPage.qml': ['report.list','report.show','report.export'],
        'ui_qml/pages/DeveloperLabPage.qml': ['devlab.run'],
    }
    for p, ids in checks.items():
        t = Path(p).read_text(encoding='utf-8')
        for aid in ids:
            assert aid in t
