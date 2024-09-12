# Copyright (c) 2023 Benjamin Lubin and Sebastien Lahaie.
#
# This file is part of Adaptive-Price-CA
# (see https://github.com/blubin/Adaptive-Price-CA).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Create test instances based on a particular generator description"""

from generators import QuadValueGenerator, CATSGenerator
from generators import CanadianGenerator, CanadianGeneratorExpanded

# Here we provide the parameter sets that define generator configs:

######################
### For Unit Tests ###
######################

"""
A simple version of the QuadraticValue generator
"""
QUAD_VALUE_UNIT_SMALL = {'generator' : 'quadvalue', \
                         'subdir' : 'unit', \
                         'prefix' : 'qvsmall', \
                         'agents' : 2, \
                         'goods'  : 5, \
                         'subset' : 3, \
                         'cap'    : None}
"""
A simple test of the CATS generator
"""
CATS_UNIT_SMALL = {'generator' : 'CATS', \
                   'subdir' : 'unit', \
                   'prefix' : 'CATSsmall', \
                   'distribution' : 'regions', \
                   'goods' : 5, \
                   'bids' : 10, \
                   'int_prices' : False, \
                   'type' : 'MultiMinded'}

############################
### For Canadian Auction ###
############################

CANADIAN_SUPPLEMENT = {'generator' : 'CASupplement'}

#####################################
### For Canadian Auction Expanded ###
#####################################

# LOMAX S2

CA_SUPP_LOMAX_S2_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS2L0', \
                       'distribution' : 'lomax', \
                       'shape' : 2,\
                       'locationpct' : 0.0} 

CA_SUPP_LOMAX_S2_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementLomax', \
                         'prefix' : 'CASuppLomaxS2L05', \
                         'distribution' : 'lomax', \
                         'shape' : 2,\
                         'locationpct' : 0.5} 

CA_SUPP_LOMAX_S2_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS2L075', \
                       'distribution' : 'lomax', \
                       'shape' : 2,\
                       'locationpct' : 0.75} 

# LOMAX S3

CA_SUPP_LOMAX_S3_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS3L0', \
                       'distribution' : 'lomax', \
                       'shape' : 3,\
                       'locationpct' : 0.0} 

CA_SUPP_LOMAX_S3_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementLomax', \
                         'prefix' : 'CASuppLomaxS3L05', \
                         'distribution' : 'lomax', \
                         'shape' : 3,\
                         'locationpct' : 0.5} 

CA_SUPP_LOMAX_S3_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS3L075', \
                       'distribution' : 'lomax', \
                       'shape' : 3,\
                       'locationpct' : 0.75} 

# LOMAX S4

CA_SUPP_LOMAX_S4_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS4L0', \
                       'distribution' : 'lomax', \
                       'shape' : 4,\
                       'locationpct' : 0.0} 

CA_SUPP_LOMAX_S4_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementLomax', \
                         'prefix' : 'CASuppLomaxS4L05', \
                         'distribution' : 'lomax', \
                         'shape' : 4,\
                         'locationpct' : 0.5} 

CA_SUPP_LOMAX_S4_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementLomax', \
                       'prefix' : 'CASuppLomaxS4L075', \
                       'distribution' : 'lomax', \
                       'shape' : 4,\
                       'locationpct' : 0.75} 

# LOGNORM .125

CA_SUPP_LOGNORM_S0125_L0 = {'generator' : 'CASupplementExpanded', \
                            'subdir' : 'CASupplementLognorm', \
                            'prefix' : 'CASuppLognormS0125L0', \
                            'distribution' : 'lognorm', \
                            'shape' : 0.125,\
                            'locationpct' : 0.0} 

CA_SUPP_LOGNORM_S0125_L05 = {'generator' : 'CASupplementExpanded', \
                              'subdir' : 'CASupplementLognorm', \
                              'prefix' : 'CASuppLognormS0125L05', \
                              'distribution' : 'lognorm', \
                              'shape' : 0.125,\
                              'locationpct' : 0.5} 

CA_SUPP_LOGNORM_S0125_L075 = {'generator' : 'CASupplementExpanded', \
                            'subdir' : 'CASupplementLognorm', \
                            'prefix' : 'CASuppLognormS0125L075', \
                            'distribution' : 'lognorm', \
                            'shape' : 0.125,\
                            'locationpct' : 0.75} 

# LOGNORM .25

CA_SUPP_LOGNORM_S025_L0 = {'generator' : 'CASupplementExpanded', \
                           'subdir' : 'CASupplementLognorm', \
                           'prefix' : 'CASuppLognormS025L0', \
                           'distribution' : 'lognorm', \
                           'shape' : 0.25,\
                           'locationpct' : 0.0} 

CA_SUPP_LOGNORM_S025_L05 = {'generator' : 'CASupplementExpanded', \
                             'subdir' : 'CASupplementLognorm', \
                             'prefix' : 'CASuppLognormS025L05', \
                             'distribution' : 'lognorm', \
                             'shape' : 0.25,\
                             'locationpct' : 0.5} 

