#include "APIEnvir.h"
#include "ACAPinc.h" // ArchiCAD API includes
#include <fstream>
#include <iostream>

void SaveActiveProjectPath() {
    API_ProjectInfo projectInfo;
    GSErrCode err = ACAPI_Environment(APIEnv_ProjectID, &projectInfo, 0);

    if (err == NoError && projectInfo.location != nullptr) {
        IO::Path path;
        projectInfo.location->ToPath(&path);

        GS::UniString projectPath = path.ToString();

        // Write the path to a file
        std::ofstream outFile("C:\\path\\to\\output\\archicad_project_path.txt"); // Replace with the desired path
        if (outFile.is_open()) {
            outFile << projectPath.ToCStr().Get(); // Convert GS::UniString to C-string
            outFile.close();
        } else {
            ACAPI_WriteReport("Failed to open file for writing.", true);
        }
    } else {
        ACAPI_WriteReport("Error retrieving project info or no project loaded.", true);
    }
}

API_AddonType __ACENV_CALL CheckEnvironment(API_EnvirParams* envir) {
    return APIAddon_Normal;
}

GSErrCode __ACENV_CALL RegisterInterface(void) {
    return NoError;
}

GSErrCode __ACENV_CALL Initialize(void) {
    SaveActiveProjectPath(); // Call the function when the add-on is loaded
    return NoError;
}

GSErrCode __ACENV_CALL FreeData(void) {
    return NoError;
}
