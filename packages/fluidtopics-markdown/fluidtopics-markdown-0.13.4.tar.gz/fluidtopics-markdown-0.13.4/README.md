# Markdown to Fluitopics Command Line Tool

The purpose of this tool is to collect documentation existing in the form
of Markdown files from various places in a project and push it to
a [Fluid Topics](https://www.fluidtopics.com/) portal.

The tool uses the FTML connector:

- https://doc.fluidtopics.com/r/Upload-FTML-Content-to-Fluid-Topics/Configure-FTML-Content

## Features

- Collect all Markdown files (.md) contained in a project.
- Make it possible to define content as  public or internal based on [metadata contained
  in the Markdown files](https://stackoverflow.com/questions/44215896/markdown-metadata-format).
- Build the Table of Contents in FLuid Topics (ftmap) based on metadata contained in the Markdown files.
- Publish the collected documentation to a Fluid Topics portal.

## Documentation

Documentation of the md2ft commmand line tool is available [here](https://doc.fluidtopics.com/r/Technical-Notes/Markdown-to-Fluid-Topics-md2ft).

## Availability

fluidtopics-markdown is available:

- as a Python module: <https://pypi.org/project/fluidtopics-markdown/>
- as a Docker image that can be used along with a CI: <https://hub.docker.com/r/fluidtopics/markdown>
