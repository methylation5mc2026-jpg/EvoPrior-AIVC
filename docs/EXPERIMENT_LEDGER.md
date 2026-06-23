# 实验台账

所有实验必须追加记录，不覆盖旧记录。

## 记录模板

```text
Experiment ID:
Date:
Role:
Objective:
Dataset:
Dataset version/checksum:
Split ID:
Config path:
Git commit:
Seed(s):
Command:
Outputs:
Metrics:
Assumptions:
Known risks:
Rollback note:
Claim status:
```

## 当前记录

### EXP-0000: 仓库初始化

- Date: 2026-06-23
- Role: Research lead / MLOps / Evaluation engineer
- Objective: 创建项目上下文、目录骨架、最小指标测试和切分泄漏测试。
- Dataset: none
- Dataset version/checksum: none
- Split ID: synthetic only
- Config path: none
- Git commit: 待首次提交后填写
- Seed(s): tests use fixed toy values
- Command: `python -m pytest`
- Outputs: none
- Metrics: unit tests only; 9 tests passed on 2026-06-23
- Assumptions: 文档使用中文内容；代码与约定路径保留英文命名以保证工具兼容。
- Known risks: 文献地图只是初始种子，不可作为完整综述。
- Rollback note: 删除本次新增文件或回退初始化提交即可恢复空仓库状态。
- Claim status: 无性能或 SOTA 声称。
