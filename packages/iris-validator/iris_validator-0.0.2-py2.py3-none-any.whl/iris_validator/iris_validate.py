# -*- coding: utf-8 -*-
"""
stationxml_validator class and associated functions
for verifying stationxml against each rule

:copyright:
    Mike Hagerty (m.hagerty@isti.com), 2020-2022
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

import os
import re
import sys

import numpy as np

import logging as logger
logger.basicConfig(level=logger.WARN)

import obspy
#from obspy import read_inventory
from obspy.io.stationxml.core import _read_stationxml
from . import installation_dir

from obspy.core.inventory.response import PolesZerosResponseStage, FIRResponseStage
from obspy.core.inventory.response import ResponseStage, CoefficientsTypeResponseStage
from obspy.core.inventory.response import PolynomialResponseStage
from obspy.core.inventory.response import InstrumentPolynomial
from obspy.core.inventory.response import InstrumentSensitivity
from obspy.core.inventory.response import ResponseListResponseStage
from obspy.geodetics import gps2dist_azimuth

from .iris_rules import error_codes, restrictions, test_xmls
from .iris_unit_names import unit_names
unit_names_lower = [x.lower() for x in unit_names]

class epoch():
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return f'[{self.start_date} - {self.end_date}]'


SEISMIC_UNITS = {
            "meter", "m", "m/s", "m/s**2",
            "centimeter", "cm", "cm/s", "cm/s**2",
            "millimeter", "mm", "mm/s", "mm/s**2", "mm/hour",
            "micrometer", "um", "um/s", "um/s**2",
            "nanometer", "nm", "nm/s", "nm/s**2",
            }

DIGITAL_UNITS = {'count', 'counts'}

indent = 8 * ' '

non_traditional_orientations = "%s1 — Channel Azimuth is greater than 5 degrees from north (Reversed: south).\n" \
                               "%s2 — Channel Azimuth is greater than 5 degrees from east (Reversed: west).\n" \
                               "%s3 — Channel Dip is greater than 5 degrees from vertical.\n" % \
                                (indent, indent, indent)

class stationxml_validator():
    '''
    Class to read stationxml into Inventory (if necessary) and validate inventory
    '''

    station_code = None

    def __init__(self, stationxml_or_inventory, kwargs=None, ignore=[]):
        #self.stationxml = stationxml
        self.errors = []
        self.warnings = []
        self.return_codes = []

        self.inv = None

        self.ignore = ignore

        if isinstance(stationxml_or_inventory, obspy.core.inventory.inventory.Inventory):
            self.stationxml = None
            self.inv = stationxml_or_inventory
        else:
            self.stationxml = stationxml_or_inventory
            logger.debug("stationxml_validator: attempt to read file=[%s]" % self.stationxml)
            try:
                self.inv = _read_stationxml(self.stationxml)
            except Exception as ex:
                template = "read_inventory: An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
        if kwargs:
            self.inv = self.inv.select(**kwargs)

    def validate_inventory(self):
        if self.inv is None:
            print("Unable to validate_inventory as it wasn't read properly")
            return

        for network in self.inv.networks:
            print("validate network:%s on:%s off:%s" % (network.code, network.start_date, network.end_date))
            self.validate_network(network)
            for station in network.stations:
                #print("  validate station:%s on:%s off:%s" % (station.code, station.start_date, station.end_date))
                self.station_code = station.code[:]
                self.validate_station(station)
                for channel in station.channels:
                    #print("validate channel")
                    #print("validate channel=%s sr:%f" % (channel.code, channel.sample_rate))
                    #print("    validate channel:%s loc:%s on:%s off:%s" %
                          #(channel.code, channel.location_code, channel.start_date, channel.end_date))
                    self.validate_channel(channel, self.station_code, network.code)
                    if channel.response:
                        #print("validate response")
                        self.validate_response(channel, self.station_code, network.code)

    def validate_network(self, network):
        for rule_code in get_rules(level='network'):
            if int(rule_code) in self.ignore:
                logger.info("ignore rule:%s" % rule_code)
                continue
            func_name = "self.validate_rule_%s" % rule_code
            logger.debug("call func:%s for net code:%s" % (func_name, network.code))
            eval(func_name)(network)
        return

    def validate_station(self, station):
        for rule_code in get_rules(level='station'):
            if int(rule_code) in self.ignore:
                logger.info("ignore rule:%s" % rule_code)
                continue
            func_name = "self.validate_rule_%s" % rule_code
            logger.debug("call func:%s for stn code:%s" % (func_name, station.code))
            eval(func_name)(station)
        return

    def validate_channel(self, channel, sta, net):
        for rule_code in get_rules(level='channel'):
            if int(rule_code) in self.ignore:
                logger.info("ignore rule:%s" % rule_code)
                continue
            func_name = "self.validate_rule_%s" % rule_code
            #msg = msg_hdr(sta, channel)
            #print("rule_code:%s msg_hdr:%s" % (rule_code, msg))
            if enforce_rule(channel, rule_code):
                logger.debug("call func:%s for chn code:%s" % (func_name, channel.code))
                eval(func_name)(channel, msg_hdr=msg_hdr(net, sta, channel))
            else:
                logger.debug("Rule:[%s] --> Skip Chn:%s" % (rule_code, channel.code))
        return

    def validate_response(self, channel, sta, net):
        for rule_code in get_rules(level='response'):
            if int(rule_code) in self.ignore:
                logger.info("ignore rule:%s" % rule_code)
                continue
            func_name = "self.validate_rule_%s" % rule_code
            if enforce_rule(channel, rule_code):
                logger.debug("call func:%s for chn code:%s" % (func_name, channel.code))
                #eval(func_name)(channel)
                eval(func_name)(channel, msg_hdr=msg_hdr(net, sta, channel))
            else:
                logger.debug("Rule:[%s] --> Skip Chn:%s" % (rule_code, channel.code))
        return

    def validate_rule(self, rule_code):
        """
        Now is the time
        """
        func_name = "self.validate_rule_%s" % rule_code

        if rule_code not in error_codes.keys():
            logger.error("validate_rule: Unknown rule_code:%s" % rule_code)
            return

        if rule_code[0] == '1':
            for network in self.inv.networks:
                eval(func_name)(network)
        elif rule_code[0] == '2':
            for network in self.inv.networks:
                for station in network.stations:
                    eval(func_name)(station)
        elif rule_code[0] in ['3', '4']:
            for network in self.inv.networks:
                for station in network.stations:
                    for channel in station.channels:
                        eval(func_name)(channel)
        return

    #   <-- Network Definition Errors -->

    def validate_rule_101(self, network):
        """101 Network:Code must be assigned a string consisting of 1-2 uppercase characters A-Z and or
               numeric characters 0-9.
        """

        rule_code = '101'
        #print("Inside validate_rule_101 network.code=[%s]" % network.code)
        if not valid_ascii(network.code, 1, 2):
            msg = "Invalid network code: [%s]" % network.code
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    # <-- Network Time Errors -->

    def validate_rule_110(self, network):
        """110 If Network:startDate is included then it must occur before Network:endDate if
               Network:endDate is included. [112]
        """

        rule_code = '110'
        if network.start_date is None or network.end_date is None:
            return True
        if network.end_date <= network.start_date:
            msg = "Network:%s invalid start_date=%s >= end_date=%s" % \
                    (network.code, network.start_date, network.end_date)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    def validate_rule_111(self, network):
        """111 Station:Epoch cannot be partly concurrent with any other Station:Epoch
               encompassed in parent Network:Epoch.
        """

        rule_code = '111'
        epoch_dict = {}
        overlapping = False
        for station in network.stations:
            key = station.code
            if key not in epoch_dict:
                epoch_dict[key] = []
            epoch_dict[key].append(epoch(station.start_date, station.end_date))

        for stn in epoch_dict:
            epochs = epoch_dict[stn]
            epochs.sort(key=lambda x: x.start_date, reverse=False)

            overlaps = overlapping_epochs(epochs)
            if overlaps:
                overlapping = True
                msg = "network:%s station:%s contains overlapping epochs" % (network.code, stn)
                self.errors.append((print_error(rule_code), msg))
                for overlap in overlaps:
                    self.errors.append("             epoch:[%s]" % overlap)
                self.return_codes.append(rule_code)
        if overlapping:
            return False
        else:
            return True

    def validate_rule_112(self, network):
        """112 Network:Epoch must encompass all subordinate Station:Epoch [Epoch=startDate-endDate]. [110, 210]"""

        rule_code = '112'

        (earliest_start_date, latest_end_date) = get_first_start_last_end_dates(network.stations)

        passed = True

        if network.start_date is not None:
            if network.start_date > earliest_start_date:
                msg = "Network:%s start_date=%s > earliest station_start_date=%s" % \
                        (network.code, network.start_date, earliest_start_date)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        if network.end_date is not None:
            if network.end_date < latest_end_date:
                msg = "Network:%s end_date=%s < latest station_end_date=%s" % \
                        (network.code, network.end_date, latest_end_date)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

    def validate_rule_112_OLD(self, network):
        """112 Network:Epoch must encompass all subordinate Station:Epoch [Epoch=startDate-endDate]. [110, 210]"""

        rule_code = '112'
        if network.start_date is None:
            msg = "Network:%s startDate not set --> Can't validate [112]" % network.code
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        (earliest_start_date, latest_end_date) = get_first_start_last_end_dates(network.stations)

        #MTH: if endDates are not set in the Station or Channel xml, latest_end_date will be None
        #     This could cause problems later if it's compare to another None object using '<'
        #if latest_end_date is None:
            #print("endDate is None!")

        if network.end_date is None:
            if network.start_date <= earliest_start_date:
                return True
            else:
                msg = "Network:%s start_date=%s > earliest station_start_date=%s" % \
                        (network.code, network.start_date, earliest_start_date)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False
        else:
            if network.start_date <= earliest_start_date and network.end_date >= latest_end_date:
                return True
            else:
                self.errors.append(print_error(rule_code))
                self.errors.append("        Network:%s does not encompass station epochs" % network.code)
                self.errors.append("        network epochs:[%s - %s]" % (network.start_date, network.end_date))
                self.errors.append("        station epochs:[%s - %s]" % (earliest_start_date, latest_end_date))
                self.return_codes.append(rule_code)
                return False

    # <-- Station Definition Errors -->

    def validate_rule_201(self, station):
        """201 Station:Code must be assigned a string consisting of 1-5 uppercase characters A-Z and or
               numeric characters 0-9.
        """
        rule_code = '201'
        if not valid_ascii(station.code, 1, 5):
            msg = "Invalid station code: [%s]" % station.code
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    # <-- Station Time Errors -->

    def validate_rule_210(self, station):
        """210 Station:startDate is required and must occur before Station:endDate
               if Station:endDate is available. [112, 212]
        """
        rule_code = '210'
        if station.start_date is None:
            msg = "station:%s startDate is not set" % station.code
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        if station.end_date and station.end_date <= station.start_date:
            msg = "station:%s start_date=[%s] >= end_date=[%s]" % \
                    (station.code, station.start_date, station.end_date)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        return True

    def validate_rule_211(self, station):
        """211 Channel:Epoch cannot be partly concurrent with any other Channel:Epoch encompassed
               in parent Station:Epoch.
        """
        rule_code = '211'
        pass_test = True
        if getattr(station, 'channels', None) is None or station.channels is None:
            msg = "station:%s contains 0 channels --> Can't validate [%s]" % (station.code, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return True

        epoch_dict = {}
        for channel in station.channels:
            if channel.start_date is None:
                msg = "station:%s channel:%s.%s has empty start_date --> Can't sort/test epochs!" % \
                    (station.code, channel.location_code, channel.code)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
            else:
                key = "%s.%s" % (channel.location_code, channel.code)
                if key not in epoch_dict:
                    epoch_dict[key] = []
                epoch_dict[key].append(epoch(channel.start_date, channel.end_date))

        for chan in epoch_dict:
            epochs = epoch_dict[chan]
            epochs.sort(key=lambda x: x.start_date, reverse=False)
            overlaps = overlapping_epochs(epochs)
            if overlaps:
                pass_test = False
                msg = "station:%s channel:%s has overlapping epochs" % (station.code, chan)
                self.return_codes.append(rule_code)
                self.errors.append((print_error(rule_code), msg))
                self.errors.append("        Station:%s Chan:%s has overlapping epochs" % (station.code, chan))
                for overlap in overlaps:
                    self.errors.append("        epoch:[%s]" % overlap)

        return pass_test


    def validate_rule_212(self, station):
        """212 Station:Epoch must encompass all subordinate Channel:Epoch [Epoch=startDate-endDate]. [210]
        """
        rule_code = '212'
        if station.start_date is None:
            msg = "station:%s startDate is not set --> Can't validate [%s]" % (station.code, rule_code)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        if getattr(station, 'channels', None) is None or not station.channels:
            msg = "station:%s contains 0 channels --> Can't validate [%s]" % (station.code, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        (earliest_start_date, latest_end_date) = get_first_start_last_end_dates(station.channels)

        passed = True

        if station.start_date > earliest_start_date:
            msg = "Station:%s start_date=%s > earliest channel_start_date=%s" % \
                    (station.code, station.start_date, earliest_start_date)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            passed = False

        if station.end_date is not None:
            if station.end_date < latest_end_date:
                msg = "Station:%s end_date=%s < latest channel_end_date=%s" % \
                        (station.code, station.end_date, latest_end_date)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

    def validate_rule_212_OLD(self, station):
        """212 Station:Epoch must encompass all subordinate Channel:Epoch [Epoch=startDate-endDate]. [210]
        """
        rule_code = '212'
        if station.start_date is None:
            msg = "station:%s startDate is not set --> Can't validate [%s]" % (station.code, rule_code)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        if getattr(station, 'channels', None) is None or not station.channels:
            msg = "station:%s contains 0 channels --> Can't validate [%s]" % (station.code, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        (earliest_start_date, latest_end_date) = get_first_start_last_end_dates(station.channels)

        if station.end_date is None:
            if station.start_date <= earliest_start_date:
                return True
            else:
                msg = "Station:%s start_date=%s >= earliest channel_start_date=%s" % \
                        (station.code, station.start_date, earliest_start_date)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False
        else:
            if station.start_date <= earliest_start_date and station.end_date >= latest_end_date:
                return True
            else:
                self.errors.append(print_error(rule_code))
                self.errors.append("        Station:%s does not encompass channel epochs" % station.code)
                self.errors.append("        station epochs:[%s - %s]" % (station.start_date, station.end_date))
                self.errors.append("        channel epochs:[%s - %s]" % (earliest_start_date, latest_end_date))
                self.return_codes.append(rule_code)
                return False

    # <-- Station Position Errors -->

    # MTH: Rules 220 & 221 are deprecated since station latitude/longitude are
    #      already checked in the FDSN schema

    def validate_rule_220(self, station):
        """220 Station:Latitude must be assigned a value between -90 and 90."""
        rule_code = '220'
        if station.latitude is None or station.latitude < -90. or station.latitude >= 90.:
            msg = "station:%s invalid latitude:%s" % (station.code, station.latitude)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    def validate_rule_221(self, station):
        """221 Station:Longitude must be assigned a value between -180 and 180."""
        rule_code = '221'
        if station.longitude is None or station.longitude < -180. or station.longitude > 180.:
            msg = "station:%s invalid longitude:%s" % (station.code, station.longitude)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    def validate_rule_222(self, station):
        """222 Station:Position must be within 1 km of all subordinate Channel:Position. Restrictions 'C1', 'C2'"""
        rule_code = '222'

        passed = True

        for channel in station.channels:
            if getattr(channel, 'latitude', None) and getattr(channel, 'longitude', None):
                distaz = gps2dist_azimuth(station.latitude, station.longitude, channel.latitude, channel.longitude)
                dist = distaz[0]/1000.  # Dist in m --> km
                azim = distaz[1]
                baz  = distaz[2]

                if dist > 1.:
                    msg = "Sta:%s Cha:%s Loc:%s On:%s Off:%s Channel is separated by %.1f km (> 1km) from Station!" % \
                            (station.code, channel.code, channel.location_code, channel.start_date,
                             channel.end_date, dist)
                    self.errors.append((print_error(rule_code), msg))
                    self.return_codes.append(rule_code)
                    msg = "        station lat:%.4f lon:%.4f vs channel lat:%.4f lon:%.4f" % \
                            (station.latitude, station.longitude, channel.latitude, channel.longitude)
                    #self.errors.append(('', msg))
                    self.errors.append((msg,))

                    passed = False
            else:
                msg = "Station:%s Chan:%s - Channel does not have latitude/longitude set --> Can't validate Rule:%s" % \
                       (station.code, channel.code, rule_code)
                self.warnings.append((print_error(rule_code), msg))
                passed = False

        return passed

    def validate_rule_223(self, station):
        """223 Station:Elevation must be within 1 km of all subordinate Channel:Elevation.. Restrictions 'C1', 'C2'"""
        rule_code = '223'

        passed = True

        for channel in station.channels:
            if getattr(channel, 'elevation', None):
                # MTH: elevation should be in METERS for both station/channel
                dist = np.abs(station.elevation - channel.elevation)
                if dist > 1e3:
                    #msg = "Station:%s Chan:%s - Channel depth is separated > 1km from Station!" % \
                            #(station.code, channel.code)
                    msg = "Sta:%s Cha:%s On:%s Off:%s - Channel depth=%.1f is separated > 1km from Station!" % \
                            (station.code, channel.code, fix_date(channel.start_date),
                             fix_date(channel.end_date), dist)
                    self.warnings.append((print_error(rule_code), msg))
                    passed = False
            else:
                msg = "Station:%s Chan:%s - Channel does not have elevation set --> Can't validate Rule:%s" % \
                       (station.code, channel.code, rule_code)
                self.warnings.append((print_error(rule_code), msg))
                passed = False

        return passed

    # <-- Channel Definition Errors -->

    def validate_rule_301(self, channel, msg_hdr=''):
        """301 Channel:Code must be assigned a string consisting of 3 uppercase characters A-Z
               and or numeric characters 0-9.
        """
        rule_code = '301'
        if not valid_ascii(channel.code, 3, 3):
            msg = msg_hdr + "invalid channel code has len=%d != 3" % (len(channel.code))
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        return True

    def validate_rule_302(self, channel, msg_hdr=''):
        """302 Channel:locationCode must be assigned a string consisting of 0-2 uppercase A-Z and numeric 0-9
               characters OR 2 whitespace characters OR --.
        """
        rule_code = '302'
        exceptions = ["  ", "--"]
        if getattr(channel, 'location_code', None) and not valid_ascii(channel.location_code, 0, 2):
            if channel.location_code in exceptions:
                pass
            else:
                msg = msg_hdr + "invalid channel_location code: [%s]" % (channel.location_code)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False

        return True

    def validate_rule_303(self, channel, msg_hdr=''):
        """303 If CalibrationUnits are included then CalibrationUnits:Name must be assigned
               a value from the IRIS StationXML Unit dictionary, case inconsistencies trigger warnings.
        """
        rule_code = '303'
        if getattr(channel, 'calibration_units', None):
            cal_units = channel.calibration_units
            if cal_units not in unit_names:
                if cal_units.lower() in unit_names_lower:
                    msg = msg_hdr + "calibration_units [%s] not in unit_names but lowercase is" % cal_units
                    self.warnings.append((print_error(rule_code), msg))
                else:
                    msg = msg_hdr + "calibration_units [%s] not in unit_names" % cal_units
                    self.errors.append((print_error(rule_code), msg))
                    self.return_codes.append(rule_code)
                    return False

        return True

    # MTH: I'm not sure about this: seems like you could have a channel without a sensor
    # 304 Channel:Sensor:Description cannot be null.

    # 1. If we read in a stationxml with empty sensor description using read_inventory,
    #          then obspy will set sensor.description = "None" <str>
    # 2. If someone creates an inv on the fly with empty sensor description,
    #          then obspy will set sensor.description = None <NoneType>
    # So we need to test for both

    # Jan 2020 Update to IRIS validation rules:
    # 304: Channel:Sensor:Description must be included and assigned a string consisting of
    #    at least 1 case insensitive A-Z and numeric 0-9 characters.
    def validate_rule_304(self, channel, msg_hdr=''):
        """304 Channel:Sensor:Description must be included and assigned a string consisting of
               at least 1 case insensitive A-Z and numeric 0-9 characters.
        """
        rule_code = '304'

        if getattr(channel, 'sensor', None) is None:
            msg = msg_hdr + "does not have a sensor --> Can't validate rule %d" % rule_code
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        description = getattr(channel.sensor, 'description', None)
        if description is None or len(description.strip()) == 0:
            msg = msg_hdr + "has a sensor but sensor.description is None"
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        elif description == 'None':
            msg = msg_hdr + "has a sensor with sensor.description set to string='None' "
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        # MTH: I think IRIS's definition is too narrow - surely spaces, commas and hyphens are valid!
        """
        elif len(re.sub("[a-zA-Z0-9_\-, \.]", '', description)) != 0:
            msg = msg_hdr + "has a sensor but sensor.description = [%s] is invalid" % description
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        """

        return True

    def validate_rule_305(self, channel, msg_hdr=''):
        """305 If Channel:SampleRate equals 0 or is not included then Response must not be included. [411, 421]"""
        rule_code = '305'
        #print("** Enter validate_rule_305 channel.srate=[%s]" % channel.sample_rate)
        if channel.response:
            if getattr(channel, 'sample_rate', None) is None:
                #print("** MTH: sample_rate is None")
                msg = msg_hdr + "has a response but channel.sample_rate is empty"
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False

            if float(channel.sample_rate) == 0:
                #print("** MTH: sample_rate is 0")
                msg = msg_hdr + "has a response but channel.sample_rate == 0"
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False
        return True


    # <-- Channel Time Errors -->

    def validate_rule_310(self, channel, msg_hdr=''):
        """310 Channel:startDate must be included and must occur before Channel:endDate if included."""
        rule_code = '310'
        if getattr(channel, 'start_date', None) is None:
            msg = msg_hdr + "start_date not set"
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        if getattr(channel, 'end_date', None) and channel.end_date <= channel.start_date:
            msg = msg_hdr + "has start_date=[%s] >= end_date=[%s]" % (channel.start_date, channel.end_date)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    # <-- Channel Position Errors -->
    # This section has been deprecated since these rules are already enforced by schema
    # Probably can't get here since obspy won't allow Channel(..) with bad lat/lon
    # 320 Channel:Latitude must be assigned a value between -90 and 90.

    # <-- Channel Orientation Errors -->

    def validate_rule_320(self, channel, msg_hdr=''):
        """320 If Channel:Code[2]==(H | L | M | N) THEN Channel:Azimuth and Channel:Dip must be included."""
        rule_code = '320'
        if len(channel.code) != 3:
            msg = msg_hdr + "!= 3-chars--> Can't validate [%s]" % (rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        if channel.code[1] in ['H', 'L', 'M', 'N'] and \
            (channel.azimuth is None or channel.dip is None):
            msg = msg_hdr + "azimuth:%s dip:%s" % (channel.azimuth, channel.dip)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True

    # 321 If Channel:Code[2] == (H | L | M | N) then Stage[1]:InputUnit must equal *m/s* AND 
    #     Stage[Last]:OutputUnits must equal count*
    # MTH: What this is trying to say is that InputUnit must be ground motion,
    #      not necessarily velocity

    def validate_rule_321(self, channel, msg_hdr=''):
        """321 If Channel:Code[2] == (H | L | M | N) then Stage[1]:InputUnit must be seismic
               e.g., {'m', 'm/s', 'm/s*s', etc}      AND
               Stage[Last]:OutputUnits must be digital - e.g, {'count', 'counts'}
        """
        rule_code = '321'

        if len(channel.code) != 3:
            msg = msg_hdr + "!= 3-chars--> Can't validate [%s]"
            self.warnings.append((print_error(rule_code), msg))
            return False

        if not channel.response:
            msg = msg_hdr + "has no response --> Can't validate rule:%s" % (rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        if channel.code[1] in ['H', 'L', 'M', 'N']:
            stages = channel.response.response_stages
            if not stages:
                msg = msg_hdr + "has response but no response_stages"
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                return False

            if stages[0].input_units is None:
                msg = msg_hdr + "response 1st stage input_units is None!"
                self.warnings.append((print_error(rule_code), msg))
                return False

            if stages[-1].output_units is None:
                msg = msg_hdr + "response last stage output_units is None!"
                self.warnings.append((print_error(rule_code), msg))
                return False

            if stages[0].input_units.lower() not in SEISMIC_UNITS or \
               stages[-1].output_units.lower() not in DIGITAL_UNITS:
                #msg = "Sta:%s Cha:%s On:%s Off:%s response has 1st stage units=[%s] and last stage units=[%s]" % \
                    #(self.station_code, channel.code, fix_date(channel.start_date), fix_date(channel.end_date),
                     #stages[0].input_units, stages[-1].output_units)
                msg = msg_hdr + "response has 1st stage units=[%s] and last stage units=[%s]" % \
                                 (stages[0].input_units, stages[-1].output_units)
                self.warnings.append((print_error(rule_code), msg))
                #self.return_codes.append(rule_code)
                return False

        return True


    # Rules 330/331 are deprecated since these are already checked in FDSN Schema

    # 330 Azimuth must be assigned a value between 0 and 360.
    '''
    def validate_rule_330(self, channel):
        rule_code = '330'
        if channel.azimuth is None or channel.azimuth < 0 or channel.azimuth > 360:
            msg = "Stn:%s Chan:%s has invalid azimuth=[%s]" % (self.station_code, channel.code, channel.azimuth)
            #msg = "Chan:%s has invalid azimuth=[%s]" % (channel.code, channel.azimuth)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True
    '''

    # 331 Dip must be assigned a value between -90 and 90.
    '''
    def validate_rule_331(self, channel):
        rule_code = '331'
        if channel.dip is None or channel.dip < -90 or channel.dip > 90:
            msg = "Stn:%s Chan:%s has invalid dip=[%s]" % (self.station_code, channel.code, channel.dip)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False
        return True
    '''

    # N — Dip 0, Azimuth 0 degrees (Reversed: Dip 0, Azimuth 180 degrees).
    # E — Dip 0, Azimuth 90 degrees (Reversed: Dip 0, Azimuth 270 degrees).
    # Z — Dip -90, Azimuth 0 degrees (Reversed: Dip 90, Azimuth 0 degrees).

    def validate_rule_332(self, channel, msg_hdr=''):
        """332 If Channel:Code[LAST]==N then Channel:Azimuth must be assigned (>=355.0 or <=5.0)
               or (>=175.0 and <=185.0)
               and Channel:Dip must be assigned (>=-5 AND <=5.0).
        """
        rule_code = '332'
        if channel.code is None or len(channel.code) < 1:
            #msg = "Stn:%s Missing channel.code --> Can't validate rule:%s" % \
                    #(self.station_code, rule_code)
            msg = msg_hdr + "Missing channel.code --> Can't validate rule:%s" % rule_code
            self.warnings.append((print_error(rule_code), msg))
            return False

        if channel.code[-1] != 'N':
            return True

        if channel.azimuth is None or channel.dip is None:
            msg = msg_hdr + "is missing either azimuth=[%s] or dip=[%s] --> Can't validate rule:%s" % \
                             (channel.azimuth, channel.dip, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False


        #print("Check channel.dip=%s channel.azimuth=%s" % (channel.dip, channel.azimuth))
        if channel.dip >= -5. and channel.dip <= 5 and \
           ((channel.azimuth >= 355 and channel.azimuth <= 360) or \
            (channel.azimuth >= 0 and channel.azimuth <= 5) or \
            (channel.azimuth >= 175 and channel.azimuth <= 185.)):
            return True
        else:
            #msg = "Stn:%s Chan:%s Has incorrect dip:%f and/or azim:%f for a chan of type: '%s'\n" \
                    #"Consider using Non-traditional Orthogonal Orientations:\n" % \
                    #(self.station_code, channel.code, channel.dip, channel.azimuth, channel.code[2])
            msg = msg_hdr + "Has incorrect dip:%.2f and/or azim:%.2f for a chan of type: '%s'\n" \
                    "%sConsider using Non-traditional Orthogonal Orientations:" % \
                    (channel.dip, channel.azimuth, channel.code[2], indent)
            self.warnings.append((print_error(rule_code), msg))
            self.warnings.append((non_traditional_orientations,))
            return False

    def validate_rule_333(self, channel, msg_hdr=''):
        """333 If Channel:Code[LAST]==E then Channel:Azimuth must be assigned (>=85.0 and <=95.0)
               or (>=265.0 and <=275.0) and Channel:Dip must be ASSIGNED (>=-5.0 and <=5.0).
        """
        rule_code = '333'
        if channel.code is None or len(channel.code) < 1:
            #msg = "Stn:%s Missing channel.code --> Can't validate rule:%s" % \
                    #(self.station_code, rule_code)
            msg = msg_hdr + "Missing channel.code --> Can't validate rule:%s" % rule_code
            self.warnings.append((print_error(rule_code), msg))
            return False
        if channel.azimuth is None or channel.dip is None:
            msg = msg_hdr + "is missing either azimuth=[%s] or dip=[%s] --> Can't validate rule:%s" % \
                             (channel.azimuth, channel.dip, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        if channel.code[-1] != 'E':
            return True

        if channel.dip >= -5. and channel.dip <= 5 :
           if (channel.azimuth >= 85 and channel.azimuth <= 95) \
           or (channel.azimuth >= 265 and channel.azimuth <= 275.):
            return True

        else:
            msg = msg_hdr + "Has incorrect dip:%f and/or azim:%f for a chan of type: '%s'\n" \
                    "%sConsider using Non-traditional Orthogonal Orientations:\n" % \
                    (channel.dip, channel.azimuth, channel.code[2], indent)
            self.warnings.append((print_error(rule_code), msg))
            self.warnings.append((non_traditional_orientations,))
            #self.return_codes.append(rule_code)
            return False

    def validate_rule_334(self, channel, msg_hdr=''):
        """334 If Channel:Code[LAST]==Z then Channel:Azimuth must be assigned (>=355.0 or <=5.0)
               and Channel:Dip must be assigned (>=-85.0 and <=-90.0) or (>=85.0 and <=90.0).
        """
        rule_code = '334'
        if channel.code is None or len(channel.code) < 1:
            #msg = "Stn:%s Missing channel.code --> Can't validate rule:%s" % \
                    #(self.station_code, rule_code)
            msg = msg_hdr + "Missing channel.code --> Can't validate rule:%s" % rule_code
            self.warnings.append((print_error(rule_code), msg))
            return False
        if channel.azimuth is None or channel.dip is None:
            msg = msg_hdr + "is missing either azimuth=[%s] or dip=[%s] --> Can't validate rule:%s" % \
                             (channel.azimuth, channel.dip, rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        if channel.code[-1] != 'Z':
            return True

        if (channel.azimuth >= 355. and channel.azimuth <= 360.) or \
           (channel.azimuth >= 0.  and channel.azimuth <= 5.):
           if (channel.dip >= 85.  and channel.dip <= 90.) or \
              (channel.dip >= -90. and channel.dip <= -85.):
            return True
        else:
            msg = msg_hdr + "Has incorrect dip:%.2f and/or azim:%.2f for a chan of type: '%s'\n" \
                    "Consider using Non-traditional Orthogonal Orientations:\n" % \
                    (channel.dip, channel.azimuth, channel.code[2])
            self.warnings.append((print_error(rule_code), msg))
            self.warnings.append((non_traditional_orientations,))
            #self.return_codes.append(rule_code)
            return False

    # <-- Response Stage Errors -->

    def missing_response(self, channel, rule_code):
        if getattr(channel, 'response', None) is None or channel.response.response_stages is None:
            m = msg_hdr(self.station.code, channel)
            msg = m + "has no response stages--> Can't validate [%s]" % (rule_code)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)

    def validate_rule_401(self, channel, msg_hdr=''):
        """401 Stage:number must start at 1 and be sequential."""
        rule_code = '401'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages

        if len(stages) == 0:
            msg = msg_hdr + "has response with 0 stages --> Nothing left to check"
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        sequence_numbers = []
        for stage in stages:
            sequence_numbers.append(stage.stage_sequence_number)
        increasing = all(i < j for i, j in zip(sequence_numbers, sequence_numbers[1:]))
        if increasing and sequence_numbers[0] == 1:
            return True
        else:
            msg = msg_hdr + "invalid stage_sequence_numbers=[%s]" % (sequence_numbers)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

    def validate_rule_402(self, channel, msg_hdr=''):
        """402 Stage[N]:InputUnits:Name and/or Stage[N]:OutputUnits:Name are not defined
               in Unit name overview for IRIS StationXML validator.
               Capitalized unit names trigger warnings.
        """
        rule_code = '402'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages

        passed = True
        for i, stage in enumerate(stages):
            i_stage = i+1
            input_units = getattr(stage, 'input_units', None)
            if input_units is None:
                msg = msg_hdr + "stage:%d input_units is NOT set" % (i_stage)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False
            else:
                if input_units not in unit_names:
                    if input_units.lower() in unit_names_lower:
                        msg = msg_hdr + "stage:%d input_units [%s] not in unit_names but lowercase is" % \
                                        (i_stage, input_units)
                        self.warnings.append((print_error(rule_code), msg))
                    else:
                        msg = msg_hdr + "stage:%d input_units [%s] not in unit_names" % \
                                        (i_stage, input_units)
                        self.errors.append((print_error(rule_code), msg))
                        self.return_codes.append(rule_code)
                        passed = False
            output_units = getattr(stage, 'output_units', None)
            if output_units is None:
                msg = msg_hdr + "stage:%d output_units is NOT set" % (i_stage)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False
            else:
                if output_units not in unit_names:
                    if output_units.lower() in unit_names_lower:
                        msg = msg_hdr + "stage:%d output_units [%s] not in unit_names but lowercase is" % \
                                        (i_stage, output_units)
                        self.warnings.append((print_error(rule_code), msg))
                    else:
                        msg = msg_hdr + "stage:%d output_units [%s] not in unit_names" % \
                                        (i_stage, output_units)
                        self.errors.append((print_error(rule_code), msg))
                        self.return_codes.append(rule_code)
                        passed = False
        return passed

    def validate_rule_403(self, channel, msg_hdr=''):
        """403 If length(Stage) > 1 then Stage[N]:InputUnits:Name must
               equal Stage[N-1]:OutputUnits:Name.
        """
        rule_code = '403'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages
        if len(stages) <= 1:
            return True

        passed = True
        for i in range(len(stages)-1):
            i_stage = i+1
            stage1 = stages[i]
            stage2 = stages[i+1]

            # MTH: make sure COUNT and counts appear equal for this test
            input_units = stage2.input_units.lower()
            output_units = stage1.output_units.lower()
            if input_units[-1] == 's' and output_units[-1] != 's':
                input_units = input_units[:-1]
            elif input_units[-1] != 's' and output_units[-1] == 's':
                output_units = output_units[:-1]

            # This will still catch 'v' != 'volts' but that's another issue
            if input_units != output_units:
                #print("input_units:[%s] != output_units[%s]" % (input_units, output_units))
                msg = msg_hdr + "stage[%d] output_units=%s != stage[%d] input_units=%s" % \
                                (i_stage, stage1.output_units, i_stage+1, stage2.input_units)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

    def validate_rule_404(self, channel, msg_hdr=''):
        """404 If Stage[N]:PolesZeros:PzTransferFunctionType:Digital or Stage[N]:FIR or
                  Stage[N]:Coefficients:CfTransferFunctionType:DIGITAL are included
               then Stage[N] must include Stage[N]:Decimation and Stage[N]:StageGain elements.
        """
        rule_code = '404'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages

        passed = True
        for i, stage in enumerate(stages):
            if isinstance(stage, CoefficientsTypeResponseStage) or \
            isinstance(stage, FIRResponseStage) or \
            (isinstance(stage, PolesZerosResponseStage) \
                and stage.pz_transfer_function_type == "DIGITAL (Z-TRANSFORM)") :
                if stage.stage_gain and stage.decimation_factor and stage.decimation_factor >= 1:
                    pass
                else:
                    msg = msg_hdr + "stage:%d missing stage_gain and/or decimation_factor" % (i+1)
                    self.errors.append((print_error(rule_code), msg))
                    self.return_codes.append(rule_code)
                    passed = False
                    #print(msg)
        return passed

    def validate_rule_405(self, channel, msg_hdr=''):
        """405 Stage of type ResponseList cannot be the only stage included in a response. [420]"""
        rule_code = '405'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages
        if len(stages) == 1 and isinstance(stages[0], ResponseListResponseStage):
            self.errors.append(print_error(rule_code))
            self.return_codes.append(rule_code)
            return False

        return True

    # <-- ResponseType and StageGain Errors -->

    def validate_rule_410(self, channel, msg_hdr=''):
        """410 If InstrumentSensitivity is included then InstrumentSensitivity:Value must be
               assigned a double > 0.0.
        """
        rule_code = '410'
        if self.missing_response(channel, rule_code):
            return False

        response = channel.response
        if not response.instrument_sensitivity:
            return True

        if response.instrument_sensitivity.value and response.instrument_sensitivity.value > 0.:
            return True
        else:
            msg = msg_hdr + "Missing response.instrument_sensitivity or instrument_sensitivity <= 0."
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

    def validate_rule_411(self, channel, msg_hdr=''):
        """411 If InstrumentSensitivity is included then InstrumentSensitivity:Frequency must be assigned
               a double < Channel:SampleRate/2 [Nyquist Frequency].
        """
        rule_code = '411'
        if self.missing_response(channel, rule_code):
            return False

        response = channel.response
        if not response.instrument_sensitivity:
            return True

        if getattr(channel, 'sample_rate', None) is None:
            msg = msg_hdr + "has empty sample_rate --> Can't validate [%s]" % (rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        if getattr(response.instrument_sensitivity, 'frequency', None) is None:
            msg = msg_hdr + "response instrument_sensitivity missing frequency --> Can't validate [%s]" % (rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        sensitivity = response.instrument_sensitivity
        chan_nyquist_freq = channel.sample_rate/2.
        if sensitivity.frequency > chan_nyquist_freq:
            msg = msg_hdr + "instrument_sensitivity.freq:%f must be less than 1/2 of channel.sample_rate:%f" % \
                            (sensitivity.frequency, channel.sample_rate)
            #self.errors.append((print_error(rule_code), msg))
            #self.return_codes.append(rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return False

        return True

    # MTH: Unlikely that all stage_gain frequencies agree
    #      For now let's just compare sensitivities:
    #      The issue is that when obspy combines the NRL sensor (with gain/sensitivity calculated at one frequency)
    #          with the NRL datalogger (sensitivity at another frequency), it needs to adjust these to match.
    #          I think that for a non-flat sensor response, it recalculates the sensitivity away from the flat part
    #          so it changes from the value given in NRL.

    def validate_rule_412(self, channel, msg_hdr=''):
        """412 InstrumentSensitivity:Value must equal the product of all StageGain:Value if all StageGain:Frequency
               are equal to InstrumentSensitivity:Frequency [Normalization Frequency]. [410]
        """
        rule_code = '412'
        if self.missing_response(channel, rule_code):
            return False

        response = channel.response
        if not response.instrument_sensitivity:
            return True

        sensitivity = response.instrument_sensitivity

        passed = True
        overall_gain = 1.
        normalization_freq = set()
        for i, stage in enumerate(response.response_stages):
            if getattr(stage, 'stage_gain', None) is None or stage.stage_gain <= 0:
                msg = msg_hdr + "stage:%d has gain:%s --> Can't validate [%s]" % \
                                (i, stage.stage_gain, rule_code)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False
                return False

            overall_gain *= stage.stage_gain
            normalization_freq.add(stage.stage_gain_frequency)

        if len(normalization_freq) == 1:
            diff = 100. * np.abs(overall_gain - sensitivity.value) / np.abs(sensitivity.value)
            # MTH: I'm interpreting overall sensitivity variation <5% as being "equal"
            if diff > 5.:
                msg = msg_hdr + "Calc stage0 gain:%f vs sensitivity:%f differs by > 5 percent" % \
                                (overall_gain, sensitivity.value)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

                #print(msg)
                #print("recalculate")
                #old = response.instrument_sensitivity.value
                #response.recalculate_overall_sensitivity()
                #new = response.instrument_sensitivity.value
                #print("old sensitivity: %12.8e" % old)
                #print("new sensitivity: %12.8e" % new)
                #exit()

        return passed


    def validate_rule_413(self, channel, msg_hdr=''):
        """413 All Stages must include StageGain:Value assigned as a double > 0.0 and
               StageGain:Frequency assigned as a double.
        """
        rule_code = '413'
        if self.missing_response(channel, rule_code):
            return False

        passed = True
        stages = channel.response.response_stages
        for i, stage in enumerate(stages):
            if stage.stage_gain is None or stage.stage_gain <= 0.:
                msg = msg_hdr + "stage:%d invalid stage_gain=[%s]" % (i+1, stage.stage_gain)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False
                return False
            try:
                float(stage.stage_gain_frequency)
            except ValueError:
                msg = msg_hdr + "stage:%d invalid stage_gain_frequency=[%s]" % \
                                (i+1, stage.stage_gain_frequency)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

    def validate_rule_414(self, channel, msg_hdr=''):
        """414 If Stage[N]:PolesZeros contains Zero:Real==0 and Zero:Imaginary==0 then
               InstrumentSensitivity:Frequency cannot equal 0 and Stage[N]:StageGain:Frequency cannot equal 0.
        """
        rule_code = '414'
        if self.missing_response(channel, rule_code):
            return False

        response = channel.response
        stages = channel.response.response_stages

        passed = True
        for i, stage in enumerate(stages):
            if isinstance(stage, PolesZerosResponseStage):
                zeros = stage.zeros
                for zero in zeros:
                    if zero.real == 0. and zero.imag == 0.:
                        if response.instrument_sensitivity.frequency is None or \
                           response.instrument_sensitivity.frequency == 0 or \
                           stage.stage_gain_frequency is None or stage.stage_gain_frequency == 0:
                            msg = msg_hdr + "pz_stage contains zero at origin --> instrument_sensitivity_freq can't == 0"
                            self.errors.append((print_error(rule_code), msg))
                            self.return_codes.append(rule_code)
                            passed = False
        return passed

    def validate_rule_415(self, channel, msg_hdr=''):
        """415 Response must be of type InstrumentPolynomial if a Polynomial stage exist. [410,413,420]"""
        rule_code = '415'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages

        passed = True
        for i, stage in enumerate(stages):
            if isinstance(stage, PolynomialResponseStage) and channel.response.instrument_polynomial is None:
                msg = msg_hdr + "response contains Polynomial stage but no InstrumentPolynomial block"
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

    def validate_rule_416(self, channel, msg_hdr=''):
        """416 Response must include InstrumentSensitivity if no Polynomial stages are included."""
        rule_code = '416'
        if self.missing_response(channel, rule_code):
            return False

        response = channel.response
        stages = response.response_stages

        has_polynomial_stage = False
        for i, stage in enumerate(stages):
            if isinstance(stage, PolynomialResponseStage):
                has_polynomial_stage = True
                break
        if not has_polynomial_stage and not getattr(response, 'instrument_sensitivity', None):
            msg = msg_hdr + "response contains no polynomial stage but no InstrumentSensitivity block"
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        return True

    # <-- Response Decimation Errors -->

    def validate_rule_420(self, channel, msg_hdr=''):
        """420 A Response must contain at least one instance of Response:Stage:Decimation. [404,405,414,415]"""
        rule_code = '420'
        if self.missing_response(channel, rule_code):
            return False
        stages = channel.response.response_stages

        decimation_stage_found = False
        for stage in stages:
            if getattr(stage, 'decimation_factor') and stage.decimation_factor >= 1:
                decimation_stage_found = True
                break
        if not decimation_stage_found:
            msg = msg_hdr + "response contains 0 decimation stages"
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        return True

    def validate_rule_421(self, channel, msg_hdr=''):
        """421 Stage[Final]:Decimation:InputSampleRate divided by Stage[Final]:Decimation:Factor
               must equal Channel:SampleRate. [305]
        """
        rule_code = '421'
        if self.missing_response(channel, rule_code):
            return False

        if getattr(channel, 'sample_rate', None) is None:
            msg = msg_hdr + "has empty sample_rate --> Can't validate [%s]" % (rule_code)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        stages = channel.response.response_stages

        if len(stages) == 0:
            msg = msg_hdr + "has NO response_stages to check --> Skipping rule:%s" % (rule_code)
            self.warnings.append((print_error(rule_code), msg))
            return True

        if stages[-1].decimation_factor is None or stages[-1].decimation_factor == 0.:
            msg = msg_hdr + "final stage decimation_factor not set or == 0."
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        expected_final_srate = stages[-1].decimation_input_sample_rate / stages[-1].decimation_factor
        if expected_final_srate != channel.sample_rate:
            msg = msg_hdr + "expected_final_srate=%f != channel.sample_rate=%f" % \
                            (expected_final_srate, channel.sample_rate)
            self.errors.append((print_error(rule_code), msg))
            self.return_codes.append(rule_code)
            return False

        return True


    def validate_rule_422(self, channel, msg_hdr=''):
        """422 Stage[N]:Decimation:InputSampleRate must equal Stage[N-1]:Decimation:InputSampleRate
               divided by Stage[N-1]:Decimation:Factor.
        """
        rule_code = '422'
        if self.missing_response(channel, rule_code):
            return False
        stages = channel.response.response_stages

        verbose = False   # MTH: in case we want to implement this in the future

        stages_with_decimation = []
        for stage in stages:
            if stage.decimation_input_sample_rate:
                stages_with_decimation.append(stage)

        passed = True
        for i in range(len(stages_with_decimation)-1):
            stage1 = stages_with_decimation[i]
            stage2 = stages_with_decimation[i+1]
            #print("Rule:%s chan:%s stage1:%d" % (rule_code, channel.code, i+1))
            if stage1.decimation_input_sample_rate is None:
                pass
            else:
                expected_input_sample_rate = stage1.decimation_input_sample_rate / stage1.decimation_factor
                if stage2.decimation_input_sample_rate != expected_input_sample_rate:
                    msg = msg_hdr + "stage:%d has input_sr:%f != expected_sr:%f" % \
                              (stage2.stage_sequence_number, stage2.decimation_input_sample_rate, expected_input_sample_rate)
                              #(i+1, stage2.decimation_input_sample_rate, expected_input_sample_rate)
                    self.errors.append((print_error(rule_code), msg))
                    self.return_codes.append(rule_code)
                    passed = False
                    if verbose:
                        for stage in stages_with_decimation:
                            msg = "stage:[%d] input_sample_rate:%s decimation:%s" % \
                            (stage.stage_sequence_number, stage.decimation_input_sample_rate, stage.decimation_factor)
                            self.errors.append((msg, ))

        return passed

    def validate_rule_423(self, channel, msg_hdr=''):
        """423 If Decimation and StageGain are included in Stage[N] then
               PolesZeros or Coefficients or ResponseList or FIR must also be included in Stage[N].
        """

        rule_code = '423'
        if self.missing_response(channel, rule_code):
            return False

        stages = channel.response.response_stages

        passed = True

        allowed_types = ['PolesZerosResponseStage',
                         'CoefficientsTypeResponseStage',
                         'FIRResponseStage',
                         'ResponseListResponseStage'
                         ]

        for i, stage in enumerate(stages):
            stage_type = type(stage).__name__
            if stage.decimation_input_sample_rate and stage_type not in allowed_types:
                msg = msg_hdr + "response stage:%d has type:%s and input_sample_rate:%s --> decimation element is not allowed!" % \
                            (i, type(stage).__name__, stage.decimation_input_sample_rate)
                #print(msg)
                self.errors.append((print_error(rule_code), msg))
                self.return_codes.append(rule_code)
                passed = False

        return passed

### End of stationxml_validator class

def get_first_start_last_end_dates(station_or_channel_list):

    # MTH: All Stations must have a startDate but not necessarily an endDate
    # MTH: All Channels must have a startDate but not necessarily an endDate

    nepochs = len(station_or_channel_list)
    newlist = sorted(station_or_channel_list, key=lambda x: x.start_date, reverse=False)
    earliest_start = newlist[0].start_date

    slist = []
    for station_or_channel in station_or_channel_list:
        if getattr(station_or_channel, 'end_date', None) is not None:
            slist.append(station_or_channel)
    if slist:
        #newlist = sorted(station_or_channel_list, key=lambda x: x.end_date, reverse=True)
        newlist = sorted(slist, key=lambda x: x.end_date, reverse=True)
        latest_end = newlist[0].end_date
        # MTH: Do I need to check len slist vs station_or_channel_list
        #      and if slist is smaller, then latest_end = None ??
    else:
        latest_end = None

    return(earliest_start, latest_end)

def overlapping_epochs(epoch_list):

    overlap = False

    overlap_epochs = []

    for i in range(len(epoch_list)-1):

        epoch1 = epoch_list[i]
        epoch2 = epoch_list[i+1]

        if epoch1.start_date == epoch2.start_date:
            #print("Epochs have same start_date")
            overlap = True
        # epoch1 better be closed
        elif epoch1.end_date is None:
            #print("Earlier epoch not closed!")
            overlap = True
        # epoch1 close must precede epoch2 start
        elif epoch1.end_date > epoch2.start_date:
            #print("epoch1 end > epoch2 start")
            overlap = True

        if overlap:
            #print("Epoch:%s overlaps with epoch:%s" % (epoch1, epoch2))
            overlap_epochs.append(epoch1)
            overlap_epochs.append(epoch2)
            #return 1

    #return 0
    return overlap_epochs

def print_error(code):
    return "  [%s] %s" % (code, error_codes[code]['description'])
    #print("  [%s] %s" % (code, error_codes[code]['description']) )

def valid_ascii(string, min_len, max_len):
    # Network/Station/Channel codes must all be upper-case ascii chars

    #print("valid_ascii: string=[%s] len=%d min_len=%d max_len=%d" % (string, len(string), min_len, max_len))
    if isinstance(string, str) and len(string) >= min_len and len(string) <= max_len \
            and len(re.sub("[A-Z0-9]", '', string)) == 0:
                return 1
    else:
        return 0


def enforce_rule(channel, ERROR_CODE):

    # For future enforcement of any network/station exceptions:
    if not isinstance(channel, obspy.core.inventory.channel.Channel):
        return True

    restriction_list = error_codes[ERROR_CODE]['restrictions']

    for restriction_code in restriction_list:
        restriction_dict = restrictions[restriction_code]
        key = restriction_dict['key']
        if key == "Channel:Code":
            if channel.code in restriction_dict['immune']:
                #print("Chan:%s IS immune to rule:%s" % (channel.code, ERROR_CODE))
                return False

        # C2 : Channel:Type == "HEALTH", "FLAG", "MAINTENANCE" does not trigger Validation tests 
        #      that are subject to this restriction
        elif key == "Channel:Type":
            #print("Check channel type --> NOT implemented yet")
            pass
        elif key == "Response":
            if channel.response and channel.response.instrument_polynomial:
                #print("channel:%s has instrument polynomial --> Immune from rule:[%s]" % \
                      #(channel.code, ERROR_CODE))
                return False

    #print("Chan:%s is NOT immune to rule:%s" % (channel.code, ERROR_CODE))
    return True

levels = {'1':'network',
          '2':'station',
          '3':'channel',
          '4':'response'}

def get_string_from_level(n):
    fname = "get_string_from_level"
    if n not in levels.keys():
        s = ",".join(levels.keys())
        logger.error("%s: level must be in [%s]", (fname, s))
        return None
    return levels[n]

def get_rules(level='network'):

    if level not in levels.values():
        print("get_rules: Unknown level=[%s]" % level)
        return None

    k = list(levels.keys())[list(levels.values()).index(level)]

    rules = []
    for key in error_codes.keys():
        if key[0] == k:
            rules.append(key)

    # MTH: Hack to keep rule levels isolated
    #      IRIS Rule 321 is the ONLY level 3xx rule that requires
    #      the channel to have a response in order to validate
    #      ===> Move it to the Response level 4xx:
    if level == 'channel':
        rules = [rule for rule in rules if rule != '321']
    elif level == 'response':
        rules.append('321')

    return rules


def validate_stationxml_file_vs_rules(stationxml_file):
    '''
        Test input stationxml_file against all rules
    '''
    validator = stationxml_validator(stationxml_file)
    validator.validate_inventory()
    print("[ERRORS]:\n")
    for error in validator.errors:
        print(error)
    print("\n[WARNINGS]:\n")
    for warning in validator.warnings:
        print(warning)

    return

def stationxml_passes_rule(xmlfile, rule_code):
    '''
        Set up an xmlfile to pass against a single rule_code validator
    '''
    import warnings
    warnings.simplefilter('ignore')
    validator = stationxml_validator(xmlfile)
    warnings.simplefilter('module')

    func_name = "validator.validate_rule_%s" % rule_code

    passes = []
    networks = validator.inv.networks
    stations = []
    channels = []
    for network in networks:
        for station in network.stations:
            stations.append(station)
            for channel in station.channels:
                channels.append(channel)

    if rule_code[0] == '1':
        args = networks
    elif rule_code[0] == '2':
        args = stations
    elif rule_code[0] in ['3', '4']:
        args = channels

    for arg in args:
        passes.append(eval(func_name)(arg))

    if len(passes) == 1:
        passes = passes[0]

    return passes, validator.errors


def validate_iris_stationxml_examples_vs_rules():
    '''
        Loop through IRIS validation stationxmlfile examples (e.g., 'F1_304.xml')
            Test to see that file F?_XXX.xml correctly FAILS rule_code=XXX
            -or-
            Test to see that file P?_XXX.xml correctly PASSES rule_code=XXX
    '''

    test_dir = os.path.join(installation_dir(), 'iris_resources')

    for rule in error_codes.keys():
        files = test_xmls[rule]

        for fname in files:
            xmlfile = os.path.join(test_dir, fname)
            #code = fname[3:6]
            code = rule

            #print("Check file:%s against Rule:%s [file:%s]" % (fname, code, xmlfile))
            print("Check file:%s against Rule:%s" % (fname, code))
            if not os.path.isfile(xmlfile):
                print("******* Error: Can't find file:%s" % fname)
                continue

            passed, errors = stationxml_passes_rule(xmlfile, code)

            #for error in errors:
                #print(error)

            if fname[0:1] == 'P':
                if not passed:
                    print("ERROR: xmlfile=[%s] should have PASSED but failed" % fname)
                else:
                    print("SUCCESS: xmlfile=[%s] PASSED as expected" % fname)
            elif fname[0:1] == 'F':
                if passed:
                    print("ERROR: xmlfile=[%s] should NOT have PASSED!" % fname)
                else:
                    print("SUCCESS: xmlfile=[%s] FAILED as expected" % fname)


    return

def msg_hdr(net, sta, channel):
    msg = "Net:%s Sta:%s Cha:%s Loc:%s On:%s Off:%s " % \
            (net, sta, channel.code, channel.location_code,
             fix_date(channel.start_date),
             fix_date(channel.end_date))
    return msg

def fix_date(utc):
    if utc is None:
        return None
    return utc.datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

def main():

    files = ['F1_305.xml', 'F2_305.xml']

    #for fname in files:
        #xmlfile = os.path.join(TEST_DIR, fname)
        #rule = fname[3:6]
        #passed, errors = stationxml_passes_rule(xmlfile, rule)
    validator = stationxml_validator('./iris_resources/F1_423.xml')
    validator.validate_rule('423')

    #print(inv)
    exit()

    TEST_DIR = "/Users/mth/mth/python_pkgs/stationxml-validator/src/test/resources/"
    validate_iris_stationxml_examples_vs_rules()
    exit()
    validate_stationxml_file_vs_rules(os.path.join(TEST_DIR, 'Validator_Pass.xml'))

if __name__ == "__main__":
    main()
