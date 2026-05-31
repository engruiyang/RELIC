# TASK26H-5 User Card Controls

本任务把 User 页面剩余的注册、登录、下拉选择和 Profile 弹出卡片接入现有 desktop card 渲染管线。

## 边界

- 不新增旧式独立面板。
- 不绕过 `DesktopLayoutPreview / DesktopLayoutCardPreview`。
- 不新增后端用户系统。
- 按钮仍通过已有 `guiBridge.invokeAction(action_id, args_json)` 调用 `GuiFacade.invoke_action`。

## 新增能力

- `input` widget：在卡片中显示 `TextField`。
- `select` widget：在卡片中显示 `ComboBox` 下拉选择。
- `${input.<widget_id>}` / `${select.<widget_id>}` 参数占位符：按钮点击时由同卡片内输入框或下拉值替换。
- `user_profile_popup_card`：通过卡片按钮打开 profile 弹出卡片。

## User 页面新增卡片

- `user_credentials_card`：注册、登录、显示输入用户 Profile。
- `user_selector_card`：下拉选择用户，并加载或显示 Profile。
- `user_profile_popup_card`：按钮控制的 Profile 弹出卡片。

## 美工可调项

这些卡片仍支持原有 TASK26 可调样式：位置、大小、背景色、透明度、边框颜色、边框宽度、圆角、背景图、玻璃效果、字号、行距、按钮高度和反馈区高度。
