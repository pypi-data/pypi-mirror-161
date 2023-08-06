# djangOK
A pre-commit hook to run Django check ensuring that the code is Ok.

Can be installed as a pre-commit

```yaml
repos:
        - repo: https://github.com/mkalioby/djangOK
          rev: v0.8.1
          hooks:
             - id: djangOK
               args: []
```

there is an optional argument which is the folder path of `manage.py`

### Note
The hook is currently always_run mode.
