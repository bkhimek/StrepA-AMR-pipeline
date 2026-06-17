process AMRFINDER {

    tag "${sample_id}"
    label 'process_medium'

    publishDir "${params.outdir}/amrfinder", mode: 'copy'

    input:
    tuple val(sample_id), path(fasta)

    output:
    tuple val(sample_id), path("${sample_id}.amrfinder.tsv"), emit: results
    path "${sample_id}.amrfinder.tsv",                        emit: tsv_only

    script:
    def db_flag = params.amrfinder_db ? "--database ${params.amrfinder_db}" : ''
    """
    if [ -z "${params.amrfinder_db}" ]; then
        amrfinder --update
    fi

    amrfinder \\
        --nucleotide ${fasta} \\
        --organism Streptococcus_pyogenes \\
        --name ${sample_id} \\
        ${db_flag} \\
        --plus \\
        --threads ${task.cpus} \\
        --output ${sample_id}.amrfinder.tsv
    """
}
