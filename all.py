#! /usr/bin/env python
import sys
import random
import os
import time
import getopt

wait = None
min_per_node = 0
max_per_node = 1000
monitor_time = None

splits = { (2,1) : '0;1',
(3,1) : '0;1;2',
(3,2) : '0,1;1,2;2,0',
(4,1) : '0;1;2;3',
(4,2) : '0,1;1,2;2,3;3,0',
(4,3) : '0,1,2;1,2,3;2,0,3;3,0,1',
(5,1) : '0;1;2;3;4',
(5,2) : '0,1;1,2;2,3;3,4;4,0',
(5,3) : '0,1,3;1,2,4;2,1,3;3,0,4;4,0,2',
(5,4) : '0,1,2,3;1,0,2,4;2,1,3,4;3,0,1,4;4,0,2,3',
(6,1) : '0;1;2;3;4;5',
(6,2) : '0,1;1,2;2,3;3,4;4,5;5,0',
(6,3) : '0,1,3;1,2,5;2,1,3;3,0,4;4,2,5;5,0,4',
(6,4) : '0,1,3,5;1,2,4,5;2,0,1,3;3,0,1,4;4,2,3,5;5,0,2,4',
(6,5) : '0,1,3,4,5;1,0,2,4,5;2,0,1,3,5;3,0,1,2,4;4,1,2,3,5;5,0,2,3,4',
(7,1) : '0;1;2;3;4;5;6',
(7,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,0',
(7,3) : '0,1,2;1,2,3;2,1,3;3,0,4;4,5,6;5,4,6;6,0,5',
(7,4) : '0,1,2,5;1,2,3,6;2,0,1,3;3,0,1,4;4,3,5,6;5,2,4,6;6,0,4,5',
(7,5) : '0,1,2,5,6;1,0,2,3,6;2,0,1,3,4;3,0,1,4,5;4,2,3,5,6;5,2,3,4,6;6,0,1,4,5',
(7,6) : '0,1,2,3,5,6;1,0,2,3,4,6;2,0,1,3,4,5;3,0,1,4,5,6;4,1,2,3,5,6;5,0,2,3,4,6;6,0,1,2,4,5',
(8,1) : '0;1;2;3;4;5;6;7',
(8,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,0',
(8,3) : '0,1,2;1,2,3;2,1,3;3,0,4;4,5,6;5,6,7;6,5,7;7,0,4',
(8,4) : '0,1,2,3;1,2,3,5;2,0,1,3;3,0,1,4;4,5,6,7;5,4,6,7;6,2,5,7;7,0,4,6',
(8,5) : '0,1,2,3,7;1,0,2,3,5;2,0,1,3,4;3,0,1,4,6;4,3,5,6,7;5,2,4,6,7;6,1,2,5,7;7,0,4,5,6',
(8,6) : '0,1,2,3,4,7;1,0,2,3,5,6;2,0,1,3,4,5;3,0,1,4,6,7;4,2,3,5,6,7;5,2,3,4,6,7;6,0,1,2,5,7;7,0,1,4,5,6',
(8,7) : '0,1,2,3,4,6,7;1,0,2,3,4,5,6;2,0,1,3,4,5,7;3,0,1,4,5,6,7;4,1,2,3,5,6,7;5,0,2,3,4,6,7;6,0,1,2,3,5,7;7,0,1,2,4,5,6',
(9,1) : '0;1;2;3;4;5;6;7;8',
(9,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,0',
(9,3) : '0,1,2;1,2,3;2,1,3;3,0,4;4,5,8;5,6,7;6,5,7;7,4,8;8,0,6',
(9,4) : '0,1,2,3;1,2,3,8;2,0,1,3;3,0,1,4;4,5,6,8;5,4,6,7;6,2,5,7;7,4,5,8;8,0,6,7',
(9,5) : '0,1,2,3,5;1,0,2,3,8;2,0,1,3,4;3,0,1,4,8;4,5,6,7,8;5,2,4,6,7;6,2,3,5,7;7,4,5,6,8;8,0,1,6,7',
(9,6) : '0,1,2,3,5,7;1,0,2,3,6,8;2,0,1,3,4,8;3,0,1,4,5,8;4,2,5,6,7,8;5,2,3,4,6,7;6,1,2,3,5,7;7,0,4,5,6,8;8,0,1,4,6,7',
(9,7) : '0,1,2,3,5,7,8;1,0,2,3,6,7,8;2,0,1,3,4,6,8;3,0,1,2,4,5,8;4,2,3,5,6,7,8;5,0,2,3,4,6,7;6,1,2,3,4,5,7;7,0,1,4,5,6,8;8,0,1,4,5,6,7',
(10,1) : '0;1;2;3;4;5;6;7;8;9',
(10,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,0',
(10,3) : '0,1,2;1,2,3;2,1,3;3,0,4;4,5,9;5,6,7;6,5,7;7,4,8;8,6,9;9,0,8',
(10,4) : '0,1,2,3;1,2,3,9;2,0,1,3;3,0,1,4;4,5,8,9;5,4,6,7;6,2,5,7;7,4,5,8;8,6,7,9;9,0,6,8',
(10,5) : '0,1,2,3,5;1,2,3,7,9;2,0,1,3,9;3,0,1,4,8;4,5,6,8,9;5,2,4,6,7;6,2,4,5,7;7,3,4,5,8;8,0,6,7,9;9,0,1,6,8',
(10,6) : '0,1,2,3,5,9;1,2,3,5,7,9;2,0,1,3,8,9;3,0,1,2,4,8;4,5,6,7,8,9;5,2,3,4,6,7;6,0,2,4,5,7;7,3,4,5,6,8;8,0,1,6,7,9;9,0,1,4,6,8',
(10,7) : '0,1,2,3,5,6,9;1,2,3,5,7,8,9;2,0,1,3,5,8,9;3,0,1,2,4,8,9;4,2,5,6,7,8,9;5,0,2,3,4,6,7;6,0,2,3,4,5,7;7,1,3,4,5,6,8;8,0,1,4,6,7,9;9,0,1,4,6,7,8',
(11,1) : '0;1;2;3;4;5;6;7;8;9;10',
(11,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,0',
(11,3) : '0,1,3;1,0,2;2,3,9;3,1,4;4,5,7;5,4,6;6,2,7;7,5,8;8,9,10;9,8,10;10,0,6',
(11,4) : '0,1,3,8;1,0,2,3;2,3,9,10;3,1,4,9;4,5,6,7;5,4,6,7;6,2,5,7;7,2,5,8;8,1,9,10;9,0,8,10;10,0,4,6',
(11,5) : '0,1,3,8,9;1,0,2,3,5;2,3,8,9,10;3,1,4,9,10;4,2,5,6,7;5,3,4,6,7;6,2,4,5,7;7,2,5,6,8;8,0,1,9,10;9,0,1,8,10;10,0,4,6,7',
(11,6) : '0,1,3,8,9,10;1,0,2,3,5,9;2,1,3,8,9,10;3,1,4,8,9,10;4,2,3,5,6,7;5,2,3,4,6,7;6,0,2,4,5,7;7,2,4,5,6,8;8,0,1,6,9,10;9,0,1,7,8,10;10,0,4,5,6,7',
(11,7) : '0,1,3,4,8,9,10;1,0,2,3,5,7,9;2,1,3,6,8,9,10;3,1,4,5,8,9,10;4,2,3,5,6,7,10;5,2,3,4,6,7,8;6,0,1,2,4,5,7;7,0,2,4,5,6,8;8,0,1,3,6,9,10;9,0,1,2,7,8,10;10,0,4,5,6,7,9',
(12,1) : '0;1;2;3;4;5;6;7;8;9;10;11',
(12,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,0',
(12,3) : '0,1,3;1,0,2;2,3,10;3,4,9;4,5,7;5,4,6;6,1,7;7,2,8;8,9,11;9,8,10;10,5,11;11,0,6',
(12,4) : '0,1,2,3;1,0,2,3;2,3,9,10;3,4,8,9;4,5,6,7;5,4,6,7;6,0,1,7;7,1,2,8;8,9,10,11;9,8,10,11;10,4,5,11;11,0,5,6',
(12,5) : '0,1,2,3,9;1,0,2,3,8;2,3,9,10,11;3,4,8,9,10;4,2,5,6,7;5,3,4,6,7;6,0,1,4,7;7,1,2,5,8;8,1,9,10,11;9,0,8,10,11;10,4,5,6,11;11,0,5,6,7',
(12,6) : '0,1,2,3,9,10;1,0,2,3,8,9;2,3,8,9,10,11;3,4,8,9,10,11;4,2,3,5,6,7;5,2,3,4,6,7;6,0,1,4,5,7;7,1,2,5,6,8;8,0,1,9,10,11;9,0,1,8,10,11;10,4,5,6,7,11;11,0,4,5,6,7',
(12,7) : '0,1,2,3,6,9,10;1,0,2,3,8,9,10;2,1,3,8,9,10,11;3,4,5,8,9,10,11;4,2,3,5,6,7,8;5,2,3,4,6,7,11;6,0,1,4,5,7,9;7,1,2,4,5,6,8;8,0,1,3,9,10,11;9,0,1,7,8,10,11;10,0,4,5,6,7,11;11,0,2,4,5,6,7',
(13,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12',
(13,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,0',
(13,3) : '0,1,8;1,0,2;2,3,10;3,4,9;4,2,5;5,4,6;6,1,7;7,3,8;8,9,11;9,10,12;10,7,11;11,6,12;12,0,5',
(13,4) : '0,1,8,9;1,0,2,3;2,3,10,12;3,4,8,9;4,2,5,6;5,2,4,6;6,0,1,7;7,1,3,8;8,9,10,11;9,10,11,12;10,5,7,11;11,6,7,12;12,0,4,5',
(13,5) : '0,1,3,8,9;1,0,2,3,9;2,3,10,11,12;3,4,8,9,10;4,1,2,5,6;5,2,4,6,7;6,0,1,2,7;7,0,1,3,8;8,9,10,11,12;9,8,10,11,12;10,4,5,7,11;11,5,6,7,12;12,0,4,5,6',
(13,6) : '0,1,3,8,9,10;1,0,2,3,9,12;2,3,9,10,11,12;3,4,8,9,10,11;4,0,1,2,5,6;5,2,3,4,6,7;6,0,1,2,7,8;7,0,1,2,3,8;8,1,9,10,11,12;9,5,8,10,11,12;10,4,5,6,7,11;11,4,5,6,7,12;12,0,4,5,6,7',
(13,7) : '0,1,3,8,9,10,11;1,0,2,3,7,9,12;2,3,8,9,10,11,12;3,4,6,8,9,10,11;4,0,1,2,3,5,6;5,0,2,3,4,6,7;6,0,1,2,7,8,9;7,0,1,2,3,5,8;8,1,4,9,10,11,12;9,1,5,8,10,11,12;10,4,5,6,7,11,12;11,2,4,5,6,7,12;12,0,4,5,6,7,10',
(14,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13',
(14,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,0',
(14,3) : '0,1,9;1,2,8;2,3,10;3,4,12;4,3,5;5,2,6;6,1,7;7,0,8;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,0,4',
(14,4) : '0,1,9,12;1,0,2,8;2,3,10,13;3,4,9,12;4,2,3,5;5,2,3,6;6,1,7,8;7,0,1,8;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,0,4,5',
(14,5) : '0,1,8,9,12;1,0,2,8,9;2,3,10,11,13;3,4,9,10,12;4,1,2,3,5;5,2,3,6,7;6,0,1,7,8;7,0,1,3,8;8,9,10,11,13;9,10,11,12,13;10,5,6,7,11;11,4,6,7,12;12,2,4,5,13;13,0,4,5,6',
(14,6) : '0,1,8,9,10,12;1,0,2,8,9,13;2,3,9,10,11,13;3,4,9,10,11,12;4,0,1,2,3,5;5,1,2,3,6,7;6,0,1,3,7,8;7,0,1,2,3,8;8,9,10,11,12,13;9,8,10,11,12,13;10,4,5,6,7,11;11,4,5,6,7,12;12,2,4,5,6,13;13,0,4,5,6,7',
(14,7) : '0,1,8,9,10,11,12;1,0,2,7,8,9,13;2,3,6,9,10,11,13;3,4,9,10,11,12,13;4,0,1,2,3,5,8;5,1,2,3,4,6,7;6,0,1,3,7,8,9;7,0,1,2,3,5,8;8,1,9,10,11,12,13;9,0,8,10,11,12,13;10,4,5,6,7,11,12;11,2,4,5,6,7,12;12,2,3,4,5,6,13;13,0,4,5,6,7,10',
(15,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14',
(15,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,0',
(15,3) : '0,1,14;1,2,9;2,3,10;3,4,12;4,0,5;5,3,6;6,7,8;7,1,8;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,0,2',
(15,4) : '0,1,12,14;1,2,8,9;2,3,10,13;3,4,12,14;4,0,1,5;5,2,3,6;6,7,8,9;7,0,1,8;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,0,2,3',
(15,5) : '0,1,9,12,14;1,2,8,9,14;2,3,10,11,13;3,4,10,12,14;4,0,1,5,8;5,0,2,3,6;6,1,7,8,9;7,0,1,3,8;8,9,10,11,13;9,6,10,11,13;10,6,7,11,12;11,4,6,7,12;12,2,4,5,13;13,4,5,7,14;14,0,2,3,5',
(15,6) : '0,1,9,10,12,14;1,2,8,9,13,14;2,3,9,10,11,13;3,4,10,11,12,14;4,0,1,3,5,8;5,0,2,3,6,8;6,0,1,7,8,9;7,0,1,2,3,8;8,9,10,11,12,13;9,6,10,11,13,14;10,4,6,7,11,12;11,4,5,6,7,12;12,2,4,5,7,13;13,4,5,6,7,14;14,0,1,2,3,5',
(15,7) : '0,1,9,10,11,12,14;1,2,8,9,10,13,14;2,3,8,9,10,11,13;3,4,10,11,12,13,14;4,0,1,3,5,6,8;5,0,1,2,3,6,8;6,0,1,3,7,8,9;7,0,1,2,3,8,9;8,9,10,11,12,13,14;9,6,7,10,11,13,14;10,4,5,6,7,11,12;11,2,4,5,6,7,12;12,0,2,4,5,7,13;13,4,5,6,7,12,14;14,0,1,2,3,4,5',
(16,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15',
(16,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,0',
(16,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,8;5,0,6;6,7,9;7,1,8;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,3,15;15,0,2',
(16,4) : '0,1,12,15;1,2,9,14;2,3,10,13;3,4,12,15;4,1,5,8;5,0,6,8;6,7,9,14;7,0,1,8;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,2,3,15;15,0,2,3',
(16,5) : '0,1,12,14,15;1,2,9,14,15;2,3,10,11,13;3,4,10,12,15;4,0,1,5,8;5,0,1,6,8;6,7,8,9,14;7,0,1,8,9;8,9,10,11,13;9,6,10,11,13;10,6,7,11,12;11,4,6,7,12;12,3,4,5,13;13,2,4,5,14;14,2,3,5,15;15,0,2,3,7',
(16,6) : '0,1,10,12,14,15;1,2,9,13,14,15;2,3,10,11,13,14;3,4,10,11,12,15;4,0,1,5,8,9;5,0,1,2,6,8;6,1,7,8,9,14;7,0,1,3,8,9;8,9,10,11,12,13;9,6,10,11,13,15;10,4,6,7,11,12;11,4,5,6,7,12;12,0,3,4,5,13;13,2,4,5,7,14;14,2,3,5,8,15;15,0,2,3,6,7',
(16,7) : '0,1,10,11,12,14,15;1,2,9,10,13,14,15;2,3,9,10,11,13,14;3,4,10,11,12,13,15;4,0,1,3,5,8,9;5,0,1,2,4,6,8;6,0,1,7,8,9,14;7,0,1,3,8,9,14;8,9,10,11,12,13,15;9,6,10,11,12,13,15;10,4,5,6,7,11,12;11,2,4,5,6,7,12;12,0,3,4,5,7,13;13,2,4,5,6,7,14;14,1,2,3,5,8,15;15,0,2,3,6,7,8',
(17,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16',
(17,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,0',
(17,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,8;5,1,6;6,7,16;7,8,9;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,0,15;15,2,16;16,0,3',
(17,4) : '0,1,12,15;1,2,14,16;2,3,10,13;3,4,12,15;4,5,8,9;5,1,6,8;6,7,14,16;7,1,8,9;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,0,3,15;15,0,2,16;16,0,2,3',
(17,5) : '0,1,12,14,15;1,2,14,15,16;2,3,10,11,13;3,4,10,12,15;4,1,5,8,9;5,0,1,6,8;6,7,9,14,16;7,1,8,9,16;8,9,10,11,13;9,10,11,12,13;10,5,6,7,11;11,4,6,7,12;12,4,5,7,13;13,4,5,6,14;14,0,2,3,15;15,0,2,3,16;16,0,2,3,8',
(17,6) : '0,1,10,12,14,15;1,2,13,14,15,16;2,3,10,11,13,14;3,4,10,11,12,15;4,1,5,8,9,16;5,0,1,6,8,9;6,7,8,9,14,16;7,0,1,8,9,16;8,9,10,11,12,13;9,10,11,12,13,15;10,4,5,6,7,11;11,4,5,6,7,12;12,3,4,5,7,13;13,2,4,5,6,14;14,0,2,3,6,15;15,0,2,3,7,16;16,0,1,2,3,8',
(17,7) : '0,1,10,11,12,14,15;1,2,10,13,14,15,16;2,3,4,10,11,13,14;3,4,10,11,12,13,15;4,0,1,5,8,9,16;5,0,1,6,8,9,16;6,1,7,8,9,14,16;7,0,1,3,8,9,16;8,9,10,11,12,13,15;9,10,11,12,13,14,15;10,4,5,6,7,11,12;11,2,4,5,6,7,12;12,3,4,5,6,7,13;13,2,4,5,6,7,14;14,0,2,3,6,8,15;15,0,2,3,5,7,16;16,0,1,2,3,8,9',
(18,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17',
(18,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,0',
(18,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,9;5,6,8;6,7,17;7,8,16;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,0,15;15,2,16;16,1,17;17,0,3',
(18,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,9,16;5,1,6,8;6,7,14,17;7,8,9,16;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,0,3,15;15,0,2,16;16,1,8,17;17,0,2,3',
(18,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,10,12,15;4,5,8,9,16;5,1,6,8,9;6,7,14,16,17;7,8,9,16,17;8,9,10,11,13;9,10,11,12,13;10,5,6,7,11;11,4,6,7,12;12,4,5,7,13;13,4,5,6,14;14,0,2,3,15;15,0,2,3,16;16,0,1,8,17;17,0,1,2,3',
(18,6) : '0,1,10,12,14,15;1,2,13,14,15,17;2,3,10,11,13,14;3,4,10,11,12,15;4,5,8,9,16,17;5,1,6,8,9,16;6,7,9,14,16,17;7,1,8,9,16,17;8,9,10,11,12,13;9,10,11,12,13,15;10,4,5,6,7,11;11,4,5,6,7,12;12,0,4,5,7,13;13,2,4,5,6,14;14,0,2,3,6,15;15,0,2,3,7,16;16,0,1,3,8,17;17,0,1,2,3,8',
(18,7) : '0,1,10,11,12,14,15;1,2,10,13,14,15,17;2,3,10,11,12,13,14;3,4,10,11,12,13,15;4,1,5,8,9,16,17;5,1,6,8,9,16,17;6,7,8,9,14,16,17;7,0,1,8,9,16,17;8,9,10,11,12,13,15;9,10,11,12,13,14,15;10,2,4,5,6,7,11;11,4,5,6,7,12,16;12,0,3,4,5,7,13;13,2,4,5,6,7,14;14,0,2,3,4,6,15;15,0,2,3,6,7,16;16,0,1,3,8,9,17;17,0,1,2,3,5,8',
(19,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18',
(19,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,0',
(19,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,18;5,6,9;6,7,17;7,8,16;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,3,15;15,2,16;16,1,17;17,0,18;18,0,8',
(19,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,16,18;5,6,8,9;6,7,14,17;7,8,16,18;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,2,3,15;15,2,3,16;16,0,1,17;17,0,1,18;18,0,8,9',
(19,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,10,12,15;4,5,9,16,18;5,6,8,9,18;6,7,14,16,17;7,8,16,17,18;8,9,10,11,13;9,6,10,11,13;10,6,7,11,12;11,4,6,7,12;12,2,4,5,13;13,4,5,7,14;14,0,2,3,15;15,2,3,5,16;16,0,1,8,17;17,0,1,3,18;18,0,1,8,9',
(19,6) : '0,1,10,12,14,15;1,2,13,14,15,17;2,3,10,11,13,14;3,4,10,11,12,15;4,5,9,16,17,18;5,6,8,9,16,18;6,7,14,16,17,18;7,8,9,16,17,18;8,9,10,11,12,13;9,6,10,11,13,15;10,4,6,7,11,12;11,4,5,6,7,12;12,2,4,5,7,13;13,4,5,6,7,14;14,0,1,2,3,15;15,0,2,3,5,16;16,0,1,2,8,17;17,0,1,3,8,18;18,0,1,3,8,9',
(19,7) : '0,1,10,11,12,14,15;1,2,10,13,14,15,17;2,3,10,11,13,14,17;3,4,10,11,12,13,15;4,5,8,9,16,17,18;5,1,6,8,9,16,18;6,7,9,14,16,17,18;7,8,9,14,16,17,18;8,9,10,11,12,13,15;9,6,10,11,12,13,15;10,4,5,6,7,11,12;11,4,5,6,7,12,16;12,0,2,4,5,7,13;13,3,4,5,6,7,14;14,0,1,2,3,4,15;15,0,2,3,5,7,16;16,0,1,2,8,17,18;17,0,1,3,6,8,18;18,0,1,2,3,8,9',
(20,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19',
(20,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,0',
(20,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,19;5,6,18;6,7,17;7,8,16;8,9,11;9,10,13;10,7,11;11,6,12;12,5,13;13,4,14;14,3,15;15,2,16;16,1,17;17,0,18;18,9,19;19,0,8',
(20,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,16,19;5,6,9,18;6,7,14,17;7,8,16,19;8,9,10,11;9,10,11,13;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,2,3,15;15,2,3,16;16,0,1,17;17,0,1,18;18,8,9,19;19,0,8,18',
(20,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,10,12,15;4,5,16,18,19;5,6,9,18,19;6,7,14,16,17;7,8,16,17,19;8,9,10,11,13;9,6,10,11,13;10,6,7,11,12;11,4,6,7,12;12,2,4,5,13;13,4,5,7,14;14,0,2,3,15;15,2,3,5,16;16,0,1,8,17;17,0,1,3,18;18,1,8,9,19;19,0,8,9,18',
(20,6) : '0,1,10,12,14,15;1,2,13,14,15,17;2,3,10,11,13,14;3,4,10,11,12,15;4,5,16,17,18,19;5,6,9,16,18,19;6,7,14,16,17,19;7,8,16,17,18,19;8,9,10,11,12,13;9,6,10,11,13,15;10,4,6,7,11,12;11,4,5,6,7,12;12,2,3,4,5,13;13,2,4,5,7,14;14,0,2,3,6,15;15,2,3,5,7,16;16,0,1,8,9,17;17,0,1,3,8,18;18,0,1,8,9,19;19,0,1,8,9,18',
(20,7) : '0,1,10,11,12,14,15;1,2,10,13,14,15,17;2,3,10,11,13,14,17;3,4,10,11,12,13,15;4,5,9,16,17,18,19;5,6,8,9,16,18,19;6,7,14,16,17,18,19;7,8,14,16,17,18,19;8,9,10,11,12,13,15;9,6,10,11,12,13,15;10,4,5,6,7,11,12;11,4,5,6,7,12,16;12,2,3,4,5,7,13;13,2,4,5,6,7,14;14,0,1,2,3,6,15;15,0,2,3,5,7,16;16,0,1,8,9,17,19;17,0,1,3,4,8,18;18,0,1,3,8,9,19;19,0,1,2,8,9,18',
(21,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20',
(21,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,0',
(21,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,19;5,6,18;6,7,17;7,8,16;8,9,11;9,10,13;10,4,11;11,7,12;12,2,13;13,5,14;14,0,15;15,3,16;16,8,17;17,1,18;18,19,20;19,9,20;20,0,6',
(21,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,16,19;5,6,18,20;6,7,14,17;7,8,16,19;8,6,9,11;9,10,11,13;10,4,7,11;11,4,7,12;12,2,5,13;13,2,5,14;14,0,3,15;15,0,3,16;16,1,8,17;17,1,8,18;18,9,19,20;19,9,18,20;20,0,6,10',
(21,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,12,13,15;4,5,16,18,19;5,6,18,19,20;6,7,14,16,17;7,8,16,17,19;8,6,9,10,11;9,4,10,11,13;10,4,7,11,12;11,4,6,7,12;12,0,2,5,13;13,2,3,5,14;14,0,2,3,15;15,0,3,5,16;16,1,8,17,20;17,1,8,9,18;18,8,9,19,20;19,1,9,18,20;20,0,6,7,10',
(21,6) : '0,1,10,12,14,15;1,2,14,15,16,17;2,3,10,11,13,15;3,4,11,12,13,15;4,5,16,17,18,19;5,6,9,18,19,20;6,7,14,16,17,19;7,8,14,16,17,19;8,6,7,9,10,11;9,4,10,11,12,13;10,4,6,7,11,12;11,4,5,6,7,12;12,0,2,3,5,13;13,0,2,3,5,14;14,0,2,3,4,15;15,0,2,3,5,16;16,1,8,17,18,20;17,1,8,9,18,20;18,1,8,9,19,20;19,1,8,9,18,20;20,0,6,7,10,13',
(21,7) : '0,1,10,11,12,14,15;1,2,14,15,16,17,19;2,3,10,11,12,13,15;3,4,10,11,12,13,15;4,5,14,16,17,18,19;5,6,9,17,18,19,20;6,7,14,16,17,18,19;7,8,14,16,17,19,20;8,6,7,9,10,11,13;9,4,6,10,11,12,13;10,4,5,6,7,11,12;11,4,5,6,7,12,16;12,0,2,3,4,5,13;13,0,2,3,5,7,14;14,0,2,3,4,8,15;15,0,1,2,3,5,16;16,1,8,9,17,18,20;17,1,2,8,9,18,20;18,0,1,8,9,19,20;19,1,3,8,9,18,20;20,0,6,7,10,13,15',
(22,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21',
(22,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,0',
(22,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,19;5,6,18;6,7,17;7,8,16;8,9,11;9,10,13;10,5,11;11,4,12;12,3,13;13,2,14;14,1,15;15,0,16;16,9,17;17,8,18;18,19,20;19,20,21;20,6,21;21,0,7',
(22,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,16,19;5,6,18,20;6,7,14,17;7,8,16,19;8,9,10,11;9,10,11,13;10,4,5,11;11,4,5,12;12,2,3,13;13,2,3,14;14,0,1,15;15,0,1,16;16,8,9,17;17,8,9,18;18,19,20,21;19,18,20,21;20,6,7,21;21,0,6,7',
(22,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,10,12,15;4,5,16,18,19;5,6,18,19,20;6,7,14,16,17;7,8,16,17,19;8,9,10,11,13;9,10,11,12,13;10,4,5,7,11;11,4,5,6,12;12,1,2,3,13;13,0,2,3,14;14,0,1,3,15;15,0,1,2,16;16,8,9,17,20;17,8,9,18,21;18,9,19,20,21;19,8,18,20,21;20,4,6,7,21;21,0,5,6,7',
(22,6) : '0,1,10,12,14,15;1,2,13,14,15,17;2,3,10,11,13,14;3,4,10,11,12,15;4,5,16,17,18,19;5,6,16,18,19,20;6,7,14,16,17,19;7,8,16,17,18,19;8,9,10,11,12,13;9,10,11,12,13,15;10,4,5,6,7,11;11,4,5,6,7,12;12,0,1,2,3,13;13,0,1,2,3,14;14,0,1,2,3,15;15,0,1,2,3,16;16,8,9,17,20,21;17,8,9,18,20,21;18,8,9,19,20,21;19,8,9,18,20,21;20,4,5,6,7,21;21,0,4,5,6,7',
(22,7) : '0,1,10,11,12,14,15;1,2,10,13,14,15,17;2,3,10,11,12,13,14;3,4,10,11,12,13,15;4,5,16,17,18,19,21;5,6,16,17,18,19,20;6,7,14,16,17,18,19;7,6,8,16,17,18,19;8,7,9,10,11,12,13;9,10,11,12,13,14,15;10,2,4,5,6,7,11;11,4,5,6,7,12,16;12,0,1,2,3,5,13;13,0,1,2,3,4,14;14,0,1,2,3,9,15;15,0,1,2,3,8,16;16,8,9,17,19,20,21;17,3,8,9,18,20,21;18,1,8,9,19,20,21;19,0,8,9,18,20,21;20,4,5,6,7,15,21;21,0,4,5,6,7,20',
(23,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22',
(23,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,0',
(23,3) : '0,1,15;1,2,14;2,3,10;3,4,12;4,5,19;5,6,18;6,7,17;7,8,16;8,9,11;9,10,13;10,2,11;11,5,12;12,0,13;13,3,14;14,8,15;15,1,16;16,17,22;17,9,18;18,19,20;19,20,21;20,7,21;21,4,22;22,0,6',
(23,4) : '0,1,12,15;1,2,14,17;2,3,10,13;3,4,12,15;4,5,16,19;5,6,18,20;6,7,14,17;7,8,16,19;8,4,9,11;9,10,11,13;10,2,5,11;11,2,5,12;12,0,3,13;13,0,3,14;14,1,8,15;15,1,8,16;16,9,17,22;17,9,18,22;18,19,20,21;19,18,20,21;20,6,7,21;21,4,10,22;22,0,6,7',
(23,5) : '0,1,12,14,15;1,2,14,15,17;2,3,10,11,13;3,4,12,13,15;4,5,16,18,19;5,6,18,19,20;6,7,14,16,17;7,8,16,17,19;8,4,9,10,11;9,10,11,12,13;10,2,4,5,11;11,2,5,7,12;12,0,3,8,13;13,0,1,3,14;14,0,1,8,15;15,1,3,8,16;16,9,17,20,22;17,9,18,21,22;18,19,20,21,22;19,9,18,20,21;20,2,6,7,21;21,4,6,10,22;22,0,5,6,7',
(23,6) : '0,1,10,12,14,15;1,2,14,15,16,17;2,3,10,11,12,13;3,4,11,12,13,15;4,5,16,17,18,19;5,6,18,19,20,21;6,7,14,16,17,19;7,8,14,16,17,19;8,4,6,9,10,11;9,10,11,12,13,15;10,2,4,5,7,11;11,2,4,5,7,12;12,0,1,3,8,13;13,0,1,3,8,14;14,0,1,3,8,15;15,0,1,3,8,16;16,9,17,18,20,22;17,9,18,20,21,22;18,9,19,20,21,22;19,9,18,20,21,22;20,2,5,6,7,21;21,2,4,6,10,22;22,0,5,6,7,13',
(23,7) : '0,1,10,11,12,14,15;1,2,12,14,15,16,17;2,3,10,11,12,13,15;3,4,10,11,12,13,15;4,5,16,17,18,19,21;5,6,17,18,19,20,21;6,7,14,16,17,18,19;7,8,14,16,17,19,20;8,4,6,9,10,11,13;9,6,10,11,12,13,15;10,2,3,4,5,7,11;11,2,4,5,7,12,16;12,0,1,2,3,8,13;13,0,1,3,5,8,14;14,0,1,3,8,15,22;15,0,1,3,8,9,16;16,9,17,18,19,20,22;17,0,9,18,20,21,22;18,8,9,19,20,21,22;19,1,9,18,20,21,22;20,2,4,5,6,7,21;21,2,4,6,7,10,22;22,0,5,6,7,13,14',
(24,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23',
(24,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,0',
(24,3) : '0,1,9;1,2,8;2,3,22;3,4,23;4,3,5;5,2,6;6,1,7;7,0,8;8,9,20;9,10,21;10,11,13;11,12,14;12,13,15;13,12,14;14,11,15;15,10,16;16,7,17;17,6,18;18,5,19;19,4,20;20,16,21;21,17,22;22,18,23;23,0,19',
(24,4) : '0,1,9,15;1,2,8,14;2,3,10,22;3,4,12,23;4,3,5,19;5,2,6,18;6,1,7,17;7,0,8,16;8,9,11,20;9,10,13,21;10,3,11,13;11,2,12,14;12,1,13,15;13,0,12,14;14,9,11,15;15,8,10,16;16,7,17,22;17,6,18,23;18,5,19,20;19,4,20,21;20,4,16,21;21,5,17,22;22,6,18,23;23,0,7,19',
(24,5) : '0,1,9,12,15;1,2,8,14,17;2,3,10,13,22;3,4,12,15,23;4,3,5,16,19;5,2,6,18,20;6,1,7,14,17;7,0,8,16,19;8,9,10,11,20;9,10,11,13,21;10,2,3,11,13;11,2,3,12,14;12,0,1,13,15;13,0,1,12,14;14,8,9,11,15;15,8,9,10,16;16,7,17,22,23;17,6,18,22,23;18,5,19,20,21;19,4,18,20,21;20,4,5,16,21;21,4,5,17,22;22,6,7,18,23;23,0,6,7,19',
(24,6) : '0,1,9,12,14,15;1,2,8,14,15,17;2,3,10,11,13,22;3,4,10,12,15,23;4,3,5,16,18,19;5,2,6,18,19,20;6,1,7,14,16,17;7,0,8,16,17,19;8,9,10,11,13,20;9,10,11,12,13,21;10,2,3,5,11,13;11,2,3,4,12,14;12,0,1,9,13,15;13,0,1,8,12,14;14,1,8,9,11,15;15,0,8,9,10,16;16,7,17,20,22,23;17,6,18,21,22,23;18,5,19,20,21,22;19,4,18,20,21,23;20,4,5,6,16,21;21,4,5,7,17,22;22,3,6,7,18,23;23,0,2,6,7,19',
(24,7) : '0,1,9,10,12,14,15;1,2,8,13,14,15,17;2,3,10,11,13,14,22;3,4,10,11,12,15,23;4,3,5,16,17,18,19;5,2,6,16,18,19,20;6,1,7,14,16,17,19;7,0,8,16,17,18,19;8,9,10,11,12,13,20;9,10,11,12,13,15,21;10,2,3,4,5,11,13;11,2,3,4,5,12,14;12,0,1,8,9,13,15;13,0,1,8,9,12,14;14,0,1,8,9,11,15;15,0,1,8,9,10,16;16,7,17,20,21,22,23;17,6,18,20,21,22,23;18,5,19,20,21,22,23;19,4,18,20,21,22,23;20,4,5,6,7,16,21;21,4,5,6,7,17,22;22,2,3,6,7,18,23;23,0,2,3,6,7,19',
(25,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24',
(25,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,0',
(25,3) : '0,1,23;1,2,9;2,3,21;3,4,22;4,0,5;5,3,6;6,7,8;7,1,8;8,9,24;9,10,20;10,11,13;11,12,15;12,10,13;13,12,14;14,6,15;15,11,16;16,4,17;17,7,18;18,2,19;19,5,20;20,17,21;21,18,22;22,19,23;23,14,24;24,0,16',
(25,4) : '0,1,9,23;1,2,9,23;2,3,21,22;3,4,21,22;4,0,5,8;5,2,3,6;6,1,7,8;7,0,1,8;8,9,20,24;9,10,20,24;10,11,12,13;11,12,13,15;12,10,11,13;13,12,14,15;14,6,7,15;15,10,11,16;16,4,5,17;17,6,7,18;18,2,3,19;19,4,5,20;20,16,17,21;21,18,19,22;22,14,19,23;23,14,18,24;24,0,16,17',
(25,5) : '0,1,9,15,23;1,2,9,14,23;2,3,10,21,22;3,4,12,21,22;4,0,5,8,19;5,2,3,6,18;6,1,7,8,17;7,0,1,8,16;8,9,11,20,24;9,10,13,20,24;10,0,11,12,13;11,3,12,13,15;12,8,10,11,13;13,1,12,14,15;14,6,7,15,23;15,9,10,11,16;16,4,5,17,20;17,6,7,18,22;18,2,3,19,24;19,4,5,20,21;20,5,16,17,21;21,6,18,19,22;22,7,14,19,23;23,4,14,18,24;24,0,2,16,17',
(25,6) : '0,1,9,12,15,23;1,2,9,14,17,23;2,3,10,13,21,22;3,4,12,15,21,22;4,0,5,8,16,19;5,2,3,6,18,20;6,1,7,8,14,17;7,0,1,8,16,19;8,9,10,11,20,24;9,10,11,13,20,24;10,0,1,11,12,13;11,2,3,12,13,15;12,8,9,10,11,13;13,0,1,12,14,15;14,6,7,15,22,23;15,8,9,10,11,16;16,4,5,17,18,20;17,6,7,18,22,23;18,2,3,19,21,24;19,4,5,20,21,24;20,4,5,16,17,21;21,6,7,18,19,22;22,6,7,14,19,23;23,4,5,14,18,24;24,0,2,3,16,17',
(25,7) : '0,1,9,12,14,15,23;1,2,9,14,15,17,23;2,3,10,11,13,21,22;3,4,10,12,15,21,22;4,0,5,8,16,19,24;5,2,3,6,18,19,20;6,1,7,8,14,16,17;7,0,1,8,16,17,19;8,9,10,11,13,20,24;9,10,11,12,13,20,24;10,0,1,2,11,12,13;11,1,2,3,12,13,15;12,8,9,10,11,13,23;13,0,1,3,12,14,15;14,6,7,8,15,22,23;15,8,9,10,11,16,22;16,4,5,17,18,20,21;17,6,7,9,18,22,23;18,2,3,19,20,21,24;19,4,5,18,20,21,24;20,4,5,7,16,17,21;21,0,6,7,18,19,22;22,4,6,7,14,19,23;23,4,5,6,14,18,24;24,0,2,3,5,16,17',
(26,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25',
(26,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,0',
(26,3) : '0,1,22;1,2,23;2,3,20;3,4,21;4,5,8;5,0,6;6,7,9;7,1,8;8,9,24;9,10,25;10,11,13;11,12,15;12,11,13;13,10,14;14,7,15;15,6,16;16,5,17;17,4,18;18,3,19;19,2,20;20,17,21;21,18,22;22,19,23;23,14,24;24,16,25;25,0,12',
(26,4) : '0,1,22,23;1,2,22,23;2,3,20,21;3,4,20,21;4,1,5,8;5,0,3,6;6,7,8,9;7,1,8,9;8,9,24,25;9,10,24,25;10,11,13,15;11,10,12,15;12,6,11,13;13,10,12,14;14,4,7,15;15,6,11,16;16,2,5,17;17,4,7,18;18,0,3,19;19,2,5,20;20,17,18,21;21,17,18,22;22,14,19,23;23,14,19,24;24,13,16,25;25,0,12,16',
(26,5) : '0,1,9,22,23;1,2,8,22,23;2,3,20,21,24;3,4,20,21,25;4,0,1,5,8;5,0,1,3,6;6,7,8,9,14;7,1,8,9,23;8,9,20,24,25;9,10,21,24,25;10,11,12,13,15;11,10,12,13,15;12,6,10,11,13;13,10,11,12,14;14,4,6,7,15;15,6,7,11,16;16,2,4,5,17;17,4,5,7,18;18,0,2,3,19;19,2,3,5,20;20,16,17,18,21;21,17,18,19,22;22,14,18,19,23;23,14,19,22,24;24,13,16,17,25;25,0,12,15,16',
(26,6) : '0,1,9,15,22,23;1,2,8,14,22,23;2,3,10,20,21,24;3,4,12,20,21,25;4,0,1,5,8,19;5,0,1,3,6,18;6,7,8,9,14,17;7,1,8,9,16,23;8,9,11,20,24,25;9,10,13,21,24,25;10,1,11,12,13,15;11,0,10,12,13,15;12,6,9,10,11,13;13,8,10,11,12,14;14,4,6,7,15,22;15,6,7,11,16,23;16,2,4,5,17,20;17,4,5,7,18,25;18,0,2,3,19,24;19,2,3,5,20,21;20,6,16,17,18,21;21,7,17,18,19,22;22,4,14,18,19,23;23,5,14,19,22,24;24,3,13,16,17,25;25,0,2,12,15,16',
(26,7) : '0,1,9,12,15,22,23;1,2,8,14,17,22,23;2,3,10,13,20,21,24;3,4,12,15,20,21,25;4,0,1,5,8,19,24;5,0,1,3,6,18,19;6,7,8,9,14,16,17;7,1,8,9,14,16,23;8,9,10,11,20,24,25;9,10,11,13,21,24,25;10,0,1,11,12,13,15;11,0,1,10,12,13,15;12,6,8,9,10,11,13;13,8,9,10,11,12,14;14,4,6,7,15,22,23;15,6,7,11,16,22,23;16,2,4,5,17,20,21;17,4,5,7,18,20,25;18,0,2,3,19,24,25;19,2,3,5,18,20,21;20,6,7,16,17,18,21;21,3,7,17,18,19,22;22,4,5,14,18,19,23;23,2,5,14,19,22,24;24,3,6,13,16,17,25;25,0,2,4,12,15,16',
(27,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26',
(27,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,26;26,0',
(27,3) : '0,1,21;1,2,22;2,3,26;3,4,20;4,5,8;5,1,6;6,7,23;7,8,9;8,9,24;9,10,25;10,11,13;11,10,12;12,6,13;13,11,14;14,4,15;15,7,16;16,2,17;17,5,18;18,0,19;19,3,20;20,15,21;21,18,22;22,19,23;23,14,24;24,16,25;25,12,26;26,0,17',
(27,4) : '0,1,21,22;1,2,21,22;2,3,20,26;3,4,20,26;4,1,5,8;5,1,6,8;6,7,9,23;7,8,9,23;8,9,24,25;9,10,24,25;10,11,12,13;11,10,12,13;12,6,11,13;13,6,11,14;14,4,7,15;15,4,7,16;16,2,5,17;17,2,5,18;18,0,3,19;19,0,3,20;20,15,17,21;21,18,19,22;22,14,19,23;23,14,18,24;24,10,16,25;25,12,16,26;26,0,15,17',
(27,5) : '0,1,21,22,23;1,2,9,21,22;2,3,20,24,26;3,4,20,25,26;4,0,1,5,8;5,1,3,6,8;6,7,9,21,23;7,8,9,22,23;8,9,24,25,26;9,10,20,24,25;10,6,11,12,13;11,10,12,13,15;12,6,10,11,13;13,6,11,12,14;14,2,4,7,15;15,4,5,7,16;16,2,4,5,17;17,2,5,7,18;18,0,3,8,19;19,0,1,3,20;20,14,15,17,21;21,17,18,19,22;22,14,18,19,23;23,14,18,19,24;24,10,13,16,25;25,11,12,16,26;26,0,15,16,17',
(27,6) : '0,1,9,21,22,23;1,2,9,21,22,23;2,3,20,24,25,26;3,4,20,24,25,26;4,0,1,3,5,8;5,0,1,3,6,8;6,7,9,18,21,23;7,8,9,21,22,23;8,9,20,24,25,26;9,10,20,24,25,26;10,6,11,12,13,14;11,6,10,12,13,15;12,6,10,11,13,15;13,6,10,11,12,14;14,2,4,5,7,15;15,2,4,5,7,16;16,2,4,5,7,17;17,2,4,5,7,18;18,0,1,3,8,19;19,0,1,3,8,20;20,14,15,17,19,21;21,16,17,18,19,22;22,14,17,18,19,23;23,14,18,19,22,24;24,10,12,13,16,25;25,11,12,13,16,26;26,0,11,15,16,17',
(27,7) : '0,1,9,15,21,22,23;1,2,9,14,21,22,23;2,3,10,20,24,25,26;3,4,12,20,24,25,26;4,0,1,3,5,8,19;5,0,1,3,6,8,18;6,7,9,17,18,21,23;7,8,9,16,21,22,23;8,9,11,20,24,25,26;9,10,13,20,24,25,26;10,6,8,11,12,13,14;11,1,6,10,12,13,15;12,6,10,11,13,15,23;13,6,9,10,11,12,14;14,2,4,5,7,15,21;15,2,4,5,7,16,22;16,2,4,5,7,17,20;17,2,4,5,7,18,25;18,0,1,3,8,19,24;19,0,1,3,8,20,26;20,7,14,15,17,19,21;21,4,16,17,18,19,22;22,5,14,17,18,19,23;23,2,14,18,19,22,24;24,6,10,12,13,16,25;25,0,11,12,13,16,26;26,0,3,11,15,16,17',
(28,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27',
(28,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,26;26,27;27,0',
(28,3) : '0,1,20;1,2,21;2,3,26;3,4,27;4,5,9;5,6,8;6,7,22;7,8,23;8,9,24;9,10,25;10,11,13;11,10,12;12,7,13;13,6,14;14,5,15;15,4,16;16,3,17;17,2,18;18,1,19;19,0,20;20,15,21;21,18,22;22,19,23;23,14,24;24,16,25;25,12,26;26,11,27;27,0,17',
(28,4) : '0,1,20,21;1,2,20,21;2,3,26,27;3,4,26,27;4,5,8,9;5,6,8,9;6,7,22,23;7,8,22,23;8,9,24,25;9,10,24,25;10,11,12,13;11,10,12,13;12,6,7,13;13,6,7,14;14,4,5,15;15,4,5,16;16,2,3,17;17,2,3,18;18,0,1,19;19,0,1,20;20,15,18,21;21,15,18,22;22,14,19,23;23,14,19,24;24,10,16,25;25,12,16,26;26,11,17,27;27,0,11,17',
(28,5) : '0,1,14,20,21;1,2,20,21,23;2,3,24,26,27;3,4,25,26,27;4,1,5,8,9;5,0,6,8,9;6,7,20,22,23;7,8,21,22,23;8,9,24,25,26;9,10,24,25,27;10,7,11,12,13;11,6,10,12,13;12,6,7,11,13;13,6,7,10,14;14,3,4,5,15;15,2,4,5,16;16,2,3,5,17;17,2,3,4,18;18,0,1,9,19;19,0,1,8,20;20,15,17,18,21;21,15,18,19,22;22,14,18,19,23;23,14,19,22,24;24,10,12,16,25;25,12,13,16,26;26,11,16,17,27;27,0,11,15,17',
(28,6) : '0,1,14,20,21,22;1,2,9,20,21,23;2,3,24,25,26,27;3,4,24,25,26,27;4,1,5,8,9,23;5,0,1,6,8,9;6,7,20,21,22,23;7,8,20,21,22,23;8,9,24,25,26,27;9,10,24,25,26,27;10,6,7,11,12,13;11,6,10,12,13,15;12,4,6,7,11,13;13,6,7,10,11,14;14,2,3,4,5,15;15,2,4,5,7,16;16,0,2,3,5,17;17,2,3,4,5,18;18,0,1,8,9,19;19,0,1,3,8,20;20,15,17,18,19,21;21,15,17,18,19,22;22,14,16,18,19,23;23,14,18,19,22,24;24,10,12,13,16,25;25,10,12,13,16,26;26,11,12,16,17,27;27,0,11,14,15,17',
(28,7) : '0,1,14,20,21,22,24;1,2,9,20,21,23,25;2,3,22,24,25,26,27;3,4,23,24,25,26,27;4,0,1,5,8,9,23;5,0,1,3,6,8,9;6,7,20,21,22,23,26;7,8,20,21,22,23,27;8,9,20,24,25,26,27;9,10,21,24,25,26,27;10,6,7,11,12,13,15;11,6,10,12,13,14,15;12,4,5,6,7,11,13;13,4,6,7,10,11,14;14,2,3,4,5,7,15;15,2,4,5,6,7,16;16,0,2,3,5,8,17;17,1,2,3,4,5,18;18,0,1,2,8,9,19;19,0,1,3,8,9,20;20,12,15,17,18,19,21;21,10,15,17,18,19,22;22,14,16,17,18,19,23;23,14,16,18,19,22,24;24,10,11,12,13,16,25;25,10,12,13,16,18,26;26,11,12,13,16,17,27;27,0,11,14,15,17,19',
(29,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28',
(29,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,26;26,27;27,28;28,0',
(29,3) : '0,1,27;1,2,20;2,3,25;3,4,26;4,5,23;5,6,9;6,7,21;7,8,22;8,9,28;9,10,24;10,6,11;11,10,12;12,4,13;13,7,14;14,2,15;15,5,16;16,0,17;17,3,18;18,8,19;19,1,20;20,17,21;21,15,22;22,19,23;23,14,24;24,16,25;25,12,26;26,13,27;27,11,28;28,0,18',
(29,4) : '0,1,20,27;1,2,20,27;2,3,25,26;3,4,25,26;4,5,9,23;5,6,9,23;6,7,21,22;7,8,21,22;8,9,24,28;9,10,24,28;10,6,11,13;11,6,10,12;12,4,7,13;13,4,7,14;14,2,5,15;15,2,5,16;16,0,3,17;17,0,3,18;18,1,8,19;19,1,8,20;20,11,17,21;21,14,15,22;22,15,19,23;23,14,18,24;24,12,16,25;25,12,16,26;26,10,13,27;27,11,17,28;28,0,18,19',
(29,5) : '0,1,20,21,27;1,2,20,22,27;2,3,25,26,28;3,4,24,25,26;4,5,8,9,23;5,1,6,9,23;6,7,21,22,27;7,8,20,21,22;8,9,24,25,28;9,10,24,26,28;10,4,6,11,13;11,6,7,10,12;12,4,6,7,13;13,4,7,11,14;14,0,2,5,15;15,2,3,5,16;16,0,2,3,17;17,0,3,5,18;18,1,8,19,23;19,1,8,9,20;20,11,15,17,21;21,14,15,17,22;22,14,15,19,23;23,14,18,19,24;24,12,13,16,25;25,10,12,16,26;26,10,13,18,27;27,11,12,17,28;28,0,16,18,19',
(29,6) : '0,1,20,21,22,27;1,2,20,21,22,27;2,3,24,25,26,28;3,4,24,25,26,28;4,1,5,8,9,23;5,1,6,8,9,23;6,7,20,21,22,27;7,8,20,21,22,27;8,9,24,25,26,28;9,10,24,25,26,28;10,4,6,7,11,13;11,4,6,7,10,12;12,4,6,7,11,13;13,4,6,7,11,14;14,0,2,3,5,15;15,0,2,3,5,16;16,0,2,3,5,17;17,0,2,3,5,18;18,1,8,9,19,23;19,1,8,9,20,23;20,11,12,15,17,21;21,14,15,17,19,22;22,14,15,18,19,23;23,14,16,18,19,24;24,10,12,13,16,25;25,10,12,13,16,26;26,10,13,14,18,27;27,11,12,15,17,28;28,0,16,17,18,19',
(29,7) : '0,1,20,21,22,27,28;1,2,20,21,22,24,27;2,3,21,24,25,26,28;3,4,22,24,25,26,28;4,0,1,5,8,9,23;5,1,3,6,8,9,23;6,7,20,21,22,25,27;7,8,20,21,22,26,27;8,9,24,25,26,27,28;9,10,20,24,25,26,28;10,4,6,7,11,13,15;11,4,6,7,10,12,13;12,4,6,7,10,11,13;13,4,6,7,11,12,14;14,0,2,3,5,8,15;15,0,1,2,3,5,16;16,0,2,3,5,17,23;17,0,2,3,5,9,18;18,1,2,8,9,19,23;19,1,5,8,9,20,23;20,11,12,15,17,18,21;21,11,14,15,17,19,22;22,14,15,16,18,19,23;23,14,16,17,18,19,24;24,6,10,12,13,16,25;25,7,10,12,13,16,26;26,10,13,14,18,19,27;27,4,11,12,15,17,28;28,0,14,16,17,18,19',
(30,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29',
(30,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,26;26,27;27,28;28,29;29,0',
(30,3) : '0,1,26;1,2,27;2,3,24;3,4,25;4,5,22;5,6,23;6,7,20;7,8,21;8,9,28;9,10,29;10,7,11;11,6,12;12,5,13;13,4,14;14,3,15;15,2,16;16,1,17;17,0,18;18,9,19;19,8,20;20,11,21;21,17,22;22,15,23;23,14,24;24,16,25;25,12,26;26,13,27;27,10,28;28,18,29;29,0,19',
(30,4) : '0,1,26,27;1,2,26,27;2,3,24,25;3,4,24,25;4,5,22,23;5,6,22,23;6,7,20,21;7,8,20,21;8,9,28,29;9,10,28,29;10,6,7,11;11,6,7,12;12,4,5,13;13,4,5,14;14,2,3,15;15,2,3,16;16,0,1,17;17,0,1,18;18,8,9,19;19,8,9,20;20,11,17,21;21,11,17,22;22,14,15,23;23,14,15,24;24,12,16,25;25,12,16,26;26,10,13,27;27,10,13,28;28,18,19,29;29,0,18,19',
(30,5) : '0,1,20,26,27;1,2,21,26,27;2,3,18,24,25;3,4,24,25,29;4,5,9,22,23;5,6,8,22,23;6,7,20,21,26;7,8,20,21,27;8,9,24,28,29;9,10,25,28,29;10,5,6,7,11;11,4,6,7,12;12,4,5,7,13;13,4,5,6,14;14,1,2,3,15;15,0,2,3,16;16,0,1,3,17;17,0,1,2,18;18,8,9,19,22;19,8,9,20,23;20,11,15,17,21;21,11,14,17,22;22,11,14,15,23;23,14,15,17,24;24,12,13,16,25;25,10,12,16,26;26,10,13,19,27;27,10,12,13,28;28,16,18,19,29;29,0,18,19,28',
(30,6) : '0,1,20,26,27,29;1,2,20,21,26,27;2,3,18,24,25,28;3,4,24,25,26,29;4,5,9,21,22,23;5,6,8,9,22,23;6,7,20,21,26,27;7,8,20,21,22,27;8,9,24,25,28,29;9,10,24,25,28,29;10,4,5,6,7,11;11,4,6,7,10,12;12,2,4,5,7,13;13,4,5,6,7,14;14,0,1,2,3,15;15,0,2,3,5,16;16,0,1,3,8,17;17,0,1,2,3,18;18,8,9,19,22,23;19,1,8,9,20,23;20,11,12,15,17,21;21,11,14,15,17,22;22,11,14,15,18,23;23,14,15,17,19,24;24,6,12,13,16,25;25,10,12,13,16,26;26,10,13,16,19,27;27,10,11,12,13,28;28,16,17,18,19,29;29,0,14,18,19,28',
(30,7) : '0,1,20,24,26,27,29;1,2,20,21,25,26,27;2,3,18,24,25,28,29;3,4,24,25,26,28,29;4,5,9,20,21,22,23;5,6,8,9,21,22,23;6,7,20,21,22,26,27;7,8,20,21,22,23,27;8,9,24,25,26,28,29;9,10,24,25,27,28,29;10,4,5,6,7,11,13;11,4,6,7,10,12,15;12,2,3,4,5,7,13;13,2,4,5,6,7,14;14,0,1,2,3,5,15;15,0,2,3,4,5,16;16,0,1,3,8,9,17;17,0,1,2,3,8,18;18,1,8,9,19,22,23;19,0,1,8,9,20,23;20,10,11,12,15,17,21;21,11,14,15,17,19,22;22,11,14,15,17,18,23;23,11,14,15,17,19,24;24,6,7,12,13,16,25;25,6,10,12,13,16,26;26,10,12,13,16,19,27;27,10,11,12,13,18,28;28,14,16,17,18,19,29;29,0,14,16,18,19,28',
(31,1) : '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30',
(31,2) : '0,1;1,2;2,3;3,4;4,5;5,6;6,7;7,8;8,9;9,10;10,11;11,12;12,13;13,14;14,15;15,16;16,17;17,18;18,19;19,20;20,21;21,22;22,23;23,24;24,25;25,26;26,27;27,28;28,29;29,30;30,0',
(31,3) : '0,1,27;1,2,20;2,3,25;3,4,26;4,5,23;5,6,9;6,7,21;7,8,22;8,9,28;9,10,29;10,6,11;11,10,12;12,4,13;13,7,14;14,2,15;15,5,16;16,0,17;17,3,18;18,8,19;19,1,20;20,17,21;21,15,22;22,19,23;23,14,24;24,16,25;25,12,26;26,13,27;27,11,28;28,29,30;29,18,30;30,0,24',
(31,4) : '0,1,26,27;1,2,20,21;2,3,24,25;3,4,26,27;4,5,22,23;5,6,8,9;6,7,20,21;7,8,22,23;8,9,28,30;9,10,28,29;10,6,7,11;11,10,12,13;12,4,5,13;13,6,7,14;14,2,3,15;15,4,5,16;16,0,1,17;17,2,3,18;18,8,9,19;19,0,1,20;20,11,17,21;21,14,15,22;22,15,19,23;23,14,18,24;24,12,16,25;25,12,16,26;26,10,13,27;27,11,17,28;28,25,29,30;29,18,19,30;30,0,24,29',
(31,5) : '0,1,20,26,27;1,2,20,21,27;2,3,24,25,26;3,4,25,26,27;4,5,9,22,23;5,6,8,9,23;6,7,20,21,22;7,8,21,22,23;8,9,28,29,30;9,10,28,29,30;10,6,7,11,13;11,6,10,12,13;12,4,5,7,13;13,4,6,7,14;14,2,3,5,15;15,2,4,5,16;16,0,1,3,17;17,0,2,3,18;18,1,8,9,19;19,0,1,8,20;20,11,15,17,21;21,14,15,17,22;22,14,15,19,23;23,14,18,19,24;24,10,12,16,25;25,11,12,16,26;26,10,13,18,27;27,11,12,17,28;28,24,25,29,30;29,16,18,19,30;30,0,24,28,29',
(31,6) : '0,1,20,21,26,27;1,2,20,21,22,27;2,3,24,25,26,28;3,4,25,26,27,29;4,5,8,9,22,23;5,1,6,8,9,23;6,7,20,21,22,27;7,8,20,21,22,23;8,9,24,28,29,30;9,10,25,28,29,30;10,4,6,7,11,13;11,6,7,10,12,13;12,4,5,6,7,13;13,4,6,7,11,14;14,0,2,3,5,15;15,2,3,4,5,16;16,0,1,2,3,17;17,0,2,3,5,18;18,1,8,9,19,23;19,0,1,8,9,20;20,11,12,15,17,21;21,14,15,17,19,22;22,14,15,17,19,23;23,14,18,19,24,30;24,10,12,13,16,25;25,10,11,12,16,26;26,10,13,16,18,27;27,11,12,15,17,28;28,18,24,25,29,30;29,14,16,18,19,30;30,0,24,26,28,29',
(31,7) : '0,1,20,21,22,26,27;1,2,20,21,22,26,27;2,3,24,25,26,28,29;3,4,25,26,27,28,29;4,5,8,9,20,22,23;5,1,6,8,9,21,23;6,7,20,21,22,23,27;7,8,9,20,21,22,23;8,9,24,25,28,29,30;9,10,24,25,28,29,30;10,4,6,7,11,12,13;11,6,7,10,12,13,15;12,2,4,5,6,7,13;13,4,5,6,7,11,14;14,0,2,3,4,5,15;15,2,3,4,5,7,16;16,0,1,2,3,8,17;17,0,1,2,3,5,18;18,0,1,8,9,19,23;19,0,1,3,8,9,20;20,10,11,12,15,17,21;21,14,15,17,19,22,30;22,14,15,17,18,19,23;23,14,16,18,19,24,30;24,6,10,12,13,16,25;25,10,11,12,13,16,26;26,10,11,13,16,18,27;27,11,12,14,15,17,28;28,18,19,24,25,29,30;29,14,16,17,18,19,30;30,0,24,26,27,28,29' }



def do_cmd(s):
	print s
	sys.stdout.flush()
	os.system(s)

def run_experiment(nodes, deg, desc, cmd, policy, rebalance=None):
	global wait
	global monitor_time
	
	if rebalance is None:
		if policy == 'global':
			rebalance = True
		else:
			assert policy == 'local'
			rebalance = False

	print 'Experiment', 'nodes:', nodes, 'deg:', deg, 'desc:', desc, 'cmd:', cmd, policy, 'rebalance:', rebalance

	if rebalance:

		do_cmd('rm -f .kill')
		do_cmd('rm -rf .hybrid')

		opts = ''
		if not wait is None:
			opts += '--wait %d ' % wait
		if not monitor_time is None:
			opts += '--monitor %f ' % monitor_time
		do_cmd('${MERCURIUM}/../rebalance/rebalance.py ' + opts + '10000 > rebalance-out-%d-%d.txt &' % (nodes,deg))
		time.sleep(1)

	# Run experiment
	s = 'NANOS6_CLUSTER_SPLIT="%s" ' % desc
	s += 'NANOS6_CLUSTER_HYBRID_POLICY="%s" ' % policy
	s += 'MV2_ENABLE_AFFINITY=0 '
	s += 'mpirun -np %d %s ' % (nodes*deg, cmd)
	do_cmd(s)

	if rebalance:
		do_cmd('touch .kill')



# Run experiments
def main(argv):

	global wait
	global min_per_node
	global max_per_node
	global monitor_time
	os.environ['NANOS6_ENABLE_DLB'] = '1'

	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'wait=', 'min-per-node=', 'max-per-node', 'monitor='] )

	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--wait':
			wait = int(a)
		elif o == '--min-per-node':
			min_per_node = int(a)
		elif o == '--max-per-node':
			max_per_node = int(a)
		elif o == '--monitor':
			monitor_time = float(a)

	assert len(args) >= 2
	num_nodes = int(args[0])
	cmd = ' '.join(args[1:])

	do_cmd('pwd')

	for (nodes,deg), desc in sorted(splits.items()):
		if nodes == num_nodes:
			if deg >= min_per_node and deg <= max_per_node:

				for policy in ['global', 'local']:
					# Clean DLB
					do_cmd('mpirun -np %d dlb_shm -d' % num_nodes)

					run_experiment(nodes, deg, desc, cmd)

					time.sleep(1)
					while os.path.exists('.kill'):
						time.sleep(1)

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
