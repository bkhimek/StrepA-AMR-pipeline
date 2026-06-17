process SUMMARY {

    label 'process_low'

    publishDir "${params.outdir}", mode: 'copy'

    input:
    path amrfinder_tsvs
    path mlst_tsvs
    path emmtyper_tsvs

    output:
    path 'summary.tsv', emit: summary

    script:
    """
    #!/usr/bin/env python3
    import os, glob, csv

    def parse_amrfinder(path):
        genes = []
        with open(path) as fh:
            reader = csv.DictReader(fh, delimiter='\t')
            for row in reader:
                if row.get('Type', '') in ('AMR', 'STRESS', 'VIRULENCE', 'POINT'):
                    genes.append(row.get('Element symbol', '').strip())
        return ';'.join(sorted(set(genes))) if genes else 'none'

    def parse_mlst(path):
        with open(path) as fh:
            line = fh.readline().strip()
        parts = line.split('\t')
        if len(parts) < 3:
            return 'unknown', 'unknown', ''
        return parts[1], parts[2], ';'.join(parts[3:]) if len(parts) > 3 else ''

    def parse_emmtyper(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    return parts[1]
        return 'unknown'

    amr_files  = {os.path.basename(f).replace('.amrfinder.tsv', ''): f for f in glob.glob('*.amrfinder.tsv')}
    mlst_files = {os.path.basename(f).replace('.mlst.tsv', ''): f      for f in glob.glob('*.mlst.tsv')}
    emm_files  = {os.path.basename(f).replace('.emmtyper.tsv', ''): f  for f in glob.glob('*.emmtyper.tsv')}

    samples = sorted(set(list(amr_files) + list(mlst_files) + list(emm_files)))

    with open('summary.tsv', 'w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(['sample_id', 'mlst_scheme', 'ST', 'mlst_alleles', 'emm_type', 'amr_genes'])
        for s in samples:
            scheme, st, alleles = parse_mlst(mlst_files[s]) if s in mlst_files else ('NA','NA','NA')
            emm   = parse_emmtyper(emm_files[s]) if s in emm_files else 'NA'
            genes = parse_amrfinder(amr_files[s]) if s in amr_files else 'NA'
            writer.writerow([s, scheme, st, alleles, emm, genes])

    print(f"Summary written: {len(samples)} samples.")
    """
}
