# LibSAN

Python library to manage Storage Area Network devices
## Installation
### Dependencies
 * Python>=3.6
 * pip
 * augeas-libs

#### Fedora, RHEL-7, RHEL-8 | x86_64, python3
`yum install python3-pip augeas-libs python3-netifaces`

##### pip >= 20.3 is needed for manylinux2014 wheels
`python3 -m pip install pip>=20.3`

### How to install the module:
`python3 -m pip install libsan` \
or with optional ssh support: \
`python3 -m pip install libsan[ssh]`

### From source
`git clone; cd python-libsan` \
`python3 -m pip install .` \
or \
`python3 -m pip install .[ssh]`
##### Alternatively on older systems:
`python setup.py install .`

### How to uninstall the module
`python3 -m pip uninstall libsan`

##### Alternatively on older systems:
`python setup.py install --force --record files.txt` \
`cat files.txt | xargs rm -rf`

### How to create a tar file
`python3 setup.py sdist`

### How to create a rpm package
`python3 setup.py bdist --format=rpm`

## Usage:
Before using the modules copy sample_san_top.conf
to /etc/san_top.conf (this is the default path to read the config) and
edit it according to your SAN environment.
