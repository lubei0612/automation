# Repo Cache

这个目录用于存放可复用的本地 Git 仓库缓存，供批处理在无法直连 GitHub 时使用。

目录命名规则：

```text
repo_cache/
  owner__repo/
```

例如：

```text
repo_cache/
  eslint__eslint/
```

要求：

- 必须是一个真实的 git 仓库
- `.git/` 必须存在
- 仓库内容应足够支持 `git checkout`、`git diff`、`git apply`

如果设置了：

```bash
REPO_CACHE_ROOT=repo_cache
```

系统在解析 `setup_repo.sh` 时，会优先尝试把 `git clone https://github.com/owner/repo.git ...`
重写成从本地缓存 clone。
