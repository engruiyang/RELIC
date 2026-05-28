# TASK26 Desktop Schema 草案（TASK26A）

> 本文为 schema 草案说明，不接入运行流程。

## 1. desktop
建议字段：
- `desktop_id`: string
- `version`: string
- `mode`: string（如 `desktop_preview` / `desktop_active`）
- `status_bar`: object
- `dock`: object
- `pages`: array[page]
- `wallpaper`: object

## 2. status_bar
建议字段：
- `enabled`: bool
- `locked`: bool
- `position`: string（top/bottom）
- `height`: number
- `widgets`: array[widget]
- `style`: object

## 3. dock
建议字段：
- `enabled`: bool
- `locked`: bool
- `position`: string（left/right/bottom）
- `width`: number
- `height`: number
- `buttons`: array[button widget]
- `style`: object

## 4. page
建议字段：
- `page_id`: string
- `title`: string
- `subtitle`: string
- `layout`: object
- `cards`: array[card]

## 5. layout
建议字段：
- `mode`: string（`grid` / `absolute`）
- `columns`: number
- `rows`: number
- `gap`: number|object
- `padding`: number|object

## 6. card
建议字段：
- `id`: string
- `type`: string
- `title`: string
- `subtitle`: string
- `required`: bool
- `locked`: bool
- `preset`: string
- `position`: object
- `shape`: string
- `style`: object
- `widgets`: array[widget]
- `card_policy`: object

## 7. position

### grid 模式字段
- `col`: number
- `row`: number
- `col_span`: number
- `row_span`: number

### absolute 模式字段
- `x`: number
- `y`: number
- `width`: number
- `height`: number

约束建议：
- 普通页面优先使用 `grid`。
- `absolute` 仅适合 `GameCanvas`、HUD、特殊装饰页面或高级布局。

## 8. widget
建议字段：
- `type`: string
- `id`: string
- `label`: string
- `source`: string
- `value`: any
- `fallback`: any
- `format`: string
- `unit`: string
- `preset`: string
- `style`: object
- `visible_when`: object|string

## 9. button widget
建议字段：
- `type`: string（固定为 `button`）
- `id`: string
- `label`: string
- `action_id`: string
- `args`: object
- `variant`: string
- `required`: bool
- `enabled_when`: object|string
- `confirm`: object|bool
- `style`: object

## 10. pipeline_binding
建议字段：
- `pipeline_id`: string
- `mandatory`: bool
- `required_cards`: array[string]
- `required_fields`: array[string]
- `required_buttons`: array[string]
- `allowed_pages`: array[string]
- `fallback_card`: string
- `coverage_policy`: object

## 11. coverage_policy
建议字段：
- `visibility`: string（always/conditional）
- `always_accessible`: bool
- `fallback_location`: string
- `allow_hide`: bool
- `allow_collapse`: bool

## 12. 安全限制
- JSON 不能包含可执行 JavaScript。
- JSON 不能写任意函数名。
- JSON 只能引用 action_id。
- JSON 只能引用已注册 asset_id。
- JSON 中的 source 路径必须由后续 schema checker 校验。
