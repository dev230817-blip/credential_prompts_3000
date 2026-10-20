# taxonomy.md — 分组口径

本文件说明数据集的分组方式。容易混淆的四个层级必须先分开：**配额单元（quota unit）**、
**实体（entity）**、**profile 样式（style）**和**基础组（group）**。

## 1. 四个层级

| 层级 | 标识 | 含义 | 实测规模 |
| --- | --- | --- | ---: |
| 配额单元 | `quota_id` | 计数与配额的最小单位，一个单元对应一类证件或一类业务 | 29 |
| 实体 | `entity_id` | 单元内部的细分对象，例如同一单元的国徽面与人像面 | 50 |
| profile 样式 | `profile_id` | 版式与字段集合的定义，一个样式可被多个组复用 | 对象 51 个；组引用 54 个 ID（含 4 个已登记例外） |
| 基础组 | `group_id` | 一条完整的证面设计，承载一档到三档提示词 | 1,000 |

配额单元决定"做多少"，实体决定"做哪一面"，样式决定"长什么样"，基础组是实际交付单位。

## 2. 配额单元分布

| quota_id | 组数 | 包含实体 |
| --- | ---: | --- |
| E08 | 80 | E08-uk, E08-us |
| C13 | 57 | C13-main |
| C01 | 55 | C01-authority, C01-portrait |
| C16 | 51 | C16-legal, C16-teacher |
| E09 | 50 | E09-uk |
| E05 | 50 | E05-uk, E05-us |
| C08 | 50 | C08-student, C08-supplement |
| C15 | 45 | C15-main |
| E01 | 45 | E01-us |
| C17 | 41 | C17-food, C17-school |
| E06 | 41 | E06-uk, E06-us |
| C09 | 40 | C09-main |
| C10 | 40 | C10-degree, C10-graduation |
| E02 | 35 | E02-uk, E02-us |
| E04 | 30 | E04-uk, E04-us |
| C02 | 25 | C02-household, C02-person |
| C07 | 25 | C07-main |
| E03 | 25 | E03-us |
| C06 | 25 | C06-f, C06-l, C06-m, C06-q2, C06-x1 |
| C03 | 25 | C03-main |
| C11 | 25 | C11-award, C11-honor |
| E10 | 25 | E10-cslb, E10-gmc, E10-hcpc, E10-nmc |
| C05 | 20 | C05-hkmo, C05-taiwan |
| C04 | 20 | C04-main |
| C14 | 20 | C14-main |
| C19 | 15 | C19-property |
| C18 | 15 | C18-main |
| E07 | 15 | E07-uk, E07-us |
| C12 | 10 | C12-main |

`C` 前缀为中国证件，`E` 前缀为境外证件。29 个单元合计 1,000 组。

`C19-house` 与 `E10-brn` 两个实体此前被划除配额并保留了原因，因此不在上表实体列中。

## 3. 分布

按组统计：

| 维度 | 分布 |
| --- | --- |
| 国家 | 中国 604，美国 205，英国 191 |
| 可见语言 | 中文 604，英文 396 |
| 生成家族 | `1007` 976 组，`1006-preserved` 24 组 |

语言与国家分布来自 v9 的 25 组转配额（中国净增 4、美国净减 4、英国不变）。原始目标
600／400 与美国 209／英国 191 保留作历史对照。

## 4. 组与条数

| 口径 | 数量 |
| --- | ---: |
| 基础组 | 1,000 |
| 三档组 | 993 |
| 仅 clean 组 | 7 |
| 提示词 | 2,986 |

993 组各有 clean、subtle、strong 三档，共 2,979 条；7 组只有 clean，共 7 条。合计 2,986 条。

仅 clean 的 7 组全部来自 `E07-uk`（UKMT 数学竞赛证书）：该证书不印分数与编号，没有可设计的
单图可判证面错误，因此按既定边界不做异常。7 个 `group_id` 列在
`final/qa_report.json` 的 `counts.clean_only_group_ids`。

## 5. 档位与异常类别

三档只在已取值上制造差异，共用同一载体、字段集合、标签与构图。

`anomaly_category` 记录该条提示词设计的异常类型，例如 `order`（先后次序）、`phrase`（措辞）、
`pattern`（整串匹配）、`number_structure`（号码结构）、`birth`（出生日期）、
`obvious_format`（明显格式）等。`clean` 档使用 `clean` 或 `none`，24 个历史保留组使用
`legacy_preserved`。

异常的计数口径写在 `count_policy` 中：实际改动字段、目标规则和连带规则分别统计，连带失败
不计为新增改动。

## 6. 样式与模板不是同一个数

- `profile_id`（样式）按画像 ID 计。组实际引用了 54 个样式；`config/profiles.json` 有 51 条
  记录、50 个唯一 ID（存在一组重复 ID，见第 8 节）。
- 模板对象按 `config/templates.json` 中的 `spec_id` 计，共 56 条记录、55 个唯一 ID。

两者不能混称。历史模板确认覆盖的 54 个样式，指的是 129 个被确认组所落到的那 54 个 `profile_id`，
不是模板签名数量。

## 7. 已登记的关联例外

组引用的 54 个 `profile_id` 中有 4 个（`CP1005-C01`、`CP1005-C15`、`CP1005-E08`、
`CP1005-E09`）以及 3 个 `spec_id`（`EXEC-V7-C13-main`、`EXEC-V7-C17-school`、
`EXEC-V7-E06-us`）指向更早阶段的对象，这些对象不在本次公开的 `config/profiles.json` 与
`config/specs.json` 中。逐项清单见 `config/known_reference_exceptions.json` 的
`dangling_*` 字段。本次只登记，不补造对象，也不改既有 ID。

`config/profiles.json` 的 50 个唯一样式 ID 均被组引用，未被引用的配置样式为 0。
组引用的 54 个 ID 包含这 50 个配置样式与上述 4 个缺失对象 ID。

## 8. 重复 ID

原数据本身存在三组重复 ID，影响范围集中在 UKMT（`E07-uk`）相关的 7 条 clean 提示词：

| 对象 | 重复 ID | 记录数 | 内容 | 差异字段 |
| --- | --- | ---: | --- | --- |
| specs | `EXEC-V7-E07-uk` | 2 | 不同 | `fields`、`generation_contract`、`layout_observations`、`source_ids` |
| profiles | `P1007-V6-E07-uk` | 2 | 不同 | `clean_only`、`source_ids`、`template` |
| templates | `EXEC-V6-E07-uk` | 2 | 相同 | — |

因此各配置文件的“记录条数”与“唯一 ID 数”不同：specs 105／104、profiles 51／50、
templates 56／55。**按 ID 建字典会静默取到其中一条，掩盖“同一 ID 对应多个对象”的事实**，
所以本仓库按行处理，校验器分别报告两个数字，并在同一份异常登记中给出两条对象的哈希、差异
字段与影响范围。

本次不合并、不改名、不重建对象，也不据此重新生成 UKMT 正文。

需要说明的是：**规格 CSV 与规格 JSON 按行比较是一致的**，此前按 ID 建索引比较时才出现差异。
这一点由 `src/validate_release.py` 的 V26 逐字段对账覆盖。

当前活跃描述仍覆盖54个样式；当前保留的独立模板确认覆盖31个样式。具体历史与当前绑定见审核说明。
