############
Kahn backlog
############


***********
Iteration 0
***********

Goals: Basic serial reading and UDP submitting

- [o] Make ``kahn forward`` work for real


***********
Iteration 1
***********

- [o] Configuration with TOML file
- [o] systemd service configuration unit file
- [o] Transfer telemetry and/or simulation subsystem(s) from ``calypso-anemometer``
- [o] Plugin host for e.g. ``calypso-anemometer``


***********
Iteration 2
***********

- [o] Use Trio?

  - https://github.com/python-trio/trio
- [o] ``asyncio``? Maybe use one of

  - https://github.com/pyserial/pyserial-asyncio
  - https://github.com/changyuheng/aioserial.py
  - https://github.com/joernheissler/trio-serial
