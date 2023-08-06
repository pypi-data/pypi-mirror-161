# Example Python Package

Following this article: https://mathspp.com/blog/how-to-create-a-python-package-in-2022

## Notes

**ZSH**
In zsh, it looks like you need to quote poetry packages:

```
poetry add -D scriv[toml]
$ zsh: no matches found: scriv[toml]
```

```
poetry add -D "scriv[toml]"
$ ... installed ...
```
