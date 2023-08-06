# Drone operator exploitation number

NLDgy5tmnqlc0ix3-r9c

# ESC firmware

https://github.com/mathiasvr/bluejay

# To be tested 

https://www.thingiverse.com/thing:4867607

## Insta360 gyro data stabilizer

https://github.com/ElvinC/gyroflow

## 3D CLUT (.cube)

### Blender integration

Edit `/usr/share/blender/3.0/datafiles/colormanagement/config.ocio`

Add

```!yaml
  - !<ColorSpace>
    name: Insta360 Log
    family:
    equalitygroup:
    bitdepth: 32f
    description: BetaFPV SMO 4K - Insta360 ONE R
    isdata: false
    allocation: lg2
    to_reference: !<GroupTransform>
      children:
        - !<FileTransform> {src: /home/fab/Documents/Insta360/ONE-R-LUT/1-INCH.CUBE, interpolation: best}
        - !<ExponentTransform> {value: [2.4, 2.4, 2.4, 1.0]}
    from_reference: !<GroupTransform>
      children:
        - !<ExponentTransform> {value: [2.4, 2.4, 2.4, 1.0]}
        - !<FileTransform> {src:  /home/fab/Documents/Insta360/ONE-R-LUT/1-INCH.CUBE, interpolation: best, direction: inverse}
```

### Other

```

ffmpeg -vf:lut3d=<file>:interp=tetrahedral

-vf lut3d=/home/fab/Documents/Insta360/ONE-R-LUT/1-INCH.CUBE:interp=tetrahedral
```

https://kevinmartinjose.com/category/programming/

```python
# pip install colour-science
import colour

lut = colour.read_LUT('/home/fab/Documents/Insta360/ONE-R-LUT/4K-WIDE-ANGLE.CUBE')
colour.algebra.table_interpolation_tetrahedral([[0.5,0.5,0.5]], lut.table)
```

# Drones in a Nutshell

## goals

- professional
  - carry weight (small packages, tools, pro camera, ...)
  - watch
    - change detection
    - measurements
    - item detection
  - execute (repeatead or repeatable action)
  - detect
	  
- acrobatics / freestyle <-- around 3"
- racing <-- around 4", reference for many
- have fun / test (beginners and newcomers)

## Criterion

### Size

- XL(TODO: find name)
- 4 inc
- 3 inch
- mini / micro

### Safety

- bare / no protection
- Duct alike
- dome / other type of cover

### Image transmission

- line of sight
- analog
	- 5.8 GHz
- digital
	- DJI
	- HD-Zero/Byte frost/Bite skark/...
	- OpenHD
	- ... (recent tech)
- WiFi / Provided app


### Other considerations (advanced usage / not required)

- Long range capabilities / radio
- Flight controller capabilities
- Motors performances
- Batteries

