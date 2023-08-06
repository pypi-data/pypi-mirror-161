# -*- coding: utf-8 -*-
"""
IRIS Validation Rules, taken from:
https://github.com/iris-edu/stationxml-validator/wiki/StationXML-Validation-Rule-List

:copyright:
    Mike Hagerty (m.hagerty@isti.com), 2020-2022
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

type_Error = 'Error'
type_Warning = 'Warning'
PASS = "PASS"

test_xmls = {
    '101' : ['F1_101.xml'],
    '110' : ['F1_110.xml', 'F2_110.xml'],
    '111' : ['F1_111.xml'],
    '112' : ['F1_112.xml', 'P1_112.xml'],
    '201' : ['F1_201.xml'],
    '210' : ['F1_210.xml', 'F2_210.xml'],
    '211' : ['F1_211.xml'],
    '212' : ['F1_212.xml'],
    '222' : ['F1_222.xml'],
    '223' : ['F1_223.xml'],
    '301' : ['F1_301.xml'],
    '302' : ['F1_302.xml'],
    '303' : ['F1_303.xml'],
    '304' : ['F1_304.xml'],
    '305' : ['F1_305.xml', 'F2_305.xml', 'P1_305.xml'],
    '310' : ['F1_310.xml', 'F2_310.xml'],
    '320' : ['F1_320.xml'],
    '321' : ['F1_321.xml'],
    '332' : ['F1_332.xml', 'P1_332.xml', 'P2_332.xml', 'P3_332.xml', 'P4_332.xml'],
    # MTH: F1_333 and F1_334 don't exist in repo yet!
    #'333' : ['F1_332.xml', 'P1_332.xml', 'P2_332.xml', 'P3_332.xml', 'P4_332.xml'],
    #'334' : ['F1_332.xml', 'P1_332.xml', 'P2_332.xml', 'P3_332.xml', 'P4_332.xml'],
    # 2020-11-11 Tim Ronan supplied 333/334 files not yet in repo:
    '333' : ['F1_333.xml'],
    '334' : ['F1_334.xml'],
    '401' : ['F1_401.xml'],
    '402' : ['F1_402.xml'],
    '403' : ['F1_403.xml', 'F2_403.xml'],
    '404' : ['F1_404.xml', 'F2_404.xml', 'F3_404.xml', 'F4_404.xml', 'P1_404.xml'],
    '405' : ['F1_405.xml', 'P1_405.xml'],
    '410' : ['F1_410.xml', 'F2_410.xml'],
    '411' : ['F1_411.xml'],
    '412' : ['F1_412.xml'],
    '413' : ['F1_413.xml'],
    '414' : ['F1_414.xml', 'F2_414.xml', 'F3_414.xml', 'P1_414.xml'],
    '415' : ['F1_415.xml', 'P1_415.xml', 'P2_415.xml'],
    '416' : ['F1_416.xml'],
    '420' : ['F1_420.xml'],
    '421' : ['F1_421.xml'],
    '422' : ['F1_422.xml'],
    '423' : ['F1_423.xml'],
}

restrictions = {
  # Network
  # Station
  # Channel
    'C1' : {'description' : "The channels indicated do not trigger validation tests subject to this",
            'key' : "Channel:Code",
            #'immune' : ["SOH", "ACE", "OCF", "LOG", "VCE", "LCE", "LCQ","VCO", "VEA", "VEC", "VEP", "VKI",
                        #"VM1", "VM2", "VM3", "VPB"],
            'immune' : ["ACE", "ATC", "BDO", "EX1", "EX2", "EX3", "EX4", "EX5", "EX6", "EX7", "EX8", "EX9",
                        "GAN", "GEL", "GLA", "GLO", "GNS", "GPL", "GPS", "GST", "LCA", "LCB", "LCC", "LCD",
                        "LCE", "LCF", "LCG", "LCH", "LCI", "LCJ", "LCK", "LCL", "LCM", "LCN", "LCO", "LCP",
                        "LCQ", "LCR", "LCS", "LCT", "LCU", "LCV", "LCW", "LCX", "LCY", "LCZ", "LDE", "LDN",
                        "LDZ", "LEE", "LED", "LEO", "LEP", "LII", "LKI", "LOG", "LPL", "OAC", "OCF", "QBD",
                        "QBP", "QDG", "QDL", "QDR", "QEF", "QG1", "QGD", "QID", "QLD", "QPD", "QRD", "QRT",
                        "QTP", "QTH", "QTP", "QWD", "SBT", "SCA", "SCB", "SCC", "SCD", "SCE", "SCF", "SCG",
                        "SCH", "SCI", "SCJ", "SCK", "SCL", "SCM", "SCN", "SCO", "SCP", "SCQ", "SCR", "SCS",
                        "SCT", "SCU", "SCV", "SCW", "SCX", "SCY", "SCZ", "SDG", "SDL", "SDT", "SIO", "SOH",
                        "SMD", "SNI", "SPK", "SPO", "SRD", "SSL", "SSQ", "STH", "SWR", "TSA", "TSB", "TSC",
                        "TSD", "TSE", "TSF", "TSG", "TSH", "TSI", "TSJ", "TSK", "TSL", "TSM", "TSN", "TSO",
                        "TSP", "TSQ", "TSR", "TSS", "TST", "TSU", "TSV", "TSW", "TSX", "TSY", "TSZ", "TS0",
                        "TS1", "TS2", "TS3", "TS4", "TS5", "TS6", "TS7", "TS8", "TS9", "VAP", "VCE", "VCO",
                        "VCQ", "VDT", "VEA", "VEB", "VEC", "VED", "VEE", "VEF", "VEG", "VEH", "VEI", "VEJ",
                        "VEK", "VEL", "VEM", "VEN", "VEO", "VEP", "VEQ", "VER", "VES", "VET", "VEU", "VEV",
                        "VEW", "VEX", "VEY", "VEZ", "VFP", "VKI", "VPB", "VMA", "VMB", "VMC", "VMD", "VME",
                        "VMF", "VMG", "VMH", "VMI", "VMJ", "VMK", "VML", "VMM", "VMN", "VMO", "VMP", "VMQ",
                        "VMR", "VMS", "VMT", "VMU", "VMV", "VMW", "VMX", "VMY", "VMZ", "VM0", "VM1", "VM2",
                        "VM3", "VM4", "VM5", "VM6", "VM7", "VM8", "VM9", "VPB",
                        ],
            },
    'C2' : {'description' : "The channel types indicated do not trigger validation tests subect to this",
            'key' : "Channel:Type",
            'immune' : ["HEALTH", "FLAG", "MAINTENANCE"],
            },
  # Response
    'R1' : {'description' : "Channels containing Response:InstrumentPolynomial at stage 0 do not trigger",
            'key' : "Response",
            },
}

error_codes = {
  # Network Definition Errors
    '101' : {'description' : "Network:Code must be assigned a string consisting of 1-2 uppercase "
                             "characters A-Z and or numeric characters 0-9.",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Network Time Errors
    #'110' : {'description' : "Network:startDate is required and must occur before Network:endDate if "
                             #"Network:endDate is available. [112]",
    '110' : {'description' : "If Network:startDate is included then it must occur before Network:endDate if "
                             "Network:endDate is included. [112]",
             'type' : type_Error,
             'restrictions' : [],
            },
    '111' : {'description' : "Station:Epoch cannot be partly concurrent with any other Station:Epoch "
                             "encompassed in parent Network:Epoch.",
             'type' : type_Error,
             'restrictions' : [],
            },
    '112' : {'description' : "Network:Epoch must encompass all subordinate Station:Epoch "
                             "[Epoch=startDate-endDate]. [110, 210]",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Station Definition Errors
    '201' : {'description' : "Station:Code must be assigned a string consisting of 1-5 uppercase "
                             "characters A-Z and or numeric characters 0-9.",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Station Time Errors
    #'210' : {'description' : "Station:startDate is required and must occur before Station:endDate if "
                             #"Station:endDate is available. [112, 212]",
    '210' : {'description' : "Station:startDate must be included and must occur before Station:endDate if "
                             "Station:endDate is included. [112, 212]",
             'type' : type_Error,
             'restrictions' : [],
            },
    '211' : {'description' : "Channel:Epoch cannot be partly concurrent with any other Channel:Epoch "
                             "encompassed in parent Station:Epoch.",
             'type' : type_Error,
             'restrictions' : [],
            },
    '212' : {'description' : "Station:Epoch must encompass all subordinate Channel:Epoch "
                             "[Epoch=startDate-endDate]. [210]",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Station Position Errors
    # The next 2 have been removed - presumably because the are already enforced
    #   by FDSNStationXML schema:
    #'220' : {'description' : "Station:Latitude must be assigned a value between -90 and 90.",
             #'type' : type_Error,
             #'restrictions' : [],
            #},
    #'221' : {'description' : "Station:Longitude must be assigned a value between -180 and 180.",
             #'type' : type_Error,
             #'restrictions' : [],
            #},
    '222' : {'description' : "Station:Position must be within 1 km of all subordinate Channel:Position.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    '223' : {'description' : "Station:Elevation must be within 1 km of all subordinate Channel:Elevation.",
             #'type' : type_Error,
             'type' : type_Warning,
             'restrictions' : ['C1','C2'],
            },
  # Channel Definition Errors
    '301' : {'description' : "Channel:Code must be assigned a string consisting of 3 uppercase characters "
                             "A-Z and or numeric characters 0-9.",
             'type' : type_Error,
             'restrictions' : [],
            },
    #'302' : {'description' : "Channel:locationCode must be unassigned or be assigned a string consisting of "
                             #"1-2 uppercase alphabetic [A-Z] and or numeric characters [0-9].",
    '302' : {'description' : "Channel:locationCode must be assigned a string consisting of "
                             "0-2 uppercase alphabetic [A-Z] and or numeric characters [0-9] "
                             "OR 2 whitespace characters OR --",
             'type' : type_Error,
             'restrictions' : [],
            },
    #'303' : {'description' : "CalibrationUnits:Name is not defined in Unit name overview for "
                             #"IRIS StationXML validator.",
    '303' : {'description' : "If CalibrationUnits are included then CalibrationUnits:Name must be assigned "
                             "a value from the IRIS StationXML Unit dictionary. "
                             "Case inconsistencies trigger a warning only",
             'type' : type_Error,
             'restrictions' : [],
            },
    #'304' : {'description' : "Channel:Sensor:Description cannot be null.",
    '304' : {'description' : "Channel:Sensor:Description must be included and assigned a string consisting "
                             "of at least 1 - case insensitive A-Z and numeric 0-9 characters.",
             'type' : type_Error,
             'restrictions' : [],
            },
    #'305' : {'description' : "If Channel:SampleRate equals 0 then Response information should not be included. "
    '305' : {'description' : "If Channel:SampleRate equals 0 or is not included then "
                             "Response information must not be included. "
                             "[411, 421]",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Channel Time Errors
    #'310' : {'description' : "Channel:startDate is required and must occur before Channel:endDate if "
                             #"Channel:endDate is available.",
    '310' : {'description' : "Channel:startDate must be included and must occur before Channel:endDate "
                             "if Channel:endDate is included.",
             'type' : type_Error,
             'restrictions' : [],
            },
  # Channel Position Errors
    #'320' : {'description' : "Channel:Latitude must be assigned a value between -90 and 90.",
    '320' : {'description' : "If Channel:Code[2]==(H | L | M | N) then Channel:Azimuth and "
                             "Channel:Dip must be included.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    # MTH: 2022-07-22 - 'N' is often used for accelerometer sensor and shoulnd't be here !
    #'321' : {'description' : "Channel:Longitude must be assigned a value between -180 and 180.",
    #'321' : {'description' : "If Channel:Code[2] == (H | L | M | N) then Stage[1]:InputUnit must "
    '321' : {'description' : "If Channel:Code[2] == (H | L | M ) then Stage[1]:InputUnit must "
                             "equal *m/s* AND Stage[Last]:OutputUnits must equal count*",
             'type' : type_Warning,
             'restrictions' : ['C1','C2'],
            },
  # Channel Orientation Errors
    #'330' : {'description' : "Azimuth must be assigned a value between 0 and 360.",
             #'type' : type_Error,
             #'restrictions' : ['C1','C2'],
            #},
    #'331' : {'description' : "Dip must be assigned a value between -90 and 90.",
             #'type' : type_Error,
             #'restrictions' : ['C1','C2'],
            #},
    #'332' : {'description' : "Channel:Azimuth and or Channel:Dip do not correspond, within 5 degrees "
                             #"of tolerance, to last digit of orthogonal Channel:Code.",
             #'type' : type_Warning,
             #'restrictions' : ['C1','C2'],
            #},
    '332' : {'description' : "If Channel:Code[LAST]==N then Channel:Azimuth must be assigned "
                             "(>=355.0 or <=5.0) or (>=175.0 and <=185.0) and Channel:Dip must "
                             "be assigned (>=-5 AND <=5.0).",
             'type' : type_Warning,
             'restrictions' : ['C1','C2'],
            },
    # 333 and 334 are Missing from repo
    '333' : {'description' : "If Channel:Code[LAST]==E then Channel:Azimuth must be assigned "
                             "(>=85.0 and <=95.0) or (>=265.0 and <=275.0) and Channel:Dip must "
                             "be ASSIGNED (>=-5.0 and <=5.0).",
             'type' : type_Warning,
             'restrictions' : ['C1','C2'],
            },
    '334' : {'description' : "If Channel:Code[LAST]==Z then Channel:Azimuth must be assigned "
                             "(>=355.0 or <=5.0) and Channel:Dip must be assigned "
                             "(>=-85.0 and <=-90.0) or (>=85.0 and <=90.0).",
             'type' : type_Warning,
             'restrictions' : ['C1','C2'],
            },

  # Response Stage Errors
    '401' : {'description' : "Stage:number must start at 1 and be sequential.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    #'402' : {'description' : "Stage[N]:InputUnits:Name and/or Stage[N]:OutputUnits:Name are not defined in Unit "
                             #"name overview for IRIS StationXML validator. Capitalized unit names trigger warnings.",
    '402' : {'description' : "Stage[N]:InputUnits:Name and Stage[N]:OutputUnits:Name must be assigned "
                             "a value from the IRIS StationXML Unit dictionary, case inconsistencies "
                             "trigger warnings.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    #'403' : {'description' : "Stage[N]:InputUnits:Name must equal Stage[N-1]:OutputUnits:Name.",
    '403' : {'description' : "If length(Stage) > 1 then Stage[N]:InputUnits:Name must equal "
                             "Stage[N-1]:OutputUnits:Name.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    #'404' : {'description' : "Stage types FIR, Coefficient, or PolesZeros with transfer function type Digital "
                             #"must include Decimation and StageGain elements. [420]",
    '404' : {'description' : "If Stage[N]:PolesZeros:PzTransferFunctionType:Digital or Stage[N]:FIR or "
                             "Stage[N]:Coefficients:CfTransferFunctionType:DIGITAL are included then "
                             "Stage[N] must include Stage[N]:Decimation and Stage[N]:StageGain elements.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    '405' : {'description' : "Stage of type ResponseList cannot be the only stage included in a response. [420]",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },

    # ResponseType and StageGain Errors
    #'410' : {'description' : "InstrumentSensitivity:Value cannot be unassigned or assigned 0 or Null. [412,415]",
    '410' : {'description' : "If InstrumentSensitivity is included then InstrumentSensitivity:Value must be "
                             "assigned a double > 0.0.",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    #'411' : {'description' : "InstrumentSensitivity:Frequency must be less than Channel:SampleRate/2 "
                             #"[Nyquist Frequency]. [305]",
    '411' : {'description' : "If InstrumentSensitivity is included then InstrumentSensitivity:Frequency must "
                             "be assigned a double < Channel:SampleRate/2 [Nyquist Frequency].",
             'type' : type_Warning,
             'restrictions' : ['C1','C2','R1'],
            },
    '412' : {'description' : "InstrumentSensitivity:Value must equal the product of all StageGain:Value if all "
                             "StageGain:Frequency are equal to InstrumentSensitivity:Frequency [Normalization Frequency]. [410]",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    #'413' : {'description' : "StageGain:Value cannot be assigned 0 or Null. [404,405,415]",
    '413' : {'description' : "All Stages must include StageGain:Value assigned as a double > 0.0 and "
                             "StageGain:Frequency assigned as a double.",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    '414' : {'description' : "If Stage[N] of type PolesZeros contains a Zero where both Real and Imaginary "
                             "components equal 0 then InstrumentSensitivity:Frequency cannot equal 0 or "
                             "Stage[N]:StageGain:Frequency cannot equal 0. [420]",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    #'415' : {'description' : "Response must be of type InstrumentPolynomial if a Polynomial stage exist. [410,413,420]",
    '415' : {'description' : "If 1 or more Polynomial stages are included then the Response must also include "
                             "an InstrumentPolynomial stage",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    '416' : {'description' : "Response must include InstrumentSensitivity if no Polynomial stages are included.",
             'type' : type_Error,
             'restrictions' : ['C1','C2'],
            },
    '420' : {'description' : "A Response must contain at least one instance of Response:Stage:Decimation. [404,405,414,415]",
             'type' : type_Warning,
             'restrictions' : ['C1','C2','R1'],
            },
    #'421' : {'description' : "Stage[Final]:Decimation:InputSampleRate divided by Stage[Final]:Decimation:Factor "
                             #"must equal Channel:SampleRate. [305]",
    '421' : {'description' : "Stage[LAST]:Decimation:InputSampleRate divided by Stage[LAST]:Decimation:Factor "
                             "must equal Channel:SampleRate.",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    '422' : {'description' : "Stage[N]:Decimation:InputSampleRate must equal Stage[N-1]:Decimation:InputSampleRate "
                             "divided by Stage[N-1]:Decimation:Factor.",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },
    '423' : {'description' : "If Decimation and StageGain are included in Stage[N] then PolesZeros or "
                             "Coefficients or ResponseList or FIR must also be included in Stage[N].",
             'type' : type_Error,
             'restrictions' : ['C1','C2','R1'],
            },

}
