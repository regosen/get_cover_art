import argparse, os
from .cover_finder import CoverFinder, DEFAULTS

# This script searches apple music for artwork that is missing from your library
# It saves the artwork alongside the audio and embeds the artwork into the meta tags

# By default it will scan from the current working directory, you can override this
# with commandline parameters or arguments passed into scan_folder()

def check_art_size(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("art-size must be a positive integer")
    return ivalue

def check_throttle(value):
    fvalue = float(value)
    if fvalue < 0:
        raise argparse.ArgumentTypeError("throtte cannot be negative")
    return fvalue

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help="audio file, or folder of audio files (recursive)", default=".")

    parser_art = parser.add_argument_group('artwork options')
    parser_art.add_argument('--art-size', type=check_art_size, help="square dimensions of artwork (e.g. 500)", default=DEFAULTS.get('art_size'))
    parser_art.add_argument('--art-dest', '--dest', help="set artwork destination folder", default=DEFAULTS.get('cover_art'))
    parser_art.add_argument('--art-dest-inline', '--inline', help="put artwork in same folders as audio files", action='store_true')
    parser_art.add_argument('--art-dest-filename', default=DEFAULTS.get('art_dest_filename'), help="set artwork destination filename format. Accepts {artist}, {album}, and {title}. Default '{artist} - {album}.jpg")
    parser_art.add_argument('--external-art-mode', choices=['before', 'after', 'none'], default=DEFAULTS.get('external_art_mode'), help='Use image from local folder; "before" prevents downloads, "after" uses as a fallback.  Default is none.')
    parser_art.add_argument('--external-art-filename', default=DEFAULTS.get('external_art_filename'), help="Filename(s) of folder art to use. Accepts {artist}, {album}, and {title} for replacement: e.g. cover.jpg or {album}-{artist}.jpg", nargs="+")

    parser_behavior = parser.add_argument_group('behavior options')
    parser_behavior.add_argument('--test', '--no-embed', '--no_embed', help="scan and download only, don't embed artwork", action='store_true')
    parser_behavior.add_argument('--clear', help="clear artwork from audio file (regardless of finding art)", action='store_true')
    parser_behavior.add_argument('--no-download', '--no_download', help="embed only previously-downloaded artwork", action='store_true')
    parser_behavior.add_argument('--force', help="overwrite existing artwork", action='store_true')
    parser_behavior.add_argument('--verbose', help="print verbose logging", action='store_true')
    parser_behavior.add_argument('--no-skip', '--no_skip', help="don't skip previously-scanned files", action='store_true')
    parser_behavior.add_argument('--throttle', type=check_throttle, help="number of seconds to wait", default=0)

    parser_filters = parser.add_argument_group('filter options')
    parser_filters.add_argument('--skip-artwork', '--skip_artwork', help="(maintained between runs) file listing destination art files to skip", default=DEFAULTS.get('skip_artwork'))
    parser_filters.add_argument('--skip-artists', '--skip_artists', help="file listing artists to skip", default=DEFAULTS.get('skip_artists'))
    parser_filters.add_argument('--skip-albums', '--skip_albums', help="file listing albums to skip", default=DEFAULTS.get('skip_albums'))

    return parser.parse_args()

def main():
    args = get_args()
    finder = CoverFinder(vars(args))
    if os.path.isfile(args.path):
        finder.scan_file(args.path)
    else:
        finder.scan_folder(args.path)
    print()
    num_processed = len(finder.files_processed)
    num_skipped = len(finder.files_skipped)
    num_failed = len(finder.files_failed)
    print(f"Done!  Processed: {num_processed}, Skipped: {num_skipped}, Failed: {num_failed}")
    if finder.art_folder_override:
        print(f"Artwork folder: {finder.art_folder_override}")
    else:
        print("Artwork files are alongside audio files.")
    print()

if __name__ == '__main__':
    main()
