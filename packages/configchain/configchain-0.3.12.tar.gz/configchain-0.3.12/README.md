# ConfigChain
![Latest PyPI version](https://img.shields.io/pypi/v/configchain.svg)

The key feature of ConfigChain, is the ability to dynamically create a hierarchical configuration by composition and override it through config files and the command line. 

- Installation : `pip install configchain --upgrade`

### Usage

`````python
from configchain import configchain

cs = configchain("./tests/asset/a.yaml", "./tests/asset/b.yaml", name="app-${app}", profile="profile")
print(cs)

... ConfigSet([('app-hello',
            Config([('*',
                     ConfigSnippet([('by', 'tao'),
                                    ('env', ['ENV=${profile}', 'PROCESSES=32']),
                                    ('at', 'aws'),
                                    ('app', 'hello')])),
                    ('test',
                     ConfigSnippet([('by', 'tao'),
                                    ('env',
                                     ['ENV=${profile}',
                                      'PROCESSES=32',
                                      'PROCESSES=1']),
                                    ('at', 'docker'),
                                    ('profile', 'test'),
                                    ('app', 'hello')]))])),
           ('*',
            Config([('*',
                     ConfigSnippet([('by', 'luo'),
                                    ('env', ['ENV=${profile}']),
                                    ('at', 'aws')])),
                    ('test',
                     ConfigSnippet([('by', 'luo'),
                                    ('env', ['ENV=${profile}']),
                                    ('at', 'docker'),
                                    ('profile', 'test')]))]))])
`````

a.yaml

```yaml
by: luo
env:
  - ENV=${profile}
at: aws

---
profile: test
at: docker
```

b.yaml

```yaml
app: hello
by: tao
env:
  - PROCESSES=32

---
profile: test
env:
  - PROCESSES=1
```

### License

ConfigChain is licensed under [MIT License](LICENSE).