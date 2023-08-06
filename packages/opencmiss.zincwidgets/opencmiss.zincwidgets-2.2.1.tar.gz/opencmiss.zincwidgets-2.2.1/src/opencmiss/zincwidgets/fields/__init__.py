from opencmiss.utils.zinc.general import ChangeManager
from opencmiss.zincwidgets.fieldconditions import FieldIsRealValued, FieldIsDeterminantEligible, FieldIsSquareMatrix, FieldIsScalar, FieldIsFiniteElement, \
    FieldIsCoordinateCapable, FieldIsEigenvalues, FieldIsArgumentReal
from opencmiss.zincwidgets.fields.lists import NONE_FIELD_TYPE_NAME, FIELD_TYPES, FIELDS_REQUIRING_REAL_LIST_VALUES, FIELDS_REQUIRING_STRING_VALUE, \
    FIELDS_REQUIRING_ONE_SOURCE_FIELD, FIELDS_REQUIRING_NO_ARGUMENTS, FIELDS_REQUIRING_ONE_REAL_SOURCE_FIELD, FIELDS_REQUIRING_TWO_SOURCE_FIELDS, \
    FIELDS_REQUIRING_TWO_REAL_SOURCE_FIELDS, FIELDS_REQUIRING_THREE_SOURCE_FIELDS, FIELDS_REQUIRING_ONE_DETERMINANT_SOURCE_FIELD, FIELDS_REQUIRING_ONE_SQUARE_MATRIX_SOURCE_FIELD, \
    FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS, FIELDS_REQUIRING_ONE_REAL_FIELD_ONE_COORDINATE_FIELD, FIELDS_REQUIRING_TWO_COORDINATE_FIELDS, \
    FIELDS_REQUIRING_ONE_EIGENVALUES_SOURCE_FIELD, FIELDS_REQUIRING_ONE_ANY_FIELD_ONE_SCALAR_FIELD, FIELDS_REQUIRING_NUMBER_OF_COMPONENTS, INTERNAL_FIELD_NAMES, \
    INTERNAL_FIELD_TYPE_NAME
from opencmiss.zincwidgets.fields.requirements import FieldRequirementRealListValues, FieldRequirementStringValue, FieldRequirementSourceField, FieldRequirementNumberOfRows, \
    FieldRequirementNaturalNumberVector, FieldRequirementMesh, FieldRequirementNeverMet, FieldRequirementMeasure, FieldRequirementOptionalSourceField, \
    FieldRequirementSearchMode, FieldRequirementMeshLike, FieldRequirementNaturalNumberValue, FieldRequirementFaceType, FieldRequirementValueType, \
    FieldRequirementNumberOfComponents, FieldRequirementSourceFieldRegionDependent, FieldRequirementRegion, FieldRequirementSourceFieldRegionDependentFieldDependent, \
    FieldRequirementTimekeeper, FieldRequirementQuadratureRule


