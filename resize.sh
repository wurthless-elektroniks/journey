#!/bin/bash

ffmpeg -i gamemap.bmp -s 896x544 -sws_flags neighbor gamemap_big.png
ffmpeg -i lakemap.bmp -s 896x544 -sws_flags neighbor lakemap_big.png
