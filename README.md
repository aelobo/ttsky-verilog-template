# TinyPomodoro — Pomodoro Timer, Clock & Date Display


### Overview
Date and time clock system with Pomodoro timer. Peripherals include 4 push buttons and MAX7219 8-digit 7-segment display. Push buttons control system modes and setup of date and time. RTL overview and peripheral setup found in [docs/info.md](https://github.com/aelobo/ttsky-verilog-template/blob/main/docs/info.md) 

### How it works

- 3-mode timer and clock system driven by 50MHz clock
- Displays output on external MAX7219 8-digit 7-segment display via SPI
- 4 breadboard buttons for input

#### External hardware

- MAX7219 8-digit 7-segment LED display
- Push buttons (×4)


#### Modes

The design has three display modes, cycled with `btn_right`:

| LED[1:0] | Mode | Display format |
|----------|------|----------------|
| `00` | CLOCK | `HH MM SS --` |
| `01` | DATE | `DD - MM - -- --` |
| `10` | POMODORO | `-- -- MM SS -- -- ` |


#### Button Routing

| Button | Outside setup | Inside setup |
|--------|--------------|--------------|
| `btn_left`  | Enter setup | Exit setup and save |
| `btn_right` | Cycle mode | Cycle to next field |
| `btn_up`    | Start/pause pomodoro | Increment selected field |
| `btn_down`  | Reset pomodoro | Decrement selected field |



