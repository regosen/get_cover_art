# get_cover_art

### THE PROBLEM
Missing cover art for large imported music libraries.  

### EXISTING SOLUTIONS

1. Apple's Music App (and its predecessor iTunes) has a "Get Album Artwork" feature, but it isn't reliable and doesn't actually embed cover art into your audio files.  That means if you move your music library elsewhere, you'll be missing all your album artwork.

2. Metadata utilities like Metadatics are great (and cheap if not free), but they can require a lot of manual interaction to go through each album and select artwork from search results.  This can be forbidding for large libraries of thousands of albums.

### THIS SOLUTION
This Python package will batch-update your entire library without manual interaction for each album.

It uses Apple Music's artwork, which is already standardized and high-quality.  It also embeds the artwork directly into your audio files, so that it's independent of your player.

## Supported formats (so far)
- MP3
- MP4 (.m4a)
- FLAC
- Ogg Vorbis
- Opus

## Requirements
- Python 3.5 or greater
- Python packages: [mutagen](https://pypi.org/project/mutagen/)

### Installation on MacOS using Homebrew

```
brew install python
python3 -m pip install mutagen
python3 -m pip install get_cover_art
```
And then to upgrade existing installations:
```
python3 -m pip install --upgrade get_cover_art
```

## Usage

### From the Command Line
```
python -m get_cover_art [--path=<path_to_audio_file_or_folder>] [--test] [--other options]

  --path PATH           audio file, or folder of audio files (recursive)
  --dest DEST           destination of artwork
  --test, --no_embed    scan and download only, don't embed artwork
  --no_download         embed only previously-downloaded artwork
  --inline              put artwork in same folders as audio files
  --force               overwrite existing artwork
  --verbose             print verbose logging
  --throttle            wait X seconds between downloads
  --skip_artists SKIP_ARTISTS
                        file containing artists to skip
  --skip_albums SKIP_ALBUMS
                        file containing albums to skip
  --skip_artwork SKIP_ARTWORK
                        file containing destination art files to skip
```
if you omit `path`, it will scan the current working directory

_Pro Tip:_ You can run with `--test` first, then browse/prune the downloaded artwork, then run again with `--no_download` to embed only the artwork you didn't prune.

### From the Python Environment
```
from get_cover_art import CoverFinder

finder = CoverFinder(OPTIONS)

# then you can run either of these:
finder.scan_folder(PATH_TO_AUDIO_LIBRARY)
finder.scan_file(PATH_TO_AUDIO_FILE)
```

- `OPTIONS` is a dict of the same options listed for the commandline, e.g. `--verbose` -> `{'verbose': True}`
- you can omit `PATH_TO_AUDIO_LIBRARY` to default to your current directory
- your `CoverFinder` object keeps a list of files_processed, files_skipped, files_failed, files_invalid

## How it works
1. First, it recursively scans your provided folder for supported files.
  - Step 1 is skipped if you specified a single file instead of a folder.
2. For each file without embedded artwork (or all files if `--force` is used), attempts to download from Apple Music based on artist and album metadata.
  - Step 2 is skipped if it had already downloaded (or attempted to download) the image file.
  - Step 2 is also skipped based on `--no_download` or `--skip_*` options.
3. If artwork is found, it's embedded into the audio file.

### Why do you download from Apple Music and not Google image search?
1. Google's Image Search API requires a dev token (so does Apple Music's API, but not its public web query URL).
2. Google search queries are heavily throttled.
3. Apple Music's cover sizes are standardized and sufficiently large.

## Troubleshooting

### The artwork is embedded now, but Apple's Music App still won't show it.
Try re-importing one of your embedded files.  If the re-imported version shows artwork, you need to reimport your music library.  You can do this without losing your playlists as follows:
1. File->Library->Export Library... and name your exported library file.
2. Visit Music->Preferences...->Files and screenshot your options.  You'll need to restore them later.
3. Quit the app and relaunch while holding down the Option key.
4. Choose "Create Library..." and pick a new location.
5. Visit Music->Preferences...->Files and restore your desired options.
6. File->Library->Import Playlist... and choose your library file from step 1.  (Yes, it's called "Import Playlist..." but you actually use this to import your library.)

Step 6 will take a while.

### The artwork appears in Apple's Music App but not my iOS device.
You'll have to unsync all your music and re-sync it again.  Try it with a single file first.
