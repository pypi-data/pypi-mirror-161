import gzip
import os
import shutil
import xmltodict

from ingestion.foundation.util.cnv import extract_copy_numbers
from ingestion.foundation.util.fnv import extract_fusion_variant
from ingestion.foundation.util.ga4gh import get_test_yml, get_mrn
from ingestion.foundation.util.vcf_etl import vcf_etl, transform_scientific_notation_in_af

BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class MockLog:
    def info(self, _: str):
        pass


def read_xml(xml_file):
    with open(xml_file) as fd:
        return xmltodict.parse(fd.read())


def cleanup():
    if os.path.exists(f"{BASE_PATH}/data/foundation"):
        shutil.rmtree(f"{BASE_PATH}/data/foundation")


def test_cnv():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/sample", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample.xml")

    mock_log = MockLog()

    extract_copy_numbers(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        "sample",
        f"{BASE_PATH}/data",
        mock_log,
    )

    csv = open(f"{BASE_PATH}/data/sample/sample.copynumber.csv")
    text = csv.read()
    csv.close()

    assert (
        text
        == """sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation
SA-1612348,CDK4,44.0,amplification,"{'number-of-exons': '7 of 7', 'status': 'amplification', 'ratio': '11.63', 'interpretation': 'known'}",chr12,58093932,58188144,Pathogenic
SA-1612348,CCND3,6.0,gain,"{'number-of-exons': '5 of 5', 'status': 'amplification', 'ratio': '2.17', 'interpretation': 'known'}",chr6,41853880,41956362,Pathogenic
SA-1612348,MYC,41.0,amplification,"{'number-of-exons': '5 of 5', 'status': 'amplification', 'ratio': '10.34', 'interpretation': 'known'}",chr8,128706589,128801451,Pathogenic
SA-1612348,PIM1,6.0,gain,"{'number-of-exons': '7 of 7', 'status': 'amplification', 'ratio': '2.14', 'interpretation': 'unknown'}",chr6,37138078,37141867,Uncertain significance
SA-1612348,RAD21,7.0,gain,"{'number-of-exons': '13 of 13', 'status': 'amplification', 'ratio': '2.69', 'interpretation': 'unknown'}",chr8,117859738,117878968,Uncertain significance
"""
    )


def test_fnv():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/sample", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample.xml")

    mock_log = MockLog()

    extract_fusion_variant(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        "sample",
        f"{BASE_PATH}/data",
        mock_log,
    )

    csv = open(f"{BASE_PATH}/data/sample/sample.structural.csv")
    text = csv.read()
    csv.close()

    assert (
        text
        == """sample_id,gene1,gene2,effect,chromosome1,start_position1,end_position1,chromosome2,start_position2,end_position2,interpretation,sequence_type,in-frame,attributes
SA-1612348,NF1,N/A,truncation,chr17,29557687,29887856,chr6,66426718,66427149,Likely pathogenic,somatic,unknown,"{'equivocal': 'false', 'supporting-read-pairs': '83'}"
"""
    )


def test_yml():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/SA-1612348", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample.xml")

    yml = get_test_yml(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        f"{BASE_PATH}/data",
        None,
        True,
        ".lifeomic/foundation",
    )

    assert yml == {
        "tests": [
            {
                "name": "Foundation Medicine",
                "reference": "GRCh37",
                "sourceFile": "SA-1612348.xml",
                "testType": "FoundationOne Heme",
                "indexedDate": "2016-07-15",
                "patientIdentifier": "12345678",
                "patientDOB": "2002-12-12",
                "patientLastName": "Patient",
                "bodySite": "Bone",
                "bodySiteSystem": "http://foundation.com/bodySite",
                "bodySiteDisplay": "Bone",
                "diagnosis": "PEDIATRIC Bone osteosarcoma",
                "diagnosisDisplay": "PEDIATRIC Bone osteosarcoma",
                "diagnosisSystem": "http://foundation.com/diagnosis",
                "files": [
                    {
                        "type": "copyNumberVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.copynumber.csv",
                    },
                    {
                        "type": "structuralVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.structural.csv",
                    },
                    {
                        "type": "shortVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.nrm.vcf.gz",
                    },
                ],
                "patientInfo": {
                    "firstName": "Test",
                    "lastName": "Patient",
                    "gender": "male",
                    "dob": "2002-12-12",
                    "identifiers": [
                        {
                            "codingSystem": "http://hl7.org/fhir/v2/0203",
                            "codingCode": "MR",
                            "value": "12345678",
                        }
                    ],
                },
                "lossOfHeterozygosityScore": 21.1,
                "lossOfHeterozygosityStatus": "high",
                "msi": "stable",
                "tmb": "low",
                "tmbScore": 0.73,
            }
        ]
    }


