#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2017 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from collections import namedtuple
import threading
import sys
import six

class SingletonBase(object):
    _lock = threading.Lock()

    def __new__(cls):
        # Double-Checked Locking
        if not hasattr(cls, '_instance'):
            try:
                cls._lock.acquire()
                if not hasattr(cls, '_instance'):
                    cls._instance = super(cls.__class__, cls).__new__(cls)
            finally:
                cls._lock.release()
        return cls._instance



class MULTIPLE(SingletonBase): pass
class Uint(SingletonBase): pass
class Int(SingletonBase): pass
class Ulong(SingletonBase): pass
class Long(SingletonBase): pass
class Float(SingletonBase): pass
class String(SingletonBase): pass
class Enum(SingletonBase): pass
class Ident(SingletonBase): pass

class Datatype(SingletonBase):
    enumValues = ('UBYTE', 'SBYTE', 'UWORD', 'SWORD', 'ULONG', 'SLONG',
        'A_UINT64', 'A_INT64', 'FLOAT32_IEEE' ,'FLOAT64_IEEE'
    )

class Datasize(SingletonBase):
    enumValues = ('BYTE', 'WORD', 'LONG')

class Addrtype(SingletonBase):
    enumValues = ('PBYTE', 'PWORD', 'PLONG', 'DIRECT')

class Byteorder(SingletonBase):
    enumValues = ('LITTLE_ENDIAN', 'BIG_ENDIAN', 'MSB_LAST', 'MSB_FIRST')

class Indexorder(SingletonBase):
    enumValues = ('INDEX_INCR', 'INDEX_DECR')


CompuPair = namedtuple('CompuPair', 'inVal outVal')
CompuTriplet = namedtuple('CompuTriplet', 'valMin valMax outVal')

class KeywordType(type):
    classDict = dict()
    classes = set()

    def __new__(klass, name, bases, namespace):
        newKlass = super(klass, KeywordType).__new__(klass, name, bases, namespace)
        KeywordType.classDict[newKlass.__name__] = newKlass
        KeywordType.classes.add(newKlass.__name__.lower())

        attrs = namespace.get('attrs', [])

        fixedAttributes = []
        variableAttribute = None
        if attrs:
            fixedAttributes = [attr[1] for attr in attrs if not MULTIPLE in attr]
            variableAttribute = [attr[1] for attr in attrs if MULTIPLE in attr]
            if variableAttribute:
                #print("VA: {} ==> {}".format(newKlass.__name__, variableAttribute))
                variableAttribute = variableAttribute[0]
        setattr(newKlass, 'fixedAttributes', fixedAttributes)
        setattr(newKlass, 'variableAttribute', variableAttribute)
        setattr(newKlass, 'attrDict', dict(zip([a[1] for a in attrs], attrs)))

        return newKlass

    def __getitem__(self, key):
        return self.attrDict.get(key, None)

    @classmethod
    def getClass(klass, name):
        result = KeywordType.classDict.get(name, None)
        if not result:
            pass
        return result

@six.add_metaclass(KeywordType)
class Keyword(object):

    multiple = False
    block = False
    optional = True
    textNode = False
    attrs = []
    children = []

    @classmethod
    def attributeNames(cls):
        return [attr[1] for attr in cls.attrs if not MULTIPLE in attr]

    def __str__(self):
        return "< %s @%0X >" % (self.__class__.__name__, id(self))

##
##
##
class A2ML(Keyword):
    #multiple = True
    block = True
    # Contains AML code of interface specific description data.


class A2ML_VERSION(Keyword):
    attrs = [
        (Uint, 'VersionNo'),    # Version number of AML part.
        (Uint, 'UpgradeNo'),    # Upgrade number of AML part.
    ]


class ADDR_EPK(Keyword):
    multiple = True
    attrs = [
        (Ulong, "Address")      # Address of the EPROM identifier.
    ]


class ALIGNMENT_BYTE(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ALIGNMENT_FLOAT32_IEEE(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ALIGNMENT_FLOAT64_IEEE(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ALIGNMENT_INT64(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ALIGNMENT_LONG(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ALIGNMENT_WORD(Keyword):
    attrs = [
        (Uint, "AlignmentBorder") # Describes the border at which the value is aligned to,
            #i.e. its memory address must be dividable by the value AlignmentBorder.)
    ]


class ANNOTATION(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION_LABEL', 'ANNOTATION_ORIGIN', 'ANNOTATION_TEXT']


class ANNOTATION_LABEL(Keyword):
    attrs = [(String, "Label")]  # label or title of the annotation


class ANNOTATION_ORIGIN(Keyword):
    attrs = [(String ,"Origin")] # creator or creating system of the annotation


class ANNOTATION_TEXT(Keyword):
    """ /begin ANNOTATION_TEXT
            {string annotation_text}*
        /end ANNOTATION_TEXT
    """
    """
        One ANNOTATION_TEXT may represent a multi-line ASCII description text (voluminous
        description). Its purpose is to be an application note which explains the function
        of an identifier for the calibration engineer.
    """
    block = True
    textNode = True

    attrs = [
        (String, "Text", MULTIPLE)
    ]



class ARRAY_SIZE(Keyword):
    attrs = [
        (Uint, "Number")    # Number of measurement values included in respective measurement
                            # object  (maximum    value  of  �Number�: 32767).
    ]
    # The use of this keyword should be replaced by MATRIX_DIM.


class ASAP2_VERSION(Keyword):
    attrs = [
        (Uint, "VersionNo"),   # Version number of ASAM MCD-2MC standard.
        (Uint, "UpgradeNo"),  # Upgrade number of ASAM MCD-2MC standard.
    ]


class AXIS_DESCR(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION', 'AXIS_PTS_REF', 'BYTE_ORDER', 'CURVE_AXIS_REF', 'DEPOSIT',
        'EXTENDED_LIMITS', 'FIX_AXIS_PAR', 'FIX_AXIS_PAR_DIST', 'FIX_AXIS_PAR_LIST',
        'FORMAT', 'MAX_GRAD', 'MONOTONY', 'PHYS_UNIT', 'READ_ONLY', 'STEP_SIZE'
    ]
    attrs = [
        (Enum, "Attribute" ,
            ('CURVE_AXIS', 'COM_AXIS', 'FIX_AXIS', 'RES_AXIS', 'STD_AXIS')
         ),
        (Ident, "InputQuantity"),
        (Ident, "Conversion"),
        (Uint, "MaxAxisPoints"),
        (Float, "LowerLimit"),
        (Float, "UpperLimit"),
    ]


class AXIS_PTS(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION', 'BYTE_ORDER', 'CALIBRATION_ACCESS', 'DEPOSIT', 'DISPLAY_IDENTIFIER',
        'ECU_ADDRESS_EXTENSION', 'EXTENDED_LIMITS', 'FORMAT', 'FUNCTION_LIST', 'GUARD_RAILS',
        'IF_DATA', 'MONOTONY', 'PHYS_UNIT', 'READ_ONLY', 'REF_MEMORY_SEGMENT', 'STEP_SIZE', 'SYMBOL_LINK'
    ]
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Ulong, "Address"),
        (Ident, "InputQuantity"),
        (Ident, "Deposit"),
        (Float, "MaxDiff"),
        (Ident, "Conversion"),
        (Uint, "MaxAxisPoints"),
        (Float, "LowerLimit"),
        (Float, "UpperLimit"),
    ]


class AXIS_PTS_REF(Keyword):
    attrs = [
        (Ident, "AxisPoints") # Name of the AXIS_PTS data record which describes the axis points
                              # distribution (group axis points and record layout: see AXIS_PTS).
    ]


class AXIS_PTS_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Addressing"),
    ]


class AXIS_PTS_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Addressing"),
    ]


class AXIS_PTS_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Addressing"),
    ]


class AXIS_PTS_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Addressing"),
    ]