class FieldBase(object):

    def __init__(self):
        super().__init__()
        self._field = None

    def set_field(self, field):
        self._field = None
        if field and field.isValid():
            self._field = field

    def get_field(self):
        return self._field

    def get_field_name(self):
        if self._field is not None:
            return self._field.getName()

        return NONE_FIELD_TYPE_NAME

    def _is_defined(self):
        return bool(self._field and self._field.isValid())

    def _set_type_coordinate(self, state):
        self._field.setTypeCoordinate(state)

    def _is_type_coordinate(self):
        return self._field.isTypeCoordinate()

    def _set_managed(self, state):
        self._field.setManaged(state)

    def _is_managed(self):
        return self._field.isManaged()

    def populate_requirement(self, index, requirement):
        if self._field and self._field.isValid():
            field_type = self.get_field_type()
            field_module = self._field.getFieldmodule()
            field_cache = field_module.createFieldcache()
            if field_type == "FieldConstant":
                if index != 0:
                    return
                numberOfComponents = self._field.getNumberOfComponents()
                returnedValues = self._field.evaluateReal(field_cache, numberOfComponents)
                requirement.set_value(returnedValues[1])
            elif field_type == "FieldComponent":
                if index == 0:
                    number_of_components = self._field.getNumberOfComponents()
                    component_field = self._field.castComponent()
                    values = []
                    for i in range(1, number_of_components + 1):
                        values.append(component_field.getSourceComponentIndex(i))

                    requirement.set_value(values)
                elif index == 1:
                    requirement.set_value(self._field.getSourceField(1))
            elif field_type in FIELDS_REQUIRING_NUMBER_OF_COMPONENTS:
                number_of_components = self._field.getNumberOfComponents()
                requirement.set_value(number_of_components)
            elif field_type == "FieldStringConstant":
                if index != 0:
                    return
                text = self._field.evaluateString(field_cache)
                requirement.set_value(text)
            elif field_type == "FieldTranspose":
                if index == 0:
                    requirement.set_value("")
                elif index == 1:
                    requirement.set_value(self._field.getSourceField(1))
            elif field_type in FIELDS_REQUIRING_ONE_REAL_SOURCE_FIELD or \
                    field_type in FIELDS_REQUIRING_ONE_DETERMINANT_SOURCE_FIELD or \
                    field_type in FIELDS_REQUIRING_ONE_SQUARE_MATRIX_SOURCE_FIELD or \
                    field_type in FIELDS_REQUIRING_ONE_SOURCE_FIELD or \
                    field_type in FIELDS_REQUIRING_TWO_REAL_SOURCE_FIELDS or \
                    field_type in FIELDS_REQUIRING_TWO_SOURCE_FIELDS or \
                    field_type in FIELDS_REQUIRING_THREE_SOURCE_FIELDS or \
                    field_type in FIELDS_REQUIRING_ONE_REAL_FIELD_ONE_COORDINATE_FIELD or \
                    field_type in FIELDS_REQUIRING_TWO_COORDINATE_FIELDS or \
                    field_type in FIELDS_REQUIRING_ONE_EIGENVALUES_SOURCE_FIELD or \
                    field_type in FIELDS_REQUIRING_ONE_ANY_FIELD_ONE_SCALAR_FIELD:
                requirement.set_value(self._field.getSourceField(index + 1))
            elif field_type == "FieldEdgeDiscontinuity":
                if index == 0:
                    requirement.set_value(self._field.getSourceField(1))
                elif index == 1:
                    index = self._field.getMeasure()
                    requirement.set_value(index)
                elif index == 2:
                    field = self._field.getConditionalField()
                    if field and field.isValid():
                        requirement.set_value(field)
            elif field_type == "FieldFindMeshLocation":
                if index == 0:
                    requirement.set_value(self._field.getSourceField(1))
                elif index == 1:
                    requirement.set_value(self._field.getSourceField(2))
                elif index == 2:
                    mesh = self._field.castFindMeshLocation().getMesh()
                    requirement.set_value(mesh)
                elif index == 3:
                    index = self._field.getSearchMode()
                    requirement.set_value(index)
                elif index == 4:
                    search_mesh = self._field.castFindMeshLocation().getSearchMesh()
                    requirement.set_value(search_mesh)
            elif field_type == "FieldStoredMeshLocation":
                mesh = self._field.castStoredMeshLocation().getMesh()
                requirement.set_value(mesh)
            elif field_type == "FieldDerivative":
                if index == 0:
                    requirement.set_value(self._field.getSourceField(1))
                elif index == 1:
                    requirement.set_value(self._field.castDerivative().getXiIndex())
            elif field_type == "FieldMeshIntegral":
                if index == 0:
                    requirement.set_value(self._field.getSourceField(1))
                elif index == 1:
                    requirement.set_value(self._field.getSourceField(2))
                elif index == 2:
                    mesh = self._field.castMeshIntegral().getMesh()
                    requirement.set_value(mesh)
                elif index == 3:
                    number_of_components = self._field.getNumberOfComponents()
                    result, numbers_of_points = self._field.castMeshIntegral().getNumbersOfPoints(number_of_components)
                    requirement.set_value(numbers_of_points)
                elif index == 4:
                    quadrature_rule = self._field.castMeshIntegral().getElementQuadratureRule()
                    requirement.set_value(quadrature_rule)
            elif field_type == "FieldIsOnFace":
                requirement.set_value(self._field.castIsOnFace().getElementFaceType())
            elif field_type == "FieldNodeValue":
                if index == 0:
                    requirement.set_value(self._field.getSourceField(1))
                elif index == 1:
                    requirement.set_value(self._field.castNodeValue().getNodeValueLabel())
                elif index == 2:
                    requirement.set_value(self._field.castNodeValue().getVersionNumber())
            elif field_type in FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS:
                number_of_source_fields = self._field.getNumberOfSourceFields()
                if index < number_of_source_fields:
                    field = self._field.getSourceField(index + 1)
                    requirement.set_value(field)
                elif index == number_of_source_fields:
                    requirement.set_value(number_of_source_fields)
            elif field_type == "FieldApply":
                if index == 0:
                    field = self._field.getSourceField(1)
                    requirement.set_value(field)
                elif index == 1:
                    field = self._field.getSourceField(1)
                    requirement.set_value(field.getFieldmodule().getRegion())
                elif index == 2:
                    field = self._field.castApply().getBindArgumentField(1)
                    requirement.set_value(field)
                elif index == 3:
                    field = self._field.castApply().getBindArgumentField(1)
                    source_field = self._field.castApply().getBindArgumentSourceField(field)
                    requirement.set_value(source_field)


