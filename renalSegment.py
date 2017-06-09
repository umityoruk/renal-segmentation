import os
import sys
from Source.autoSegment import autoSegmentFromDicom

path_to_script = os.path.dirname(os.path.realpath(__file__))

input_dir = sys.argv[1]
output_dir = sys.argv[2]

recon, kidney_labels = autoSegmentFromDicom(input_dir=input_dir, output_dir=output_dir, threshold_multiplier=1, root_path=path_to_script)
