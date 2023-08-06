# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src',
 'src.blog',
 'src.builder',
 'src.converters',
 'src.dataclasses',
 'src.entities',
 'src.lib',
 'src.obsidian',
 'src.preprocessors',
 'src.tasks',
 'src.tree']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.6,<4.0.0',
 'docopt>=0.6.2,<0.7.0',
 'markdown-link-attr-modifier>=0.2.0,<0.3.0',
 'marko>=1.2.0,<2.0.0',
 'pybars4>=0.9.13,<0.10.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'python-frontmatter>=1.0.0,<2.0.0',
 'python-slugify>=5.0.2,<6.0.0',
 'validators>=0.18.2,<0.19.0',
 'watchdog>=2.1.6,<3.0.0']

entry_points = \
{'console_scripts': ['obsidian-blog = src.cli:main']}

setup_kwargs = {
    'name': 'obsidian-blog',
    'version': '0.2.1',
    'description': 'Feature rich static site generator for obsidian.md',
    'long_description': '## Obsidian SSG Blog [![PyPI](https://img.shields.io/pypi/v/obsidian-blog)](https://pypi.org/project/obsidian-blog "PyPI")\n\n**DISCLAIMER: Still work-in-progress, so API definitely will change. To use it you\'d better to have some programming experience**\n\nThe idea is to create a simple blog generated from obsidian [Map Of Content][moc]\nnotes [original zettelkasten benefit][zettelkasten].\n\n### Features\n\n- Yet another static site generator for obsidian.\n- Built to use with git, github pages and action.\n- Uses handlebars template engine\n- Supports `--watch` and `--serve` modes for local writing\n- Recursively parses [[includes]] and has cycles detection\n- Automatically copies included local images into the build\n- Supports `--drafts` mode to work unpublished files locally\n- Privacy. Notes can be published only with explicit `published: True` annotation.\n- Fluent title detection from [[note | alt title]], frontmatter `title` attribute, or a filename.\n- Render notes as links, in case they\'re included in the middle of the paragraph and have `link` frontmatter attribute.\n- Supports filename delimeters: `Topic - Category - Note` becomes just `Note`\n\n### Installation\n\n```\npip install obsidian-blog\n```\n\n### Usage\n\n```\n$ obsidian-blog -h\nobsidian-blog\n\nStatic site generator for obsidian.md notes.\n\nUsage:\n  obsidian-blog [-d] [-w] [-s] [--port <number>] [--title <string>] [--posts_dir <directory>] [--pages_dir <directory>]\n\nOptions:\n  -h --help                     Show this screen.\n  -w --watch                    Enable watcher\n  -s --serve                    Enable web-server\n  -p --port=<number>            Web-server port [default: 4200]\n  -d --drafts                   Render draft pages and posts\n\n  --title=<string>              Blog title [default: My Blog]\n\n  --version             Show version.\n```\n\n### Example\n\nSee [Obsidian Blog Theme][obsidian-blog-theme]\n\n### Env\n\n`obsidian-blog` expects you have an `.env` file. Supported variables and their default values can be found\nin `src/dataclasses/config_data`.\n\n### Blog files\n\n```\nnotes ❯ tree .blog -a -I .git\n├── .blog\n│\xa0\xa0 ├── _assets # static files to be copied into .build\n│\xa0\xa0 │\xa0\xa0 └── styles.css\n│\xa0\xa0 └── _layouts # layout files\n│\xa0\xa0     └── main.hbs # name of layout, can be selected with `layout` frontmatter attribute. Default: `main`\n├── .build # build directory created by run `obsidian-blog` to be deployed\n├── .env # environment variables\n├── Pages # Pages directory, contains handlebars and markdown files\n└── Posts # Posts directory contains obsidian markdown files (which are anyway processed via handlebars)\n```\n\n### Posts\n\nPosts are obsidian markdown files with includes, images, and anything you usually have in your obsidian notes.\nPosts are post-processed by handlebars, so you can use it if you need (but not sure if it\'s a good idea tho).\n\n```\n---\ntitle: My awesome post\ndate: 2021-01-01 (used for sorting)\npublished: True # privacy, can\'t be skipped\nlayout: main (default_layout is used if it skipped)\n---\n```\n\n### Pages\n\nPages are handlebars templates (or just markdown files), rendered via global (`pages` and `posts` lists) and local (`self` points\nto the entity being rendered) contexts.\n\n### Assets\n\nAssets are divided into 2 types:\n- `.blog/_assets` copyed during the build unconditionally\n- Images insluded either with markdown reference or incline images, or by obsidian ![[<file>]] syntax. This ones are detected and copyed during the build.\n\n### Deployment\n\nSo far I\'m using github actions to deploy my stuff to [my blog][my-blog].\n\n### Feedback and things\n\nJust text me in [telegram][tg] or file an issue. I\'d be happy to know if you want to use it.\n\n### Alternatives\n\n- [Obsidian Export][obsidian-export] - cli to render obsidian notes into markdown written in Rust\n\n[moc]: https://www.youtube.com/watch?v=7GqQKCT0PZ4\n[zettelkasten]: https://en.wikipedia.org/wiki/Niklas_Luhmann#Note-taking_system_(Zettelkasten)\n[my-blog]: https://anto.sh\n[obsidian-blog-theme]: https://github.com/A/obsidian-blog-theme/\n[tg]: https://t.me/a_shuvalov\n[obsidian-export]: https://crates.io/crates/obsidian-export\n',
    'author': "'Anton Shuvalov'",
    'author_email': 'anton@shuvalov.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
