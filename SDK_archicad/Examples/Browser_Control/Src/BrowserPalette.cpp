// *****************************************************************************
// Source code for the BrowserPalette class
// *****************************************************************************

// ---------------------------------- Includes ---------------------------------

#include	"BrowserPalette.hpp"

static const GS::Guid	paletteGuid ("{FEE27B6B-3873-4834-98B5-F0081AA4CD45}");

GS::Ref<BrowserPalette>	BrowserPalette::instance;

static GS::UniString LoadHtmlFromResource ()
{
	GS::UniString resourceData;
	GSHandle data = RSLoadResource ('DATA', ACAPI_GetOwnResModule (), 100);
	GSSize handleSize = BMhGetSize (data);
	if (data != nullptr) {
		resourceData.Append (*data, handleSize);
		BMhKill (&data);
	}
	return resourceData;
}

static GS::UniString GetStringFromJavaScriptVariable (GS::Ref<JS::Base> jsVariable)
{
	GS::Ref<JS::Value> jsValue = GS::DynamicCast<JS::Value> (jsVariable);
	if (DBVERIFY (jsValue != nullptr && jsValue->GetType () == JS::Value::STRING))
		return jsValue->GetString ();

	return GS::EmptyUniString;
}

template<class Type>
static GS::Ref<JS::Base> ConvertToJavaScriptVariable (const Type& cppVariable)
{
	return new JS::Value (cppVariable);
}

template<>
GS::Ref<JS::Base> ConvertToJavaScriptVariable (const BrowserPalette::ElementInfo& elemInfo)
{
	GS::Ref<JS::Array> js = new JS::Array ();
	js->AddItem (ConvertToJavaScriptVariable (elemInfo.guidStr));
	js->AddItem (ConvertToJavaScriptVariable (elemInfo.typeName));
	js->AddItem (ConvertToJavaScriptVariable (elemInfo.elemID));
	return js;
}

template<class Type>
static GS::Ref<JS::Base> ConvertToJavaScriptVariable (const GS::Array<Type>& cppArray)
{
	GS::Ref<JS::Array> newArray = new JS::Array ();
	for (const Type& item : cppArray) {
		newArray->AddItem (ConvertToJavaScriptVariable (item));
	}
	return newArray;
}

// -----------------------------------------------------------------------------
// Project event handler function
// -----------------------------------------------------------------------------
static GSErrCode NotificationHandler (API_NotifyEventID notifID, Int32 /*param*/)
{
	switch (notifID) {
		case APINotify_Quit:
			BrowserPalette::DestroyInstance ();
			break;
	}

	return NoError;
}   // NotificationHandler

// --- Class definition: BrowserPalette ----------------------------------------

BrowserPalette::BrowserPalette () :
	DG::Palette (ACAPI_GetOwnResModule (), BrowserPaletteResId, ACAPI_GetOwnResModule (), paletteGuid),
	browser (GetReference (), BrowserId)
{
	ACAPI_ProjectOperation_CatchProjectEvent (APINotify_Quit, NotificationHandler);
	Attach (*this);
	BeginEventProcessing ();
	InitBrowserControl ();
}

BrowserPalette::~BrowserPalette ()
{
	EndEventProcessing ();
}

bool BrowserPalette::HasInstance ()
{
	return instance != nullptr;
}

void BrowserPalette::CreateInstance ()
{
	DBASSERT (!HasInstance ());
	instance = new BrowserPalette ();
	ACAPI_KeepInMemory (true);
}

BrowserPalette&	BrowserPalette::GetInstance ()
{
	DBASSERT (HasInstance ());
	return *instance;
}

void BrowserPalette::DestroyInstance ()
{
	instance = nullptr;
}

void BrowserPalette::Show ()
{
	DG::Palette::Show ();
	SetMenuItemCheckedState (true);
}

void BrowserPalette::Hide ()
{
	DG::Palette::Hide ();
	SetMenuItemCheckedState (false);
}

void BrowserPalette::InitBrowserControl ()
{
	browser.LoadHTML (LoadHtmlFromResource ());
	RegisterACAPIJavaScriptObject ();
	UpdateSelectedElementsOnHTML ();
}

void  BrowserPalette::RegisterACAPIJavaScriptObject ()
{
	JS::Object* jsACAPI = new JS::Object ("ACAPI");

	jsACAPI->AddItem (new JS::Function ("GetSelectedElements", [] (GS::Ref<JS::Base>) {
		return ConvertToJavaScriptVariable (GetSelectedElements ());
	}));

	jsACAPI->AddItem (new JS::Function ("AddElementToSelection", [] (GS::Ref<JS::Base> param) {
		ModifySelection (GetStringFromJavaScriptVariable (param), AddToSelection);
		return ConvertToJavaScriptVariable (true);
	}));

	jsACAPI->AddItem (new JS::Function ("RemoveElementFromSelection", [] (GS::Ref<JS::Base> param) {
		ModifySelection (GetStringFromJavaScriptVariable (param), RemoveFromSelection);
		return ConvertToJavaScriptVariable (true);
	}));

	browser.RegisterAsynchJSObject (jsACAPI);
}

