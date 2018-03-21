# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

"""
Imported from LoadReductions.bas
"""

import logging


log = logging.getLogger(__name__)


def AdjustScnLoads(z):
    # Check for zero values
    if z.n23 == 0:
        z.n23 = 0.0000001
    if z.n24 == 0:
        z.n24 = 0.0000001
    if z.n42 == 0:
        z.n42 = 0.0000001

    # Estimate sediment reductions for row crops based on ag BMPs
    z.SROWBMP1 = (z.n25 / 100) * z.n1 * z.n79
    z.SROWBMP2 = (z.n26 / 100) * z.n1 * z.n81
    z.SROWBMP3 = (z.n27 / 100) * z.n1 * z.n82
    z.SROWBMP4 = (z.n27b / 100) * z.n1 * z.n82b
    z.SROWBMP5 = (z.n28 / 100) * z.n1 * z.n83
    z.SROWBMP8 = (z.n29 / 100) * z.n1 * z.n84
    z.SROWRED = z.n1 - (z.SROWBMP1 + z.SROWBMP2 + z.SROWBMP3 + z.SROWBMP4 + z.SROWBMP5 + z.SROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if z.n42 > 0:
            z.SROWSM1 = (z.n43 / z.n42) * z.SROWRED * z.n80
        if z.n42 > 0:
            z.SROWSM2 = (z.n46c / z.n42) * z.SROWRED * z.n85d
        z.SROWBUF = z.SROWSM1 + z.SROWSM2
    else:
        if (z.n42 > 0):
            z.SROWBUF = (z.n43 / z.n42) * z.SROWRED * z.n80

    z.n1Start = z.n1
    z.n1 = z.SROWRED - z.SROWBUF
    if (z.n1 < (z.n1Start * 0.05)):
        z.n1 = z.n1Start * 0.05

    # Calculate total nitrogen reduction for row crops based on ag BMPs
    z.NROWBMP6 = (z.n28b / 100) * z.n5 * z.n70
    z.NROWNM = z.n5 - z.NROWBMP6
    z.NROWBMP1 = (z.n25 / 100) * z.NROWNM * z.n63
    z.NROWBMP2 = (z.n26 / 100) * z.NROWNM * z.n65
    z.NROWBMP3 = (z.n27 / 100) * z.NROWNM * z.n66
    z.NROWBMP4 = (z.n27b / 100) * z.NROWNM * z.n66b
    z.NROWBMP5 = (z.n28 / 100) * z.NROWNM * z.n67
    z.NROWBMP8 = (z.n29 / 100) * z.NROWNM * z.n68
    z.NROWRED = z.NROWNM - (z.NROWBMP1 + z.NROWBMP2 + z.NROWBMP3 + z.NROWBMP4 + z.NROWBMP5 + z.NROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            z.NROWSM1 = (z.n43 / z.n42) * z.NROWRED * z.n64
        if (z.n42 > 0):
            z.NROWSM2 = (z.n46c / z.n42) * z.NROWRED * z.n69c
        z.NROWBUF = z.NROWSM1 + z.NROWSM2
    else:
        if (z.n42 > 0):
            z.NROWBUF = (z.n43 / z.n42) * z.NROWRED * z.n64

    z.n5Start = z.n5
    z.n5 = z.NROWRED - z.NROWBUF
    if (z.n5 < (z.n5Start * 0.05)):
        z.n5 = z.n5Start * 0.05

    # Calculate dissolved nitrogen reduction for row crops based on ag BMPs
    z.NROWBMP6 = (z.n28b / 100) * z.n5dn * z.n70
    z.NROWNM = z.n5dn - z.NROWBMP6
    z.NROWBMP1 = (z.n25 / 100) * z.NROWNM * z.n63
    z.NROWBMP2 = (z.n26 / 100) * z.NROWNM * z.n65
    z.NROWBMP3 = (z.n27 / 100) * z.NROWNM * z.n66
    z.NROWBMP4 = (z.n27b / 100) * z.NROWNM * z.n66b
    z.NROWBMP5 = (z.n28 / 100) * z.NROWNM * z.n67
    z.NROWBMP8 = (z.n29 / 100) * z.NROWNM * z.n68
    z.NROWRED = z.NROWNM - (z.NROWBMP1 + z.NROWBMP2 + z.NROWBMP3 + z.NROWBMP4 + z.NROWBMP5 + z.NROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            z.NROWSM1 = (z.n43 / z.n42) * z.NROWRED * z.n64
        if (z.n42 > 0):
            z.NROWSM2 = (z.n46c / z.n42) * z.NROWRED * z.n69c
        z.NROWBUF = z.NROWSM1 + z.NROWSM2
    else:
        if (z.n42 > 0):
            z.NROWBUF = (z.n43 / z.n42) * z.NROWRED * z.n64

    z.n5dnStart = z.n5dn
    z.n5dn = z.NROWRED - z.NROWBUF
    if (z.n5dn < (z.n5dnStart * 0.05)):
        z.n5dn = z.n5dnStart * 0.05

    # Calculate total phosphorus reduction for row crops based on ag BMPs
    z.PROWBMP6 = (z.n28b / 100) * z.n12 * z.n78
    z.PROWNM = z.n12 - z.PROWBMP6
    z.PROWBMP1 = (z.n25 / 100) * z.PROWNM * z.n71
    z.PROWBMP2 = (z.n26 / 100) * z.PROWNM * z.n73
    z.PROWBMP3 = (z.n27 / 100) * z.PROWNM * z.n74
    z.PROWBMP4 = (z.n27b / 100) * z.PROWNM * z.n74b
    z.PROWBMP5 = (z.n28 / 100) * z.PROWNM * z.n75

    z.PROWBMP8 = (z.n29 / 100) * z.PROWNM * z.n76
    z.PROWRED = z.PROWNM - (z.PROWBMP1 + z.PROWBMP2 + z.PROWBMP3 + z.PROWBMP4 + z.PROWBMP5 + z.PROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            z.PROWSM1 = (z.n43 / z.n42) * z.PROWRED * z.n72
        if (z.n42 > 0):
            z.PROWSM2 = (z.n46c / z.n42) * z.PROWRED * z.n77c
        z.PROWBUF = z.PROWSM1 + z.PROWSM2
    else:
        if (z.n42 > 0):
            z.PROWBUF = (z.n43 / z.n42) * z.PROWRED * z.n72

    z.n12Start = z.n12
    z.n12 = z.PROWRED - z.PROWBUF
    if (z.n12 < (z.n12Start * 0.05)):
        z.n12 = z.n12Start * 0.05

    # Calculate dissolved phosphorus reduction for row crops based on ag BMPs
    z.PROWBMP6 = (z.n28b / 100) * z.n12dp * z.n78
    z.PROWNM = z.n12dp - z.PROWBMP6
    z.PROWBMP1 = (z.n25 / 100) * z.PROWNM * z.n71
    z.PROWBMP2 = (z.n26 / 100) * z.PROWNM * z.n73
    z.PROWBMP3 = (z.n27 / 100) * z.PROWNM * z.n74
    z.PROWBMP4 = (z.n27b / 100) * z.PROWNM * z.n74b
    z.PROWBMP5 = (z.n28 / 100) * z.PROWNM * z.n75

    z.PROWBMP8 = (z.n29 / 100) * z.PROWNM * z.n76
    z.PROWRED = z.PROWNM - (z.PROWBMP1 + z.PROWBMP2 + z.PROWBMP3 + z.PROWBMP4 + z.PROWBMP5 + z.PROWBMP8)
    if (z.SMCheck == "Both" or z.SMCheck == "Upland"):
        if (z.n42 > 0):
            z.PROWSM1 = (z.n43 / z.n42) * z.PROWRED * z.n72
        if (z.n42 > 0):
            z.PROWSM2 = (z.n46c / z.n42) * z.PROWRED * z.n77c
        z.PROWBUF = z.PROWSM1 + z.PROWSM2
    else:
        if (z.n42 > 0):
            z.PROWBUF = (z.n43 / z.n42) * z.PROWRED * z.n72

    z.n12dpStart = z.n12dp
    z.n12dp = z.PROWRED - z.PROWBUF
    if (z.n12dp < (z.n12dpStart * 0.05)):
        z.n12dp = z.n12dpStart * 0.05

    # Calculate sed reduction for hay/pasture based on ag BMPs
    z.SHAYBMP4 = (z.n33c / 100) * z.n2 * z.n82b
    z.SHAYBMP5 = (z.n35 / 100) * z.n2 * z.n83
    z.SHAYBMP7 = (z.n36 / 100) * z.n2 * z.n84b
    z.SHAYBMP8 = (z.n37 / 100) * z.n2 * z.n84

    z.n2Start = z.n2
    z.n2 = z.n2 - (z.SHAYBMP4 + z.SHAYBMP5 + z.SHAYBMP7 + z.SHAYBMP8)
    if (z.n2 < (z.n2Start * 0.05)):
        z.n2 = z.n2Start * 0.05

    # Calculate total nitrogen reduction for hay/pasture based on different percent usage of BMPs
    z.NHAYBMP6 = (z.n35b / 100) * z.n6 * z.n70
    z.NHAYNM = z.n6 - z.NHAYBMP6
    z.NHAYBMP4 = (z.n33c / 100) * z.NHAYNM * z.n66b
    z.NHAYBMP5 = (z.n35 / 100) * z.NHAYNM * z.n67
    z.NHAYBMP7 = (z.n36 / 100) * z.NHAYNM * z.n68b
    z.NHAYBMP8 = (z.n37 / 100) * z.NHAYNM * z.n68

    z.n6Start = z.n6
    z.n6 = z.NHAYNM - (z.NHAYBMP4 + z.NHAYBMP5 + z.NHAYBMP7 + z.NHAYBMP8)
    if (z.n6 < (z.n6Start * 0.05)):
        z.n6 = z.n6Start * 0.05

    # Calculate dissolved nitrogen reduction for hay/pasture
    z.NHAYBMP6 = (z.n35b / 100) * z.n6dn * z.n70
    z.NHAYNM = z.n6dn - z.NHAYBMP6
    z.NHAYBMP4 = (z.n33c / 100) * z.NHAYNM * z.n66b
    z.NHAYBMP5 = (z.n35 / 100) * z.NHAYNM * z.n67
    z.NHAYBMP7 = (z.n36 / 100) * z.NHAYNM * z.n68b
    z.NHAYBMP8 = (z.n37 / 100) * z.NHAYNM * z.n68

    z.n6dnStart = z.n6dn
    z.n6dn = z.NHAYNM - (z.NHAYBMP4 + z.NHAYBMP5 + z.NHAYBMP7 + z.NHAYBMP8)
    if (z.n6dn < (z.n6dnStart * 0.05)):
        z.n6dn = z.n6dnStart * 0.05

    # Calculate total phosphorus reduction for hay/pasture based on different percent usage of BMPs
    z.PHAYBMP6 = (z.n35b / 100) * z.n13 * z.n78
    z.PHAYNM = z.n13 - z.PHAYBMP6
    z.PHAYBMP4 = (z.n33c / 100) * z.PHAYNM * z.n74b
    z.PHAYBMP5 = (z.n35 / 100) * z.PHAYNM * z.n75
    z.PHAYBMP7 = (z.n36 / 100) * z.PHAYNM * z.n76b
    z.PHAYBMP8 = (z.n37 / 100) * z.PHAYNM * z.n76

    z.n13Start = z.n13
    z.n13 = z.PHAYNM - (z.PHAYBMP4 + z.PHAYBMP5 + z.PHAYBMP7 + z.PHAYBMP8)
    if (z.n13 < (z.n13Start * 0.05)):
        z.n13 = z.n13Start * 0.05

    # Calculate dissolved phosphorus reduction for hay/pasture
    z.PHAYBMP6 = (z.n35b / 100) * z.n13dp * z.n78
    z.PHAYNM = z.n13dp - z.PHAYBMP6
    z.PHAYBMP4 = (z.n33c / 100) * z.PHAYNM * z.n74b
    z.PHAYBMP5 = (z.n35 / 100) * z.PHAYNM * z.n75
    z.PHAYBMP7 = (z.n36 / 100) * z.PHAYNM * z.n76b
    z.PHAYBMP8 = (z.n37 / 100) * z.PHAYNM * z.n76

    z.n13dpStart = z.n13dp
    z.n13dp = z.PHAYNM - (z.PHAYBMP4 + z.PHAYBMP5 + z.PHAYBMP7 + z.PHAYBMP8)
    if (z.n13dp < (z.n13dpStart * 0.05)):
        z.n13dp = z.n13dpStart * 0.05

    # Calculate nitrogen reducton for animal activities based on differnt percent usage of BMPs
    z.NAWMSL = (z.n41b / 100) * z.n85h * z.GRLBN
    z.NAWMSP = (z.n41d / 100) * z.n85j * z.NGLBN
    z.NRUNCON = (z.n41f / 100) * z.n85l * (z.GRLBN + z.NGLBN)
    if z.n42 > 0:
        z.NFENCING = (z.n45 / z.n42) * z.n69 * z.GRSN
        z.NAGBUFFER = (z.n43 / z.n42) * z.n64 * (z.n7b - (z.NGLBN + z.GRLBN + z.GRSN))

    z.n7b = z.n7b - (z.NAWMSL + z.NAWMSP + z.NRUNCON + z.NFENCING + z.NAGBUFFER)

    # Calculate phosphorus reduction for animal activities based on different percent of BMPs
    z.PAWMSL = (z.n41b / 100) * z.n85i * z.GRLBP
    z.PAWMSP = (z.n41d / 100) * z.n85k * z.NGLBP
    z.PRUNCON = (z.n41f / 100) * z.n85m * (z.GRLBP + z.NGLBP)
    z.PHYTASEP = (z.n41h / 100) * z.n85n * (z.NGLManP + z.NGLBP)
    if z.n42 > 0:
        z.PFENCING = (z.n45 / z.n42) * z.n77 * z.GRSP
        z.PAGBUFFER = (z.n43 / z.n42) * z.n72 * (z.n14b - (z.NGLBP + z.GRLBP + z.GRSP))

    z.n14b = z.n14b - (z.PAWMSL + z.PAWMSP + z.PRUNCON + z.PHYTASEP + z.PFENCING + z.PAGBUFFER)

    # Calculate Urban Load Reductions

    # High Urban S load
    # Urban Sediment Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    z.SURBWETH = z.n25b * z.n2b * z.n85b
    z.n2b = z.n2b - z.SURBWETH
    if z.n2b < 0:
        z.n2b = 0

    # . . . Low-density areas
    z.SURBWETL = z.n25b * z.n2c * z.n85b
    z.n2c = z.n2c - z.SURBWETL
    if z.n2c < 0:
        z.n2c = 0

    # Urban Nitrogen Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    z.NURBWETH = z.n25b * z.n6b * z.n69b
    z.n6b = z.n6b - z.NURBWETH
    if z.n6b < 0:
        z.n6b = 0

    # Urban Dissolved Nitrogen Reduction
    z.NURBWETH = z.n25b * z.n6bdn * z.n69b
    z.n6bdn = z.n6bdn - z.NURBWETH
    if z.n6bdn < 0:
        z.n6bdn = 0

    # . . . Low-density areas
    z.NURBWETL = z.n25b * z.n6c * z.n69b
    z.n6c = z.n6c - z.NURBWETL
    if z.n6c < 0:
        z.n6c = 0

    # Urban Dissolved Nitrogen Reduction
    z.NURBWETL = z.n25b * z.n6cdn * z.n69b
    z.n6cdn = z.n6cdn - z.NURBWETL
    if z.n6cdn < 0:
        z.n6cdn = 0

    # Urban Phosphorus Load Reduction from Wetlands and Streambank Stabilization
    # . . . High-density areas
    z.PURBWETH = z.n25b * z.n13b * z.n77b
    z.n13b = z.n13b - z.PURBWETH
    if z.n13b < 0:
        z.n13b = 0

    # Urban Dissolved Phosphorus Reduction
    z.PURBWETH = z.n25b * z.n13bdp * z.n77b
    z.n13bdp = z.n13bdp - z.PURBWETH
    if z.n13bdp < 0:
        z.n13bdp = 0

    # . . . Low-density areas
    z.PURBWETL = z.n25b * z.n13c * z.n77b
    z.n13c = z.n13c - z.PURBWETL
    if z.n13c < 0:
        z.n13c = 0

    # Urban Dissolved Phosphorus Reduction
    z.PURBWETL = z.n25b * z.n13cdp * z.n77b
    z.n13cdp = z.n13cdp - z.PURBWETL
    if z.n13cdp < 0:
        z.n13cdp = 0

    # Farm animal FC load reductions
    z.FCAWMSL = (z.n41b / 100) * z.n85q * z.GRLBFC
    z.FCAWMSP = (z.n41d / 100) * z.n85r * z.NGLBFC
    z.FCRUNCON = (z.n41f / 100) * z.n85s * (z.NGLBFC + z.GRLBFC)
    z.FCFENCING = (z.n45 / z.n42) * z.n85p * z.GRSFC
    z.FCAGBUFFER = (z.n43 / z.n42) * z.n85o * (z.n139 - (z.NGLBFC + z.GRLBFC + z.GRSFC))
    if z.FCAGBUFFER < 0:
        z.FCAGBUFFER = 0

    # For Animal FC
    z.n145 = z.n139 - (z.FCAWMSL + z.FCAWMSP + z.FCRUNCON + z.FCFENCING + z.FCAGBUFFER)
    if z.n145 < 0:
        z.n145 = 0

    # For urban FC
    z.FCURBBIO = z.n142 * z.RetentEff * z.n85u
    z.FCURBWET = z.n142 * z.n25b * z.n85t
    z.FCURBBUF = z.n142 * z.FilterEff * z.PctStrmBuf * z.n85o
    z.n148 = z.n142 - (z.FCURBBIO + z.FCURBWET + z.FCURBBUF)
    if z.n148 < 0:
        z.n148 = 0

    # Calculations for Unpaved Roads N, P and Sed Load Reduction
    if z.n42c > 0:
        z.SEDUNPAVED = (z.n46o / z.n42c) * z.n2d * z.n85g * 1.4882
        z.n2d = z.n2d - z.SEDUNPAVED
        if z.n2d < 0:
            z.n2d = 0

        z.NUNPAVED = (z.n46o / z.n42c) * z.n6d * z.n85e * 1.4882
        z.n6d = z.n6d - z.NUNPAVED
        if z.n6d < 0:
            z.n6d = 0

        z.NUNPAVED = (z.n46o / z.n42c) * z.n6ddn * z.n85e * 1.4882
        z.n6ddn = z.n6ddn - z.NUNPAVED
        if z.n6ddn < 0:
            z.n6ddn = 0

        z.PUNPAVED = (z.n46o / z.n42c) * z.n13d * z.n85f * 1.4882
        z.n13d = z.n13d - z.PUNPAVED
        if z.n13d < 0:
            z.n13d = 0

        z.PUNPAVED = (z.n46o / z.n42c) * z.n13ddp * z.n85f * 1.4882
        z.n13ddp = z.n13ddp - z.PUNPAVED
        if z.n13d < 0:
            z.n13ddp = 0
