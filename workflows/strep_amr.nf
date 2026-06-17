nextflow.enable.dsl = 2

include { AMRFINDER } from '../modules/amrfinder'
include { MLST      } from '../modules/mlst'
include { EMMTYPER  } from '../modules/emmtyper'
include { SUMMARY   } from '../modules/summary'

workflow STREP_AMR {

    take:
    ch_genomes

    main:
    AMRFINDER ( ch_genomes )
    MLST      ( ch_genomes )
    EMMTYPER  ( ch_genomes )

    ch_amr_tsvs  = AMRFINDER.out.tsv_only.collect()
    ch_mlst_tsvs = MLST.out.tsv_only.collect()
    ch_emm_tsvs  = EMMTYPER.out.tsv_only.collect()

    SUMMARY ( ch_amr_tsvs, ch_mlst_tsvs, ch_emm_tsvs )

    emit:
    amrfinder_results = AMRFINDER.out.results
    mlst_results      = MLST.out.results
    emmtyper_results  = EMMTYPER.out.results
    summary           = SUMMARY.out.summary
}
