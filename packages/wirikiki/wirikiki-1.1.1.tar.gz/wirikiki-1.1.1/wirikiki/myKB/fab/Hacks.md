# Hacks

## Share bluetooth on multiboot

```
cd /home/fab/media/Windows/Windows/System32/config
chntpw -e SYSTEM
```
In the shell:
```
> cd ControlSet001\Services\BTHPORT\Parameters\Keys
> ls
Node has 1 subkeys and 0 values
  key name
  <001a7dda7112>

> cd 001a7dda7112
> hex f4bcda8f0d4f
```
Copy the key, and then copy it on the linux setup before restarting bluetooth:
```
sudo vi /var/lib/bluetooth/00:1A:7D:DA:71:12/F4:BC:DA:8F:0D:4F/info
```

## Windows product KEY

VK7JG-NPHTM-C97JM-9MPGT-3V66T