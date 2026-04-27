# Batch Output Root

运行批处理后，批次目录会创建在这里。

预期结构示例：

```text
batches/
  2026-04-24-batch-001/
    accepted/
    unresolved/
    invalid/
    timeout/
    reports/
    workspace/
    manifests/
```

不要手动把候选 zip 放到这里；候选输入应放到 `input_zips/`。
