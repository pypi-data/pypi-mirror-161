# cnvrg-sdk

#### Local Setup

- brew install pyenv
- pyenv install 3.5.9
  ```
  MIGHT NEED TO RUN BIG SUR PATCH:
  CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix bzip2)/include -I$(brew --prefix readline)/include -I$(xcrun --show-sdk-path)/usr/include" LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix zlib)/lib -L$(brew --prefix bzip2)/lib" pyenv install --patch 3.5.9 < <(curl -sSL https://github.com/python/cpython/commit/8ea6353.patch\?full_index\=1)
  ```
- pyenv global 3.5.9
- pyenv init 
  - add output to zshrc
- git clone https://github.com/AccessibleAI/cnvrg-sdk.git
- cd cnvrg-sdk
- python -m venv venv
- source venv/bin/activate
  - add the following function to zshrc:
    ```
    function cd() {
  	builtin cd $1
	
  	if [[ -f venv/bin/activate ]] ; then
    	  source venv/bin/activate
  	fi
    }
    ```
- pip install -e ".[options]"

    available options are:
  - dev - to install packages relevant for testing
  - azure - to install packages relevant for azure storage client
  - google - to install packages relevant for gcp storage client
  - python3.6 - to make the sdk work with old version of python(3.6)
  
  NOTE: S3/minio packages are installed by default.

#### Configure Pycharm
- Pycharm -> Preferences -> Tools -> Python integrated tools
  - Set Testing to pytest
  - Set docstring format to Epytext (enables auto docstring gen when writing """ (Enter) "")


#### Running tests
install the following dependencies:
```shell
pip install pytest
pip install coverage
```

#### Adding new packages

- pip install <PACKAGE>
- pip freeze > requirements.txt
- if package is for production add it to setup.py

#### Publishing the package

- Update version in cnvrg/_version.py
- Update setup packages
  ```
  pip3 install --upgrade setuptools wheel
  ```
- Install twine
  ```
  pip3 install --upgrade twine
  ```
- Make sure to bump the version
- Run build command
  ```
  python3 setup.py sdist bdist_wheel
  ```
- Upload the package (test)
  ```
  python3 -m twine upload --skip-existing --repository testpypi dist/*
  ```
- Package is available in:

  https://test.pypi.org/project/cnvrg-new/0.1.1/
  ```
  pip install -i https://test.pypi.org/simple/ cnvrg-new==0.1.1
  ```
	
