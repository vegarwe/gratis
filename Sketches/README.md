% RePaper Code

# Code

This project officially supports the Arduino-based platform. The Ti LaunchPad suppor that is 
available in the original [repaper/gratis]((https://github.com/repaper/gratis) repository 
has been commented out and is completely untested.

The examples have been verified on Arduino Leonardo (R3) and Arduino Uno (R2) boards using
the 1.0.5 version of the IDE.

## Source Code Repository

The source code to the Repaper software is hosted by
[GitHub](https://github.com/repaper/gratis). The [example programs](#example-programs) are in
[Sketches](https://github.com/repaper/gratis/tree/master/Sketches) directory.


## Development Tools

This project officially supports the Arduino-based platform.

### Arduino

The [Arduino web site](http://www.arduino.cc) has download links for
Windows, Mac OS/X and other operating systems.

Note: [Java](http://java.com) is necessary to run the GUI, but it is
possible to install a command line only version.

# Example Programs

**IMPORTANT NOTES for COG V2**

1. The programs below only support the COG V2 using the `EPD2` library.
2. The COG V2 does not use PWM - the pin is used as chip select for the
   onboard SPI-NOR flash instead.

---

The example programs support both the Arduino (Atmel AVR) and the
Energia (TI LaunchPad with MSP430G2553).

The files include some conditional code to switch between the two platforms.
This code does the following:

1. Convert PROGMEM types to normal types for the TI MCU since it has a unified
   address space.

2. Adjust the I/O pins definitions and ADC reference for differences between
   the two platforms.

## Demo Sketch

> Link to the [demo source](https://github.com/repaper/gratis/tree/master/Sketches/demo).

This example first clears the screen, then toggles between two images.
Needs the serial port (9600 8N1) connected and displays the version,
temperature and compensation values on each cycle.

This is built upon the EPD API in the libraries folder and shows how
to use the API to display images from the MCU FLASH.  Only a few images
are possible to be stored since the on-chip FLASH is limited.

Not: This will not run on the TI LaunchPad with a 2.7" display as the
resulting code exceeds the 16kB memory size, only 1.44" and 2.0" will
fit on this platform.

## Command Sketch

> Link to the [command source](https://github.com/repaper/gratis/tree/master/Sketches/command).

A command-line example that accepts single character command from the
serial port (9600 8N1).  Functions include XBM upload to the SPI FLASH
chip on the EPD evaluation board, display image from this FLASH and
several other functions.

Use the `h` command on the serial port (9600 8N1) to obtain a list of
commands.  Some of the commands are shown like `e<ss>` this *<ss>*
represents a two digit FLASH sector number in the range *00..ff* (a
total of 256 sectors).  The 1.44" and 2.0" display images take one sector
but the 2.7" displays take two adjacent sectors.

When using the serial monitor on Arduino/Energia IDE any command that
take a hex number as parameter needs a `<space>` character after it, as
the **Send** button will not automatically add a CR/LF.  For single
letter commands like the `t` temperature sensor read just type the
character and click **Send**.

The 4 stage display cycle is split into two separate commands. The `r`
command removes an image and the `i` command displays an image.
e.g. if the current image was from sector 30 and you wanted to change
to sector 43 then type `r30<space>i43<space>` into the serial monitor
and click **Send**.

The upload command `u` need a terminal emulator with ASCII upload
capability or the ability to respond to a paste of the entire contents
of an XBM file.  Also note that the `u` command does not erase the
sector before uploading.  To use the upload to upload an XBM into
sector 3b for example type `u3b<space>` then start the ASCII upload or
paste the contents of the XBM file into the terminal window on upload
completion an image size message is displayed.

The image stored is compatible with the flash_loader sketch as
described below and that program can be used to cycle through a set of
images uploaded by this program.


## Flash Loader Sketch

> Link to the [flash loader source](https://github.com/repaper/gratis/tree/master/Sketches/flash_loader).

this program has two modes of operation:

1. Copy a #included image to the FLASH chip on the eval board.  define
   the image name and the destination sector.  After programming the
   image will be displayed

2. Display a sequence of images from the FLASH chip on the eval board.
   A list of sector numbers an millisecod delay times defined by the
   `DISPLAY_LIST` macro to enable this mode.  In this mode the flash
   programming does not occur.  The images are stored in the same
   format as the command program above, so any images uploaded by it
   can be displayed by this program


## Libraries

> Link to the [libraries source](https://github.com/repaper/gratis/tree/master/Sketches/libraries).
(copy all of these to you local libraries folder)

* **Images** - Sample XBM files.  The demo program includes two of
  these directly.  The Command program can use these files for its
  upload command.
* **FLASH** - Driver for the SPI FLASH chip on the EPD eval board.
* **EPD2** - E-Ink Panel driver (COG V2) *experimental*.
* **LM75** - Temperature sensor driver.


# Connection of EPD board to Arduino

> See: Using the Extension board with Ardunio ([HTML](http://learn.adafruit.com/repaper-eink-development-board), [PDF](http://learn.adafruit.com/downloads/pdf/repaper-eink-development-board.pdf)) by [Adafruit](http://www.adafruit.com)

The board needs a cable to connect to the Arduino.  The EPD boards
are dual voltage and include a 3.3V regulator for the EPD panel and
level converters and so it can directly connect to the 5 Volt
Arduinos.  Note that the board uses the SPI interface, which is on
different pins depending on the particular Arduino version.  The
[Extension Board](http://repaper.org/doc/extension_board.html) has a
table of [Pin Assignments](http://repaper.org/doc/extension_board.html#pin-assignment)
for some Arduinos; the main difference is the three SPI pin (SI, SO,
CLK) location which vary between the various Arduinos an can be on
dedicated pins, overlapped with Digital I/O or shared with the ICSP
header.

<table>
  <tr><td colspan="2">Arduino Leonardo</td><td colspan="2">Arduino Uno</td><td colspan="2">Display</td></tr>
  <tr><td>GND</td><td>GND</td>     <td>GND</td><td>GND</td>      <td>1</td><td>GND</td></tr>
  <tr><td>3V3</td><td>3V3</td>     <td>3V3</td><td>3V3</td>      <td>2</td><td>3V3</td></tr>
  <tr><td>ICSP-3</td><td>SCK</td>  <td>ICSP-3</td><td>SCK</td>   <td>3</td><td>SCK</td></tr>
  <tr><td>ICSP-4</td><td>MOSI</td> <td>ICSP-4</td><td>MOSI</td>  <td>4</td><td>MOSI</td></tr>
  <tr><td>ICSP-1</td><td>MISO</td> <td>ICSP-1</td><td>MISO</td>  <td>5</td><td>MISO</td></tr>
  <tr><td>8</td><td>GPIO</td>      <td>8</td><td>GPIO</td>       <td>6</td><td>SSEL</td></tr>
  <tr><td>7</td><td>GPIO</td>      <td>7</td><td>GPIO</td>       <td>7</td><td>Busy</td></tr>
  <tr><td>10</td><td>GPIO</td>     <td>10</td><td>GPIO</td>      <td>8</td><td>Border Ctrl</td></tr>
  <tr><td>SCL/3</td><td>SCL</td>   <td>SCL/A5</td><td>SCL</td>   <td>9</td><td>SCL</td></tr>
  <tr><td>SDA/2</td><td>SDA</td>   <td>SCL/A4</td><td>SDA</td>   <td>10</td><td>SDA</td></tr>
  <tr><td>9</td><td>GPIO</td>      <td>9</td><td>GPIO</td>       <td>11</td><td>CS Flash</td></tr>
  <tr><td>6</td><td>GPIO</td>      <td>6</td><td>GPIO</td>       <td>12</td><td>Reset</td></tr>
  <tr><td>5</td><td>GPIO</td>      <td>5</td><td>GPIO</td>       <td>13</td><td>Pwr</td></tr>
  <tr><td>4</td><td>GPIO</td>      <td>4</td><td>GPIO</td>       <td>14</td><td>Discharge</td></tr>
</table>


