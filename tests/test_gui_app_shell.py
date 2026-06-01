from pathlib import Path


def test_app_shell_tokens_present() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    for t in [
        'property string currentPage: "home"',
        'home','user','calibration','training','report','developer_lab',
        'Home','User','Calibration','Training','Report','Developer Lab',
        'current_user_id','connection_status','quality_state','control_state',
        'session_active','profile_status','calibration_status','latest_report_path',
        'profile_loaded','user_type','attention_low_threshold','attention_high_threshold',
        'preferred_game_id','calibration_usable','last_calibration_id','failure_reason',
        'First Profile Calibration','Quick Check','Periodic Recalibration',
        'Triggered Recalibration','GameCanvas will be restored in TASK24',
        'score','combo','level','session_elapsed_ms','behavior_sample_count',
        'Fragment Lock','Signal Hunter','Stabilizer','last_session_status',
        'current_session_id','attention','gyro_x','sqi','fi_smoothed',
        'warning_flags','error_flags'
    ]:
        assert t in qml


def test_diagnostics_user_visible_navigation_is_removed_but_compat_host_remains() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    home = Path('ui_qml/pages/HomePage.qml').read_text(encoding='utf-8')
    assert 'text: "Diagnostics"' not in qml
    assert 'text: "Go Diagnostics"' not in qml
    assert 'Go Diagnostics' not in home
    assert 'DiagnosticsPage' in qml
    assert 'visible: root.currentPage === "diagnostics"' in qml
    assert 'Go Developer Lab' in home
    assert 'navigateTo("developer_lab")' in home


def test_home_page_formal_shortcut_cards_present() -> None:
    home = Path('ui_qml/pages/HomePage.qml').read_text(encoding='utf-8')
    for token in [
        'RELIC Focus Training',
        'home_intro_card',
        'home_workflow_card',
        'home_shortcut_cards',
        'home_entry_user_card',
        'home_entry_calibration_card',
        'home_entry_training_card',
        'home_entry_report_card',
        'home_entry_developer_lab_card',
        'home_status_overview_card',
        'Open User',
        'Open Calibration',
        'Open Training',
        'Open Report',
        'Open Developer Lab',
        'navigateTo("user")',
        'navigateTo("calibration")',
        'navigateTo("training")',
        'navigateTo("report")',
        'navigateTo("developer_lab")',
        'Page Commands',
        'Page Feedback',
    ]:
        assert token in home
    assert 'Go Diagnostics' not in home


def test_shell_card_topbar_and_sidebar_tokens_present() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    for token in [
        'shell_top_status_card',
        'shell_brand_card',
        'shell_status_chip_current_user',
        'shell_status_chip_connection',
        'shell_status_chip_quality',
        'shell_status_chip_control',
        'shell_status_chip_session',
        'shell_status_chip_current_page',
        'shell_left_nav_card',
        'shell_nav_header_card',
        'shell_nav_info_accent_strip',
        'NAVIGATION INFO',
        'Page shortcuts',
        'Cards below are clickable',
        'shell_nav_readability_tokens',
        'navInfoCardBackground',
        'navInfoCardText',
        'navActionCardBackground',
        'navActionCardText',
        'navCardMutedText',
        'shell_nav_card_home',
        'shell_nav_card_user',
        'shell_nav_card_calibration',
        'shell_nav_card_training',
        'shell_nav_card_report',
        'shell_nav_card_developer_lab',
        'shell_nav_active_strip_home',
        'shell_nav_active_strip_user',
        'shell_nav_active_strip_calibration',
        'shell_nav_active_strip_training',
        'shell_nav_active_strip_report',
        'shell_nav_active_strip_developer_lab',
        'shell_global_safety_card',
        'shell_content_host_card',
        'navCardBackground',
        'navCardBorder',
        'navCardText',
        'goPage',
    ]:
        assert token in qml
    assert 'text: "Diagnostics"' not in qml
    assert 'shell_nav_card_diagnostics' not in qml


def test_app_shell_layout_json_has_card_shell_fields() -> None:
    text = Path('assets/layouts/app_shell.json').read_text(encoding='utf-8')
    for token in [
        'card_status_bar',
        'desktop_card_nav',
        'top_bar_height',
        'nav_width',
        'corner_radius',
        'nav_card_padding',
        'nav_item_gap',
        'status_chip_radius',
        'active_page_color',
        'active_page_text',
        'inactive_page_text',
        'nav_info_background',
        'nav_info_text',
        'non_clickable_nav_info_card',
        'clickable_nav_action_card',
        'safety_card_background',
        'shell_content_host_card',
    ]:
        assert token in text



def test_shell_nav_readability_colors_are_explicit() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    layout = Path('assets/layouts/app_shell.json').read_text(encoding='utf-8')
    for token in [
        '#EAF6FF',
        '#FFFFFF',
        '#CFE8F7',
        '#7FA4B8',
        'inactive_page_text',
        'active_page_text',
        'nav_info_text',
        'nav_info_muted_text',
        'active_page_accent_strip',
    ]:
        assert token in qml or token in layout
    assert 'return root.isCurrentPage(pageId) ? "#06131D"' not in qml