class FieldTypeBase(object):

    def __init__(self):
        super().__init__()
        self._field_type = None
        self._properties = None
        self._managed = False
        self._type_coordinate = False
        self._region = None
        self._timekeeper = None

    def _pre_set_managed(self, state):
        self._managed = state

    def _pre_is_managed(self):
        return self._managed

    def _pre_set_type_coordinate(self, state):
        self._type_coordinate = state

    def _pre_is_type_coordinate(self):
        return self._type_coordinate

    def _requirements(self, kind=None):
        def _filter(p):
            if kind is None:
                return True

            return p["group"] == kind

        return [r for p in self._properties if _filter(p) for r in p["requirements"]]

    def set_region(self, region):
        self._region = region

    def set_timekeeper(self, timekeeper):
        self._timekeeper = timekeeper

    def set_field_type(self, field_type):
        self._field_type = NONE_FIELD_TYPE_NAME
        if field_type in FIELD_TYPES:
            self._field_type = field_type

    def get_field_type(self):
        return self._field_type

    def has_requirements_met(self):
        if self._properties is None:
            return False

        return all([r.fulfilled() for r in self._requirements()])

    def has_additional_requirements_met(self):
        return all([r.fulfilled() for r in self._requirements("Additional Properties")])

    def set_required_source_fields(self):
        """
        For fields that have a variable number of source fields this method
        updates the source field parameters when the number of source fields
        property changes.
        """
        additional_properties = self._requirements("Additional Properties")
        field_requirements = []
        for index in range(additional_properties[0].value()):
            field_requirements.append(FieldRequirementSourceField(self._region, f"Source Field {index + 1}:", FieldIsRealValued))
        parameters_index = -1
        for index, prop in enumerate(self._properties):
            if prop["group"] == "Parameters":
                parameters_index = index
                break

        self._properties[parameters_index] = {"group": "Parameters", "requirements": field_requirements}

    def properties(self):
        if self._properties is not None:
            return self._properties

        watch_regions = []
        field_requirements = []
        if self._field_type in FIELDS_REQUIRING_REAL_LIST_VALUES:
            field_requirements.append(FieldRequirementRealListValues())
        elif self._field_type in FIELDS_REQUIRING_STRING_VALUE:
            field_requirements.append(FieldRequirementStringValue())
        elif self._field_type in FIELDS_REQUIRING_ONE_SOURCE_FIELD:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:"))
        elif self._field_type in FIELDS_REQUIRING_NO_ARGUMENTS:
            pass
        elif self._field_type == "FieldTranspose":
            field_requirements.append(FieldRequirementNumberOfRows())
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsRealValued))
        elif self._field_type == "FieldComponent":
            field_requirements.append(FieldRequirementNaturalNumberVector("Component Indices:"))
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsRealValued))
        elif self._field_type in FIELDS_REQUIRING_ONE_REAL_SOURCE_FIELD or \
                self._field_type == "FieldEdgeDiscontinuity":
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsRealValued))
        elif self._field_type in FIELDS_REQUIRING_TWO_SOURCE_FIELDS:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 1:"))
            field_label = "Embedded Location:" if self._field_type == "FieldEmbedded" else "Source Field 2:"
            field_requirements.append(FieldRequirementSourceField(self._region, field_label))
        elif self._field_type in FIELDS_REQUIRING_TWO_REAL_SOURCE_FIELDS:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 1:", FieldIsRealValued))
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 2:", FieldIsRealValued))
        elif self._field_type in FIELDS_REQUIRING_THREE_SOURCE_FIELDS:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 1:", FieldIsRealValued))
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 2:", FieldIsRealValued))
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 3:"))
        elif self._field_type in FIELDS_REQUIRING_ONE_DETERMINANT_SOURCE_FIELD:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsDeterminantEligible))
        elif self._field_type in FIELDS_REQUIRING_ONE_SQUARE_MATRIX_SOURCE_FIELD:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsSquareMatrix))
        elif self._field_type in FIELDS_REQUIRING_NUMBER_OF_COMPONENTS:
            field_requirements.append(FieldRequirementNumberOfComponents())
        elif self._field_type == "FieldFindMeshLocation":
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsRealValued))
            field_requirements.append(FieldRequirementSourceField(self._region, "Mesh Field:", FieldIsRealValued))
            field_requirements.append(FieldRequirementMesh(self._region))
        elif self._field_type == "FieldStoredMeshLocation":
            field_requirements.append(FieldRequirementMesh(self._region))
        elif self._field_type == "FieldGradient":
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsRealValued))
            field_requirements.append(FieldRequirementSourceField(self._region, "Coordinate Field:", FieldIsCoordinateCapable))
        elif self._field_type == "FieldDerivative":
            field_requirements.append(FieldRequirementSourceField(self._region, "Coordinate Field:", FieldIsCoordinateCapable))
            field_requirements.append(FieldRequirementNaturalNumberValue("xi index:"))
        elif self._field_type == "FieldFibreAxes":
            field_requirements.append(FieldRequirementSourceField(self._region, "Fibre Field:", FieldIsCoordinateCapable))
            field_requirements.append(FieldRequirementSourceField(self._region, "Coordinate Field:", FieldIsCoordinateCapable))
        elif self._field_type in FIELDS_REQUIRING_ONE_ANY_FIELD_ONE_SCALAR_FIELD:
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:"))
            field_requirements.append(FieldRequirementSourceField(self._region, "Time Field:", FieldIsScalar))
        elif self._field_type == "FieldEigenvectors":
            field_requirements.append(FieldRequirementSourceField(self._region, "Eigenvalues Field:", FieldIsEigenvalues))
        elif self._field_type == "FieldIsOnFace":
            field_requirements.append(FieldRequirementFaceType())
        elif self._field_type == "FieldNodeValue":
            field_requirements.append(FieldRequirementSourceField(self._region, "Source Field:", FieldIsFiniteElement))
            field_requirements.append(FieldRequirementValueType())
            field_requirements.append(FieldRequirementNaturalNumberValue("Version number:"))
        elif self._field_type == "FieldMeshIntegral":
            field_requirements.append(FieldRequirementSourceField(self._region, "Integrand Field:"))
            field_requirements.append(FieldRequirementSourceField(self._region, "Coordinate Field:", FieldIsCoordinateCapable))
            field_requirements.append(FieldRequirementMeshLike(self._region))
        elif self._field_type in FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS:
            if self._is_defined():
                number_of_source_fields = self._field.getNumberOfSourceFields()
                for i in range(number_of_source_fields):
                    field_requirements.append(FieldRequirementSourceField(self._region, f"Source Field {i + 1}", FieldIsRealValued))
            else:
                field_requirements.append(FieldRequirementSourceField(self._region, "Source Field 1:", FieldIsRealValued))
        elif self._field_type == "FieldApply":
            region_dependent_field = FieldRequirementSourceFieldRegionDependent(self._region.getRoot(), "Source Field:", None)
            watch_regions.append(region_dependent_field)
            field_requirements.append(region_dependent_field)
        elif self._field_type == "FieldTimeValue":
            field_requirements.append(FieldRequirementTimekeeper(self._timekeeper))

        additional_requirements = []
        if self._field_type == "FieldEdgeDiscontinuity":
            additional_requirements.append(FieldRequirementMeasure())
            additional_requirements.append(FieldRequirementOptionalSourceField(self._region, "Conditional Field:", FieldIsScalar))
        elif self._field_type == "FieldFindMeshLocation":
            additional_requirements.append(FieldRequirementSearchMode())
            additional_requirements.append(FieldRequirementMeshLike(self._region))
        elif self._field_type == "FieldMeshIntegral":
            additional_requirements.append(FieldRequirementNaturalNumberVector("Numbers of Points:"))
            additional_requirements.append(FieldRequirementQuadratureRule())
        elif self._field_type == "FieldApply":
            controlling_region = FieldRequirementRegion(self._region.getRoot(), "Evaluate Field Region:")
            region_chooser = controlling_region.region_chooser()
            additional_requirements.append(controlling_region)
            region_dependent_field = FieldRequirementSourceFieldRegionDependentFieldDependent(self._region.getRoot(), watch_regions[0], "Bind Argument Field:", FieldIsArgumentReal)
            watch_regions.append(region_dependent_field)
            additional_requirements.append(region_dependent_field)
            additional_requirements.append(FieldRequirementSourceField(self._region, "Bind Source Field:", None))

            def _apply_region_chooser():
                new_region = region_chooser.getRegion()
                for watch_region in watch_regions:
                    watch_region.set_region(new_region)

            region_chooser.activated.connect(_apply_region_chooser)
        elif self._field_type in FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS:
            additional_requirements.append(FieldRequirementNaturalNumberValue("Number of Fields:"))

        self._properties = [{"group": "Parameters", "requirements": field_requirements}]
        self._properties.append({"group": "Additional Properties", "requirements": additional_requirements})

        if self._is_defined():
            for r in self._requirements():
                r.set_finalised()

        return self._properties

    def _define_additional_properties(self, new_field):
        additional_requirements = self._requirements("Additional Properties")
        if self._field_type == "FieldEdgeDiscontinuity":
            new_field.setMeasure(additional_requirements[0].value())
            conditional_field = additional_requirements[1].value()
            if conditional_field and conditional_field.isValid():
                new_field.setConditionalField(conditional_field)
        elif self._field_type == "FieldFindMeshLocation":
            new_field.setSearchMode(additional_requirements[0].value())
            new_field.setSearchMesh(additional_requirements[1].value())
        elif self._field_type == "FieldApply":
            new_field.setBindArgumentSourceField(additional_requirements[1].value(), additional_requirements[2].value())
        elif self._field_type == "FieldMeshIntegral":
            new_field.setNumbersOfPoints(additional_requirements[0].value())
            new_field.setElementQuadratureRule(additional_requirements[1].value())

    def define_new_field(self, field_module, field_name):
        field_requirements = self._requirements("Parameters")

        args = []
        for req in field_requirements:
            args.append(req.value())

        with ChangeManager(field_module):
            methodToCall = getattr(field_module, "create" + self._field_type)
            if self._field_type in FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS:
                new_field = methodToCall(args)
            else:
                new_field = methodToCall(*args)

            self._define_additional_properties(new_field)

            new_field.setName(field_name)
            new_field.setManaged(self._managed)
            new_field.setTypeCoordinate(self._type_coordinate)

        return new_field


