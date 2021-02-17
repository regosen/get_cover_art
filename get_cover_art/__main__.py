import argparse, os
from .cover_finder import CoverFinder, DEFAULTS

# This script searches apple music for artwork that is missing from your library
# It saves the artwork alongside the audio and embeds the artwork into the meta tags

# By default it will scan from the current working directory, you can override this
# with commandline parameters or arguments passed into scan_folder()

parser = argparse.ArgumentParser()
parser.add_argument('--path', help="audio file, or folder of audio files (recursive)", default=".")
parser.add_argument('--dest', help="destination of artwork", default=DEFAULTS.get('cover_art'))

parser.add_argument('--test', '--no_embed', help="scan and download only, don't embed artwork", action='store_true')
parser.add_argument('--no_download', help="embed only previously-downloaded artwork", action='store_true')
parser.add_argument('--inline', help="put artwork in same folders as audio files", action='store_true')
parser.add_argument('--force', help="overwrite existing artwork", action='store_true')
parser.add_argument('--verbose', help="print verbose logging", action='store_true')
parser.add_argument('--throttle', help="number of seconds between queries", default=0)

parser.add_argument('--skip_artists', help="file containing artists to skip", default=DEFAULTS.get('skip_artists'))
parser.add_argument('--skip_albums', help="file containing albums to skip", default=DEFAULTS.get('skip_albums'))
parser.add_argument('--skip_artwork', help="file containing destination art files to skip", default=DEFAULTS.get('skip_artwork'))
args = parser.parse_args()

finder = CoverFinder(vars(args))
if os.path.isfile(args.path):
    finder.scan_file(args.path)
else:
    finder.scan_folder(args.path)
print()
num_processed = len(finder.files_processed)
num_skipped = len(finder.files_skipped)
num_failed = len(finder.files_failed)
print("Done!  Processed: %d, Skipped: %d, Failed: %d" % (num_processed, num_skipped, num_failed))
if finder.art_folder_override:
    print("Artwork folder: " + finder.art_folder_override)
else:
    print("Artwork files are alongside audio files.")
print()
