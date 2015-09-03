# About Cloudviz2
This package provides an API to discover CloudWatch metrics and UI to display it. While this information is available
through the AWS console, it requires one to log in to the console. Making it inconvenient for the purpose of dashboards.
Cloudviz2 uses server-side component which talks to AWS using API keys and provides metric data in [d3](http://d3js.org/)
friendly format. The front-end is uses [NVD3](http://nvd3.org/) to display the data.

Cloudviz2 is (currently) unsanctioned fork of [Cloudviz](https://github.com/mbabineau/cloudviz). While project evolved from
Cloudviz it now shares very little code and technology with the original project. As a result a rename is likely.

## Installing & Running

### Frontend

1. Install npm
  On Mac OS X
  ```
  brew install npm
  ```

  On Debian-like
  as root:
  ```
  aptitude install npm
  ln -s /usr/bin/nodejs /usr/bin/node
  ```

2. Install Bower
  From within the project directory
  ```
  npm install bower
  ```

3. Using Bower install required JavaScript Libraries
  From within the project directory
  ```
  bower install
  ```

### Backend

1. Optionally enable virtualenv
2. Install Python dependencies
  From within the project directory
  ```
  pip install -e .
  ```

### Running

1. Start standalone 'development' server
   ```
   pserve etc/localhost.ini
   ```

   This will server Cloudviz2 on port 11217. Note if there are a lot of metrics, first metric discovery can take a long
   time (minutes). But these results are cached using beaker, and subsequent requests will be significantly faster.


# Licensing
Copyright 2015 (Ilya Sukhanov)[https://github.com/IlyaSukhanov]
Copyright 2010 [Bizo, Inc.](http://bizo.com) (Mike Babineau <[michael.babineau@gmail.com](mailto:michael.babineau@gmail.com)>)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
