Micropython code for UPD socket communication directly between two (or more?) Pi Pico W.

I have tested this using the Identical file on two seperate Pico W and it works good. The issue is if one device gets turned off, both must be turned off, then turned back on again, one 10 seconds later than the other to get them to reconnect. Aside from resetting or powering one off, I have not had any connectivity issues between the two Pico-W in testing.

I know using threads for something like this is not the best idea, but I wanted to see if it could be done.
