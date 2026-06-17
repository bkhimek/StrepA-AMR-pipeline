process MLST {

    tag "${sample_id}"
    label 'process_low'

    publishDir "${params.outdir}/mlst", mode: 'copy'

    input:
    tuple val(sample_id), path(fasta)

    output:
    tuple val(sample_id), path("${sample_id}.mlst.tsv"), emit: results
    path "${sample_id}.mlst.tsv",                        emit: tsv_only

    script:
    """
    mlst \\
        --scheme ${params.mlst_scheme} \\
        --threads ${task.cpus} \\
        --quiet \\
        ${fasta} \\
        > ${sample_id}.mlst.tsv
    """
}