CA_SUPP_LOGNORM_S025_L075 = {'generator' : 'CASupplementExpanded', \
                           'subdir' : 'CASupplementLognorm', \
                           'prefix' : 'CASuppLognormS025L075', \
                           'distribution' : 'lognorm', \
                           'shape' : 0.25,\
                           'locationpct' : 0.75} 

# LOGNORM .5

CA_SUPP_LOGNORM_S05_L0 = {'generator' : 'CASupplementExpanded', \
                          'subdir' : 'CASupplementLognorm', \
                          'prefix' : 'CASuppLognormS05L0', \
                          'distribution' : 'lognorm', \
                          'shape' : 0.5,\
                          'locationpct' : 0.0} 

CA_SUPP_LOGNORM_S05_L05 = {'generator' : 'CASupplementExpanded', \
                            'subdir' : 'CASupplementLognorm', \
                            'prefix' : 'CASuppLognormS05L05', \
                            'distribution' : 'lognorm', \
                            'shape' : 0.5,\
                            'locationpct' : 0.5} 

CA_SUPP_LOGNORM_S05_L075 = {'generator' : 'CASupplementExpanded', \
                          'subdir' : 'CASupplementLognorm', \
                          'prefix' : 'CASuppLognormS05L075', \
                          'distribution' : 'lognorm', \
                          'shape' : 0.5,\
                          'locationpct' : 0.75} 

# GAMMA 2

CA_SUPP_GAMMA_S2_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS2L0', \
                       'distribution' : 'gamma', \
                       'shape' : 2,\
                       'locationpct' : 0.0} 

CA_SUPP_GAMMA_S2_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementGamma', \
                         'prefix' : 'CASuppGammaS2L05', \
                         'distribution' : 'gamma', \
                         'shape' : 2,\
                         'locationpct' : 0.5} 

CA_SUPP_GAMMA_S2_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS2L075', \
                       'distribution' : 'gamma', \
                       'shape' : 2,\
                       'locationpct' : 0.75} 

# GAMMA 3

CA_SUPP_GAMMA_S3_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS3L0', \
                       'distribution' : 'gamma', \
                       'shape' : 3,\
                       'locationpct' : 0.0} 

CA_SUPP_GAMMA_S3_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementGamma', \
                         'prefix' : 'CASuppGammaS3L05', \
                         'distribution' : 'gamma', \
                         'shape' : 3,\
                         'locationpct' : 0.5} 

CA_SUPP_GAMMA_S3_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS3L075', \
                       'distribution' : 'gamma', \
                       'shape' : 3,\
                       'locationpct' : 0.75} 

# GAMMA 4

CA_SUPP_GAMMA_S4_L0 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS4L0', \
                       'distribution' : 'gamma', \
                       'shape' : 4,\
                       'locationpct' : 0.0} 

CA_SUPP_GAMMA_S4_L05 = {'generator' : 'CASupplementExpanded', \
                         'subdir' : 'CASupplementGamma', \
                         'prefix' : 'CASuppGammaS4L05', \
                         'distribution' : 'gamma', \
                         'shape' : 4,\
                         'locationpct' : 0.5} 

CA_SUPP_GAMMA_S4_L075 = {'generator' : 'CASupplementExpanded', \
                       'subdir' : 'CASupplementGamma', \
                       'prefix' : 'CASuppGammaS4L075', \
                       'distribution' : 'gamma', \
                       'shape' : 4,\
                       'locationpct' : 0.75} 

##################################
### For Main Experiments Tests ###
##################################

### Quadratic Value

qv_g10a5s5c5= {'generator' : 'quadvalue', \
               'subdir' : 'qv_g10a5s5c5', \
               'prefix' : 'qv_g10a5s5c5', \
               'goods'  : 10, \
               'agents' : 5, \
               'subset' : 5, \
               'cap'    : 5}

qv_g20a5s5c5= {'generator' : 'quadvalue', \
               'subdir' : 'qv_g20a5s5c5', \
               'prefix' : 'qv_g20a5s5c5', \
               'goods'  : 20, \
               'agents' : 5, \
               'subset' : 5, \
               'cap'    : 5}

qv_g20a5s10c10= {'generator' : 'quadvalue', \
               'subdir' : 'qv_g20a5s10c10', \
               'prefix' : 'qv_g20a5s10c10', \
               'goods'  : 20, \
               'agents' : 5, \
               'subset' : 10, \
               'cap'    : 10}

qv_g30a5s5c5= {'generator' : 'quadvalue', \
               'subdir' : 'qv_g30a5s5c5', \
               'prefix' : 'qv_g30a5s5c5', \
               'goods'  : 30, \
               'agents' : 5, \
               'subset' : 5, \
               'cap'    : 5}

qv_g30a5s15c15= {'generator' : 'quadvalue', \
               'subdir' : 'qv_g30a5s15c15', \
               'prefix' : 'qv_g30a5s15c15', \
               'goods'  : 30, \
               'agents' : 5, \
               'subset' : 15, \
               'cap'    : 15}

