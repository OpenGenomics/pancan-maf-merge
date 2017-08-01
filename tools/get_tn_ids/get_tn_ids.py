##
# returns a 2 tuple with the names of the genotype fields that correspond to the normal and tumor samples

import argparse
import json
import hgsc_vcf

parser = argparse.ArgumentParser()
parser.add_argument("--input")

def main(fpath):
    sample_headers = []
    field_header = None
    with open(fpath, 'r') as fi:
        for line in fi.readlines():
            if line[0] != '#':
                break
            if '##SAMPLE' == line[:8]:
                sample_headers.append(line)
            if '#CHROM' == line[:6]:
                field_header = [c.strip() for c in line.split('\t')]

    primaryline = [l for l in sample_headers if 'ID=PRIMARY' in l]
    normalline = [l for l in sample_headers if 'ID=NORMAL' in l]

    if primaryline:
        primarysplit = hgsc_vcf.metainfo.ComplexHeaderLine(string = primaryline[0])
    else:
        # check if there is a METASTATIC sample (SKCM for example)
        primaryline = [l for l in sample_headers if 'ID=METASTATIC' in l or 'ID=RECURRANCE' in l]
        if primaryline:
            primarysplit = hgsc_vcf.metainfo.ComplexHeaderLine(string = primaryline[0])
            # we did find a METASTATIC sample, convert the field_header
        else:
            raise ValueError("Could not find ID=PRIMARY or ID=METASTATIC or ID=RECURRANCE in file %s, start again :)" % fpath)

    if normalline:
        normalsplit = hgsc_vcf.metainfo.ComplexHeaderLine(string = normalline[0])
    else:
        raise ValueError("Could not find ID=NORMAL in the file %s, start again :)" % fpath)

    samples = [s for s in field_header[9:] if s in ('NORMAL', 'PRIMARY', 'TUMOR', 'METASTATIC', 'RECURRANCE', normalsplit.fields['SampleTCGABarcode'], primarysplit.fields['SampleTCGABarcode'])]

    if len(samples) < 2:
        raise ValueError("Fewer than 2 samples found: %s" % samples)
    elif len(samples) > 2:
        raise ValueError("More than 2 samples found: %s" % samples)

    # ok so we have the data that we need
    if samples[0] == normalsplit.fields['SampleTCGABarcode']:
        return samples[0], samples[1], normalsplit.fields['SampleTCGABarcode'], primarysplit.fields['SampleTCGABarcode']
    elif samples[0] == 'NORMAL':
        return samples[0], samples[1], normalsplit.fields['SampleTCGABarcode'], primarysplit.fields['SampleTCGABarcode']
    elif samples[1] == normalsplit.fields['SampleTCGABarcode']:
        return samples[1], samples[0], normalsplit.fields['SampleTCGABarcode'], primarysplit.fields['SampleTCGABarcode']
    elif samples[1] == 'NORMAL':
        return samples[1], samples[0], normalsplit.fields['SampleTCGABarcode'], primarysplit.fields['SampleTCGABarcode']
    else:
        raise ValueError("Can't figure out the tumor and normal sample id's in %s" % samples)


if __name__ == '__main__':
    args = parser.parse_args()
    a, b, c, d = main(args.input)
    print json.dumps({"nid": a, "tid": b, "nbar": c, "tbar": d})
