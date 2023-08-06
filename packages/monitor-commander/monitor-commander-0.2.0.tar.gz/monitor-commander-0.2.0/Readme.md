# monitor-commander

monitor-commander controls your monitors using [DDC/CI](https://en.wikipedia.org/wiki/Display_Data_Channel).

Use cases:
 - Virtual KVM switch (switch monitors inputs between conputers)
 - Auto monitor settings if you often switch between desks

## Installation

### Supported platforms

You will need a linux distribution with python3.8 or above.
If not possible, check the alternatives section bellow.

### ddcutil

First, you will need to install and configure ddcutil. Check the documentation on [install](https://www.ddcutil.com/install/) and [configuration](https://www.ddcutil.com/config/).

To test your installation, run:

```
$ sudo ddcutil detect
```
It must report some connected displays For example:
```
Display 1
   I2C bus:             /dev/i2c-0
   EDID synopsis:
      Mfg id:           DEL
      Model:            DELL P2411H
      Serial number:    F8NDP11G119U
      Manufacture year: 2011
      EDID version:     1.3
   VCP version:         2.1
```

### Dependencies

```
$ sudo apt install python3-argcomplete python3-typedload python3-yaml
```

### monitor-commander

Copy the [monitor-commander script](monitor-commander/monitor-commander.py) to `/usr/local/bin/monitor-commander` and make it executable.
```
$ sudo chmod +x /usr/local/bin/monitor-commander
```

## Usage as a KVM Switch

The concept of the Virtual KVM Switch is to use the different inputs of monitors to plug your different computers.
You can the use the presence of a device like your keyboard or mouse to trigger the switch of your monitor(s).
This allows you to use much cheaper USB switch instead of a full KVM switch.

### Check Monitor support

First step is to check your monitor capabilities. For this VCP feature 60 (Input source is used)
```
$ sudo ddcutil -d 1 capabilities
...
Feature: 60 (Input Source)
   Values:
      0f: DisplayPort-1
      11: HDMI-1
...
```
Here the monitor has two inputs. Let's test that you can switch them.
```
$ sudo ddcutil -d 1 setvcp 60 0x0f
$ sudo ddcutil -d 1 setvcp 60 0x11
```

If the monitor is correctly switching, you can continue to next step.

If you have multiple monitors, repeat by increasing the value of the `-d` parameter.

### Write configuration file

Now you can start to write the configuration file.
In this exemple, there are two monitors (named left and right) connected to two computers (laptop and dektop).

First let's identify the monitors:
```
$ sudo monitor-commander monitors
display: 1
bus: 0
manufacturer: 'DEL'
model: 'DELL P2411H'
serial_number: 'F8NDP11G119U'
year: 2011
edid_version: '1.3'
vcp_version: '2.1'
=> No match in configured monitors

display: 2
bus: 1
manufacturer: 'ACR'
model: 'Acer X243W'
serial_number: 'LAG040064310'
year: 2007
edid_version: '1.3'
vcp_version: '2.1'
=> No match in configured monitors
```

You can now write the config file `/usr/local/etc/monitor-commander.yml`:
```yml
monitors:
  - name: left
    selector:
      serial_number: LAG040064310
    presets:
      desktop:
        60: "0x11"
      laptop:
        60: "0x0f"
  - name: right
    selector:
      serial_number: LAG040064310
    presets:
      desktop:
        60: "0x11"
      laptop:
        60: "0x0f"
```
Note: One the laptop, replace `default: desktop` by `default: laptop`.

You should now be able to switch your monitors using
```
$ sudo monitor-commander set laptop
$ sudo monitor-commander set desktop
```

### Udev rule

The last step is to automate this when the switch

#### Identify device

Now you need to identify the properties of the device you will use to do trigger the switch.
Run the following command, plug the device and kill the command with ctrl+C.
The output is pretty verbose but you care only about the first block.
```
$ sudo udevadm monitor -p -s usb/usb_device
monitor will print the received events for:
UDEV - the event which udev sends out after rule processing
KERNEL - the kernel uevent

KERNEL[6994.988641] add      /devices/pci0000:00/0000:00:14.0/usb2/2-3 (usb)
ACTION=add
DEVPATH=/devices/pci0000:00/0000:00:14.0/usb2/2-3
SUBSYSTEM=usb
DEVNAME=/dev/bus/usb/002/003
DEVTYPE=usb_device
PRODUCT=3a2/936/6354
TYPE=9/0/3
BUSNUM=002
DEVNUM=003
SEQNUM=512
MAJOR=189
MINOR=134

```

#### Write udev rule

Most likelly, you want to identify the device by the PRODUCT string. This is normally unique per usb device model.
In case you have several identical devices, you can use DEVPATH instead. Just replace PRODUCT and the associated value by DEVPATH bellow.

Create file `/etc/udev/rules.d/10-monitor-commander.rules`
```
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ENV{PRODUCT}=="3a2/936/6354", RUN+="/usr/bin/systemd-run --collect -u monitor-commander-udev /usr/local/bin/monitor-commander set desktop"
```
Of course replace `desktop` at the end by the name of the preset in the config file.

Congratulation, you should be all set.

#### Debug

In case of issues, you can use the command bellow
```
$ sudo journalctl -fu systemd-udevd --grep monitor-commander
$ sudo journalctl -fu monitor-commander-udev
```

## Usage as a generic monitor configuration

Monitors are often default to settings with very high brightness and too much blue.
If your company uses shared desk, setting screen every morning can quickly become a burden.

```yml
monitors:
  - name: U3011
    selector:
      model: DELL U3011 # Limit to known screen models
    presets:
      color:
        10: 40 # Brightness
        16: 99 # Video gain: Red
        18: 99 # Video gain: Green
        "1A": 90 # Video gain: Blue
        12: 75 # Contrast
```
To get the values, you can set them manually on your screen and use `sudo ddcutil getvcp ALL` to display the corresponding codes.

```
$ sudo monitor-commander set color
```
## Alternatives

[display-switch](https://github.com/haimgel/display-switch) works for simple virtual KVM switch use cases. Advantage is that it is cross platform and the config files are simpler (but more limited).

For manual scripting, you can use [ddcutil (Linux)](https://www.ddcutil.com/), [ddcctl (OSX)](https://github.com/kfix/ddcctl), [winddcutil (Windows)](https://github.com/scottaxcell/winddcutil).