void BrowserPalette::UpdateSelectedElementsOnHTML ()
{
	browser.ExecuteJS ("UpdateSelectedElements ()");
}

void BrowserPalette::SetMenuItemCheckedState (bool isChecked)
{
	API_MenuItemRef	itemRef = {};
	GSFlags			itemFlags = {};

	itemRef.menuResID = BrowserPaletteMenuResId;
	itemRef.itemIndex = BrowserPaletteMenuItemIndex;

	ACAPI_MenuItem_GetMenuItemFlags (&itemRef, &itemFlags);
	if (isChecked)
		itemFlags |= API_MenuItemChecked;
	else
		itemFlags &= ~API_MenuItemChecked;
	ACAPI_MenuItem_SetMenuItemFlags (&itemRef, &itemFlags);
}

void BrowserPalette::PanelResized (const DG::PanelResizeEvent& ev)
{
	BeginMoveResizeItems ();
	browser.Resize (ev.GetHorizontalChange (), ev.GetVerticalChange ());
	EndMoveResizeItems ();
}

void BrowserPalette::PanelCloseRequested (const DG::PanelCloseRequestEvent&, bool* accepted)
{
	Hide ();
	*accepted = true;
}

GS::Array<BrowserPalette::ElementInfo> BrowserPalette::GetSelectedElements ()
{
	API_SelectionInfo	selectionInfo;
	GS::Array<API_Neig>	selNeigs;
	ACAPI_Selection_Get (&selectionInfo, &selNeigs, false, false);
	BMKillHandle ((GSHandle*)&selectionInfo.marquee.coords);

	GS::Array<BrowserPalette::ElementInfo> selectedElements;
	for (const API_Neig& neig : selNeigs) {
		API_Elem_Head elemHead = {};
		elemHead.guid = neig.guid;
		ACAPI_Element_GetHeader (&elemHead);

		ElementInfo elemInfo;
		elemInfo.guidStr = APIGuidToString (elemHead.guid);
		ACAPI_Element_GetElemTypeName (elemHead.type, elemInfo.typeName);
		ACAPI_Element_GetElementInfoString (&elemHead.guid, &elemInfo.elemID);
		selectedElements.Push (elemInfo);
	}
	return selectedElements;
}

void BrowserPalette::ModifySelection (const GS::UniString& elemGuidStr, BrowserPalette::SelectionModification modification)
{
	ACAPI_Selection_Select ({ API_Neig (APIGuidFromString (elemGuidStr.ToCStr ().Get ())) }, modification == AddToSelection);
}

GSErrCode BrowserPalette::SelectionChangeHandler (const API_Neig*)
{
	if (BrowserPalette::HasInstance ())
		BrowserPalette::GetInstance ().UpdateSelectedElementsOnHTML ();
	return NoError;
}

GSErrCode BrowserPalette::PaletteControlCallBack (Int32, API_PaletteMessageID messageID, GS::IntPtr param)
{
	switch (messageID) {
		case APIPalMsg_OpenPalette:
			if (!HasInstance ())
				CreateInstance ();
			GetInstance ().Show ();
			break;

		case APIPalMsg_ClosePalette:
			if (!HasInstance ())
				break;
			GetInstance ().Hide ();
			break;

		case APIPalMsg_HidePalette_Begin:
			if (HasInstance () && GetInstance ().IsVisible ())
				GetInstance ().Hide ();
			break;

		case APIPalMsg_HidePalette_End:
			if (HasInstance () && !GetInstance ().IsVisible ())
				GetInstance ().Show ();
			break;

		case APIPalMsg_DisableItems_Begin:
			if (HasInstance () && GetInstance ().IsVisible ())
				GetInstance ().DisableItems ();
			break;

		case APIPalMsg_DisableItems_End:
			if (HasInstance () && GetInstance ().IsVisible ())
				GetInstance ().EnableItems ();
			break;

		case APIPalMsg_IsPaletteVisible:
			*(reinterpret_cast<bool*> (param)) = HasInstance () && GetInstance ().IsVisible ();
			break;

		default:
			break;
	}

	return NoError;
}

GSErrCode BrowserPalette::RegisterPaletteControlCallBack ()
{
	return ACAPI_RegisterModelessWindow (
					GS::CalculateHashValue (paletteGuid),
					PaletteControlCallBack,
					API_PalEnabled_FloorPlan + API_PalEnabled_Section + API_PalEnabled_Elevation +
					API_PalEnabled_InteriorElevation + API_PalEnabled_3D + API_PalEnabled_Detail +
					API_PalEnabled_Worksheet + API_PalEnabled_Layout + API_PalEnabled_DocumentFrom3D,
					GSGuid2APIGuid (paletteGuid));
}
