/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_top (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // All output pins must be assigned. If not used, assign to 0.

    wire [7:0] range_out;
    wire       error_out;

    assign uo_out = range_out;

    assign uio_out[0]   = 1'b0;       
    assign uio_out[1]   = 1'b0;       // Pin 1 is now an input, so drive 0
    assign uio_out[2]   = error_out;  // Pin 2 outputs 'error'
    assign uio_out[7:3] = 5'b0;

    assign uio_oe = 8'b0000_0110;

    RangeFinder #(.WIDTH(8)) r(.data_in(ui_in),
                                .clock(clk),
                                .reset(~rst_n),
                                .go(uio_in[0]),
                                .finish(uio_in[1]),
                                .range(range_out),
                                .error(error_out));

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, uio_in[7:2], 1'b0};

endmodule
