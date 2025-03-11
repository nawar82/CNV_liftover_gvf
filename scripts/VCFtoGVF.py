import vcf

# Input and output file names
input_vcf = "input.vcf"
output_gvf = "output.gvf"

# Open the VCF file
vcf_reader = vcf.Reader(open(input_vcf, 'r'))

with open(output_gvf, 'w') as gvf_out:
    # Write GVF headers
    gvf_out.write("##gff-version 3\n")
    gvf_out.write("##gvf-version 1.07\n")

    # Write sequence-region lines from VCF contigs
    # GVF requires these lines to declare chromosome lengths
    for contig in vcf_reader.contigs:
        length = vcf_reader.contigs[contig].length
        gvf_out.write("##sequence-region {} 1 {}\n".format(contig, length))

    # For each record (variant) in the VCF:
    # - Extract positions, type, copy number, etc.
    for record in vcf_reader:
        chrom = record.CHROM
        start = record.POS
        end = record.INFO.get('END')
        
        # If no END found, skip or set end = start for safety
        if end is None:
            # Structural variants should have an END, but if not:
            end = start  
        
        # Determine variant type
        # SVTYPE might be present in INFO
        svtype = record.INFO.get('SVTYPE', None)
        
        # If SVTYPE not present, try to infer from ALT field:
        # For example, ALT might be <DUP> or just '.' for normal segments
        if not svtype:
            for alt in record.ALT:
                # alt could be a pyvcf.model._SV object if structural variant
                # or a string like '<DUP>'
                alt_str = str(alt)
                if '<DUP>' in alt_str.upper():
                    svtype = 'DUP'
                    break
            # If still not found, assume a normal segment (CN=2?), 
            # but let's just default to a neutral type
            if not svtype:
                # If CN != 2, it might be a deletion if CN < 2
                # We'll guess based on copy number below
                svtype = 'CNV'

        # Extract genotype fields
        # Assume one sample; adjust if multiple samples present
        sample = record.samples[0] if len(record.samples) > 0 else None
        copy_number = None
        if sample:
            cn = sample['CN'] if 'CN' in sample.data._fields else None
            if cn is not None:
                copy_number = cn
        
        # If we still don't have a variant type and we know CN:
        # If CN < 2 => DEL, CN > 2 => DUP, CN=2 => neutral
        if svtype == 'CNV' and copy_number is not None:
            if copy_number < 2:
                svtype = 'DEL'
            elif copy_number > 2:
                svtype = 'DUP'
            else:
                svtype = 'CNV'

        # Set attributes for GVF
        # Example attributes: ID, variant_type, copy_number
        variant_id = record.ID if record.ID else "{}_{}_{}".format(chrom, start, end)
        attributes = []
        attributes.append("ID={}".format(variant_id))
        attributes.append("variant_type={}".format(svtype))
        if copy_number is not None:
            attributes.append("copy_number={}".format(copy_number))

        # Variant_seq and Reference_seq are not strictly required, but GVF usually has them.
        # For large structural variants, these can be omitted or set to 'N'.
        # If DUP or DEL, we can say Variant_seq=duplication or deletion
        variant_seq = 'unknown'
        if svtype == 'DUP':
            variant_seq = 'duplication'
        elif svtype == 'DEL':
            variant_seq = 'deletion'
        # If neutral CNV, just say 'N' or omit
        attributes.append("Variant_seq={}".format(variant_seq))
        attributes.append("Reference_seq=N")

        # Construct the GVF line
        # GVF uses GFF-like format: seqid, source, type, start, end, score, strand, phase, attributes
        # Here:
        # seqid = chrom
        # source = "gCNV" or "GATK"
        # type = "copy_number_variation" or something similar
        # start, end already known
        # score = "."
        # strand = "+" (CNVs are usually not strand-specific)
        # phase = "."
        # attributes = semicolon separated

        gvf_line = [
            chrom,
            "gCNV",
            "copy_number_variation",
            str(start),
            str(end),
            ".",
            "+",
            ".",
            ";".join(attributes)
        ]

        gvf_out.write("\t".join(gvf_line) + "\n")
