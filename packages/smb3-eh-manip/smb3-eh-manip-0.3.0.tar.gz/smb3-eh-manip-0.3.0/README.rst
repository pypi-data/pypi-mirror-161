smb3-eh-manip
==============

.. image:: https://badge.fury.io/py/smb3-eh-manip.png
    :target: https://badge.fury.io/py/smb3-eh-manip

Ingest video data from a capture card to render a smb3 eh TAS

Installation
------------

Note: Ensure python3 is installed

Install this package and dependencies via pip::

    pip install smb3-eh-manip

Running
-------

Note: You must configure+calibrate before running!

From a cmd prompt, powershell, or terminal with working python3::

    python -m smb3_eh_manip.main

config.ini
----------

In config.ini you'll note several configurable values. These are values
that work for *my* config, with an avermedia capture card. The images and values
might be different, especially for different capture cards.

`show_capture_video` This is an optional debugging property to help identify
your video capture source index. It shows what images are matched, and should
be disabled after configuration to reduce computational load.

`video_capture_source` This is the index of the video card in your system.
To configure this, ensure `show_capture_video` is set to true, run the tool,
and see if the capture window is correct. You should see your nes output.
Note: this can be the path to a video, if you'd like :shrug:

`write_capture_video` Writes the capture card video to a file, by default,
capture.avi in the current working directory. This can be used to get trigger
images directly from the capture card in a complementary way to how the tool
works.

`enable_video_player` Enabled/disables a TAS EH video playing directly from
this tool upon seeing the trigger frame.

`enable_fceux_tas_start` Enable/disables sending fceux the 'pause' keystroke
when the trigger frame has been detected.

`latency_frames` We need to measure the perceived latency of what frame this
tool thinks we are playing against the monitor the player is perceiving. We
need to offset the beginning of TAS playback that amount.

Example: it takes ~36ms for the avermedia 4k capture card to show frames on
screen, 30.66ms for that to get to this tool and render a video frame. That's
[conveniently ;)] 66.6ms, or 4 nes frames. So we should begin the playback 4
frames in.

`computer` Select what the tool is comparing against. Initially this should be
`calibration` until the `latency_frames` are identified. The value `eh` is when
attempting runs. `twoone` is experimental but should aid in practice.

Calibration
-----------

Players can run the smb3 practice rom which includes in-level frame timer that
increments by one each frame. With `computer` set to `calibration`, run the
tool, run the game, and enter 1-1. The second window running the video should
appear with some perceived latency. Take a picture with the fastest camera
setting, and compare the frame counts.

Example: After starting 1-1, I took about a second to take a picture. The ingame
timer on my tv was 55, and the ingame timer on the TAS was 50. Thus, my
`latency_frames` should be set to `5` in `config.ini`.

Note: I am not convinced this is consistent when running+recording with OBS.
More testing is required. This is extremely important to be consistent, otherwise
this tool is significantly less helpful.

Usage
-----

Set `computer` to `eh` and optionally set `show_capture_video` to `false`.
Run the app. Ensure it is synced with the TAS.

Revel in victory.

TODO
----

* Develop practice methodology (starting from 2-1, validate if runner ended on correct frame)

Development
-----------

Run test suite to ensure everything works::

    make test

Release
-------

To publish your plugin to pypi, sdist and wheels are registered, created and uploaded with::

    make release-test

For test. After ensuring the package works, run the prod target and win::

    make release-prod

License
-------

Copyright (c) 2021 Jon Robison

See LICENSE for details