### Regions

cats_reg_g10b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g10b50', \
                      'prefix' : 'cats_reg_g10b50', \
                'distribution' : 'regions', \
                       'goods' : 10, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_reg_g20b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g20b50', \
                      'prefix' : 'cats_reg_g20b50', \
                'distribution' : 'regions', \
                       'goods' : 20, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_reg_g20b100 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g20b100', \
                      'prefix' : 'cats_reg_g20b100', \
                'distribution' : 'regions', \
                       'goods' : 20, \
                        'bids' : 100, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_reg_g20b300 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g20b300', \
                      'prefix' : 'cats_reg_g20b300', \
                'distribution' : 'regions', \
                       'goods' : 20, \
                        'bids' : 300, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_reg_g20b500 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g20b500', \
                      'prefix' : 'cats_reg_g20b500', \
                'distribution' : 'regions', \
                       'goods' : 20, \
                        'bids' : 500, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_reg_g30b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g30b50', \
                      'prefix' : 'cats_reg_g30b50', \
                'distribution' : 'regions', \
                       'goods' : 30, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_reg_g30b150 = {'generator' : 'CATS', \
                      'subdir' : 'cats_reg_g30b150', \
                      'prefix' : 'cats_reg_g30b150', \
                'distribution' : 'regions', \
                       'goods' : 30, \
                        'bids' : 150, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


### Paths

cats_path_g10b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g10b50', \
                      'prefix' : 'cats_path_g10b50', \
                'distribution' : 'paths', \
                       'goods' : 10, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_path_g20b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g20b50', \
                      'prefix' : 'cats_path_g20b50', \
                'distribution' : 'paths', \
                       'goods' : 20, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_path_g20b100 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g20b100', \
                      'prefix' : 'cats_path_g20b100', \
                'distribution' : 'paths', \
                       'goods' : 20, \
                        'bids' : 100, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_path_g20b300 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g20b300', \
                      'prefix' : 'cats_path_g20b300', \
                'distribution' : 'paths', \
                       'goods' : 20, \
                        'bids' : 300, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_path_g20b500 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g20b500', \
                      'prefix' : 'cats_path_g20b500', \
                'distribution' : 'paths', \
                       'goods' : 20, \
                        'bids' : 500, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_path_g30b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g30b50', \
                      'prefix' : 'cats_path_g30b50', \
                'distribution' : 'paths', \
                       'goods' : 30, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_path_g30b150 = {'generator' : 'CATS', \
                      'subdir' : 'cats_path_g30b150', \
                      'prefix' : 'cats_path_g30b150', \
                'distribution' : 'paths', \
                       'goods' : 30, \
                        'bids' : 150, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

### Arbitrary

cats_arbitrary_g10b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g10b50', \
                      'prefix' : 'cats_arbitrary_g10b50', \
                'distribution' : 'arbitrary', \
                       'goods' : 10, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_arbitrary_g20b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g20b50', \
                      'prefix' : 'cats_arbitrary_g20b50', \
                'distribution' : 'arbitrary', \
                       'goods' : 20, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_arbitrary_g20b100 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g20b100', \
                      'prefix' : 'cats_arbitrary_g20b100', \
                'distribution' : 'arbitrary', \
                       'goods' : 20, \
                        'bids' : 100, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_arbitrary_g20b300 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g20b300', \
                      'prefix' : 'cats_arbitrary_g20b300', \
                'distribution' : 'arbitrary', \
                       'goods' : 20, \
                        'bids' : 300, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}


cats_arbitrary_g20b500 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g20b500', \
                      'prefix' : 'cats_arbitrary_g20b500', \
                'distribution' : 'arbitrary', \
                       'goods' : 20, \
                        'bids' : 500, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_arbitrary_g30b50 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g30b50', \
                      'prefix' : 'cats_arbitrary_g30b50', \
                'distribution' : 'arbitrary', \
                       'goods' : 30, \
                        'bids' : 50, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

cats_arbitrary_g30b150 = {'generator' : 'CATS', \
                      'subdir' : 'cats_arbitrary_g30b150', \
                      'prefix' : 'cats_arbitrary_g30b150', \
                'distribution' : 'arbitrary', \
                       'goods' : 30, \
                        'bids' : 150, \
                  'int_prices' : False, \
                        'type' : 'MultiMinded'}

##########################
### The Factory Itself ###
##########################

class GeneratorFactory(object):
    """ A Factory for Generators
    """
    @classmethod
    def get(cls, params):
        """ Get the appropriate generator instance
        """
        if QuadValueGenerator.is_generator_for(params):
            return QuadValueGenerator(params)
        elif CATSGenerator.is_generator_for(params):
            return CATSGenerator(params)
        elif CanadianGenerator.is_generator_for(params):
            return CanadianGenerator(params)
        elif CanadianGeneratorExpanded.is_generator_for(params):
            return CanadianGeneratorExpanded(params)
        else: # pragma: no cover
            raise ValueError("Unknown generator")
