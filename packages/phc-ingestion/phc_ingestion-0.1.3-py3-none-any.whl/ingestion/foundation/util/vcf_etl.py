from natsort import natsorted
import re
import datetime
from pysam import tabix_compress
import os
import errno


def generate_empty_vcf(prefix: str, out_vcf: str) -> None:
    if not os.path.exists(os.path.dirname(out_vcf)):
        try:
            os.makedirs(os.path.dirname(out_vcf))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(out_vcf, "w+") as foutW:
        # Create a VCF file with an empty header if none was provided
        # Check it out it's the VCF header ONLY
        foutW.write("##fileformat=VCFv4.1\n")
        foutW.write("##filedate=" + datetime.datetime.now().isoformat() + "\n")
        foutW.write('##FILTER=<ID=PASS,Description="All filters passed">\n')
        foutW.write('##FILTER=<ID=R8,Description="IndelRepeatLength is greater than 8">\n')
        foutW.write(
            '##FILTER=<ID=R8.1,Description="IndelRepeatLength of a monomer is greater than 8">\n'
        )
        foutW.write(
            '##FILTER=<ID=R8.2,Description="IndelRepeatLength of a dimer is greater than 8">\n'
        )
        foutW.write('##FILTER=<ID=sb,Description="Variant strand bias high">\n')
        foutW.write(
            '##FILTER=<ID=sb.s,Description="Variant strand bias significantly high (only for SNV)">\n'
        )
        foutW.write(
            '##FILTER=<ID=rs,Description="Variant with rs (dbSNP) number in a non-core gene">\n'
        )
        foutW.write(
            '##FILTER=<ID=FP,Description="Possibly false positives due to high similarity to off-target regions">\n'
        )
        foutW.write('##FILTER=<ID=NC,Description="Noncoding INDELs on non-core genes">\n')
        foutW.write('##FILTER=<ID=lowDP,Description="low depth variant">\n')
        foutW.write('##FILTER=<ID=Benign,Description="Benign variant">\n')
        foutW.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
        foutW.write(
            '##FORMAT=<ID=AF,Number=1,Type=String,Description="Variant Allele Frequency">\n'
        )
        foutW.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + prefix + "\n")

    tabix_compress(out_vcf, f"{out_vcf}.gz", force=True)
    os.remove(out_vcf)


def vcf_etl(in_vcf: str, out_vcf: str, base_xml_name: str) -> bool:
    headers = []
    vars = []

    if not os.path.exists(os.path.dirname(out_vcf)):
        try:
            os.makedirs(os.path.dirname(out_vcf))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(in_vcf) as f:
        lines = f.readlines()
        if len(lines) == 0:
            generate_empty_vcf(base_xml_name, out_vcf)
            return False
        else:
            for line in lines:
                if line.startswith("#"):
                    headers.append(line)
                else:
                    vars.append(line)

            sorted_vars = natsorted(vars)

            with open(out_vcf, "w+") as w:
                for header in headers:
                    if "=af," in header:
                        header = header.replace("=af", "=AF")

                    if "#CHROM" in header:
                        w.write('##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">\n')
                        w.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
                        w.write(
                            '##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Number of reads harboring allele (in order specified by GT)">\n'
                        )
                        header = header.strip("\n") + "\tFORMAT\t" + base_xml_name + "\n"

                    w.write(header)

                for var in sorted_vars:
                    var = var.replace("af=", "AF=")
                    var = transform_scientific_notation_in_af(var)
                    af_match = re.search(r"AF=(\d*\.?\d*)", var)
                    if not af_match:
                        raise RuntimeError("Failed to find AF for var")
                    af = float(af_match.group(1))
                    depth_match = re.search(r"depth=(\d*\.?\d*)", var)
                    if not depth_match:
                        raise RuntimeError("Failed to find depth for var")
                    depth = int(depth_match.group(1))
                    alt_depth = int(round(depth * af))
                    ref_depth = depth - alt_depth
                    ad = f"{ref_depth},{alt_depth}"
                    gt = "1/1" if af > 0.9 else "0/1"
                    vcf_format = "GT:DP:AD"
                    sample = ":".join([gt, str(depth), ad])
                    var = var.strip("\n") + f"\t{vcf_format}\t{sample}\n"
                    w.write(var)

            tabix_compress(out_vcf, f"{out_vcf}.gz", force=True)
            os.remove(out_vcf)
            return True


def transform_scientific_notation_in_af(var: str) -> str:
    var_split = var.split("\t")
    var_info = var_split[-1]
    var_info_split = var_info.split(";")
    var_info_list = [x for x in var_info_split if x.startswith("AF=")]

    # No AF= in line so lets return as is and move on
    if len(var_info_list) != 1:
        return var
    var_info_af = var_info_list[0]
    af_split = var_info_af.split("=")
    af_original_value = af_split[1]
    af_float_value = float(af_original_value)
    var = var.replace(af_original_value, str(af_float_value))
    return var