class AXIS_PTS_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Addressing"),
    ]


class AXIS_RESCALE_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Uint, "MaxNumberOfRescalePairs"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Adressing"),
    ]


class AXIS_RESCALE_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Uint, "MaxNumberOfRescalePairs"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Adressing"),
    ]


class AXIS_RESCALE_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Uint, "MaxNumberOfRescalePairs"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Adressing"),
    ]


class AXIS_RESCALE_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Uint, "MaxNumberOfRescalePairs"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Adressing"),
    ]


class AXIS_RESCALE_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Uint, "MaxNumberOfRescalePairs"),
        (Indexorder, "IndexIncr"),
        (Addrtype, "Adressing"),
    ]


class BIT_MASK(Keyword):
    attrs = [
        (Ulong, "Mask")     # mask to mask out single bits.
    ]


class BIT_OPERATION(Keyword):
    children = ['LEFT_SHIFT', 'RIGHT_SHIFT', 'SIGN_EXTEND']
    block = True


class BYTE_ORDER(Keyword):
    attrs = [
        (Byteorder, "ByteOrder")
    ]


class CALIBRATION_ACCESS(Keyword):
    attrs = [
        (Enum, "Type", ('CALIBRATION', 'NO_CALIBRATION', 'NOT_IN_MCD_SYSTEM', 'OFFLINE_CALIBRATION'))
    ]


class CALIBRATION_HANDLE(Keyword):
    multiple = True
    children = ['CALIBRATION_HANDLE_TEXT']
    block = True
    attrs = [
        (Long, "Handle", MULTIPLE)
    ]


class CALIBRATION_HANDLE_TEXT(Keyword):
    attrs = [
        (String, "Text")
    ]


class CALIBRATION_METHOD(Keyword):
    multiple = True
    children = ['CALIBRATION_HANDLE']
    block = True
    attrs = [
        (String, "Method"), # the string identifies the calibration method to be used.
                            # A convention regarding the meaning of the calibration
                            # methods. The following strings are already in use: ‘
                            # InCircuit’, ‘SERAM’, ‘DSERAP’, ‘BSERAP’
        (Ulong, "Version")  # Version number of the method used.
    ]


class CHARACTERISTIC(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION', 'AXIS_DESCR', 'BIT_MASK', 'BYTE_ORDER', 'CALIBRATION_ACCESS',
        'COMPARISON_QUANTITY', 'DEPENDENT_CHARACTERISTIC', 'DISCRETE', 'DISPLAY_IDENTIFIER',
        'ECU_ADDRESS_EXTENSION', 'EXTENDED_LIMITS', 'FORMAT', 'FUNCTION_LIST', 'GUARD_RAILS',
        'IF_DATA', 'MAP_LIST', 'MATRIX_DIM', 'MAX_REFRESH', 'NUMBER', 'PHYS_UNIT', 'READ_ONLY',
        'REF_MEMORY_SEGMENT', 'STEP_SIZE', 'SYMBOL_LINK', 'VIRTUAL_CHARACTERISTIC'
    ]
    attrs = [
        (Ident, "Name"),
        (String ,"LongIdentifier"),
        (Enum, "Type", ('ASCII', 'CURVE', 'MAP', 'CUBOID', 'CUBE_4', 'CUBE_5', 'VAL_BLK', 'VALUE')),
        (Ulong, "Address"),
        (Ident, "Deposit"),
        (Float, "MaxDiff"),
        (Ident, "Conversion"),
        (Float, "LowerLimit"),
        (Float, "UpperLimit"),
    ]


class COEFFS(Keyword):
    attrs = [
        (Float,  "a"),
        (Float,  "b"),
        (Float,  "c"),
        (Float,  "d"),
        (Float,  "e"),
        (Float,  "f"),
    ]


class COEFFS_LINEAR(Keyword):
    attrs = [
        (Float,  "a"),
        (Float,  "b"),
    ]


class COMPARISON_QUANTITY(Keyword):
    attrs = [
        (Ident, "Name")
    ]


class COMPU_METHOD(Keyword):
    multiple = True
    block = True
    children = ['COEFFS', 'COEFFS_LINEAR', 'COMPU_TAB_REF', 'FORMULA', 'REF_UNIT', 'STATUS_STRING_REF']
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Enum, "ConversionType", ('IDENTICAL', 'FORM', 'LINEAR', 'RAT_FUNC', 'TAB_INTP', 'TAB_NOINTP', 'TAB_VERB')),
        (String, "Format"),
        (String, "Unit"),
    ]


class COMPU_TAB(Keyword):
    multiple = True
    block = True
    children = ['DEFAULT_VALUE', 'DEFAULT_VALUE_NUMERIC']
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Enum, "ConversionType", ('TAB_INTP', 'TAB_NOINTP')),
        (Uint, "NumberValuePairs"),
##
##  TODO: (float InVal float OutVal)* !!!
##
    ]


class COMPU_TAB_REF(Keyword):
    attrs = [
        (Ident, "ConversionTable")
    ]


class COMPU_VTAB(Keyword):
    multiple = True
    block = True
    children = ['DEFAULT_VALUE']
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Enum, "ConversionType", ('TAB_VERB',)),
        (Uint, "NumberValuePairs"),
##
##  TODO: (float InVal float OutVal)* !!!
##
    ]


class COMPU_VTAB_RANGE(Keyword):
    multiple = True
    block = True
    children = ['DEFAULT_VALUE']
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Uint, "NumberValueTriples"),
##
##  TODO: (float InValMin float InValMax string OutVal)* !!!
##
    ]


class CPU_TYPE(Keyword):
    attrs = [
        (String, "CPU")
    ]


