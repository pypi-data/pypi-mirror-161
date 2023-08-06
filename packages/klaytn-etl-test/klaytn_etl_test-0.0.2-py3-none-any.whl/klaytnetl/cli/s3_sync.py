import os, glob, logging, boto3

def get_path(tmpdir, path):
    if path is None:
        return None
    elif tmpdir is None:
        return os.path.normpath(path)
    else:
        return os.path.normpath(os.path.join(tmpdir, path))


def sync_to_s3(s3_bucket, tmpdir, outputs, is_single_file):
    s3 = boto3.resource('s3')

    for output_path in filter(lambda o: o is not None, outputs):
        temp_path = get_path(tmpdir, output_path)
        for file in _get_files(temp_path, is_single_file):
            out = os.path.join(os.path.normpath(output_path), os.path.basename(file))
            logging.info(f"Transfer {file} --> s3://{s3_bucket}/{out}")
            s3.Object(s3_bucket, out).put(Body=open(file, 'rb'))


def _get_files(path, is_single_file):
    import os, glob

    if is_single_file:
        path = os.path.normpath(path)
    else:
        path = (os.path.join(os.path.normpath(path), '*'))

    return glob.glob(path)
