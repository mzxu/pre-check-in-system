# Pre-check-in verification system
# test modify and git commit
A system aims to implement tests/verification before the code truly committed.


## Features

	1. Integrated with CI system
	2. Compatible with all svn clients
	3. Distributed test execution 
	4. Concurrent commits support
	5. Extendable and Scalable

## Limitation

	1. Complicated configuration
	2. Commits cannot be canceled if the pre-commit hook is triggered
	3. If several developers commit the same file at the same time, only the first successful commit can be accepted.

## To-do

	1. Code optimization to improve the stability and performance 
	2. BI report
	3. Failure investigation portal 


* Powered by SMA QE team ,released in 2012.
* Visit our [wiki](http://tech-websrvr/technology/wiki/index.php?title=CTC_Social_Team_Wiki_Site) page.