class CURVE_AXIS_REF(Keyword):
    attrs = [
        (Ident, "CurveAxis")
    ]


class CUSTOMER(Keyword):
    attrs = [
        (String, "Customer")
    ]


class CUSTOMER_NO(Keyword):
    attrs = [
        (String, "Number")
    ]


class DATA_SIZE(Keyword):
    attrs = [
        (Uint, "Size")
    ]


class DEF_CHARACTERISTIC(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE)
    ]


class DEFAULT_VALUE(Keyword):
    attrs = [
        (String, "Display_String")
    ]


class DEFAULT_VALUE_NUMERIC(Keyword):
    attrs = [
        (Float, "Display_Value")
    ]


class DEPENDENT_CHARACTERISTIC(Keyword):
    block = True
    attrs = [
        (String, "Formula"),
        (Ident, "Characteristic", MULTIPLE),
    ]


class DEPOSIT(Keyword):
    attrs = [
        (Enum, "Mode", ('ABSOLUTE', 'DIFFERENCE'))
    ]


class DISCRETE(Keyword):
    pass


class DISPLAY_IDENTIFIER(Keyword):
    attrs = [
        (Ident, "Display_Name")
    ]


class DIST_OP_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]


class DIST_OP_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]


class DIST_OP_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]


class DIST_OP_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]


class DIST_OP_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]


class ECU(Keyword):
    attrs = [
        (String, "ControlUnit")
    ]


class ECU_ADDRESS(Keyword):
    attrs = [
        (Ulong, "Address")
    ]


class ECU_ADDRESS_EXTENSION(Keyword):
    attrs = [
        (Int, "Extension")
    ]


class ECU_CALIBRATION_OFFSET(Keyword):
    attrs = [
        (Long, "Offset")
    ]


class EPK(Keyword):
    attrs = [
        (String, "Identifier")
    ]


class ERROR_MASK(Keyword):
    attrs = [
        (Ulong, "Mask")
    ]


class EXTENDED_LIMITS(Keyword):
    attrs = [
        (Float, "LowerLimit"),
        (Float, "UpperLimit"),
    ]


class FIX_AXIS_PAR(Keyword):
    attrs = [
        (Int, "Offset"),
        (Int, "Shift"),
        (Uint, "Numberapo"),
    ]


class FIX_AXIS_PAR_DIST(Keyword):
    attrs = [
        (Int, "Offset"),
        (Int, "Distance"),
        (Uint, "Numberapo"),
    ]


class FIX_AXIS_PAR_LIST(Keyword):
    block = True
    attrs = [
        (Float, "AxisPts_Value", MULTIPLE),
    ]


class FIX_NO_AXIS_PTS_X(Keyword):
    attrs = [
        (Uint, "NumberOfAxisPoints")
    ]


class FIX_NO_AXIS_PTS_Y(Keyword):
    attrs = [
        (Uint, "NumberOfAxisPoints")
    ]


class FIX_NO_AXIS_PTS_Z(Keyword):
    attrs = [
        (Uint, "NumberOfAxisPoints")
    ]


class FIX_NO_AXIS_PTS_4(Keyword):
    attrs = [
        (Uint, "NumberOfAxisPoints")
    ]


class FIX_NO_AXIS_PTS_5(Keyword):
    attrs = [
        (Uint, "NumberOfAxisPoints")
    ]


class FNC_VALUES(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
        (Enum, "IndexMode",
            ('ALTERNATE_CURVES', 'ALTERNATE_WITH_X', 'ALTERNATE_WITH_Y', 'COLUMN_DIR', 'ROW_DIR')
        ),
        (Addrtype, "Addresstype"),
    ]


class FORMAT(Keyword):
    attrs = [
        (String, "FormatString")
    ]


class FORMULA(Keyword):
    children = ['FORMULA_INV']
    block = True
    attrs = [
        (String, "F_x")
    ]


class FORMULA_INV(Keyword):
    attrs = [
        (String, "G_x")
    ]


class FRAME(Keyword):
    children = ['FRAME_MEASUREMENT', 'IF_DATA']
    block = True
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Uint, "ScalingUnit"),
        (Ulong, "Rate"),
    ]


class FRAME_MEASUREMENT(Keyword):
    attrs = [
        (Ident, "Identifier", MULTIPLE)
    ]


class FUNCTION(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION', 'DEF_CHARACTERISTIC', 'FUNCTION_VERSION', 'IF_DATA', 'IN_MEASUREMENT',
        'LOC_MEASUREMENT', 'OUT_MEASUREMENT', 'REF_CHARACTERISTIC', 'SUB_FUNCTION'
    ]
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
    ]


class FUNCTION_LIST(Keyword):
    block = True
    attrs = [
        (Ident, "Name", MULTIPLE),
    ]


class FUNCTION_VERSION(Keyword):
    attrs = [
        (String, "VersionIdentifier")
    ]


class GROUP(Keyword):
    multiple = True
    children = ['ANNOTATION', 'FUNCTION_LIST', 'IF_DATA', 'REF_CHARACTERISTIC', 'REF_MEASUREMENT',
        'ROOT', 'SUB_GROUP'
    ]
    block = True
    attrs = [
        (Ident, "GroupName"),
        (String, "GroupLongIdentifier"),
    ]


class GUARD_RAILS(Keyword):
    pass


class HEADER(Keyword):
    children = ['PROJECT_NO', 'VERSION']
    block = True
    attrs = [
        (String, "Comment")
    ]


class IDENTIFICATION(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype")
    ]

class RAM(Keyword):
    pass


class ROM(Keyword):
    pass


class FLASH(Keyword):
    pass


class EEPROM(Keyword):
    pass


class RAM_INIT_BY_ECU(Keyword):
    pass


class RAM_INIT_BY_TOOL(Keyword):
    pass


class AUTO_FLASH_BACK(Keyword):
    pass


class FLASH_BACK(Keyword):
    pass


class DEFAULT(Keyword):
    pass

class CAN_ID_VARIABLE(Keyword):
    pass

class REDUCTION_ALLOWED(Keyword):
    pass

class EXCLUSIVE(Keyword):
    multiple = True
    attrs = [
        (Int, "Exclusive")
    ]

class RASTER(Keyword):
    multiple = True
    attrs = [
        (String, "RasterName"),
        (String, "RasterShortName"),
        (Int, "RasterID"),
        (Int, "ScalingUnit"),
        (Ulong, "Rate")
    ]

class RASTERAttr(Keyword):
    multiple = True
    attrs = [
        (Int, "RasterNr"),
    ]

class FIRST_PID(Keyword):
    multiple = True
    attrs = [
        (String, "FirstPiD")
    ]

class LENGTH(Keyword):
    multiple = True
    attrs = [
        (Int, "LENGTH")
    ]

