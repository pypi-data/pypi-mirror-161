"""
   Copyright 2016 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from math import sqrt, floor
from opencmiss.zinc.field import Field


def FieldIsRealArgument(field):
    """
    Conditional function returning true if the field is real argument
    """
    return field.castArgumentReal().isValid()


def FieldIsRealValued(field):
    """
    Conditional function returning true if the field has real values
    """
    return field.getValueType() == Field.VALUE_TYPE_REAL


def FieldIsScalar(field):
    """
    Conditional function returning true if the field is real with 1 component
    """
    return (field.getValueType() == Field.VALUE_TYPE_REAL) and \
           (field.getNumberOfComponents() == 1)


def FieldIsCoordinateCapable(field):
    """
    Conditional function returning true if the field can be used as a coordinate
    field, i.e. is real valued with up to 3 component
    """
    return (field.getValueType() == Field.VALUE_TYPE_REAL) and \
           (field.getNumberOfComponents() <= 3)


def FieldIsOrientationScaleCapable(field):
    """
    Conditional function returning true if the field can be used to orient or scale
    glyphs. Generally, this means it has 1,2,3,4,6 or 9 components, where:
    1 = scalar (no vector, isotropic scaling).
    2 = 1 2-D vector (2nd axis is normal in plane, 3rd is out of 2-D plane);
    3 = 1 3-D vector (orthogonal 2nd and 3rd axes are arbitrarily chosen);
    4 = 2 2-D vectors (3rd axis taken as out of 2-D plane);
    6 = 2 3-D vectors (3rd axis found from cross product);
    9 = 3 3-D vectors = complete definition of 3 axes.
    """
    return (field.getValueType() == Field.VALUE_TYPE_REAL) and \
           (field.getNumberOfComponents() in [1, 2, 3, 4, 6, 9])


def FieldIsStreamVectorCapable(field):
    """
    Conditional function returning true if the field can be used as a
    streamline stream vector field.
    For a 3-D domain with a 3-D coordinate field, can have 3, 6 or 9 components;
    extra components set the lateral axes for extruded profiles.
    For a 2-D domain the stream vector may have 2 components.
    """
    return (field.getValueType() == Field.VALUE_TYPE_REAL) and \
           (field.getNumberOfComponents() in [2, 3, 6, 9])


def FieldIsRCAndThreeComponents(field):
    return (field.getCoordinateSystemType() == Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN) and \
           (field.getNumberOfComponents == 3)


def FieldIsRCAndCoordinateCapable(field):
    return (field.getCoordinateSystemType() == Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN) and \
           (FieldIsCoordinateCapable(field))


def FieldIsArgumentReal(field):
    return field.castArgumentReal().isValid()


def FieldIsMeshLocation(field):
    """
    Conditional function returning true if the field is mesh location
    """
    return field.getValueType() == Field.VALUE_TYPE_MESH_LOCATION


def FieldIsEigenvalues(field):
    eigenvaluesField = field.castEigenvalues()
    return eigenvaluesField.isValid()


def FieldIsFiniteElement(field):
    finiteElementField = field.castFiniteElement()
    return finiteElementField.isValid()


def FieldIsSquareMatrix(field):
    numberOfComponents = field.getNumberOfComponents()
    if numberOfComponents > 1:
        sqrt1 = sqrt(numberOfComponents)
        if 0 == floor(sqrt1) - sqrt1:
            return field.getValueType() == Field.VALUE_TYPE_REAL
    return False


def FieldIsDeterminantEligible(field):
    return (field.getValueType() == Field.VALUE_TYPE_REAL) and \
           (field.getNumberOfComponents() in [4, 9])


def is_field_image(self, field_in: Field):
    """
    Conditional function returning True if the field is an image field.
    """
    return field_in.castImage().isValid() and field_in.isManaged()
