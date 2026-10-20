# 字段说明

团队CSV沿用固定12列，UTF-8 BOM。variant全部clean，篡改字段与group_id为空；三视角组存入extra_json.content_group_id。sample_id为CRD-20261021-v1-00001至04290；CAT ID和父版本EXP ID分开保存。

aspect_ratio为标准输出画布（横向3:2、竖向2:3）；document_aspect_ratio为沿用的文档自身比例。三条共用fields、expected_visible_text、target_texts和content_sha256，source_prompt_sha256绑定父提示词。额外元数据不印入文书。
