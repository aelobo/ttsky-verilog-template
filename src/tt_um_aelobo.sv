/*
 * Copyright (c) 2024 Amelia Lobo
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_aelobo (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // uio[2:0] are outputs (SPI), rest unused inputs
    assign uio_oe  = 8'b0000_0111;
    assign uio_out[7:3] = 5'b0;
 
    // internal signals
    wire [7:0] led;
    wire       spi_din, spi_cs, spi_clk;

 
    ChipInterface #(
        .CLK_FREQ(50_000_000)
    ) chip (
        .clock        (clk),
        .reset_n      (rst_n),
        .btn_left     (ui_in[0]),
        .btn_right    (ui_in[1]),
        .btn_up       (ui_in[2]),
        .btn_down     (ui_in[3]),
        .led          (led),
        .spi_din      (spi_din),
        .spi_cs       (spi_cs),
        .spi_clk      (spi_clk)
    );
 
    // output mapping
    assign uo_out   = led;
    assign uio_out[0] = spi_din;
    assign uio_out[1] = spi_cs;
    assign uio_out[2] = spi_clk;

endmodule