def test_yml_with_date_namespace():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/SA-1612348", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample_namespace.xml")

    yml = get_test_yml(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        f"{BASE_PATH}/data",
        None,
        True,
        ".lifeomic/foundation",
    )

    assert yml == {
        "tests": [
            {
                "name": "Foundation Medicine",
                "reference": "GRCh37",
                "sourceFile": "SA-1612348.xml",
                "testType": "FoundationOne Heme",
                "indexedDate": "2016-07-15",
                "patientIdentifier": "12345678",
                "patientDOB": "2002-12-12",
                "patientLastName": "Patient",
                "bodySite": "Bone",
                "bodySiteSystem": "http://foundation.com/bodySite",
                "bodySiteDisplay": "Bone",
                "diagnosis": "PEDIATRIC Bone osteosarcoma",
                "diagnosisDisplay": "PEDIATRIC Bone osteosarcoma",
                "diagnosisSystem": "http://foundation.com/diagnosis",
                "files": [
                    {
                        "type": "copyNumberVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.copynumber.csv",
                    },
                    {
                        "type": "structuralVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.structural.csv",
                    },
                    {
                        "type": "shortVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.nrm.vcf.gz",
                    },
                ],
                "patientInfo": {
                    "firstName": "Test",
                    "lastName": "Patient",
                    "gender": "male",
                    "dob": "2002-12-12",
                    "identifiers": [
                        {
                            "codingSystem": "http://hl7.org/fhir/v2/0203",
                            "codingCode": "MR",
                            "value": "12345678",
                        }
                    ],
                },
                "lossOfHeterozygosityScore": -1,
                "lossOfHeterozygosityStatus": "high",
                "msi": "stable",
                "tmb": "low",
                "tmbScore": 0.73,
            }
        ]
    }


def test_vcf_etl():
    vcf_actual_lines = []
    vcf_expected_lines = []

    vcf_etl(f"{BASE_PATH}/data/sample.vcf", f"{BASE_PATH}/data/sample/sample.vcf", "SAMPLE")

    with open(f"{BASE_PATH}/data/vcf_expected.vcf") as f:
        vcf_expected_lines = f.readlines()

    with gzip.open(f"{BASE_PATH}/data/sample/sample.vcf.gz", "rt") as f:
        vcf_actual_lines = f.readlines()

    # unlike the gzip CLI tool, gzip.open leaves the input files intact, so reset the files
    with open(f"{BASE_PATH}/data/sample/sample.vcf", "w") as f:
        f.writelines(vcf_actual_lines)
    os.remove(f"{BASE_PATH}/data/sample/sample.vcf.gz")

    # lets make sure we actual read lines
    assert len(vcf_actual_lines) == 27
    # verifying that all lines in the unzipped vcf match the expected vcf
    for idx, val in enumerate(vcf_expected_lines):
        assert val == vcf_actual_lines[idx]


def test_vcf_with_scientific_notation_etl():
    vcf_actual_lines = []
    vcf_expected_lines = []

    vcf_etl(
        f"{BASE_PATH}/data/sample_scientific_notation.vcf",
        f"{BASE_PATH}/data/sample_scientific_notation/sample_scientific_notation.vcf",
        "SAMPLE",
    )

    with open(f"{BASE_PATH}/data/vcf_expected_scientific_notation.vcf") as f:
        vcf_expected_lines = f.readlines()

    with gzip.open(
        f"{BASE_PATH}/data/sample_scientific_notation/sample_scientific_notation.vcf.gz", "rt"
    ) as f:
        vcf_actual_lines = f.readlines()

    # unlike the gzip CLI tool, gzip.open leaves the input files intact, so reset the files
    with open(
        f"{BASE_PATH}/data/sample_scientific_notation/sample_scientific_notation.vcf", "w"
    ) as f:
        f.writelines(vcf_actual_lines)
    os.remove(f"{BASE_PATH}/data/sample_scientific_notation/sample_scientific_notation.vcf.gz")

    # lets make sure we actual read lines
    assert len(vcf_actual_lines) == 28
    # verifying that all lines in the unzipped vcf match the expected vcf
    for idx, val in enumerate(vcf_expected_lines):
        assert val == vcf_actual_lines[idx]


