from networktools.geo import (rad2deg, deg2rad, radius, sph_rotation_matrix,
                              llh2ecef, ecef2llh, ecef2neu)
from networktools.geo import get_vcv_matrix, rotate_vcv, vcv2dict, all_in_one_vcv
from networktools.geo import ecef2enu_rot, get_from_ecef

from networktools.time import gps_time
from datadbs.general import GeneralData
from networktools.colorprint import gprint, bprint, rprint

import math
import numpy as np
import pickle


def load_data(data):
    return (pickle.loads(data[0]), data[1])


def make_delta(station_0, input_res):
    # print(input_res)
    P0 = station_0
    P1 = input_res
    #bprint("PRE Make delta ok %s %s" %(P0,P1))
    Q0 = get_from_ecef(P0)
    Q1 = get_from_ecef(P1)
    #bprint("Make delta ok %s %s" %(Q0,Q1))
    return list(np.array(Q1)-np.array(Q0))


def make_neu(station_0, input_res):
    POSITION = station_0['llh']
    P0 = [POSITION['lat'],
          POSITION['lon'],
          POSITION['z']]
    delta = input_res['DELTA']
    dx = delta[0]
    dy = delta[1]
    dz = delta[2]
    #bprint("Making inside NEU %s" %P0)
    NEU = ecef2neu(P0, dx, dy, dz)
    return NEU


class GeoJSONData(GeneralData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station = kwargs['station']
        self.position = kwargs['position']  # has lat, lon, z reference
        #print("Inicializa GEOJSON")
        self.rotation_matrix = ecef2enu_rot(
            self.position['llh']['lon'],
            self.position['llh']['lat'])

    def manage_data(self, data):
        # get timestamp from data generated on gps
        # Remember we need milliseconds.
        #print("El mensaje se convertirá en... %s" % data)
        if 'DT_GEN' in data.keys():
            dtgen = data['DT_GEN']

        try:
            # TIME OK
            dt0, source = gps_time(data)
            time = int(dt0.timestamp()*1000)

            # GET STATION REF AND NEW DATA
            station_0 = self.position
            #gprint("Position station: %s" %station_0)

            # MAKE DELTA
            #bprint("Making delta-------")
            delta = {'DELTA': make_delta(station_0, data)}

            # MAKE NEU
            #bprint("Delta now: %s" %delta)
            neu = make_neu(station_0, delta)

            #gprint("FINAL NEU %s" %neu)

            # FIXME: Unpack the dictionary.
            geo = {'coordinates': (neu['N'], neu['E'], neu['U'])}

            if 'POSITION_VCV' in data:
                #bprint("Calculating VCV rotation: matrix-->%s" %self.rotation_matrix)
                VCV = all_in_one_vcv(self.rotation_matrix,
                                     data['POSITION_VCV'])
                sncl = '{}.FU.LY_.00'.format(self.station['code'])
                prop = {'quality': 100,
                        'EError': math.sqrt(VCV['EE']),
                        'NError': math.sqrt(VCV['NN']),
                        'UError': math.sqrt(VCV['UU']),
                        'time': time,
                        'dt': dt0,
                        'dt_gen': dtgen,
                        'sampleRate': 1,
                        'station': self.station['code'],
                        'SNCL': sncl}
            else:
                prop = {'quality': 100,
                        'time': time,
                        'dt': dt0,
                        'dt_gen': dtgen,
                        'sampleRate': 1,
                        'station': self.station['code'],
                        'SNCL': '{}.FU.LY_.00'.format(self.station['code'])}

            data = {'features': [{'geometry': {'coordinates': geo['coordinates'],
                                               'type': 'Point'},
                                  'type': 'Feature',
                                  'properties': {'coordinateType': 'NEU'}}],
                    'type': 'FeatureCollection',
                    'properties': prop}

            #rprint("Form GeoJson process, data to send: %s" %data)
        except Exception as ex:
            print("Error en conversion de JSON %s " % ex)
            self.logger.exception(ex)
            raise ex
        return data
