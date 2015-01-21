from __future__ import absolute_import

from .preprocessing import (CorpusMSAbstracts, CorpusMSAbstracts_Collocations, CorpusMSAbstracts_NER,
                                            CorpusMSAbstractsSimple)

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="TOPIC SPACE")

    parser.add_argument("-p", "--preprocessing",
                        help="Model you want to use")

    parser.add_argument("-m", "--model",
                        help="Model you want to use")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()


