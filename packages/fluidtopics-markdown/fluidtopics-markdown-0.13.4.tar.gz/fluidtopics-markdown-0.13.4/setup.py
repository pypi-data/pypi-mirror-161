# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fluidtopics', 'fluidtopics.markdown']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click-log>=0.3,<0.4',
 'click>=7,<8',
 'fluidtopics>=1.0.3,<2.0.0',
 'importlib-metadata>=3,<4',
 'lxml>=4.5.1,<5.0.0',
 'python-slugify>=4.0.0,<5.0.0',
 'requests>=2.23.0,<3.0.0']

entry_points = \
{'console_scripts': ['md2ft = fluidtopics.markdown.cli:cli']}

setup_kwargs = {
    'name': 'fluidtopics-markdown',
    'version': '0.13.4',
    'description': 'A Markdown to FluidTopics command line tool',
    'long_description': '# Markdown to Fluitopics Command Line Tool\n\nThe purpose of this tool is to collect documentation existing in the form\nof Markdown files from various places in a project and push it to\na [Fluid Topics](https://www.fluidtopics.com/) portal.\n\nThe tool uses the FTML connector:\n\n- https://doc.fluidtopics.com/r/Upload-FTML-Content-to-Fluid-Topics/Configure-FTML-Content\n\n## Features\n\n- Collect all Markdown files (.md) contained in a project.\n- Make it possible to define content as  public or internal based on [metadata contained\n  in the Markdown files](https://stackoverflow.com/questions/44215896/markdown-metadata-format).\n- Build the Table of Contents in FLuid Topics (ftmap) based on metadata contained in the Markdown files.\n- Publish the collected documentation to a Fluid Topics portal.\n\n## Documentation\n\nDocumentation of the md2ft commmand line tool is available [here](https://doc.fluidtopics.com/r/Technical-Notes/Markdown-to-Fluid-Topics-md2ft).\n\n## Availability\n\nfluidtopics-markdown is available:\n\n- as a Python module: <https://pypi.org/project/fluidtopics-markdown/>\n- as a Docker image that can be used along with a CI: <https://hub.docker.com/r/fluidtopics/markdown>\n',
    'author': 'Antidot Opensource',
    'author_email': 'opensource@antidot.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
