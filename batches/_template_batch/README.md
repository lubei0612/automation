# Template Batch Layout

这个目录只是给你看批次跑完后的标准结构。

```text
_template_batch/
  accepted/
  unresolved/
  invalid/
  timeout/
  reports/
  workspace/
  manifests/
```

真实运行时会创建类似：

```text
batches/2026-04-24-batch-001/
```

并把对应结果放进这些子目录。
