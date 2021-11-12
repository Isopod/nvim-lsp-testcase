local configs = require 'lspconfig/configs'
local util = require 'lspconfig/util'

configs.dummy = {
  default_config = {
    cmd = { 
      "dummyls.py", 
      "--save-transcript", "transcript.txt", 
      "--save-log", "log.txt" 
    };
    filetypes = {"dummy"};
    root_dir = util.root_pattern(".git");
    init_options = {}
  };
  docs = {
    description = [[
Dummy Language Server for testing
]];
    default_config = {
      root_dir = [[root_pattern(".git")]];
    };
  };
};

-- Open a file and set cursor to (line, col):
-- :edit +call\ cursor(line,col) file

-- vim:et ts=2 sw=2
