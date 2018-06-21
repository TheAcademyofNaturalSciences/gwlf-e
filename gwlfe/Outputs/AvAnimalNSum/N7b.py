from AvAnimalNSum import AvAnimalNSum
from AvAnimalNSum import AvAnimalNSum_2
from gwlfe.BMPs.AgAnimal.NAGBUFFER import NAGBUFFER
from gwlfe.BMPs.AgAnimal.NAGBUFFER import NAGBUFFER_2
from gwlfe.BMPs.AgAnimal.NAWMSL import NAWMSL
from gwlfe.BMPs.AgAnimal.NAWMSL import NAWMSL_2
from gwlfe.BMPs.AgAnimal.NAWMSP import NAWMSP
from gwlfe.BMPs.AgAnimal.NAWMSP import NAWMSP_2
from gwlfe.BMPs.AgAnimal.NFENCING import NFENCING
from gwlfe.BMPs.AgAnimal.NFENCING import NFENCING_2
from gwlfe.BMPs.AgAnimal.NRUNCON import NRUNCON
from gwlfe.BMPs.AgAnimal.NRUNCON import NRUNCON_2


def N7b(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
        GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
        Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct,
        NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    av_animal_n_sum = AvAnimalNSum(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                   NGAppNRate,
                                   Prec, DaysMonth,
                                   NGPctSoilIncRate, GRPctManApp, GRAppNRate, GRPctSoilIncRate, NGBarnNRate, AWMSNgPct,
                                   NgAWMSCoeffN,
                                   RunContPct, RunConCoeffN, PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN,
                                   PctStreams, GrazingNRate)
    nawmsl = NAWMSL(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing, GRBarnNRate,
                    Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h)
    nawmsp = NAWMSP(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                    Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j)
    nruncon = NRUNCON(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                      GRBarnNRate,
                      Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate,
                      AWMSNgPct, NgAWMSCoeffN, n41f, n85l)
    nfencing = NFENCING(PctStreams, PctGrazing, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, n42, n45, n69)
    nagbuffer = NAGBUFFER(n42, n43, n64, NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                          NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, GRPctManApp,
                          PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate,
                          GRAppNRate, GRPctSoilIncRate, GrazingNRate)
    result = av_animal_n_sum - (nawmsl + nawmsp + nruncon + nfencing + nagbuffer)
    return result


def N7b_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGAppNRate, NGPctSoilIncRate, GRAppNRate,
          GRPctSoilIncRate, GrazingNRate, GRPctManApp, PctGrazing, GRBarnNRate,
          Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h, NGPctManApp, AWMSNgPct,
          NGBarnNRate, NgAWMSCoeffN, n41d, n85j, n41f, n85l, PctStreams, n42, n45, n69, n43, n64):
    av_animal_n_sum = AvAnimalNSum_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                                     NGAppNRate, Prec, DaysMonth, NGPctSoilIncRate, GRPctManApp, GRAppNRate,
                                     GRPctSoilIncRate, NGBarnNRate, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN,
                                     PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, GrazingNRate)
    nawmsl = NAWMSL_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                      GRBarnNRate,
                      Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, n41b, n85h)
    nawmsp = NAWMSP_2(NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, NGBarnNRate,
                      Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN, n41d, n85j)
    nruncon = NRUNCON_2(NYrs, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, GRPctManApp, PctGrazing,
                        GRBarnNRate,
                        Prec, DaysMonth, AWMSGrPct, GrAWMSCoeffN, RunContPct, RunConCoeffN, NGPctManApp, NGBarnNRate,
                        AWMSNgPct, NgAWMSCoeffN, n41f, n85l)
    nfencing = NFENCING_2(PctStreams, PctGrazing, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN, n42, n45, n69)
    nagbuffer = NAGBUFFER_2(n42, n43, n64, NYrs, NGPctManApp, Grazinganimal_0, NumAnimals, AvgAnimalWt, AnimalDailyN,
                            NGBarnNRate, Prec, DaysMonth, AWMSNgPct, NgAWMSCoeffN, RunContPct, RunConCoeffN,
                            GRPctManApp,
                            PctGrazing, GRBarnNRate, AWMSGrPct, GrAWMSCoeffN, PctStreams, NGAppNRate, NGPctSoilIncRate,
                            GRAppNRate, GRPctSoilIncRate, GrazingNRate)
    result = av_animal_n_sum - (nawmsl + nawmsp + nruncon + nfencing + nagbuffer)
    return result
