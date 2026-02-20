module RangeFinder
   #(parameter WIDTH=16)
    (input  logic [WIDTH-1:0] data_in,
     input  logic             clock, reset,
     input  logic             go, finish,
     output logic [WIDTH-1:0] range,
     output logic             error);

   enum logic [1:0] {START, RUN, FINISH, ERROR} state, next_state;
   
   logic [WIDTH-1:0] high_q, low_q;

   // --------------------------------------------------------
   // Next State Logic 
   // --------------------------------------------------------
   always_comb begin
      next_state = state; 
      
      unique case (state)
         START: begin
            if (go & finish)        next_state = START;
            else if (go & !finish)  next_state = RUN;
            else if (!go & finish)  next_state = ERROR;
            else                    next_state = START;
         end
         RUN:     next_state = (finish) ? FINISH : RUN;
         FINISH:  next_state = (finish) ? FINISH : START;
         ERROR:   next_state = (go & !finish) ? START : ERROR;
      endcase
   end

   // --------------------------------------------------------
   // Output Logic 
   // --------------------------------------------------------
   always_comb begin
      range = 'x;
      error = 1'b0;

      unique case (state)
         START: begin
            if (go & finish) error = 1'b1;
            else if (finish) error = 1'b1;
         end
         RUN: begin
            if (finish) range = high_q - low_q;
         end
         FINISH: begin
            if (finish) range = high_q - low_q;
         end
         ERROR: begin
            if (go & !finish) error = 1'b0;
            else              error = 1'b1; 
         end
      endcase
   end

   // --------------------------------------------------------
   // Sequential Logic
   // --------------------------------------------------------
   always_ff @(posedge clock or posedge reset) begin
      if (reset) begin
         state  <= START;
         low_q  <= '1; 
         high_q <= '0; 
      end else begin
         state <= next_state;
                  case (state)
            START: begin
               if (go & !finish) begin
                  low_q  <= data_in;
                  high_q <= data_in;
               end else begin
                  low_q  <= '1;
                  high_q <= '0;
               end
            end
            RUN: begin
               if (data_in < low_q)  low_q  <= data_in;
               if (data_in > high_q) high_q <= data_in;
            end
         endcase
      end
   end

endmodule: RangeFinder