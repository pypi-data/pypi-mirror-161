from ..migrate import migrate_by_stylesheet
from ..utils import _print

# we need a list of params to query the user for
PARAM_LIST = [
    'segmentation_details',
]


def migrate(infile, outfile, stylesheet, args, encoding='utf-8', **params):
    if args.verbose:
        _print("migrating by stylesheet...")
    migrated = migrate_by_stylesheet(infile, stylesheet, verbose=args.verbose, **params)  # bytes
    if args.verbose:
        _print("writing output to {}...".format(outfile))
    with open(outfile, 'w') as f:
        f.write(migrated.decode(encoding))
    if args.verbose:
        _print("done")
    return outfile