def test_transform_scientific_notation_in_af():
    line_with_scientific_notation = "chr17	41228516	.	TG	T	.	PASS	AF=9.771078E-4;cds_syntax=4472delC;cosmic_status=LIKELY;depth=3087;effect=FRAMESHIFT;gene_name=BRCA1;protein_syntax=P1491fs*14;transcript_name=NM_007294"
    expected_line_with_scientific_notation = "chr17	41228516	.	TG	T	.	PASS	AF=0.0009771078;cds_syntax=4472delC;cosmic_status=LIKELY;depth=3087;effect=FRAMESHIFT;gene_name=BRCA1;protein_syntax=P1491fs*14;transcript_name=NM_007294"

    line_without_scientific_notation = "chr6	117710838	.	C	A	.	PASS	AF=0.4173;cds_syntax=1434G>T;cosmic_status=UNKNOWN;depth=1385;effect=MISSENSE;gene_name=ROS1;protein_syntax=M478I;transcript_name=NM_002944"

    # confirm we alter the scientific notation correctly
    transformed_line_with_scientific_notation = transform_scientific_notation_in_af(
        line_with_scientific_notation
    )
    assert expected_line_with_scientific_notation == transformed_line_with_scientific_notation

    # confirm we don't alter lines without scientific notation at all
    transformed_line_without_scientific_notation = transform_scientific_notation_in_af(
        line_without_scientific_notation
    )
    assert line_without_scientific_notation == transformed_line_without_scientific_notation


def test_yml_with_missing_mrn():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/SA-1612348", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample_missing_mrn.xml")

    yml = get_test_yml(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        f"{BASE_PATH}/data",
        None,
        True,
        ".lifeomic/foundation",
    )

    assert yml == {
        "tests": [
            {
                "name": "Foundation Medicine",
                "reference": "GRCh37",
                "sourceFile": "SA-1612348.xml",
                "testType": "FoundationOne Heme",
                "indexedDate": "2016-07-15",
                "patientIdentifier": "",
                "patientDOB": "2002-12-12",
                "patientLastName": "Patient",
                "bodySite": "Bone",
                "bodySiteSystem": "http://foundation.com/bodySite",
                "bodySiteDisplay": "Bone",
                "diagnosis": "PEDIATRIC Bone osteosarcoma",
                "diagnosisDisplay": "PEDIATRIC Bone osteosarcoma",
                "diagnosisSystem": "http://foundation.com/diagnosis",
                "files": [
                    {
                        "type": "copyNumberVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.copynumber.csv",
                    },
                    {
                        "type": "structuralVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.structural.csv",
                    },
                    {
                        "type": "shortVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.nrm.vcf.gz",
                    },
                ],
                "patientInfo": {
                    "firstName": "Test",
                    "lastName": "Patient",
                    "gender": "male",
                    "dob": "2002-12-12",
                },
                "lossOfHeterozygosityScore": -1,
                "lossOfHeterozygosityStatus": "high",
                "msi": "stable",
                "tmb": "low",
                "tmbScore": 0.73,
            }
        ]
    }


def test_yml_with_no_biomarkers():
    cleanup()
    os.makedirs(f"{BASE_PATH}/data/SA-1612348", exist_ok=True)

    xml = read_xml(f"{BASE_PATH}/data/sample_no_biomarkers.xml")

    yml = get_test_yml(
        xml["rr:ResultsReport"]["rr:ResultsPayload"],
        "SA-1612348",
        f"{BASE_PATH}/data",
        None,
        True,
        ".lifeomic/foundation",
    )

    print(yml)
    assert yml == {
        "tests": [
            {
                "name": "Foundation Medicine",
                "reference": "GRCh37",
                "sourceFile": "SA-1612348.xml",
                "testType": "FoundationOne Heme",
                "indexedDate": "2016-07-15",
                "patientIdentifier": "12345999",
                "patientDOB": "2002-04-12",
                "patientLastName": "Patient",
                "bodySite": "Bone",
                "bodySiteSystem": "http://foundation.com/bodySite",
                "bodySiteDisplay": "Bone",
                "diagnosis": "PEDIATRIC Bone osteosarcoma",
                "diagnosisDisplay": "PEDIATRIC Bone osteosarcoma",
                "diagnosisSystem": "http://foundation.com/diagnosis",
                "files": [
                    {
                        "type": "copyNumberVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.copynumber.csv",
                    },
                    {
                        "type": "structuralVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.structural.csv",
                    },
                    {
                        "type": "shortVariant",
                        "sequenceType": "somatic",
                        "fileName": ".lifeomic/foundation/SA-1612348/SA-1612348.nrm.vcf.gz",
                    },
                ],
                "patientInfo": {
                    "firstName": "Nobiomarkers",
                    "lastName": "Patient",
                    "gender": "male",
                    "dob": "2002-04-12",
                    "identifiers": [
                        {
                            "codingSystem": "http://hl7.org/fhir/v2/0203",
                            "codingCode": "MR",
                            "value": "12345999",
                        }
                    ],
                },
                "lossOfHeterozygosityScore": 21.1,
                "lossOfHeterozygosityStatus": "high",
            }
        ]
    }


def test_get_mrn():
    missing_mrn_result = get_mrn({"LastName": "Baggins"})
    assert missing_mrn_result == ""

    existing_mrn_result = get_mrn({"LastName": "Baggins", "MRN": "mrn_001"})
    assert existing_mrn_result == "mrn_001"
