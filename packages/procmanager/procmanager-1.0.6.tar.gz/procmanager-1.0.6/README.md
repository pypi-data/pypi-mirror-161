# ProcManager

An command line to start and stop long-running processes.

## Usage

Run some program (`python -m http.server`) and keep track of it under the name **httpd**:
```bash
procmgr start -n httpd python -m http.server
```

To list currently running processes:

```bash
procmgr list
```
To remove track of no-longer running processes:

```bash
procmgr clean
```
To stop a running process:

```bash
procmgr stop <name>
```

*if not specified, name defaults to the process name (first argument of start)*

To watch the output of some process:

```bash
procmgr watch <name>
```

# Installation
```pip install procmanager```
