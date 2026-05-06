# RELIC Codex Context

This document gives Codex the project background, design target, engineering scope, HNNK platform IPC protocol notes, and current implementation plan.

The repository is for RELIC, a Python-based attention training system using a single-channel BCI headset and the HNNK platform IPC interface.

## 1. Project Identity

Project name:

- Chinese name: 意念玩家
- English name: RELIC / Relic
- Full description: 基于单通道脑机头环的专注力训练系统

Project members from the design document:

- Project lead: 彭睿扬
- Team members: 石若瀚，赵家兴
- Advisor: 黄狮勇
- Institution: 武汉大学地球与空间科学技术学院

Project positioning:

RELIC is a lightweight focus training and state management system. It uses a single-channel EEG headset, IMU-related motion information, and user behavior during training tasks to estimate the user's focus state, adjust training difficulty, and generate real-time and post-session feedback.

The system is designed for:

- learning and study preparation
- work focus training
- mild self-regulation and relaxation
- state recovery between tasks
- focus training games

Important product boundary:

- RELIC should be described as a training and state-management tool.
- RELIC should not claim disease diagnosis, medical treatment, or clinical rehabilitation effects.
- The headset manual also states that the official product is not a medical device.
- The project may discuss focus training trends and state feedback, but it should avoid promising immediate or guaranteed improvement.

## 2. Research and Design Rationale

The design document uses the following engineering assumptions:

1. Single-channel EEG can provide useful information for attention assessment.
2. Frontal theta-related features may be useful for sustained attention detection.
3. Reaction time variability, abbreviated as RTV, is more informative than average reaction time alone for sustained attention fluctuation.
4. Wearable single-channel EEG is easily affected by dry electrode contact, head movement, muscle artifacts, and environmental noise.
5. A real-time signal quality gate is required before using EEG values for focus estimation.
6. Dynamic Difficulty Adjustment, abbreviated as DDA, can improve serious game training experience when the adjustment logic is explicit and tied to task goals.
7. Neurofeedback effects in healthy adults are generally small, so RELIC should focus on long-term trend tracking and self-regulation practice.

Engineering implication:

The system should not rely on a single attention score alone. Focus estimation should fuse:

- platform attention value or EEG-derived score
- IMU / head stability information
- behavior metrics from the training task

## 3. Overall Product Goal

The goal is to build a lightweight attention training platform with the following capabilities:

1. Connect to the official HNNK platform.
2. Receive real-time online algorithm output from the platform.
3. Receive or derive attention-related values.
4. Optionally receive gyroscope / focus-point information.
5. Record all raw platform messages.
6. Run at least one training game.
7. Estimate focus state in real time.
8. Adjust game difficulty according to focus and performance.
9. Generate immediate and session-level reports.
10. Support future extension to raw EEG and more advanced signal processing if high-level protocol access becomes available.

The MVP should prioritize a working closed loop:

