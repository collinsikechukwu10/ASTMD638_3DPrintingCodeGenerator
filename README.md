# GCode generator for ASTM D638 Tensile Testing samples.

This generates the gcode of an ASTM D638 sample to be used for tensile testing.
The printed samples are tested to determine examine how microstructure parameters affect the strength of 3d printed builds.

The following parameters can be customized for the sample:
- [x] layer thickness
- [x] layer width
- [x] layer length
- [x] layer raster spacing
- [x] filament size
- [x] sample midsection width
- [x] sample midsection height
- [x] printer type
- [x] nozzle temperature
- [x] bed temperature
- [x] nozzle diameter
- [x] add adhesion
- [x] adhesion layer width
- [x] adhesion layer thickness
- [x] initialization speed
- [x] print speed
- [x] start point (x)
- [x] start point (y)
- [x] sample height


### Running the app

Before running, make sure you have a python environment.

- install the required libraries
```bash
python -m pip install -r requirements.txt
```

- Run the command below to start the application
```bash
python start_app.py 
```
- The application runs on port `7680` by default. Open your browser and navigate to `http://localhost:7680` to access the application.

