# E-Media
Graphical application for extracting, and displaying PNG images metadata, calculating and displaying fft. Images can
also be anonymized and encrypted using RSA algorithm.

![image](https://user-images.githubusercontent.com/62207289/178807543-01301941-6e50-4708-ba01-bd583730020b.png)

## Supported chunks
Every valid chunk will be parsed but not every chunk's data is being parsed. 
#### Supported chunks for data parsing:
* `IHDR`: image header
* `PLTE`: palette: a list of colors
* `IDAT`: image data
* `IEND`: end of file
* `sBIT`: significant bits: color-accuracy of the source data
* `gAMA`: image gamma
* `sRGB`: standard RGB colour space
* `pHYs`: physical pixel dimensions
* `tEXt`: textual data
* `iTXt`: international textual data
* `zTXt`: compressed textual data
* `iCCP`: embedded ICC profile
* `tIME`: last modification time
* `bKGD`: background colour
* `cHRM`: primary chromaticities and white point
* `hIST`: image histogram
* `sPLT`: suggested palette
* `eXIf`: exchangeable image file format data

## RSA
The app uses 2 diffrent RSA implementations:  
  1. Custom one implemented by us  
  2. Using PyCryptodome library (currently only key generation works)

## Getting Started
1. Clone repo
```
git clone https://github.com/KacperSynator/E-media.git
```

2. Setup environment
```
# using pip
pip install -r requirements.txt

# using Conda
conda create --name <env_name> --file requirements.txt
```

3. Run main.py
```
python main.py
```

## Authors 

Contributors names and contact info
* Kacper Synator  (https://github.com/KacperSynator)
* Paweł Potoczek (https://github.com/PPotoczek)