```text
HNNK platform output
    -> IPC receiver
    -> raw data logger
    -> attention / gyro parser
    -> focus model
    -> game state
    -> behavior event recorder
    -> difficulty controller
    -> session report
4. System Architecture

The design document divides the system into five layers.

4.1 Device Acquisition Layer

Responsibilities:

connect to the official HNNK platform
receive online algorithm output
receive attention score
receive gyroscope or focus-point output if available
store timestamps for synchronization
provide a unified data source interface to upper modules

Initial MVP data sources:

PlatformIpcDataSource: receives actual platform IPC messages
MockDataSource: generates simulated attention and gyro values for offline testing
ReplayDataSource: replays JSONL logs from previous sessions
4.2 Signal Quality Control Layer

Responsibilities:

judge whether the current data is usable
prevent bad electrode contact or motion artifacts from directly influencing training state
output SQI, Signal Quality Index
decide whether the system can enter training, should warn the user, or should request quick check / recalibration

MVP SQI can be simplified because basic protocol access may only provide platform attention value, not raw EEG.

Suggested MVP quality signals:

attention value stays at 0 for too long
attention value is missing for too long
platform connection is disconnected
gyroscope output shows continuous large motion
behavior performance suddenly collapses
no valid IPC message is received within timeout

Future SQI can use raw EEG when high-level ipc_device_data access is available.

4.3 State Estimation Layer

Responsibilities:

calculate EEG score, IMU score, and behavior score
calculate Focus Index, abbreviated as FI
output both continuous FI and discrete state
keep sliding-window state history
avoid state flickering by requiring continuous windows

State estimation follows a quality-first two-stage design:

Stage 1: SQI check
Stage 2: FI and state calculation when SQI is acceptable

This allows the app to separate wearing / contact problems from actual user focus state changes.

4.4 Training Game Layer

The full design includes three independent games:

Fragment Lock / 碎片锁定
Signal Hunter / 信号猎手
Stabilizer / 稳定协议

The user chooses one game per session.

MVP should implement only Fragment Lock first.

4.5 Result Feedback Layer

Responsibilities:

show real-time focus state
show real-time reward / assistance / protection feedback
save session logs
generate session summary
generate 7-day or 14-day trend data in later versions

Immediate outputs:

FI
SI, Stability Index
LFS, Longest Focus Stability duration
RTV
game score
hit rate
false action rate
omission rate
difficulty changes

Long-term outputs:

7-day average FI trend
14-day average FI trend
SI trend
RTV improvement trend
score growth curve for each game
5. Calibration and Personalization
5.1 First Profile Calibration

First-time users should complete a 2 to 3 minute calibration.

Suggested calibration segments:

Resting fixation segment
build baseline EEG / platform attention value
build quiet IMU baseline
detect unstable wearing
Simple reaction segment
build individual reaction time baseline
estimate mouse / hand response delay
initialize RT stability model
Low-load sustained attention segment
build preliminary attention-related baseline
observe attention fluctuation
connect attention value, RTV, and head-motion perturbation

MVP can implement a simplified version:

20 seconds quiet baseline
20 seconds simple click reaction test
store result in a local profile JSON file
5.2 Quick Check Before Each Training Session

Each training session should start with a 15 to 20 second quick check.

Quick check should verify:

electrode contact appears acceptable
current quiet state has not deviated too much from profile baseline
reaction speed is not clearly abnormal
attention value is not stuck at 0
platform IPC messages are arriving

If quick check passes:

enter selected game directly

If quick check fails:

ask user to adjust headset
ask user to wipe electrode / skin if necessary
ask user to restart headset or official software if attention stays at 0
optionally enter Stabilizer recovery mode
5.3 Periodic Recalibration

Periodic recalibration should be triggered by:

fixed number of sessions
fixed number of days
repeated low SQI
sudden behavior degradation
state distribution significantly different from historical baseline

MVP can only record the conditions and show a warning. Full recalibration can be implemented later.

6. Focus Index Model
6.1 Original Design Formula

The design document defines Focus Index as:

FI = 100 × (0.55 × S_EEG + 0.15 × S_IMU + 0.30 × S_B)

Where:

S_EEG is the EEG or platform attention score.
S_IMU is the posture / head stability score.
S_B is the behavior performance score.
6.2 MVP Formula

Because the basic platform protocol may only expose online attention output, MVP should implement:

S_EEG = clamp(attention / 100, 0, 1)

For IMU score:

S_IMU = 1 - gyro_penalty

Where gyro_penalty should be clamped to [0, 1].

For behavior score:

S_B =
    0.35 × Accuracy
  + 0.20 × (1 - Omission)
  + 0.15 × (1 - FalseAction)
  + 0.30 × RT_Stability

Then:

FI = 100 × (0.55 × S_EEG + 0.15 × S_IMU + 0.30 × S_B)

All component scores should be clamped into [0, 1].

FI should be clamped into [0, 100].

6.3 Behavior Metrics

Definitions:

Accuracy: correct actions / total required actions
Omission: missed targets / total targets
FalseAction: false clicks or invalid actions / total user actions
RT_Stability: stability of reaction time compared with individual baseline

RT stability should focus on reaction time fluctuation.

Possible MVP implementation:

rt_deviation = abs(current_rt - baseline_rt) / max(baseline_rt, 1e-6)
RT_Stability = clamp(1 - rt_deviation / allowed_ratio, 0, 1)

A more stable version should use sliding-window standard deviation or median absolute deviation.

6.4 State Machine

The design document uses four main states:

High Focus / 高专注
Stable Focus / 稳定专注
Distracted / 分心
Fatigued / 疲劳

Initial engineering thresholds:

FI >= 80 and maintained for 2 consecutive windows:
    High Focus

60 <= FI < 80:
    Stable Focus

40 <= FI < 60 or behavior metrics degrade:
    Distracted

FI < 40 for about 10 seconds, with both behavior and posture decline:
    Fatigued

Implementation requirements:

Use sliding windows.
Avoid changing state on a single noisy sample.
Keep timestamps for state transitions.
Store state history in session logs.
Treat these thresholds as engineering defaults; later versions should personalize them.
7. Training Games
7.1 Fragment Lock / 碎片锁定

MVP priority: highest.

Purpose:

sustained attention training
stable execution training
reaction-time fluctuation observation

Gameplay:

a target fragment appears on screen
user clicks, drags, or holds briefly to lock the target
early MVP can use simple click only
later versions can support drag or dwell-time mechanics

Core metrics:

FI
hit rate
RTV
LFS, longest continuous stable-focus duration
reaction time
miss count
false click count
difficulty level

Feedback rules:

High Focus: increase score multiplier and slightly speed up target refresh.
Stable Focus: maintain standard pace.
Distracted: highlight target and slow down pace.
Fatigued: reduce challenge and suggest recovery mode.

MVP implementation requirements:

draw one target at a time
record target spawn timestamp
record click timestamp
calculate reaction time
determine hit or miss
update behavior window
update FI
update difficulty every 5 seconds or after each round
save all events to JSONL
7.2 Signal Hunter / 信号猎手

MVP priority: later.

Purpose:

selective attention training
anti-interference training

Gameplay:

display real target among noise and false targets
user must choose the real target
difficulty changes false target count, target similarity, and reaction window

Core metrics:

anti-interference accuracy
false selection rate
RTV under noise
FI
difficulty level

Implementation can wait until Fragment Lock works.

7.3 Stabilizer / 稳定协议

MVP priority: later, but quick-check failure can recommend this mode.

Purpose:

relaxation
low-fluctuation maintenance
recovery from distraction or mild fatigue

Gameplay:

low-stimulation environment
user maintains a stable center zone
focus is on smooth state recovery rather than high-frequency operation

Core metrics:

FI
SI, Stability Index
recovery time
motion control score

Use cases:

before study
between tasks
mild fatigue recovery
after Fragment Lock failure
8. Dynamic Difficulty Adjustment

The design document defines short-window performance as:

Perf = 0.40 × Accuracy + 0.30 × RT_Stability + 0.30 × SI_window

Adjustment rule:

If two consecutive windows are High Focus or Stable Focus
and Perf > 0.72:
    increase difficulty by 1 level

If two consecutive windows are Distracted or Fatigued
or Perf < 0.45:
    decrease difficulty by 1 level

Rate limit:

At most one difficulty change every 10 seconds.

Purpose:

keep training challenging
avoid repeated up-down oscillation
reduce frustration
prevent fatigue state from being punished by harder tasks

Difficulty variables for Fragment Lock:

target size
target lifetime
spawn interval
score multiplier
visual distraction level
target movement speed, later version

MVP difficulty levels can be integers from 1 to 5.

9. Feedback Strategy

The feedback system should follow three modes:

9.1 Reward Feedback

Used during High Focus.

Examples:

clearer visual effect
score multiplier
stable light or ring effect
subtle positive sound
progress bar acceleration
9.2 Assistance Feedback

Used during Distracted state.

Examples:

stronger target highlight
lower visual noise
longer target lifetime
slower refresh
short text prompt
9.3 Protection Feedback

Used during Fatigued state.

Examples:

stop increasing difficulty
reduce challenge
suggest Stabilizer mode
suggest ending current session
avoid strong negative feedback

The system should protect user engagement. It should not shame the user for low attention scores.

10. Official HNNK Platform Integration
10.1 Process Roles

Official protocol roles:

Server: HNNK platform process
Client: RELIC controller process

During early development, RELIC should act as a TCP client.

The official platform listens on a port. RELIC connects to it.

10.2 Supported Connection Modes

The official protocol mentions two connection modes.

LocalSocket Mode

Platform starts controller process with command-line argument:

-server_name=[server_name]

Default server name:

HNNKPlatform

The controller process parses the argument and connects to the agreed local socket / pipe.

This mode is useful after packaging and official platform launch integration.

TCP Socket Mode

Official platform listens on TCP.

Default normal module port:

127.0.0.1:8000

RELIC should connect to:

host = 127.0.0.1
port = 8000

For MVP, use TCP mode first.

10.3 Correct Startup Flow During Development

Recommended manual startup flow:

1. Start the official HNNK / 科创平台 software.
2. Power on and wear the headset.
3. Confirm the headset is connected in the official platform.
4. Select an attention / 专注度 / 多模态 / gyroscope-related paradigm.
5. Configure TCP address:
       IP: 127.0.0.1
       Port: 8000
6. Save port settings.
7. Create a custom paradigm.
8. Enter the paradigm detail page.
9. Start RELIC manually:
       python run.py
   or:
       python run_ipc_test.py
10. RELIC connects to 127.0.0.1:8000.
11. RELIC receives ipc_user_info and ipc_algorithm_test.

Official development notes say that during development, if the custom paradigm's system execution path is not configured, a warning may appear. This does not block manual development. After packaging, configure the generated executable path in the official platform.

10.4 Official Python Demo Structure

Official basic example project structure includes:

app/
    main_window.py
    title_bar.py

dist/
    packaged software output

doc/
    platform socket protocol documents

ipc_socket/
    official socket communication library, PyQt5 >= 5.15

Resource/
    resources

run.py
    start file

python_demo.spec
    packaging script

package.bat
    one-click packaging script

RELIC does not have to copy the official project exactly, but the structure should remain compatible with official expectations.

Recommended RELIC structure:

Relic/
  README.md
  AGENTS.md
  requirements.txt
  run.py
  run_ipc_test.py

  app/
    main_window.py
    calibration_window.py
    result_window.py
    game_fragment_lock.py
    game_signal_hunter.py
    game_stabilizer.py

  relic_core/
    __init__.py
    ipc_client.py
    protocol.py
    data_source.py
    mock_data_source.py
    replay_data_source.py
    focus_model.py
    signal_quality.py
    state_machine.py
    difficulty.py
    session_recorder.py
    user_profile.py
    models.py

  docs/
    CODEX_CONTEXT.md
    protocol_notes.md
    dev_plan.md

  tests/
    test_json_stream_parser.py
    test_focus_model.py
    test_state_machine.py
    test_difficulty.py
    test_session_recorder.py

  resources/
    icons/
    sounds/

  logs/
    .gitkeep
11. IPC Message Format

Official protocol says the basic JSON structure requires msg.

General form:

{
  "msg": "xxxx",
  "data1": "optional",
  "data2": "optional"
}

The protocol document says JSON nesting is not supported because multiple packets can be merged together. However, official examples use result_args as a JSON object. Therefore RELIC should:

parse nested dictionaries defensively
send simple messages when possible
never assume that one TCP recv call equals one complete JSON object
support sticky packets
support split packets
log malformed input for debugging
12. Important General IPC Protocols
12.1 ipc_user_info

Direction:

Platform -> RELIC

Sent after connection.

Example fields:

{
  "msg": "ipc_user_info",
  "user_name": "string",
  "user_id": 0,
  "user_token": "string",
  "group_id": "string",
  "group_name": "string",
  "subgroup_id": "string",
  "subgroup_name": "string",
  "real_name": "string",
  "nick_name": "string",
  "research_no": "string",
  "group_use": "string",
  "sub_set": "string",
  "father_id": "string",
  "group_type": "string",
  "layout_type": 0
}

layout_type meaning:

0 = default layout
1 = split-screen layout

If split-screen mode is used, RELIC should send its window handle back:

{
  "msg": "ipc_user_info",
  "window": 123456
}

MVP can ignore split-screen embedding if using a standalone window.

12.2 ipc_set_visible

Direction:

Platform -> RELIC
or
RELIC -> Platform

Meaning:

Control whether the main window is visible.

Example:

{
  "msg": "ipc_set_visible",
  "visible": true
}

RELIC should implement this later if official embedding is needed.

12.3 ipc_exit

Direction:

Platform -> RELIC

Meaning:

The controller process should exit.

Example:

{
  "msg": "ipc_exit"
}

RELIC should close logs cleanly before exit.

13. Device Data Protocols

These protocols may require advanced or high-level access. MVP should not depend on them.

13.1 ipc_device_info

Direction:

Platform -> RELIC

Contains device state:

{
  "msg": "ipc_device_info",
  "device_id": "string",
  "devie_name": "string",
  "device_type": 1,
  "battery": 100,
  "sample_rate": 250,
  "eeg_channel": 1,
  "other_channel": 1,
  "wear": true,
  "connect": true,
  "channel_labels": ["Fp1"]
}

Potential use:

battery display
connection state display
wear state quality gate
sample rate display
channel count verification
13.2 ipc_device_data

Direction:

Platform -> RELIC

High-level real-time raw data:

{
  "msg": "ipc_device_data",
  "data": [0.1, 0.2, 0.3],
  "samples": 1,
  "start": 1234567890
}

Official description:

data size = samples × (eeg_channel + other_channel)

Future use:

raw EEG recording
band-power extraction
theta feature
artifact detection
real SQI model
13.3 ipc_device_gyroscope

Direction:

Platform -> RELIC

High-level gyroscope data:

{
  "msg": "ipc_device_gyroscope",
  "gyroscopeX": 0.0,
  "gyroscopeY": 0.0,
  "gyroscopeZ": 0.0
}

Official meaning:

gyroscopeX: yaw / 偏航
gyroscopeY: pitch / 俯仰
gyroscopeZ: roll / 翻滚

Potential use:

head motion penalty
posture stability score
quick check
Stabilizer game
13.4 ipc_device_gyro_calibration

Direction:

RELIC -> Platform
Platform -> RELIC

Command:

{
  "msg": "ipc_device_gyro_calibration"
}

Result:

{
  "msg": "ipc_device_gyro_calibration",
  "result": true
}

Future use:

optional gyro calibration button in settings
14. Algorithm Interface Protocols
14.1 ipc_algorithm_start_test

Direction:

RELIC -> Platform
Platform -> RELIC

For attention algorithm:

{
  "msg": "ipc_algorithm_start_test",
  "algorithm_args": {}
}

Result:

{
  "msg": "ipc_algorithm_start_test",
  "result": true,
  "fail_message": ""
}

For gyroscope algorithm:

{
  "msg": "ipc_algorithm_start_test",
  "algorithm_args": {
    "left": 0,
    "top": 0,
    "width": 1920,
    "height": 1080,
    "sensitivityX": 8,
    "sensitivityY": 8
  }
}

Gyroscope parameter meaning:

left: global screen x of active area
top: global screen y of active area
width: active area width
height: active area height
sensitivityX: x sensitivity, range [1, 15], usually 8
sensitivityY: y sensitivity, range [1, 15], usually 8

MVP may rely on the platform UI to start test mode manually. Later RELIC can send ipc_algorithm_start_test.

14.2 ipc_algorithm_stop_test

Direction:

RELIC -> Platform
Platform -> RELIC

Stop command:

{
  "msg": "ipc_algorithm_stop_test"
}

Result:

{
  "msg": "ipc_algorithm_stop_test",
  "result": true,
  "fail_message": ""
}
14.3 ipc_algorithm_test

Direction:

Platform -> RELIC

This is the most important MVP message.

General form:

{
  "msg": "ipc_algorithm_test",
  "algorithm_name": "attention",
  "result_args": {
    "data": 67
  }
}

Official basic-mode output examples:

p300, ssvep, mi, p300_ssvep, p300_mi: data is a string representing predicted instruction.
attention: data is an integer attention value.
blink: data is a string, "1" indicates blink.
gyroscope: data is an object containing focus position and gyro data.
multi-modal control: data may be attention, blink, or gyroscope depending on algorithm_name.

For attention:

{
  "msg": "ipc_algorithm_test",
  "algorithm_name": "attention",
  "result_args": {
    "data": 72
  }
}

Parser output should be:

AttentionSample(value=72, timestamp=...)

For gyroscope in basic mode:

{
  "msg": "ipc_algorithm_test",
  "algorithm_name": "gyroscope",
  "result_args": {
    "data": {
      "focus_x": 500,
      "focus_y": 300,
      "focus_area_x": 0,
      "focus_area_y": 0,
      "focus_area_width": 1920,
      "focus_area_height": 1080,
      "gyroscope_x": 0.1,
      "gyroscope_y": -0.2,
      "gyroscope_z": 0.0
    }
  }
}

Parser output should include:

focus_x
focus_y
focus_area_x
focus_area_y
focus_area_width
focus_area_height
gyroscope_x
gyroscope_y
gyroscope_z

Parser should tolerate inconsistent key naming such as:

algorithm_name:
algorithm_name
gyroscope_x
gyroscopeX
15. Mouse Module Special Protocol

Mouse module has a separate protocol. It is only for the official platform mouse module.

Important differences:

TCP default port is 9527.
It is different from normal module port 8000.
It does not require manual port configuration in the same way.
It is not the preferred path for RELIC MVP.

Mouse protocol messages:

15.1 ipc_mouse_list

Direction:

RELIC -> Platform mouse module

Send character / action list:

{
  "msg": "ipc_mouse_list",
  "list": ["测试按键1", "测试按键2"]
}
15.2 ipc_test_start

Direction:

RELIC -> Platform mouse module
{
  "msg": "ipc_test_start"
}
15.3 ipc_test_stop

Direction:

RELIC -> Platform mouse module
{
  "msg": "ipc_test_stop"
}
15.4 ipc_mouse_data

Direction:

RELIC -> Platform mouse module
{
  "msg": "ipc_mouse_data",
  "time": "2026-05-06 20:00:00.123",
  "data": "0"
}

data is the index in the previously sent list.

15.5 ipc_algorithm_stop_test

Direction:

Platform mouse module -> RELIC
{
  "msg": "ipc_algorithm_stop_test",
  "result": true,
  "fail_message": ""
}

MVP instruction:

Use normal algorithm IPC on port 8000 first. Add mouse protocol only if the official workflow requires a mouse-module report upload.

16. Headset Usage Notes Relevant to Software

The official headset is a NingNao / HNNK attention training headset.

Important hardware facts from the manual:

signal type: bioelectric signal
Bluetooth version: 5.0
battery life: about 8 hours
Bluetooth range: within 5 meters
full charge time: about 2 hours
charging input: DC 5V / 500 mA
weight: about 50 g
size: about 180 × 150 × 26 mm
usage environment: -10°C to 38°C

Wear instructions:

front electrode, left electrode, and right electrode should be installed correctly
adjust strap tightness before use
three electrodes must touch skin stably
avoid hair between electrode and skin
power button should align with nose center line
front lower edge should be close to eyebrows
left and right electrodes should fit inward as much as possible
glasses users should keep side electrodes close to glasses arms

Software should include user-facing hints:

keep electrode-contact skin clean
wipe electrode or skin with wet tissue, alcohol, or saline if signal is unstable
replace electrode if signal quality remains bad
avoid charging while wearing
use in a calm environment
avoid high temperature, low temperature, humidity, dust, and strong electromagnetic environments
if waveform has no signal or attention score stays at 0, restart headset and official software

The official product requires network connection during use. RELIC should not assume the official platform works fully offline.

17. Data Logging Requirements

Every received raw IPC message should be saved.

Recommended format:

logs/ipc_raw.jsonl

Each line:

{
  "timestamp": 1770000000.123,
  "direction": "in",
  "msg": "ipc_algorithm_test",
  "raw": {
    "msg": "ipc_algorithm_test",
    "algorithm_name": "attention",
    "result_args": {
      "data": 67
    }
  }
}

Game event log:

logs/session_YYYYMMDD_HHMMSS.jsonl

Each event should include:

timestamp
session_id
event_type
attention_value
gyro values if available
FI
state
SQI
difficulty_level
target_id
hit / miss
reaction_time_ms
false_click
omission
current_score

Session summary:

logs/session_YYYYMMDD_HHMMSS_summary.json

Suggested fields:

{
  "session_id": "string",
  "start_time": 0,
  "end_time": 0,
  "duration_sec": 0,
  "game": "fragment_lock",
  "avg_fi": 0,
  "max_fi": 0,
  "min_fi": 0,
  "avg_attention": 0,
  "hit_rate": 0,
  "false_action_rate": 0,
  "omission_rate": 0,
  "rt_mean_ms": 0,
  "rt_std_ms": 0,
  "rtv": 0,
  "lfs_sec": 0,
  "difficulty_start": 1,
  "difficulty_end": 1,
  "difficulty_changes": 0
}
18. Module Design
18.1 relic_core/ipc_client.py

Responsibilities:

TCP connect to official platform
receive bytes
feed bytes into stream parser
emit parsed messages
provide callbacks
write raw JSONL logs
reconnect later if needed

Callbacks:

on_status(text: str) -> None
on_message(message: IpcMessage) -> None
on_attention(sample: AttentionSample) -> None
on_gyroscope(sample: GyroscopeSample) -> None
18.2 relic_core/protocol.py

Responsibilities:

dataclasses for messages
parser helpers
safe field extraction
algorithm_name normalization
result_args normalization

Dataclasses:

IpcMessage
AttentionSample
GyroscopeSample
DeviceInfo
UserInfo
18.3 relic_core/data_source.py

Responsibilities:

define abstract interface for platform, mock, and replay data sources

Suggested interface:

class DataSource:
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def set_on_attention(self, callback) -> None: ...
    def set_on_gyroscope(self, callback) -> None: ...
18.4 relic_core/mock_data_source.py

Responsibilities:

simulate attention values
simulate gyro values
simulate missing data and attention stuck at 0
enable UI and game testing without official platform
18.5 relic_core/replay_data_source.py

Responsibilities:

read JSONL logs
replay attention and gyro samples according to timestamps
reproduce bugs from previous sessions
18.6 relic_core/focus_model.py

Responsibilities:

compute S_EEG
compute S_IMU
compute S_B
compute FI
return FocusSnapshot
18.7 relic_core/signal_quality.py

Responsibilities:

compute SQI
detect stale attention values
detect attention stuck at 0
detect high gyro noise
detect missing platform messages
18.8 relic_core/state_machine.py

Responsibilities:

convert FI and SQI to state
apply sliding-window debounce
track state duration
output state transitions
18.9 relic_core/difficulty.py

Responsibilities:

compute Perf
decide difficulty changes
enforce 10-second rate limit
expose difficulty parameters to games
18.10 relic_core/session_recorder.py

Responsibilities:

create session id
write JSONL events
write summary JSON
flush safely on exit
18.11 app/game_fragment_lock.py

Responsibilities:

render target
collect clicks
compute hit / miss / reaction time
report events to recorder
consume difficulty parameters
show focus feedback
19. MVP Development Order

Build in this order:

Create relic_core/protocol.py
Create relic_core/ipc_client.py
Create run_ipc_test.py
Confirm connection to 127.0.0.1:8000
Print ipc_user_info
Print all ipc_algorithm_test names
Extract attention values
Write raw logs to logs/ipc_raw.jsonl
Add mock data source
Add focus model
Add state machine
Add session recorder
Add Fragment Lock MVP
Add 15 to 20 second quick check
Add session summary
Add packaging later

Do not start with all three games.

Do not start with advanced raw EEG processing.

Do not block MVP on raw EEG access.

20. Testing Requirements

Core logic should be unit-testable without official platform.

Required tests:

tests/test_json_stream_parser.py
tests/test_focus_model.py
tests/test_state_machine.py
tests/test_difficulty.py
tests/test_session_recorder.py
20.1 JSON Stream Parser Tests

Must handle:

one JSON object in one packet
multiple JSON objects in one packet
one JSON object split across multiple packets
whitespace between JSON objects
invalid partial JSON that becomes valid later
non-dict JSON values should be ignored or safely logged
20.2 Focus Model Tests

Must verify:

attention 0 maps to S_EEG 0
attention 100 maps to S_EEG 1
FI is clamped to [0, 100]
behavior penalties reduce FI
gyro penalties reduce FI
20.3 State Machine Tests

Must verify:

High Focus requires consecutive windows
Fatigued requires duration
low SQI blocks normal state update
state does not flicker on one noisy sample
20.4 Difficulty Tests

Must verify:

Perf > 0.72 can increase difficulty
Perf < 0.45 can decrease difficulty
difficulty stays within allowed range
10-second rate limit works
21. Coding Style

Use Python 3.10+.

Prefer:

small modules
dataclasses
type hints
standard library first
clear error handling
explicit timestamps
JSONL for logs

Avoid:

putting platform IPC, UI, game logic, and focus model in one file
hardcoding thresholds deep inside UI files
silently dropping malformed protocol data
making the game depend directly on socket code
assuming official platform is always available
requiring the headset for unit tests
22. Current Immediate Task

The current engineering task is the IPC parser and receiver.

Create:

relic_core/protocol.py
relic_core/ipc_client.py
run_ipc_test.py

Minimum requirements:

Use Python standard library only.
Connect to 127.0.0.1:8000.
Parse continuous JSON stream from TCP.
Support sticky packets and split packets.
Log every raw message to logs/ipc_raw.jsonl.
Extract attention samples from ipc_algorithm_test.
Prepare for gyroscope extraction.
Expose callbacks:
on_message
on_attention
on_gyroscope
on_status
Provide a minimal test runner.
Keep the implementation UI-independent.

Done when:

python run_ipc_test.py starts without import errors.
The client connects after the official platform enters the paradigm detail page.
ipc_user_info is printed when received.
ipc_algorithm_test message names are printed.
Attention values are printed when received.
logs/ipc_raw.jsonl is created and contains raw platform messages.
Unit tests for JSON stream parsing pass.
23. Example Runtime Output

Expected terminal output:

[STATUS] IPC connected: 127.0.0.1:8000
[MSG] ipc_user_info
[MSG] ipc_algorithm_test
[ATTENTION] 67
[MSG] ipc_algorithm_test
[ATTENTION] 72

If no attention values are printed:

Check official platform module selection.
Check whether the platform entered the paradigm detail page.
Check whether attention test mode is running.
Check whether the headset is connected and worn correctly.
Check whether attention score is stuck at 0.
Restart headset and official software if needed.
