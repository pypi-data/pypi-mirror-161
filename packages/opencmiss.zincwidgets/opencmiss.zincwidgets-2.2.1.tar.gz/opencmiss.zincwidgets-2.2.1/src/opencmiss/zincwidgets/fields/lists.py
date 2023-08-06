MEASURE_TYPES = ["C1", "G1", "Surface Normal"]
MESH_NAMES = ["mesh3d", "mesh2d", "mesh1d"]
SEARCH_MODES = ["Exact", "Nearest"]
FACE_TYPES = ["all", "any face", "no face", "xi1 = 0", "xi1 = 1", "xi2 = 0", "xi2 = 1", "xi3 = 0", "xi3 = 0"]
VALUE_TYPES = ["value", "d_ds1", "d_ds2", "d2_ds1ds2", "d_ds3", "d2_ds1ds3", "d2_ds2ds3", "d3_ds1ds2ds3"]
QUADRATURE_RULES = ["Gaussian", "Mid-point"]
INTERNAL_FIELD_NAMES = ["xi", "cmiss_number", "cmiss_selection"]

INTERNAL_FIELD_TYPE_NAME = "<internal>"
NONE_FIELD_TYPE_NAME = "<unknown>"

FIELD_TYPES = [
    'FieldAbs', 'FieldAcos', 'FieldAdd', 'FieldAlias', 'FieldAnd', 'FieldApply', 'FieldArgumentReal', 'FieldAsin',
    'FieldAtan', 'FieldAtan2', 'FieldComponent', 'FieldConcatenate', 'FieldConstant',
    'FieldCoordinateTransformation', 'FieldCos', 'FieldCrossProduct', 'FieldCurl',
    'FieldDerivative', 'FieldDeterminant', 'FieldDivergence', 'FieldDivide',
    'FieldDotProduct', 'FieldEdgeDiscontinuity', 'FieldEigenvalues',
    'FieldEigenvectors', 'FieldEmbedded', 'FieldEqualTo', 'FieldExp',
    'FieldFibreAxes', 'FieldFindMeshLocation', 'FieldFiniteElement', 'FieldGradient',
    'FieldGreaterThan', 'FieldIdentity', 'FieldIf', 'FieldIsDefined', 'FieldIsExterior',
    'FieldIsOnFace', 'FieldLessThan', 'FieldLog', 'FieldMagnitude', 'FieldMatrixInvert',
    'FieldMatrixMultiply', 'FieldMeshIntegral', 'FieldMultiply', 'FieldNodeValue', 'FieldNormalise', 'FieldNot',
    'FieldOr', 'FieldPower', 'FieldProjection', 'FieldSin', 'FieldSqrt',
    'FieldStoredMeshLocation', 'FieldStoredString', 'FieldStringConstant', 'FieldSubtract',
    'FieldSumComponents', 'FieldTan', 'FieldTimeLookup', 'FieldTimeValue', 'FieldTranspose',
    'FieldVectorCoordinateTransformation', 'FieldXor'
]

FIELDS_REQUIRING_REAL_LIST_VALUES = ['FieldConstant']
FIELDS_REQUIRING_STRING_VALUE = ['FieldStringConstant']
FIELDS_REQUIRING_NUMBER_OF_COMPONENTS = ['FieldFiniteElement', 'FieldArgumentReal']
FIELDS_REQUIRING_NO_ARGUMENTS = ['FieldStoredString', 'FieldIsExterior']
FIELDS_REQUIRING_ONE_SOURCE_FIELD = ['FieldAlias']
FIELDS_REQUIRING_ONE_REAL_SOURCE_FIELD = [
    'FieldAbs', 'FieldLog', 'FieldSqrt', 'FieldExp', 'FieldIdentity',
    'FieldNot', 'FieldSin', 'FieldCos', 'FieldTan', 'FieldAsin', 'FieldAcos',
    'FieldAtan', 'FieldMagnitude', 'FieldNormalise', 'FieldSumComponents',
    'FieldCoordinateTransformation',
]
FIELDS_REQUIRING_TWO_SOURCE_FIELDS = [
    'FieldVectorCoordinateTransformation', 'FieldCurl',
    'FieldDivergence', 'FieldEmbedded', 'FieldEqualTo',
]
FIELDS_REQUIRING_TWO_REAL_SOURCE_FIELDS = [
    'FieldAdd', 'FieldPower', 'FieldMultiply', 'FieldDivide',
    'FieldSubtract', 'FieldAnd', 'FieldGreaterThan',
    'FieldLessThan', 'FieldOr', 'FieldXor', 'FieldAtan2',
    'FieldDotProduct', 'FieldProjection'
]
FIELDS_REQUIRING_ONE_REAL_FIELD_ONE_COORDINATE_FIELD = ['FieldGradient']
FIELDS_REQUIRING_ONE_ANY_FIELD_ONE_SCALAR_FIELD = ['FieldTimeLookup']
FIELDS_REQUIRING_TWO_COORDINATE_FIELDS = ['FieldFibreAxes']
FIELDS_REQUIRING_ONE_DETERMINANT_SOURCE_FIELD = ['FieldDeterminant']
FIELDS_REQUIRING_ONE_SQUARE_MATRIX_SOURCE_FIELD = ['FieldEigenvalues', 'FieldMatrixInvert']
FIELDS_REQUIRING_ONE_EIGENVALUES_SOURCE_FIELD = ['FieldEigenvectors']
FIELDS_REQUIRING_THREE_SOURCE_FIELDS = ['FieldIf']
FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS = ['FieldConcatenate', 'FieldCrossProduct']
FIELDS_REQUIRING_MESH = ['FieldStoredMeshLocation']
