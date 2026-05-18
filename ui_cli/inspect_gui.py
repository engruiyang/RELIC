from __future__ import annotations
import argparse, json, os
from pathlib import Path
from typing import Any


PAGES = ["home","user","calibration","training","report","diagnostics","developer_lab"]
PAGE_PANELS = {
 "user":["userSummaryPanel","userFormPanel","userListPanel","userDetailPanel","userResultPanel"],
 "calibration":["calibrationUserGatePanel","calibrationBindingPanel","calibrationLatestPanel","calibrationListPanel","calibrationDetailPanel","calibrationResultPanel"],
 "training":["trainingSessionPanel","trainingRuntimePanel","trainingHudPanel","trainingGameCanvasPlaceholder","trainingResultPanel"],
 "report":["reportLatestPanel","reportListPanel","reportDetailPanel","reportResultPanel"],
 "diagnostics":["diagnosticsLiveBusPanel","diagnosticsQualityPanel","diagnosticsSnapshotPanel"],
 "developer_lab":["developerCommandDetailPanel","developerPayloadPreviewPanel","developerRunResultPanel","developerMetadataPanel"],
 "home":[],
}
ACTIONS = [("user","user.list"),("user","user.create"),("user","user.load_current"),("calibration","calibration.status"),("calibration","calibration.list"),("calibration","calibration.latest"),("report","report.refresh"),("report","report.list"),("report","report.show"),("training","game.status"),("developer_lab","devlab.run")]

def wait(ms=250):
    from PySide6.QtCore import QEventLoop, QTimer
    loop = QEventLoop(); QTimer.singleShot(ms, loop.quit); loop.exec()

def find(obj,name):
    return obj.findChild(type(obj), name)

def grab(window, path: Path):
    pix = window.screen().grabWindow(window.winId())
    if pix.isNull():
        return "grabWindow returned null pixmap"
    pix.save(str(path))
    if not path.exists() or path.stat().st_size == 0:
        return "empty screenshot file"
    return None

def build_parser():
    p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['mock','core-control','live-readonly','live-control'],default='mock'); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8000); p.add_argument('--user-id',default='TEST'); p.add_argument('--db-path',default='data/relic_local.db'); p.add_argument('--out',required=True); p.add_argument('--width',type=int,default=1280); p.add_argument('--height',type=int,default=800); p.add_argument('--no-screenshots',action='store_true'); return p

def main():
    a=build_parser().parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    try:
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
        from gui.gui_bridge import GuiBridge
        from gui.gui_facade import GuiFacade
    except ModuleNotFoundError as exc:
        report = {"mode": a.mode, "window_size": [a.width, a.height], "pages": {}, "errors": [f"PySide6 unavailable: {exc}"], "screenshots_skipped_reason": "PySide6 not installed"}
        for page in PAGES:
            report["pages"][page] = {"screenshot": f"{page}.png", "screenshots_skipped_reason": "PySide6 not installed", "visible_tokens": [], "panel_geometry": {}, "actions": {}}
        (out / "gui_inspect_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "gui_inspect_report.md").write_text("# GUI Inspect Report\n- PySide6 unavailable\n", encoding="utf-8")
        return 0
    app=QGuiApplication.instance() or QGuiApplication([])
    facade=GuiFacade(mode=a.mode,db_path=a.db_path,user_id=a.user_id,host=a.host,port=a.port)
    bridge=GuiBridge(facade)
    eng=QQmlApplicationEngine(); eng.rootContext().setContextProperty('guiBridge',bridge); eng.load(str(Path(__file__).resolve().parent.parent/'ui_qml'/'MinimalGui.qml'))
    root=eng.rootObjects()[0]; root.setProperty('width',a.width); root.setProperty('height',a.height); wait(250)
    report={"mode":a.mode,"window_size":[a.width,a.height],"pages":{},"errors":[]}
    for page in PAGES:
        root.setProperty('currentPage',page); bridge.update_state_from_facade(); wait(250)
        entry={"visible_tokens":[],"panel_geometry":{},"actions":{}}
        obj=find(root, {"home":"HomePage","user":"UserPage","calibration":"CalibrationPage","training":"TrainingPage","report":"ReportPage","diagnostics":"DiagnosticsPage","developer_lab":"DeveloperLabPage"}[page])
        if obj is not None:
            entry['visible_tokens']=list(obj.property('debugVisibleTokens') or [])
        shot=f"{page}.png"; entry['screenshot']=shot
        if a.no_screenshots:
            entry["screenshots_skipped_reason"] = "--no-screenshots requested"
        else:
            err=grab(root, out/shot)
            if err: entry['screenshot_error']=err; report['errors'].append(f"{page}: {err}")
        for panel in PAGE_PANELS.get(page,[]):
            po=find(root,panel)
            entry['panel_geometry'][panel]={"visible": bool(po and po.property('visible')), "width": float(po.property('width')) if po else 0, "height": float(po.property('height')) if po else 0}
        report['pages'][page]=entry
    for page,action in ACTIONS:
        root.setProperty('currentPage',page); bridge.invokeAction(action,'{}'); bridge.update_state_from_facade(); wait(300)
        action_json=json.loads(bridge.lastActionResultJson or '{}')
        item=report['pages'][page]['actions'].setdefault(action,{})
        item['status']=action_json.get('status',''); item['message']=action_json.get('message',''); item['items_count']=len(action_json.get('items',[]) or [])
        shot=f"{page}_after_{action.replace('.','_')}.png"; item['screenshot_after']=shot
        if a.no_screenshots:
            item["screenshots_skipped_reason"] = "--no-screenshots requested"
        else:
            err=grab(root,out/shot)
            if err: item['screenshot_error']=err; report['errors'].append(f"{action}: {err}")
    # checks
    train_tokens=report['pages']['training'].get('visible_tokens',[])
    if 'trainingGameCanvasPlaceholder' not in train_tokens: report['errors'].append('missing trainingGameCanvasPlaceholder token')
    (out/'gui_inspect_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# GUI Inspect Report',f"- mode: {a.mode}",f"- window: {a.width}x{a.height}","","## Pages"]
    for k,v in report['pages'].items(): md.append(f"- {k}: screenshot={v.get('screenshot')} tokens={','.join(v.get('visible_tokens',[]))}")
    md.append('\n## Errors'); md.extend([f"- {e}" for e in report['errors']] or ['- none'])
    (out/'gui_inspect_report.md').write_text('\n'.join(md),encoding='utf-8')
    facade.close(); return 0

if __name__=='__main__':
    raise SystemExit(main())
