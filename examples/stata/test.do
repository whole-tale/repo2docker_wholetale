ssc install outreg2

use test.dta, clear
reg y x1, robust
outreg2 using myfile, tex replace ctitle(Model 1)
