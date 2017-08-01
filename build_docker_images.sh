#!/bin/bash

build() {
  pushd .
  cd tools/$1
  docker build -t opengenomics/$1 .
  popd
}

build hgsc_vcf
build filter_muse
build filter_radia
build sort_vcf
build vcf2maf
build annotate_vcf_cosmic
build merge_vcfs
build get_tn_ids
