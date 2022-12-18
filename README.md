# A useful SEGGER RTT command line tool
This is a CLI tool for SEGGER RTT reading and mass flash via the JLink.
It is based on the Python library [`pylink-square`](https://github.com/square/pylink)

## Version Requirement
The requirements with the following version has been tested:
JLink: v6.88a
pylink-square: 0.11.1


## Get started
1. Download and install the JLink at [here](https://www.segger.com/downloads/jlink/). We have test the `v6.88a`.
2. Install the `pylink-square` library according to the [official guidance](https://github.com/square/pylink) or use the pip (version 0.11.1 has been tested)
```shell
pip install pylink-square
```

## Usage 
### Mass Flash
The script `mass_flash.py` can be used to mass flash the boards:
```shell
python3 mass_flash.py -s <JLink sequence number> -f <target binary file>
```
An example:
```shell
python3 mass_flash.py -s 1 2 3 -f test.bin
```

### Log reader
The script `log_reader.py` is used to read the log output from the board via RTT:
```shell
python3 log_reader.py -v -s <JLink sequence number> [-p <log file prefix>]
```
The optional parameter `-p` given the prefix of the log file. For example, while using `-p test`, the log output for the JLink with sequency number 1 is `"test_1.log"`.

### RTT interaction
Some times we need to interact with the boards. You can use the:
```shell
python3 rtt_view.py -v -s <JLink sequence number> [-p <log file prefix> -t]
```
The optional parameter `-p` is same as the log reader.

The optional parameter `-t` let the program to start a thread which continuous reading the board's output.
Otherwise, the program will only read the output once after the user send some message to the board.

## Tips
This is a very simple tool based on the Python scripts. 
We strongly recommend users to modify the `.bashrc` file to simplify the usage like this:
```shell
alias rv='python3 ~/rtt_cmd_tool/rtt_view.py -vt'
alias mf='python3 ~/rtt_cmd_tool/mass_flash.py'
alias lr='python3 ~/rtt_cmd_tool/log_reader.py -v'
```
