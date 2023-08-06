"""
PATHS.py


PATHS is used to input and output directories of validation
analysis.

Copyright [2013] EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the
"License"); you may not use this file except in
compliance with the License. You may obtain a copy of
the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

"""

__author__ = 'Zhe Wang'
__email__ = 'zhe@ebi.ac.uk'
__date__ = '2022-06-14'

# ENT file source path
ENTSOURCE = '/nfs/msd/work2/ftp/pdb/data/structures/all/pdb/'

# VTP file source path
VTPSOURCE = '/nfs/pdbe_staging/pdbe_data/development/staging/em/'

# CIF file source path
# CIFSOURCE = '/nfs/production/gerard/pdbe/prerelease/current/ftp/pdb/data/structures/divided/mmCIF/'
CIFSOURCE = '/nfs/ftp/public/.staging/pdbe-G79Bblrm/projects/pdb/staging/data/structures/all/mmCIF/'

MAP_SERVER_PATH = '/hps/nobackup/gerard/emdb/va/entry_results/'

# Chimera path
CHIMERA = '/hps/nobackup/gerard/emdb/va/external/chimerax/usr/libexec/UCSF-ChimeraX/bin/ChimeraX'

# Original or old Chimera
OCHIMERA = '/hps/nobackup/gerard/emdb/va/external/chimera/bin/chimera'

# For ebi server to copy data for VA
# VASOURCE = '/nfs/msd/em/ftp_rsync/staging/structures/'
VASOURCE = '/nfs/production/gerard/emdb/archive/staging/structures/'

# VAPATH
VAPATH = '/hps/software/users/gerard/emdb/va/Validation-Analysis/va/'

# Jsons and images are copied to here for display purpose
FORDISPLAY = '/nfs/nobackup/msd/em_va/development/'

# Proshade path
PROSHADEPATH = '/hps/software/users/gerard/emdb/va/external/ccpem/ccpem-1.6.0/bin/proshade'

# Meshmaker path
MESHMAKERPATH = '/nfs/msd/em/software/meshmakertest/meshmaker/build/meshmaker'

# VA production path
VA_PROD_PATH = '/nfs/public/rw/pdbe/httpd-em/sessions-prod/validation_analysis'

# VA staging path
VA_STAG_PATH = '/nfs/public/rw/pdbe/httpd-em/sessions/validation_analysis'

# Strudel lib
LIB_STRUDEL_ROOT = '/hps/nobackup/gerard/emdb/va/external/strudel_motiflib/strudel-lib.4_0.5px'

# 3DFSC fake to take positions
THREEDFSC_ROOT = '/Users/zhe/Downloads/Anisotropy/ThreeDFSC/ThreeDFSC_Start.py'
