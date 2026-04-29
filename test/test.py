# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

# ─────────────────────────────────────────────────────────────────────────────
# Pins
# ─────────────────────────────────────────────────────────────────────────────
# ui_in bits
BTN_LEFT  = 0   # enter/exit setup
BTN_RIGHT = 1   # cycle mode / cycle field
BTN_UP    = 2   # increment / start pomodoro
BTN_DOWN  = 3   # decrement / reset pomodoro

# uo_out bits  (= led[7:0])
MODE_0    = 0   # display_mode[0]
MODE_1    = 1   # display_mode[1]
IN_SETUP  = 2   # in_setup flag
LED_WORK  = 3   # pomodoro work phase
LED_BREAK = 4   # pomodoro break phase
BUZZER    = 5   # alarm active
FIELD_0   = 6   # field_sel[0]
FIELD_1   = 7   # field_sel[1]

# uio_out bits
SPI_DIN   = 0
SPI_CS    = 1
SPI_CLK   = 2


CLK_PERIOD_NS = 20       # 20 ns -> 50 MHz
CLK_HZ        = 50_000_000
DEBOUNCE_CYC  = 520_000 


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
async def reset(dut):
    dut.ena.value   = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


async def press_button(dut, bit, hold_cycles=None):
    if hold_cycles is None:
        hold_cycles = DEBOUNCE_CYC
    dut.ui_in.value = int(dut.ui_in.value) | (1 << bit)
    await ClockCycles(dut.clk, hold_cycles)
    dut.ui_in.value = int(dut.ui_in.value) & ~(1 << bit)
    await ClockCycles(dut.clk, DEBOUNCE_CYC)  # wait for release debounce


def get_mode(dut):
    return (int(dut.uo_out.value) >> MODE_0) & 0x3


def get_in_setup(dut):
    return (int(dut.uo_out.value) >> IN_SETUP) & 1


def get_field_sel(dut):
    return (int(dut.uo_out.value) >> FIELD_0) & 0x3


def get_spi_cs(dut):
    return (int(dut.uio_out.value) >> SPI_CS) & 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Reset state
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_reset_state(dut):
    """after reset -> should be in CLOCK mode."""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    assert get_mode(dut)     == 0, f"expected CLOCK mode (0) after reset, got {get_mode(dut)}"
    assert get_in_setup(dut) == 0, f"expected not in setup after reset"
    dut._log.info("PASS: reset state")


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Mode cycling with btn_right
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_mode_cycle(dut):
    """btn_right should cycle CLOCK(0) -> DATE(1) -> POMODORO(2) -> CLOCK(0)"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    assert get_mode(dut) == 0, "should start in CLOCK mode"

    await press_button(dut, BTN_RIGHT)
    assert get_mode(dut) == 1, f"expected DATE mode (1), got {get_mode(dut)}"

    await press_button(dut, BTN_RIGHT)
    assert get_mode(dut) == 2, f"expected POMODORO mode (2), got {get_mode(dut)}"

    await press_button(dut, BTN_RIGHT)
    assert get_mode(dut) == 0, f"expected CLOCK mode (0) after wrap, got {get_mode(dut)}"

    dut._log.info("PASS: mode cycling")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Enter and exit setup
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_enter_exit_setup(dut):
    """btn_left should enter setup (LED[2]=1) and pressing again should exit (LED[2]=0)"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    assert get_in_setup(dut) == 0, "should not be in setup after reset"

    # Enter setup
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 1, "should be in setup after pressing btn_left"

    # Exit setup
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 0, "should exit setup after pressing btn_left again"

    dut._log.info("PASS: enter/exit setup")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: btn_right cycles fields inside setup, not modes
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_field_cycle_in_setup(dut):
    """inside clock setup, btn_right should cycle MIN(0) -> HOUR(1) -> MIN(0)"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    # Enter setup in CLOCK mode
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 1, "should be in setup"
    assert get_mode(dut) == 0, "should still be in CLOCK mode"

    # Should start on MIN field (field_sel = 00)
    assert get_field_sel(dut) == 0, f"expected MIN field (0), got {get_field_sel(dut)}"

    # Cycle to HOUR
    await press_button(dut, BTN_RIGHT)
    assert get_in_setup(dut) == 1,  "should still be in setup after btn_right"
    assert get_mode(dut)     == 0,  "mode should not change inside setup"
    assert get_field_sel(dut) == 1, f"expected HOUR field (1), got {get_field_sel(dut)}"

    # Cycle back to MIN
    await press_button(dut, BTN_RIGHT)
    assert get_field_sel(dut) == 0, f"expected MIN field (0), got {get_field_sel(dut)}"

    # Exit setup
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 0, "should exit setup"

    dut._log.info("PASS: field cycling in setup")


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Date mode field cycling
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_date_field_cycle(dut):
    """in DATE setup, btn_right should cycle DAY(2) -> MON(3) -> DAY(2)"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    # Go to DATE mode
    await press_button(dut, BTN_RIGHT)
    assert get_mode(dut) == 1, "should be in DATE mode"

    # Enter setup
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 1

    # Should start on DAY field (field_sel = 10 = 2)
    assert get_field_sel(dut) == 2, f"expected DAY field (2), got {get_field_sel(dut)}"

    # Cycle to MON
    await press_button(dut, BTN_RIGHT)
    assert get_in_setup(dut) == 1,  "should still be in setup"
    assert get_field_sel(dut) == 3, f"expected MON field (3), got {get_field_sel(dut)}"

    # Cycle back to DAY
    await press_button(dut, BTN_RIGHT)
    assert get_field_sel(dut) == 2, f"expected DAY field (2), got {get_field_sel(dut)}"

    await press_button(dut, BTN_LEFT)
    dut._log.info("PASS: date field cycling")


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: uio_oe — SPI pins are outputs
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_uio_oe(dut):
    """uio_oe[2:0] should be 3'b111"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)
    await ClockCycles(dut.clk, 10)

    uio_oe = int(dut.uio_oe.value) & 0x7
    assert uio_oe == 0x7, f"expected uio_oe[2:0]=0b111, got {uio_oe:#05b}"
    dut._log.info("PASS: uio_oe SPI outputs set")


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: btn_right does NOT cycle modes while in setup
# ─────────────────────────────────────────────────────────────────────────────
@cocotb.test()
async def test_mode_blocked_in_setup(dut):
    """btn_right shouldn't change display_mode while in setup"""
    clock = Clock(dut.clk, CLK_PERIOD_NS, "ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    assert get_mode(dut) == 0

    # Enter setup
    await press_button(dut, BTN_LEFT)
    assert get_in_setup(dut) == 1

    # Press btn_right — should cycle field, not mode
    await press_button(dut, BTN_RIGHT)
    assert get_mode(dut) == 0, f"mode should stay CLOCK in setup, got {get_mode(dut)}"

    await press_button(dut, BTN_LEFT)
    dut._log.info("PASS: mode blocked while in setup")