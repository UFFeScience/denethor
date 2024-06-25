# Environment Setup

The commands described here were created based on the Ubuntu 22.04 operating system and may need to be adapted for other operating systems.

## Installation of Python 3.11 and Pip

To prepare Lambda function packages, it is necessary to have `Python 3.11` and the package manager `Pip` installed on your local machine. To check if Python 3.11 is installed, run the following command in the terminal:

```bash
python3.11 --version
```

If Python 3.11 is not installed, you can install it using the following command:

```bash
sudo apt-get install python3.11
python3.11 --version
# Python 3.11.0rc1

ls /usr/bin/python*
```

To check if Pip is installed, run the following command in the terminal:

```bash
pip --version
```

If Pip is not installed, you can install it using the following command:

```bash
sudo apt-get install pip
pip --version
# pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
```

## ClustalW Installation

For the execution of the workflow, it is necessary to have [ClustalW](http://www.clustal.org/clustal2/) installed. ClustalW is a software for multiple sequence alignment of protein sequences. One way to obtain this software is as follows:

```bash
sudo apt-get install curl

curl "http://www.clustal.org/download/current/clustalw-2.1-linux-x86_64-libcppstatic.tar.gz" -O

tar -xvzf clustalw-2.1-linux-x86_64-libcppstatic.tar.gz
```

If you are using the Windows operating system, you can download the ClustalW installer from this link: [Download ClustalW for Windows](http://www.clustal.org/download/current/clustalw-2.1-win.msi)

## Execution Modes

The project can be executed in two modes: *local* and *lambda*.

- The *local* mode will execute the entire workflow on the local machine.
- The *lambda* mode should be used for execution using AWS Lambda functions.

Each execution mode has its own specific instructions and configurations. They are detailed in the files **[local_setup](docs/local_setup.md)** and **[aws_setup](docs/aws_setup.md)**, respectively.

## Denethor

The file **[denethor](docs/denethor.md)** explains how the workflow execution monitoring system was implemented and which configuration files are used in the execution of activities. Execution by `Denethor` assumes that the AWS environment setup steps have already been completed.