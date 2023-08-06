# Javelin

CLI tool for managing Spearly deployments.

## Requirements
- Python 3.10+
- `GITHUB_ACCESS_TOKEN` environment variable set to a **GitHub Personal Access Token** with `repo` scope ([Ref](https://github.com/settings/tokens))
- **AWS IAM User** with `codepipeline:StartPipelineExecution` permission to the required resources ([Ref](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration))

## Installation
```sh
brew install pyenv
pyenv install
pip install javelin-cli
```

## Usage
```sh
python -m javelin --help
```
