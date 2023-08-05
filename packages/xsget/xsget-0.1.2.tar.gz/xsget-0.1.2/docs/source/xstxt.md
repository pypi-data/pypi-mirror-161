# xstxt

## FAQs

### How do we add indentation for each paragraph?

```toml
txt_replace = [
    ['^', '\u3000\u3000']
]
```

### How do we add extra empty new line for every line?

```toml
txt_replace = [
    ['\n', '\n\n']
]
```

### How do we remove multiple empty new lines from a text file?

```toml
txt_replace = [
    ['\n{3,}', '\n\n']
]
```

### How do we remove a line contains `foobar` from a text file?

```toml
txt_replace = [
    ['^.*foobar.*$', '']
]
```
