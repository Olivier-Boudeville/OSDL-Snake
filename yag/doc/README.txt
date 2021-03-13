
=============================
Managing a new gallery HOW-TO
=============================

Typical use:

 1. cd OSDL-Snake/yag
 2. cp yag-osdl.conf.sample yag-osdl.conf
 3. edit yag-osdl.conf (notably in order to specify the content_directory of interest)
 4. ./run-yag-osdl.sh (for a first inspection)
 5. ./annotate-images.sh <the content directory to annotate> (at least to specify comments and per-element themes)
 6. ./run-yag-osdl.sh
 7. edit yag-overall-themes.thm to define the hierarchy between the previously defined themes
 8. ./run-yag-osdl.sh
 9. copy the result at the root of your webserver of choice


Themes are hierarchically organised. For example:

My Theme A: My Theme B

makes 'My Theme B' a subtheme of 'My Theme A'.

One can also specify the relationships between themes in a standalone file named 'yag-overall-themes.thm', placed at the root of the content (instead of specifying them in per-content theme files).