class CAN_ID_FIXED(Keyword):
    multiple = True
    attrs = [
        (Ulong, "CanID")
    ]

class QP_BLOB(Keyword):
    multiple = True
    children = ['CAN_ID_FIXED', 'LENGTH','CAN_ID_VARIABLE', 'RASTER', 'EXCLUSIVE', 'REDUCTION_ALLOWED', 'FIRST_PID']

    attrs = [
        (Ulong, "Length"),

    ]

class SOURCE(Keyword):
    multiple = True
    children = ['QP_BLOB']
    attrs = [
        (String, "Name"),
        (Int, "BasicScaling"),
        (Int, "RateInScalingUnit")
    ]



class DEFINED_PAGES(Keyword):
    multiple = True
    children = ['RAM', 'ROM', 'FLASH', "EEPROM", 'RAM_INIT_BY_ECU', 'RAM_INIT_BY_TOOL', 'AUTO_FLASH_BACK', 'FLASH_BACK', 'DEFAULT']
    attrs = [
        (String, "Name"),
        (Int, "LogicalNo"),
        (Int, "AdressExtension"),
        (Ulong, "BaseAddress"),
        (Ulong, "MemPageSize"),
    ]

class CHECKSUM_CALCULATION(Keyword):
    multiple = True
    children = []
    attrs = [
        (Enum, "CHECKSUM_CALCULATION", ('ACTIVE_PAGE', 'BIT_OR_WITH_OPT_PAGE'))
    ]


class CHECKSUM_PARAM(Keyword):
    multiple = True
    children = ['CHECKSUM_CALCULATION']
    attrs = [
        (Int, "CheckSumProc"),
        (Ulong, "MaxBlkSize")
    ]

class DAQ_MODE(Keyword):
    multiple = True
    children = []
    attrs = [
        (Enum, "DAQ_MODE", ('ALTERNATING', 'BURST'))
    ]

class CONSISTENCY(Keyword):
    multiple = True
    children = []
    attrs = [
        (Enum, "CONSISTENCY", ('DAQ', 'ODT'))
    ]

class ADDRESS_EXTENSION(Keyword):
    multiple = True
    children = []
    attrs = [
        (Enum, "ADDRESS_EXTENSION", ('DAQ', 'ODT'))
    ]

class BYTES_ONLY(Keyword):
    pass

class RESUME_SUPPORTED(Keyword):
    pass

class STORE_SUPPORTED(Keyword):
    pass

class OPTIONAL_CMD(Keyword):
    multiple = True
    children = []
    attrs = [
        (Uint, "OPTIONAL_CMD")
    ]

class CAN_PARAM(Keyword):
    multiple = True
    children = []
    attrs = [
        (Uint, "QuartzFreq"),
        (String, "BTR0"),
        (String, "BTR1")
    ]


class BAUDRATE(Keyword):
    multiple = True
    children = []
    attrs = [
        (Ulong, "BAUDRATE")
    ]

class SAMPLE_POINT(Keyword):
    multiple = True
    children = []
    attrs = [
        (String, "SAMPLE_POINT")
    ]

class SAMPLE_RATE(Keyword):
    multiple = True
    children = []
    attrs = [
        (String, "SAMPLE_RATE")
    ]

class BTL_CYCLES(Keyword):
    multiple = True
    children = []
    attrs = [
        (String, "BTL_CYCLES")
    ]

class SJW(Keyword):
    multiple = True
    children = []
    attrs = [
        (String, "SJW")
    ]

class SYNC_EDGE(Keyword):
    multiple = True
    children = []
    attrs = [
        (Enum, "SYNC_EDGE", ('SINGLE', 'DUAL'))
    ]

class TP_BLOB(Keyword):
    multiple = True
    children = ['DAQ_MODE', "CONSISTENCY", 'ADDRESS_EXTENSION', 'BYTES_ONLY',
                'CHECKSUM_PARAM', 'OPTIONAL_CMD', 'CAN_PARAM', 'BAUDRATE', 'SAMPLE_POINT',
                'SAMPLE_RATE', 'BTL_CYCLES', 'SJW' , 'SYNC_EDGE',
                "RESUME_SUPPORTED", 'STORE_SUPPORTED', 'DEFINED_PAGES']
    attrs = [
        (Int, "CCPVersion"),
        (Int, "BlobVersion"),
        (Ulong, "CrmId"),
        (Ulong, "DtmId"),
        (Uint, "EcuStationAddr"),
        (Uint, "ByteOrder"),
    ]



class IF_DATA(Keyword):
    multiple = True
    block = True
    children = ['SOURCE', "RASTER", "TP_BLOB"]
    attrs = [
        (Ident, "Name") # The prefix "ASAP1B_" is reserved for ASAM and can be not used for proprietary Interfaces.
    ]
    """
        Data record to describe interface specific data. The parameters associated with this
        keyword have to be described in the ASAM MCD-2MC metalanguage.
        These parameters describe e.g. the access methods to the measurement data collection,
        serial communication and so on.
    """


class IN_MEASUREMENT(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE)
    ]


class LAYOUT(Keyword):
    attrs = [
        (Enum, "IndexMode", ('ROW_DIR', 'COLUMN_DIR'))
    ]


class LEFT_SHIFT(Keyword):
    attrs = [
        (Ulong, "Bitcount")
    ]


class LOC_MEASUREMENT(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE)
    ]


class MAP_LIST(Keyword):
    block = True
    attrs = [
        (Ident, "Name", MULTIPLE)
    ]


class MATRIX_DIM(Keyword):
    attrs = [
        (Uint, "xDim"),
        (Uint, "yDim"),
        (Uint, "zDim"),
    ]


class MAX_GRAD(Keyword):
    attrs = [
        (Float, "MaxGradient")
    ]


class MAX_REFRESH(Keyword):
    attrs = [
        (Uint, "ScalingUnit"),
        (Ulong, "Rate"),
    ]


class MEASUREMENT(Keyword):
    multiple = True
    block = True
    children = ['ANNOTATION', 'ARRAY_SIZE', 'BIT_MASK', 'BIT_OPERATION', 'BYTE_ORDER', 'DISCRETE',
        'DISPLAY_IDENTIFIER', 'ECU_ADDRESS', 'ECU_ADDRESS_EXTENSION', 'ERROR_MASK', 'FORMAT',
        'FUNCTION_LIST', 'IF_DATA', 'LAYOUT', 'MATRIX_DIM', 'MAX_REFRESH', 'PHYS_UNIT', 'READ_WRITE',
        'REF_MEMORY_SEGMENT', 'SYMBOL_LINK', 'VIRTUAL'
    ]
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Datatype, "Datatype"),
        (Ident, "Conversion"),
        (Uint, "Resolution"),
        (Float, "Accuracy"),
        (Float, "LowerLimit"),
        (Float, "UpperLimit"),
    ]


