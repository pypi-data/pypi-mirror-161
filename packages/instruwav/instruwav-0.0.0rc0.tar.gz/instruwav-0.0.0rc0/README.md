# Instruwav

This library lets you to form notes of different instruments from just one base note and play them

## Run

Pianoputer only works in python3 so make sure you are using python3. You can download it from <https://pypi.org>

After a few minutes finished downloading, you can install it using pip

``` bash
cd (Downloadpath)
pip install (Downloadfilename)
```
# Helps
## Changing the sound file

You can provide your own sound file by moving or copy your file into the .\instruwav\audio_files\, then configure in python.

For example:
```python
import instruwav
generator=instruwav.instrusound.engine()
# Replace filename with your file's name
generator.config("add","filename.wav")        # Add the file to the list
generator.config("audio_file","filename.wav") # switch to filename.wav as the default file
```
All changes are only made in this single program. If you want to permanetly change to all programs, adjust the _config.json file.

It looks like this:
```json
{
    "DISABLE_OUTPUT":false,
    "DEFAULT_INSTRUMENTS":
    [
        "violin_c4.wav",
        "piano_c4.wav",
        "bowl_c6.wav"
    ],
    "BASESOUND_FOLDER":".\\audio_files\\",
    "_PATH":{
        "violin":"violin_c4.wav",
        "piano":"piano_c4.wav",
        "bell":"bowl_c6.wav"
    },
    "VERSION":"2.0.2"
}
```
Add your filename to it
```json
{
    "DISABLE_OUTPUT":false,
    "DEFAULT_INSTRUMENTS":
    [
        "violin_c4.wav",
        "piano_c4.wav",
        "bowl_c6.wav",
        "filename.wav"
    ],
    "BASESOUND_FOLDER":".\\audio_files\\",
    "_PATH":{
        "violin":"violin_c4.wav",
        "piano":"piano_c4.wav",
        "bell":"bowl_c6.wav",
        "nickname":"filename.wav"
    },
    "VERSION":"2.0.2"
}
```
The file will permanetly be added in the list of available audios, and run the python program:
```python
import instruwav
generator=instruwav.instrusound.engine()
generator.config("audio_file","filename.wav")
```

## Changing the keyboard layout

Note that the default keyboard configuration (stored in file `keyboards/qwerty_piano.txt`) is for the most commonly used QWERTY keyboards. You can change the configuration so that it matches your keyboard, for instance using the alternative `keyboards/azerty_typewriter.txt`:

## Disable output
To stop the "Thank you..." change the config.json:
```yaml
DIABLE_OUTPUT: true
```


## Changelog
See changelog in the folder