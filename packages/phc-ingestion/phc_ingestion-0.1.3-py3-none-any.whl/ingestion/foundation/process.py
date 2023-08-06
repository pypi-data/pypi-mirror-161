from lifeomic_logging import scoped_logger
import xmltodict
import yaml
from pathlib import Path

from ingestion.foundation.util.cnv import extract_copy_numbers
from ingestion.foundation.util.fnv import extract_fusion_variant
from ingestion.foundation.util.ga4gh import get_test_yml
from ingestion.foundation.util.vcf_etl import vcf_etl


def read_xml(xml_file: str) -> dict:
    with open(xml_file) as fd:
        return xmltodict.parse(fd.read())


def get_specimen_name(results_payload_dict: dict) -> str:
    specimen_name = None
    if isinstance(results_payload_dict["variant-report"]["samples"]["sample"], list):
        found = list(
            filter(
                lambda x: x["@nucleic-acid-type"] == "DNA",
                results_payload_dict["variant-report"]["samples"]["sample"],
            )
        )
        if len(found) > 0:
            specimen_name = found[0]["@name"]
    else:
        specimen_name = results_payload_dict["variant-report"]["samples"]["sample"]["@name"]
    if not specimen_name:
        raise RuntimeError("Failed to find specimen name")
    return specimen_name  # type: ignore


def process(
    xml_file: str,
    vcf_file: str,
    report_file: str,
    local_output_dir: str,
    phc_output_dir: str = ".lifeomic/foundation",
) -> None:
    with scoped_logger(__name__) as log:
        xml_dict = read_xml(xml_file)
        results_payload_dict = xml_dict["rr:ResultsReport"]["rr:ResultsPayload"]

        sample_name = get_specimen_name(results_payload_dict)

        base_xml_name = Path(xml_file).stem

        vcf_name = f"{local_output_dir}/{base_xml_name}/{base_xml_name}.tcf"
        write_vcf_to_manifest = vcf_etl(vcf_file, vcf_name, base_xml_name)

        yaml_file = get_test_yml(
            results_payload_dict,
            base_xml_name,
            local_output_dir,
            report_file,
            write_vcf_to_manifest,
            phc_output_dir,
        )

        extract_copy_numbers(
            results_payload_dict, sample_name, base_xml_name, local_output_dir, log
        )

        extract_fusion_variant(
            results_payload_dict, sample_name, base_xml_name, local_output_dir, log
        )

        with open(
            f"{local_output_dir}/{base_xml_name}/{base_xml_name}.ga4gh.tmp",
            "w",
        ) as file:
            yaml.dump(yaml_file, file)