class MEMORY_LAYOUT(Keyword):
    multiple = True
    children = ['IF_DATA']
    block = True
    attrs = [
        (Enum, "PrgType", ('PRG_CODE', 'PRG_DATA', 'PRG_RESERVED')),
        (Ulong, "Address"),
        (Ulong, "Size"),
        (Long, "Offset0"),
        (Long, "Offset1"),
        (Long, "Offset2"),
        (Long, "Offset3"),
        (Long, "Offset4"),
    ]


class MEMORY_SEGMENT(Keyword):
    multiple = True
    children = ['IF_DATA']
    block = True
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Enum, "PrgType",
            ('CALIBRATION_VARIABLES', 'CODE', 'DATA', 'EXCLUDE_FROM_FLASH',
             'OFFLINE_DATA', 'RESERVED', 'SERAM', 'VARIABLES')
        ),
        (Enum, "MemoryType",
            ('EEPROM', 'EPROM', 'FLASH', 'RAM', 'ROM', 'REGISTER')
        ),
        (Enum, "Attribute",
            ('INTERN', 'EXTERN')
        ),
        (Ulong, "Address"),
        (Ulong, "Size"),
        (Long, "Offset0"),
        (Long, "Offset1"),
        (Long, "Offset2"),
        (Long, "Offset3"),
        (Long, "Offset4"),

    ]


class MOD_COMMON(Keyword):
    block = True
    children = ['ALIGNMENT_BYTE', 'ALIGNMENT_FLOAT32_IEEE', 'ALIGNMENT_FLOAT64_IEEE',
        'ALIGNMENT_INT64', 'ALIGNMENT_LONG', 'ALIGNMENT_WORD', 'BYTE_ORDER', 'DATA_SIZE',
        'DEPOSIT', 'S_REC_LAYOUT'
    ]
    attrs = [
        (String, "Comment"),
    ]


class MOD_PAR(Keyword):
    block = True
    children = ['ADDR_EPK', 'CALIBRATION_METHOD', 'CPU_TYPE', 'CUSTOMER', 'CUSTOMER_NO',
        'ECU', 'ECU_CALIBRATION_OFFSET', 'EPK', 'MEMORY_LAYOUT', 'MEMORY_SEGMENT',
        'NO_OF_INTERFACES', 'PHONE_NO', 'SUPPLIER', 'SYSTEM_CONSTANT', 'USER', 'VERSION'
    ]
    attrs = [
        (String, "Comment"),
    ]


class MODULE(Keyword):
    multiple = True
    block = True
    children = ['A2ML', 'AXIS_PTS', 'CHARACTERISTIC', 'COMPU_METHOD', 'COMPU_TAB',
        'COMPU_VTAB', 'COMPU_VTAB_RANGE', 'FRAME', 'FUNCTION', 'GROUP', 'IF_DATA',
        'MEASUREMENT', 'MOD_COMMON', 'MOD_PAR', 'RECORD_LAYOUT', 'UNIT', 'USER_RIGHTS',
        'VARIANT_CODING'
    ]
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
    ]


class MONOTONY(Keyword):
    attrs = [
        (Enum, "Monotony",
            ('MON_DECREASE', 'MON_INCREASE', 'STRICT_DECREASE', 'STRICT_INCREASE',
             'MONOTONOUS', 'STRICT_MON', 'NOT_MON'),
        )
    ]


class NO_AXIS_PTS_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_AXIS_PTS_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_AXIS_PTS_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_AXIS_PTS_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_AXIS_PTS_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_OF_INTERFACES(Keyword):
    attrs = [
        (Uint, "Num"),
    ]


class NO_RESCALE_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_RESCALE_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_RESCALE_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_RESCALE_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NO_RESCALE_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class NUMBER(Keyword):
    attrs = [
        (Uint, "Number")
    ]


class OFFSET_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class OFFSET_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class OFFSET_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class OFFSET_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class OFFSET_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datatype, "Datatype"),
    ]


class OUT_MEASUREMENT(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class PHONE_NO(Keyword):
    attrs = [
        (String, "Telnum"),
    ]


class PHYS_UNIT(Keyword):
    attrs = [
        (String, "Unit"),
    ]


class PROJECT(Keyword):
    children = ['HEADER', 'MODULE']
    block = True
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
    ]


class PROJECT_NO(Keyword):
    attrs = [
        (Ident, "ProjectNumber"),
    ]


class READ_ONLY(Keyword):
    pass


class READ_WRITE(Keyword):
    pass


class RECORD_LAYOUT(Keyword):
    multiple = True
    block = True
    children = ['ALIGNMENT_BYTE', 'ALIGNMENT_FLOAT32_IEEE', 'ALIGNMENT_FLOAT64_IEEE', 'ALIGNMENT_INT64',
        'ALIGNMENT_LONG', 'ALIGNMENT_WORD', 'AXIS_PTS_X', 'AXIS_PTS_Y', 'AXIS_PTS_Z', 'AXIS_PTS_4',
        'AXIS_PTS_5', 'AXIS_RESCALE_X', 'AXIS_RESCALE_Y', 'AXIS_RESCALE_Z', 'AXIS_RESCALE_4',
        'AXIS_RESCALE_5', 'DIST_OP_X', 'DIST_OP_Y', 'DIST_OP_Z', 'DIST_OP_4', 'DIST_OP_5',
        'FIX_NO_AXIS_PTS_X', 'FIX_NO_AXIS_PTS_Y', 'FIX_NO_AXIS_PTS_Z', 'FIX_NO_AXIS_PTS_4',
        'FIX_NO_AXIS_PTS_5', 'FNC_VALUES', 'IDENTIFICATION', 'NO_AXIS_PTS_X', 'NO_AXIS_PTS_Y',
        'NO_AXIS_PTS_Z', 'NO_AXIS_PTS_4', 'NO_AXIS_PTS_5', 'STATIC_RECORD_LAYOUT',
        'NO_RESCALE_X', 'NO_RESCALE_Y', 'NO_RESCALE_Z', 'NO_RESCALE_4', 'NO_RESCALE_5',
        'OFFSET_X', 'OFFSET_Y', 'OFFSET_Z', 'OFFSET_4', 'OFFSET_5', 'RESERVED', 'RIP_ADDR_W',
        'RIP_ADDR_X', 'RIP_ADDR_Y', 'RIP_ADDR_Z', 'RIP_ADDR_4', 'RIP_ADDR_5', 'SHIFT_OP_X',
        'SHIFT_OP_Y', 'SHIFT_OP_Z', 'SHIFT_OP_4', 'SHIFT_OP_5', 'SRC_ADDR_X', 'SRC_ADDR_Y',
        'SRC_ADDR_Z', 'SRC_ADDR_4', 'SRC_ADDR_5',
    ]
    attrs = [
        (Ident, "Name"),
    ]


