set terminal svg size 1000, 500
set xlabel "time (s)"
set ylabel "intensity"
set multiplot layout 1,2
set title "Case"
plot casefile using 1:3 with lines title low, casefile using 1:5 with lines title high
set yrange [ GPVAL_Y_MIN : GPVAL_Y_MAX ]
set title "Control"
plot controlfile using 1:3 with lines title low, controlfile using 1:5 with lines title high
