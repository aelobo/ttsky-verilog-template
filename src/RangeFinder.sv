module RangeFinder
   #(parameter WIDTH=16)
    (input  logic [WIDTH-1:0] data_in,
     input  logic             clock, reset,
     input  logic             go, finish,
     output logic [WIDTH-1:0] range,
     output logic             error);

   // Put your code here
   enum logic [1:0] {START, RUN, FINISH, ERROR} state, next_state;
   
   logic [WIDTH-1:0] high_q, low_q;

   // next state logic
   always_comb begin
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

   // output logic
   always_comb begin
      unique case (state)
         // START state; reset state and wait for go signal
         START: begin
            low_q = 16'hFFFF;
            high_q = 16'h0;
            error = 1'b0;
            range = 16'hx;

            if (go & finish) error = 1'b1;            // go AND finish asserted

            else if (go) begin                        // go asserted
               if (data_in < low_q)   low_q = data_in;
               if (data_in > high_q)  high_q = data_in; 
            end

            else if (finish) error = 1'b1;            // finish asserted before go
         end

         // RUN state; go has been asserted
         RUN: begin
            low_q = (data_in < low_q) ? data_in : low_q;
            high_q = (data_in > high_q) ? data_in : high_q;
            error = 1'b0;
            range = 16'hx;

            if (finish)  begin                        // finish asserted
               range = high_q - low_q;
               error = 1'b0;                          
            end
         end

         // FINISH state; output range while finish is asserted
         FINISH: begin
            if (finish)  begin                        // finish asserted
               range = high_q - low_q;
               error = 1'b0;                          
            end
         end

         // ERROR state; stay in error until go asserted again
         ERROR: begin
            range = 16'hx;
            if (go & !finish) error = 1'b0;
            else              error = 1'b1; 
         end

      endcase
   end

   always_ff @(posedge clock, posedge reset) begin
      if (reset)  state <= START;
      else        state <= next_state;
   end


endmodule: RangeFinder