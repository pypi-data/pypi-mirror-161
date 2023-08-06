# prettifyJsonLog
![build badge](https://github.com/neumantm/prettifyJsonLog/actions/workflows/python.yml/badge.svg)

A small python programm to make json log formats human readable

It reads log lines from stdin.
Each line must be one log entry formatted as a JSON object.

## Usage

```bash
someCommandThatProducesLogs | prettifyJsonLog
```

or

```bash
2>&1 someCommandThatProducesLogsOnStderr | prettifyJsonLog
```

## Authors

- Tim Neumann <neumantm@fius.informatik.uni-stuttgart.de>