class REF_CHARACTERISTIC(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class REF_GROUP(Keyword):
    multiple = True
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class REF_MEASUREMENT(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class REF_MEMORY_SEGMENT(Keyword):
    attrs = [
        (Ident, "Name"),
    ]


class REF_UNIT(Keyword):
    attrs = [
        (Ident, "Unit"),
    ]


class RESERVED(Keyword):
    multiple = True
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIGHT_SHIFT(Keyword):
    attrs = [
        (Ulong, "Bitcount"),
    ]


class RIP_ADDR_W(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIP_ADDR_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIP_ADDR_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIP_ADDR_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIP_ADDR_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class RIP_ADDR_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class ROOT(Keyword):
    pass


class SHIFT_OP_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SHIFT_OP_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SHIFT_OP_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SHIFT_OP_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SHIFT_OP_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SIGN_EXTEND(Keyword):
    pass


class SI_EXPONENTS(Keyword):
    attrs = [
        (Int, "Length"),
        (Int, "Mass"),
        (Int, "Time"),
        (Int, "ElectricCurrent"),
        (Int, "Temperature"),
        (Int, "AmountOfSubstance"),
        (Int, "LuminousIntensity"),
    ]


class SRC_ADDR_X(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SRC_ADDR_Y(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SRC_ADDR_Z(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SRC_ADDR_4(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class SRC_ADDR_5(Keyword):
    attrs = [
        (Uint, "Position"),
        (Datasize, "DataSize"),
    ]


class STATIC_RECORD_LAYOUT(Keyword):
    pass


class STATUS_STRING_REF(Keyword):
    attrs = [
        (Ident, "ConversionTable"),
    ]


class STEP_SIZE(Keyword):
    attrs = [
        (Float, "StepSize"),
    ]


class SUB_FUNCTION(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class SUB_GROUP(Keyword):
    block = True
    attrs = [
        (Ident, "Identifier", MULTIPLE),
    ]


class SUPPLIER(Keyword):
    attrs = [
        (String, "Manufacturer"),
    ]


class SYMBOL_LINK(Keyword):
    attrs = [
        (String, "SymbolName"),
        (Long, "Offset"),
    ]


class SYSTEM_CONSTANT(Keyword):
    multiple = True
    attrs = [
        (String, "Name"),
        (String, "Value"),
    ]


class S_REC_LAYOUT(Keyword):
    attrs = [
        (Ident, "Name"),
    ]


class UNIT(Keyword):
    multiple = True
    children = ['SI_EXPONENTS', 'REF_UNIT', 'UNIT_CONVERSION' ]
    block = True
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (String, "Display"),
        (Enum, "Type",
            ('DERIVED', 'EXTENDED_SI')
        ),
    ]


class UNIT_CONVERSION(Keyword):
    attrs = [
        (Float, "Gradient"),
        (Float, "Offset"),
    ]


class USER(Keyword):
    attrs = [
        (String, "UserName")
    ]


class USER_RIGHTS(Keyword):
    multiple = True
    children = ['READ_ONLY', 'REF_GROUP' ]
    block = True
    attrs = [
        (Ident, "UserLevelId")
    ]


class VAR_ADDRESS(Keyword):
    block = True
    attrs = [
        (Ulong, "Address", MULTIPLE),
    ]


class VAR_CHARACTERISTIC(Keyword):
    multiple = True
    children = ['VAR_ADDRESS']
    block = True
    attrs = [
        (Ident, "Name"),
        (Ident, "CriterionName", MULTIPLE),
    ]


class VAR_CRITERION(Keyword):
    multiple = True
    children = ['VAR_MEASUREMENT', 'VAR_SELECTION_CHARACTERISTIC' ]
    block = True
    attrs = [
        (Ident, "Name"),
        (String, "LongIdentifier"),
        (Ident, "Value", MULTIPLE),
    ]


class VAR_FORBIDDEN_COMB(Keyword):
    multiple = True
    attrs = [
        (Ident, "CriterionName"),
        (Ident, "CriterionValue")
        ## Hinweis: die Multiplizität bezieht sich hier auf das Tupel!!!
    ]


class VAR_MEASUREMENT(Keyword):
    attrs = [
        (Ident, "Name"),
    ]


class VAR_NAMING(Keyword):
    attrs = [
        (Enum, "Tag", ('NUMERIC', 'APLHA'))
    ]


class VAR_SELECTION_CHARACTERISTIC(Keyword):
    attrs = [
        (Ident, "Name"),
    ]


class VAR_SEPARATOR(Keyword):
    attrs = [
        (String, "Separator"),
    ]


class VARIANT_CODING(Keyword):
    children = ['VAR_CHARACTERISTIC', 'VAR_CRITERION', 'VAR_FORBIDDEN_COMB', 'VAR_NAMING',
        'VAR_SEPARATOR'
    ]
    block = True


class VERSION(Keyword):
    attrs = [
        (String, "VersionIdentifier")
    ]


class VIRTUAL(Keyword):
    block = True
    attrs = [
        (Ident, "MeasuringChannel", MULTIPLE),
    ]


class VIRTUAL_CHARACTERISTIC(Keyword):
    block = True
    attrs = [
        (String, "Formula"),
        (Ident, "Characteristic", MULTIPLE),
    ]


##
##
##
class RootElement(Keyword):
    children = ['ASAP2_VERSION', 'A2ML_VERSION', 'PROJECT']

###
###
###

KEYWORD_MAP = {
    "A2ML" : A2ML,
    "A2ML_VERSION" : A2ML_VERSION,
    "ADDR_EPK" : ADDR_EPK,
    "ADDRESS_EXTENSION" : ADDRESS_EXTENSION,
    "ALIGNMENT_BYTE" : ALIGNMENT_BYTE,
    "ALIGNMENT_FLOAT32_IEEE" : ALIGNMENT_FLOAT32_IEEE,
    "ALIGNMENT_FLOAT64_IEEE" : ALIGNMENT_FLOAT64_IEEE,
    "ALIGNMENT_INT64" : ALIGNMENT_INT64,
    "ALIGNMENT_LONG" : ALIGNMENT_LONG,
    "ALIGNMENT_WORD" : ALIGNMENT_WORD,
    "ANNOTATION" : ANNOTATION,
    "ANNOTATION_LABEL" : ANNOTATION_LABEL,
    "ANNOTATION_ORIGIN" : ANNOTATION_ORIGIN,
    "ANNOTATION_TEXT" : ANNOTATION_TEXT,
    "ARRAY_SIZE" : ARRAY_SIZE,
    "ASAP2_VERSION" : ASAP2_VERSION,
    "AUTO_FLASH_BACK" : AUTO_FLASH_BACK,
    "AXIS_DESCR" : AXIS_DESCR,
    "AXIS_PTS" : AXIS_PTS,
    "AXIS_PTS_REF" : AXIS_PTS_REF,
    "AXIS_PTS_X" : AXIS_PTS_X,
    "AXIS_PTS_Y" : AXIS_PTS_Y,
    "AXIS_PTS_Z" : AXIS_PTS_Z,
    "AXIS_PTS_4" : AXIS_PTS_4,
    "AXIS_PTS_5" : AXIS_PTS_5,
    "AXIS_RESCALE_X" : AXIS_RESCALE_X,
    "AXIS_RESCALE_Y" : AXIS_RESCALE_Y,
    "AXIS_RESCALE_Z" : AXIS_RESCALE_Z,
    "AXIS_RESCALE_4" : AXIS_RESCALE_4,
    "AXIS_RESCALE_5" : AXIS_RESCALE_5,
    "BAUDRATE" : BAUDRATE,
    "BYTES_ONLY" : BYTES_ONLY,
    "BIT_MASK" : BIT_MASK,
    "BIT_OPERATION" : BIT_OPERATION,
    "BYTE_ORDER" : BYTE_ORDER,
    "BTL_CYCLES" : BTL_CYCLES,
    "CALIBRATION_ACCESS" : CALIBRATION_ACCESS,
    "CALIBRATION_HANDLE" : CALIBRATION_HANDLE,
    "CALIBRATION_HANDLE_TEXT" : CALIBRATION_HANDLE_TEXT,
    "CALIBRATION_METHOD" : CALIBRATION_METHOD,
    "CAN_ID_FIXED" : CAN_ID_FIXED,
    "CAN_ID_VARIABLE" : CAN_ID_VARIABLE,
    "CAN_PARAM" : CAN_PARAM,
    "CHARACTERISTIC" : CHARACTERISTIC,
    "CHECKSUM_CALCULATION" : CHECKSUM_CALCULATION,
    "CHECKSUM_PARAM" : CHECKSUM_PARAM,
    "COEFFS" : COEFFS,
    "COEFFS_LINEAR" : COEFFS_LINEAR,
    "COMPARISON_QUANTITY" : COMPARISON_QUANTITY,
    "COMPU_METHOD" : COMPU_METHOD,
    "COMPU_TAB" : COMPU_TAB,
    "COMPU_TAB_REF" : COMPU_TAB_REF,
    "COMPU_VTAB" : COMPU_VTAB,
    "COMPU_VTAB_RANGE" : COMPU_VTAB_RANGE,
    "CONSISTENCY" : CONSISTENCY,
    "CPU_TYPE" : CPU_TYPE,
    "CURVE_AXIS_REF" : CURVE_AXIS_REF,
    "CUSTOMER" : CUSTOMER,
    "CUSTOMER_NO" : CUSTOMER_NO,
    "DATA_SIZE" : DATA_SIZE,
    "DAQ_MODE" : DAQ_MODE,
    "DEF_CHARACTERISTIC" : DEF_CHARACTERISTIC,
    "DEFAULT" : DEFAULT,
    "DEFAULT_VALUE" : DEFAULT_VALUE,
    "DEFAULT_VALUE_NUMERIC" : DEFAULT_VALUE_NUMERIC,
    "DEFINED_PAGES" : DEFINED_PAGES,
    "DEPENDENT_CHARACTERISTIC" : DEPENDENT_CHARACTERISTIC,
    "DEPOSIT" : DEPOSIT,
    "DISCRETE" : DISCRETE,
    "DISPLAY_IDENTIFIER" : DISPLAY_IDENTIFIER,
    "DIST_OP_X" : DIST_OP_X,
    "DIST_OP_Y" : DIST_OP_Y,
    "DIST_OP_Z" : DIST_OP_Z,
    "DIST_OP_4" : DIST_OP_4,
    "DIST_OP_5" : DIST_OP_5,
    "ECU" : ECU,
    "ECU_ADDRESS" : ECU_ADDRESS,
    "ECU_ADDRESS_EXTENSION" : ECU_ADDRESS_EXTENSION,
    "ECU_CALIBRATION_OFFSET" : ECU_CALIBRATION_OFFSET,
    "EEPROM" : EEPROM,
    "EPK" : EPK,
    "ERROR_MASK" : ERROR_MASK,
    "EXCLUSIVE" : EXCLUSIVE,
    "EXTENDED_LIMITS" : EXTENDED_LIMITS,
    "FIRST_PID" : FIRST_PID,
    "FIX_AXIS_PAR" : FIX_AXIS_PAR,
    "FIX_AXIS_PAR_DIST" : FIX_AXIS_PAR_DIST,
    "FIX_AXIS_PAR_LIST" : FIX_AXIS_PAR_LIST,
    "FIX_NO_AXIS_PTS_X" : FIX_NO_AXIS_PTS_X,
    "FIX_NO_AXIS_PTS_Y" : FIX_NO_AXIS_PTS_Y,
    "FIX_NO_AXIS_PTS_Z" : FIX_NO_AXIS_PTS_Z,
    "FIX_NO_AXIS_PTS_4" : FIX_NO_AXIS_PTS_4,
    "FIX_NO_AXIS_PTS_5" : FIX_NO_AXIS_PTS_5,
    "FNC_VALUES" : FNC_VALUES,
    "FLASH" : FLASH,
    "FLASH_BACK": FLASH_BACK,
    "FORMAT" : FORMAT,
    "FORMULA" : FORMULA,
    "FORMULA_INV" : FORMULA_INV,
    "FRAME" : FRAME,
    "FRAME_MEASUREMENT" : FRAME_MEASUREMENT,
    "FUNCTION" : FUNCTION,
    "FUNCTION_LIST" : FUNCTION_LIST,
    "FUNCTION_VERSION" : FUNCTION_VERSION,
    "GROUP" : GROUP,
    "GUARD_RAILS" : GUARD_RAILS,
    "HEADER" : HEADER,
    "IDENTIFICATION" : IDENTIFICATION,
    "IF_DATA" : IF_DATA,
    "IN_MEASUREMENT" : IN_MEASUREMENT,
    "LAYOUT" : LAYOUT,
    "LEFT_SHIFT" : LEFT_SHIFT,
    "LENGTH" : LENGTH,
    "LOC_MEASUREMENT" : LOC_MEASUREMENT,
    "MAP_LIST" : MAP_LIST,
    "MATRIX_DIM" : MATRIX_DIM,
    "MAX_GRAD" : MAX_GRAD,
    "MAX_REFRESH" : MAX_REFRESH,
    "MEASUREMENT" : MEASUREMENT,
    "MEMORY_LAYOUT" : MEMORY_LAYOUT,
    "MEMORY_SEGMENT" : MEMORY_SEGMENT,
    "MOD_COMMON" : MOD_COMMON,
    "MOD_PAR" : MOD_PAR,
    "MODULE" : MODULE,
    "MONOTONY" : MONOTONY,
    "NO_AXIS_PTS_X" : NO_AXIS_PTS_X,
    "NO_AXIS_PTS_Y" : NO_AXIS_PTS_Y,
    "NO_AXIS_PTS_Z" : NO_AXIS_PTS_Z,
    "NO_AXIS_PTS_4" : NO_AXIS_PTS_4,
    "NO_AXIS_PTS_5" : NO_AXIS_PTS_5,
    "NO_OF_INTERFACES" : NO_OF_INTERFACES,
    "NO_RESCALE_X" : NO_RESCALE_X,
    "NO_RESCALE_Y" : NO_RESCALE_Y,
    "NO_RESCALE_Z" : NO_RESCALE_Z,
    "NO_RESCALE_4" : NO_RESCALE_4,
    "NO_RESCALE_5" : NO_RESCALE_5,
    "NUMBER" : NUMBER,
    "OFFSET_X" : OFFSET_X,
    "OFFSET_Y" : OFFSET_Y,
    "OFFSET_Z" : OFFSET_Z,
    "OFFSET_4" : OFFSET_4,
    "OFFSET_5" : OFFSET_5,
    "OPTIONAL_CMD" : OPTIONAL_CMD,
    "OUT_MEASUREMENT" : OUT_MEASUREMENT,
    "PHONE_NO" : PHONE_NO,
    "PHYS_UNIT" : PHYS_UNIT,
    "PROJECT" : PROJECT,
    "PROJECT_NO" : PROJECT_NO,
    "QP_BLOB": QP_BLOB,
    "RAM" : RAM,
    "RAM_INIT_BY_ECU" : RAM_INIT_BY_ECU,
    "RAM_INIT_BY_TOOL" : RAM_INIT_BY_TOOL,
    "RASTER" : RASTER,
    "RASTERAttr" : RASTERAttr,
    "READ_ONLY" : READ_ONLY,
    "READ_WRITE" : READ_WRITE,
    "RECORD_LAYOUT" : RECORD_LAYOUT,
    "REDUCTION_ALLOWED" : REDUCTION_ALLOWED,
    "REF_CHARACTERISTIC" : REF_CHARACTERISTIC,
    "REF_GROUP" : REF_GROUP,
    "REF_MEASUREMENT" : REF_MEASUREMENT,
    "REF_MEMORY_SEGMENT" : REF_MEMORY_SEGMENT,
    "REF_UNIT" : REF_UNIT,
    "RESERVED" : RESERVED,
    "RESUME_SUPPORTED" : RESUME_SUPPORTED,
    "ROM" : ROM,
    "RIGHT_SHIFT" : RIGHT_SHIFT,
    "RIP_ADDR_W" : RIP_ADDR_W,
    "RIP_ADDR_X" : RIP_ADDR_X,
    "RIP_ADDR_Y" : RIP_ADDR_Y,
    "RIP_ADDR_Z" : RIP_ADDR_Z,
    "RIP_ADDR_4" : RIP_ADDR_4,
    "RIP_ADDR_5" : RIP_ADDR_5,
    "ROOT" : ROOT,
    "SAMPLE_RATE" : SAMPLE_RATE,
    "SAMPLE_POINT" : SAMPLE_POINT,
    "SHIFT_OP_X" : SHIFT_OP_X,
    "SHIFT_OP_Y" : SHIFT_OP_Y,
    "SHIFT_OP_Z" : SHIFT_OP_Z,
    "SHIFT_OP_4" : SHIFT_OP_4,
    "SHIFT_OP_5" : SHIFT_OP_5,
    "SIGN_EXTEND" : SIGN_EXTEND,
    "SI_EXPONENTS" : SI_EXPONENTS,
    "SJW" : SJW,
    "SOURCE": SOURCE,
    "SRC_ADDR_X" : SRC_ADDR_X,
    "SRC_ADDR_Y" : SRC_ADDR_Y,
    "SRC_ADDR_Z" : SRC_ADDR_Z,
    "SRC_ADDR_4" : SRC_ADDR_4,
    "SRC_ADDR_5" : SRC_ADDR_5,
    "STATIC_RECORD_LAYOUT" : STATIC_RECORD_LAYOUT,
    "STATUS_STRING_REF" : STATUS_STRING_REF,
    "STEP_SIZE" : STEP_SIZE,
    "STORE_SUPPORTED" : STORE_SUPPORTED,
    "SUB_FUNCTION" : SUB_FUNCTION,
    "SUB_GROUP" : SUB_GROUP,
    "SUPPLIER" : SUPPLIER,
    "SYMBOL_LINK" : SYMBOL_LINK,
    "SYNC_EDGE" : SYNC_EDGE,
    "SYSTEM_CONSTANT" : SYSTEM_CONSTANT,
    "S_REC_LAYOUT" : S_REC_LAYOUT,
    "TP_BLOB" : TP_BLOB,
    "UNIT" : UNIT,
    "UNIT_CONVERSION" : UNIT_CONVERSION,
    "USER" : USER,
    "USER_RIGHTS" : USER_RIGHTS,
    "VAR_ADDRESS" : VAR_ADDRESS,
    "VAR_CHARACTERISTIC" : VAR_CHARACTERISTIC,
    "VAR_CRITERION" : VAR_CRITERION,
    "VAR_FORBIDDEN_COMB" : VAR_FORBIDDEN_COMB,
    "VAR_MEASUREMENT" : VAR_MEASUREMENT,
    "VAR_NAMING" : VAR_NAMING,
    "VAR_SELECTION_CHARACTERISTIC" : VAR_SELECTION_CHARACTERISTIC,
    "VAR_SEPARATOR" : VAR_SEPARATOR,
    "VARIANT_CODING" : VARIANT_CODING,
    "VERSION" : VERSION,
    "VIRTUAL" : VIRTUAL,
    "VIRTUAL_CHARACTERISTIC" : VIRTUAL_CHARACTERISTIC,
}


class A2LElement(object):

    def __str__(self):
        result = []
        result.append("%s {" % self.__class__.__name__)
        for attr in self.attrs:
            value = getattr(self, attr)
            formatStr = '    %s = "%s";' if isinstance(value, str) else "    %s = %s;"
            result.append(formatStr % (attr, value))
        result.append("}")

        return "\n".join(result)


def instanceFactory(className, **kws):
    """Create an instance of a given class.
    """
    klass = type(str(className), (A2LElement, ), {})
    inst = klass()
    inst.attrs = []
    for k, v in kws.items():
        setattr(inst, k, v)
        inst.attrs.append(k)
    inst.children = []
    return inst

