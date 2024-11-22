// *****************************************************************************
// File:			Property_Test_Helper.cpp
// Description:		Property_Test add-on helper macros and functions
// Project:			APITools/Property_Test
// Namespace:		-
// Contact person:	CSAT
// *****************************************************************************

#include "Property_Test_Helpers.hpp"

API_Guid PropertyTestHelpers::RandomGuid () {
	GS::Guid guid;
	guid.Generate ();
	return GSGuid2APIGuid (guid);
}


GS::UniString PropertyTestHelpers::GenearteUniqueName ()
{
	GS::Guid guid;
	guid.Generate ();
	return guid.ToUniString ();
}


API_PropertyGroup PropertyTestHelpers::CreateExamplePropertyGroup ()
{
	API_PropertyGroup group;
	group.guid = APINULLGuid;
	group.name = "Property_Test Add-On Group - " + PropertyTestHelpers::GenearteUniqueName ();
	group.description = "Its empty.";
	return group;
}


static API_PropertyGroup CreateCommonExamplePropertyGroup ()
{
	API_PropertyGroup group;
	group.guid = APINULLGuid;
	group.name = "Property_Test Add-On Group";
	group.description = "This group is generated by the Property_Test Add-On";
	return group;
}


GSErrCode PropertyTestHelpers::GetCommonExamplePropertyGroup (API_PropertyGroup& outGroup)
{
	static API_PropertyGroup staticGroup = CreateCommonExamplePropertyGroup ();
	if (ACAPI_Property_GetPropertyGroup (staticGroup) == APIERR_BADID) { // if the group does not exist
		GS::Array<API_PropertyGroup> groups;
		GSErrCode error = ACAPI_Property_GetPropertyGroups (groups);
		if (error != NoError) {
			return error;
		}

		for (UInt32 i = 0; i < groups.GetSize (); ++i) {
			if (groups[i].name == staticGroup.name) {
				outGroup = staticGroup = groups[i];
				return NoError;
			}
		}

		error = ACAPI_Property_CreatePropertyGroup (staticGroup);
		if (error != NoError) {
			return error;
		}
	}

	outGroup = staticGroup;
	return NoError;
}


static API_PropertyDefinition CreateExamplePropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition;
	definition.guid = APINULLGuid;
	definition.groupGuid = group.guid;
	definition.name = "Property_Test Add-On Definition - " + PropertyTestHelpers::GenearteUniqueName ();
	definition.description = "An example property definition.";
	return definition;
}


API_PropertyDefinition PropertyTestHelpers::CreateExampleBoolPropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition = CreateExamplePropertyDefinition (group);
	definition.collectionType = API_PropertySingleCollectionType;
	definition.valueType = API_PropertyBooleanValueType;
	definition.measureType = API_PropertyDefaultMeasureType;
	definition.defaultValue.basicValue.singleVariant.variant.type = definition.valueType;
	definition.defaultValue.basicValue.singleVariant.variant.boolValue = false;
	return definition;
}

API_PropertyDefinition PropertyTestHelpers::CreateExampleIntPropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition = CreateExamplePropertyDefinition (group);
	definition.collectionType = API_PropertySingleCollectionType;
	definition.valueType = API_PropertyIntegerValueType;
	definition.measureType = API_PropertyDefaultMeasureType;
	definition.defaultValue.basicValue.singleVariant.variant.type = definition.valueType;
	definition.defaultValue.basicValue.singleVariant.variant.intValue = 0;
	return definition;
}


API_PropertyDefinition PropertyTestHelpers::CreateExampleStringListPropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition = CreateExamplePropertyDefinition (group);
	definition.collectionType = API_PropertyListCollectionType;
	definition.valueType = API_PropertyStringValueType;
	definition.measureType = API_PropertyDefaultMeasureType;
	// default = empty list
	return definition;
}