class FieldInterface(FieldBase, FieldTypeBase):

    def __init__(self, field, field_type):
        super(FieldInterface, self).__init__()
        self.set_field(field)
        self.set_field_type(field_type)

    def defining_field(self):
        return self.get_field() is None and self.get_field_type() != NONE_FIELD_TYPE_NAME

    def field_is_known(self):
        return self.get_field() is not None or self.get_field_type() != NONE_FIELD_TYPE_NAME

    def can_define_field(self):
        return self.defining_field() and self.has_requirements_met()

    def field_display_label(self):
        if self.defining_field():
            return self.get_field_type()

        if self.get_field_type() != NONE_FIELD_TYPE_NAME:
            return self.get_field_type()

        field_name = self.get_field_name()
        if field_name in INTERNAL_FIELD_NAMES:
            return INTERNAL_FIELD_TYPE_NAME

        return NONE_FIELD_TYPE_NAME

    def properties_enabled(self):
        return self.get_field() is not None

    def set_managed(self, state):
        if self.defining_field():
            self._pre_set_managed(state)
        else:
            self._set_managed(state)

    def set_type_coordinate(self, state):
        if self.defining_field():
            self._pre_set_type_coordinate(state)
        else:
            self._set_type_coordinate(state)

    def is_managed(self):
        if self.defining_field():
            return self._pre_is_managed()

        return self._is_managed()

    def is_type_coordinate(self):
        if self.defining_field():
            return self._pre_is_type_coordinate()

        return self._is_type_coordinate()
