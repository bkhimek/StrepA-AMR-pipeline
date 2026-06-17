process MULTIQC {

    label 'process_low'

    publishDir "${params.outdir}/multiqc", mode: 'copy'

    input:
    path multiqc_files

    output:
    path 'multiqc_report.html', emit: report
    path 'multiqc_data/',       emit: data

    script:
    def config_flag = params.multiqc_config ? "--config ${params.multiqc_config}" : ''
    """
    multiqc \\
        ${config_flag} \\
        --force \\
        --title "StrepA AMR Pipeline Report" \\
        .
    """
}