API_PropertyDefinition PropertyTestHelpers::CreateExampleStringMultiEnumPropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition = CreateExamplePropertyDefinition (group);
	definition.collectionType = API_PropertyMultipleChoiceEnumerationCollectionType;
	definition.valueType = API_PropertyStringValueType;
	definition.measureType = API_PropertyDefaultMeasureType;

	API_SingleEnumerationVariant variant;
	variant.keyVariant.type = API_PropertyGuidValueType;
	variant.keyVariant.guidValue = RandomGuid ();
	variant.displayVariant.type = definition.valueType;
	variant.displayVariant.uniStringValue = "Apple";
	variant.nonLocalizedValue = GS::NoValue;
	definition.possibleEnumValues.Push (variant);

	// The default value will be apple
	definition.defaultValue.basicValue.listVariant.variants.Push (variant.keyVariant);

	variant.keyVariant.guidValue = RandomGuid ();
	variant.displayVariant.uniStringValue = "Pear";
	definition.possibleEnumValues.Push (variant);

	variant.keyVariant.guidValue = RandomGuid ();
	variant.displayVariant.uniStringValue = "Watermelon";
	definition.possibleEnumValues.Push (variant);

	return definition;
}



API_PropertyDefinition PropertyTestHelpers::CreateExampleExpressionPropertyDefinition (API_PropertyGroup group)
{
	API_PropertyDefinition definition = CreateExamplePropertyDefinition (group);
	definition.collectionType = API_PropertySingleCollectionType;
	definition.valueType = API_PropertyStringValueType;
	definition.measureType = API_PropertyDefaultMeasureType;
	definition.defaultValue.basicValue.singleVariant.variant.type = definition.valueType;

	definition.defaultValue.hasExpression = true;
	definition.defaultValue.propertyExpressions = {"1 + 1", "CONCAT ( \"a\", \"b\" )"};
	return definition;
}


GS::Array<API_Guid>	PropertyTestHelpers::GetSelectedElements (bool assertIfNoSel /* = true*/)
{
	GSErrCode            err;
	API_SelectionInfo    selectionInfo;
	GS::Array<API_Neig>  selNeigs;

	err = ACAPI_Selection_Get (&selectionInfo, &selNeigs, true);
	BMKillHandle ((GSHandle *)&selectionInfo.marquee.coords);
	if (err == APIERR_NOSEL || selectionInfo.typeID == API_SelEmpty) {
		if (assertIfNoSel) {
			DGAlert (DG_ERROR, "Error", "Please select an element!", "", "Ok");
		}
	}

	if (err != NoError) {
		return GS::Array<API_Guid>();
	}

	GS::Array<API_Guid> guidArray;
	for (const API_Neig& neig : selNeigs) {
		guidArray.Push (neig.guid);
	}

	return guidArray;
}


void PropertyTestHelpers::CallOnSelectedElem (void (*function)(const API_Guid&), bool assertIfNoSel /* = true*/)
{
	GS::Array<API_Guid> guidArray = GetSelectedElements (assertIfNoSel);
	if (guidArray.GetSize () > 0) {
		function (guidArray[0]);
	} else if (assertIfNoSel) {
		throw GS::Exception ("No selection");
	}
}


void PropertyTestHelpers::CallOnAllSelectedElems (void (*function)(const API_Guid&), bool assertIfNoSel /* = true*/)
{
	GS::Array<API_Guid> guidArray = GetSelectedElements (assertIfNoSel);
	if (guidArray.GetSize () > 0) {
		guidArray.EnumerateConst (function);
	} else if (assertIfNoSel) {
		throw GS::Exception ("No selection");
	}
}


void PropertyTestHelpers::DebugAssert (bool success, GS::UniString expression, const char* file, UInt32 line, const char* function)
{
	if (success) {
		return;
	}

	expression += " is false.";

#if defined (DEBUVERS)
	DBBreak (file, line, expression.ToCStr ().Get (), nullptr, function, nullptr);
#else
	UNUSED_PARAMETER (function);
	DGAlert (DG_ERROR, "Assertion",	expression,
			 "At: " + GS::UniString (file) + ":" + GS::ValueToUniString (line), "Ok");
#endif

	throw GS::Exception (expression);
}


