process EMMTYPER {

    tag "${sample_id}"
    label 'process_low'

    publishDir "${params.outdir}/emmtyper", mode: 'copy'

    input:
    tuple val(sample_id), path(fasta)

    output:
    tuple val(sample_id), path("${sample_id}.emmtyper.tsv"), emit: results
    path "${sample_id}.emmtyper.tsv",                        emit: tsv_only

    script:
    """
    emmtyper \\
        --output-format verbose \\
        --output ${sample_id}.emmtyper.tsv \\
        ${fasta}
    """
}
