# SBOM analyzer script

## Usage
```
$ python3 sbom.py PATH_TO_FOLDER
```

## Considerations

If no package-lock.json is present, we don't know for sure what the resolved version will eventually be.

De-duplicating dependencies gets harder because of this, so you might see both react@19.3.0 and react@^19.3.0, or even react@18||19 in the result, repeating react several times.