void PropertyTestHelpers::DebugAssertNoError (GSErrCode error, GS::UniString expression, const char* file, UInt32 line, const char* function)
{
	if (error == NoError) {
		return;
	}

	expression += GS::UniString (" returned with ") + ErrID_To_Name (error) + ".";

#if defined (DEBUVERS)
	DBBreak (file, line, expression.ToCStr ().Get (), nullptr, function, nullptr);
#else
	UNUSED_PARAMETER (function);
	DGAlert (DG_ERROR, "Assertion",	expression,
			 "At: " + GS::UniString (file) + ":" + GS::ValueToUniString (line), "Ok");
#endif

	throw GS::Exception (expression);
}


bool operator== (const API_Variant& lhs, const API_Variant& rhs)
{
	if (lhs.type != rhs.type) {
		return false;
	}

	switch (lhs.type) {
		case API_PropertyIntegerValueType:
			return lhs.intValue == rhs.intValue;
		case API_PropertyRealValueType:
			return lhs.doubleValue == rhs.doubleValue;
		case API_PropertyStringValueType:
			return lhs.uniStringValue == rhs.uniStringValue;
		case API_PropertyBooleanValueType:
			return lhs.boolValue == rhs.boolValue;
		case API_PropertyGuidValueType:
			return lhs.guidValue == rhs.guidValue;
		default:
			return false;
	}
}


bool operator== (const API_SingleVariant& lhs, const API_SingleVariant& rhs)
{
	return lhs.variant == rhs.variant;
}


bool operator== (const API_ListVariant& lhs, const API_ListVariant& rhs)
{
	return lhs.variants == rhs.variants;
}


bool operator== (const API_SingleEnumerationVariant& lhs, const API_SingleEnumerationVariant& rhs)
{
	return lhs.keyVariant == rhs.keyVariant 
		&& lhs.displayVariant == rhs.displayVariant 
		&& lhs.nonLocalizedValue == rhs.nonLocalizedValue;
}


bool Equals (const API_PropertyDefaultValue& lhs, const API_PropertyDefaultValue& rhs, API_PropertyCollectionType collType)
{
	if (lhs.hasExpression != rhs.hasExpression) {
		return false;
	}

	if (lhs.hasExpression) {
		   return lhs.propertyExpressions == rhs.propertyExpressions;
	} else {
		   return Equals (lhs.basicValue, rhs.basicValue, collType);
	}
}


bool Equals (const API_PropertyValue& lhs, const API_PropertyValue& rhs, API_PropertyCollectionType collType)
{
	if (lhs.variantStatus != rhs.variantStatus) {
		return false;
	}

	if (lhs.variantStatus != API_VariantStatusNormal) {
		return true;
	}

	switch (collType) {
		case API_PropertySingleCollectionType:
		case API_PropertySingleChoiceEnumerationCollectionType:
			return lhs.singleVariant == rhs.singleVariant;
		case API_PropertyListCollectionType:
		case API_PropertyMultipleChoiceEnumerationCollectionType:
			return lhs.listVariant == rhs.listVariant;
		default:
			DBBREAK ();
			return false;
	}
}


bool operator== (const API_PropertyGroup& lhs, const API_PropertyGroup& rhs)
{
	return lhs.guid == rhs.guid &&
		   lhs.name == rhs.name;
}


bool operator== (const API_PropertyDefinition& lhs, const API_PropertyDefinition& rhs)
{
	return lhs.guid == rhs.guid &&
		   lhs.groupGuid == rhs.groupGuid &&
		   lhs.name == rhs.name &&
		   lhs.description == rhs.description &&
		   lhs.collectionType == rhs.collectionType &&
		   lhs.valueType == rhs.valueType &&
		   lhs.measureType == rhs.measureType &&
		   Equals (lhs.defaultValue, rhs.defaultValue, lhs.collectionType) &&
		   lhs.availability == rhs.availability &&
		   lhs.possibleEnumValues == rhs.possibleEnumValues;
}


bool operator== (const API_Property& lhs, const API_Property& rhs)
{
	if (lhs.definition != rhs.definition || lhs.isDefault != rhs.isDefault) {
		return false;
	}
	if (!lhs.isDefault) {
		return Equals (lhs.value, rhs.value, lhs.definition.collectionType);
	} else {
		return true;
	}
}
