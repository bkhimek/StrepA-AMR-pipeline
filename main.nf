#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

/*
 * StrepA-AMR-pipeline
 * AMR profiling, MLST, and emm typing for Streptococcus pyogenes
 */

include { STREP_AMR } from './workflows/strep_amr'

workflow {

    if ( !params.input ) {
        error "Please supply an input glob with --input, e.g. --input '~/s_pyogenes_project/genomes/GCF_*/GCF_*.fna'"
    }

    ch_genomes = Channel
        .fromPath( params.input, checkIfExists: true )
        .map { fasta -> tuple( fasta.baseName.replaceAll(/\.fna$/, ''), fasta ) }

    STREP_AMR ( ch_genomes )
}
