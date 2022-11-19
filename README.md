*This repo is obsolete. It contains supplementary information for NeoVim bug 16297 which was fixed on Dec 19, 2021.*

# What ~is~ was the problem?

In newer versions of Neovim (>0.5.0), the builtin LSP client does not send
`contentChanged` updates to the server. As a result, language server features
like code completion do not work.

# How to reproduce

For easier debugging, I wrote a minimal language server in Python 3
(`dummyls.py`). All it does is log the requests to a file.

0. Clone this repository and `cd` into it. 
1. Edit `dummy.lua` and replace `dummyls.py` with the absolute path of
   `dummyls.py` (or add the directory to your search path).
2. Install [`nvim-lspconfig`][0]
3. Copy `dummy.lua` into `<nvim-lspconfig>/lua/lspconfig/dummy.lua`.

4. Run `nvim -u init.vim test.pas` and do some random edits.
5. There should now be a `transcript.txt` in the current directory. Its contents
   show exactly what was sent over the wire by the Neovim LSP client (the
   responses are not included).
6. In nvim versions unaffected by the bug, `transcript.txt` contains
   `contentChanged` that look like this:
   ```
   {"method": "textDocument/didChange", "jsonrpc": "2.0", "params": {"contentChanges": ...}}}
   ```
   In nvim versions affected by the bug, those lines are *missing*.

   I included example output for both cases in `transcript.good.txt` and
   `transcript.bad.txt`.

# Automatic bisection

I already did the bisection, but in case you are curious, I included the script
I used. To use it, the repository must be cloned into the nvim sources root
folder, e.g. `~/neovim/nvim-lsp-testcase`.  Afterwards, follow steps 0 – 3 of
*How to reproduce*.

To run the automatic bisection:
```
git bisect start
git bisect good 5ad32885d
git bisect bad master
git bisect run nvim-lsp-testcase/script.sh
```

# Bisection result

I determined that the first “bad” commit is
```
519848f64 vim-patch:8.2.2596: :doautocmd may confuse scripts listening to WinEnter
```

# Observations

- The bug only occurs when `init.vim` contains the statement `syntax on`.
- The bug does **not** occur when the file edited contains a modeline specifying
  the file type, e.g.
  ```
  # vim:et ft=dummy
  ```

[0]: https://github.com/neovim/nvim-lspconfig
